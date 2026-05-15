"""Unit tests for ml.zones.delineation and ml.zones.zone_filter."""

from __future__ import annotations

import numpy as np
import pytest

from ml.zones.delineation import delineate_zones
from ml.zones.zone_filter import _PIXEL_AREA_HA, filter_minimum_zone_size

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_gradient_arrays(
    rows: int = 30,
    cols: int = 30,
    seed: int = 0,
) -> tuple[np.ndarray, np.ndarray]:
    """Create synthetic NDVI/NDRE arrays with three distinct value bands."""
    rng = np.random.default_rng(seed)
    ndvi = np.zeros((rows, cols), dtype=np.float32)
    ndre = np.zeros((rows, cols), dtype=np.float32)
    third = rows // 3
    # Low band: ~0.1, Medium: ~0.4, High: ~0.7
    ndvi[:third] = 0.1 + rng.random((third, cols)).astype(np.float32) * 0.05
    ndvi[third : 2 * third] = 0.4 + rng.random((third, cols)).astype(np.float32) * 0.05
    ndvi[2 * third :] = (
        0.7 + rng.random((rows - 2 * third, cols)).astype(np.float32) * 0.05
    )
    ndre = ndvi * 0.8 + rng.random((rows, cols)).astype(np.float32) * 0.02
    return ndvi, ndre


# ---------------------------------------------------------------------------
# delineate_zones
# ---------------------------------------------------------------------------


class TestDelineateZones:
    def test_default_k3_returns_three_zones(self) -> None:
        ndvi, ndre = _make_gradient_arrays()
        zone_map, zone_names, centroids = delineate_zones(ndvi, ndre, n_zones=3)
        assert set(zone_names) == {"Low", "Medium", "High"}
        assert centroids.shape == (3, 2)

    def test_zone_map_shape_matches_input(self) -> None:
        ndvi, ndre = _make_gradient_arrays(20, 25)
        zone_map, _, _ = delineate_zones(ndvi, ndre, n_zones=3)
        assert zone_map.shape == (20, 25)

    def test_centroids_ordered_ascending_ndvi(self) -> None:
        ndvi, ndre = _make_gradient_arrays()
        _, _, centroids = delineate_zones(ndvi, ndre, n_zones=3)
        ndvi_vals = centroids[:, 0]
        assert list(ndvi_vals) == sorted(ndvi_vals), "Centroids must be NDVI-ascending"

    def test_k2_returns_two_zones(self) -> None:
        ndvi, ndre = _make_gradient_arrays()
        zone_map, zone_names, centroids = delineate_zones(ndvi, ndre, n_zones=2)
        assert len(zone_names) == 2
        assert centroids.shape == (2, 2)
        assert set(np.unique(zone_map[zone_map >= 0])).issubset({0, 1})

    def test_k5_returns_five_zones(self) -> None:
        ndvi, ndre = _make_gradient_arrays(50, 50)
        _, zone_names, centroids = delineate_zones(ndvi, ndre, n_zones=5)
        assert len(zone_names) == 5
        assert centroids.shape == (5, 2)

    def test_nan_pixels_assigned_minus_one(self) -> None:
        ndvi, ndre = _make_gradient_arrays()
        ndvi[0, 0] = np.nan
        ndre[5, 5] = np.nan
        zone_map, _, _ = delineate_zones(ndvi, ndre)
        assert zone_map[0, 0] == -1
        assert zone_map[5, 5] == -1

    def test_invalid_n_zones_raises(self) -> None:
        ndvi, ndre = _make_gradient_arrays()
        with pytest.raises(ValueError, match="n_zones"):
            delineate_zones(ndvi, ndre, n_zones=1)
        with pytest.raises(ValueError, match="n_zones"):
            delineate_zones(ndvi, ndre, n_zones=6)

    def test_shape_mismatch_raises(self) -> None:
        ndvi = np.zeros((10, 10), dtype=np.float32)
        ndre = np.zeros((10, 11), dtype=np.float32)
        with pytest.raises(ValueError, match="same shape"):
            delineate_zones(ndvi, ndre)

    def test_too_few_valid_pixels_raises(self) -> None:
        ndvi = np.full((5, 5), np.nan, dtype=np.float32)
        ndre = np.full((5, 5), np.nan, dtype=np.float32)
        ndvi[0, 0] = 0.3
        ndre[0, 0] = 0.2
        with pytest.raises(ValueError, match="valid pixels"):
            delineate_zones(ndvi, ndre, n_zones=3)

    def test_reproducible_with_same_seed(self) -> None:
        ndvi, ndre = _make_gradient_arrays()
        zm1, _, _ = delineate_zones(ndvi, ndre, random_state=7)
        zm2, _, _ = delineate_zones(ndvi, ndre, random_state=7)
        np.testing.assert_array_equal(zm1, zm2)


# ---------------------------------------------------------------------------
# filter_minimum_zone_size
# ---------------------------------------------------------------------------


class TestFilterMinimumZoneSize:
    def _tiny_zone_map(self) -> tuple[np.ndarray, np.ndarray]:
        """Create a 100×100 zone map where zone 2 (High) covers only 2 pixels."""
        zone_map = np.zeros((100, 100), dtype=np.int8)
        zone_map[50:, :] = 1
        zone_map[0, 0] = 2  # only 1 pixel in zone 2
        centroids = np.array([[0.1, 0.08], [0.4, 0.32], [0.7, 0.56]])
        return zone_map, centroids

    def test_small_zone_merged_into_nearest(self) -> None:
        zone_map, centroids = self._tiny_zone_map()
        result = filter_minimum_zone_size(zone_map, centroids, field_area_ha=15.0)
        # Zone 2 (High, centroid NDVI=0.7) should be absorbed into zone 1 (medium, NDVI=0.4)
        # because zone 1 centroid (0.4) is closer than zone 0 (0.1)
        assert 2 not in np.unique(result)

    def test_large_zones_unchanged(self) -> None:
        ndvi, ndre = _make_gradient_arrays(100, 100)
        zone_map, zone_names, centroids = delineate_zones(ndvi, ndre, n_zones=3)
        result = filter_minimum_zone_size(zone_map, centroids, field_area_ha=20.0)
        # With 100×100 array all zones should be well above 0.5 ha threshold
        unique_before = set(z for z in np.unique(zone_map) if z >= 0)
        unique_after = set(z for z in np.unique(result) if z >= 0)
        assert unique_before == unique_after

    def test_threshold_0_5_ha_for_large_field(self) -> None:
        # 0.5 ha = 50 pixels at 10m resolution
        threshold_px = int(0.5 / _PIXEL_AREA_HA)
        zone_map = np.zeros((200, 200), dtype=np.int8)
        # Zone 1 covers exactly threshold_px - 1 pixels (just below threshold)
        zone_map[:1, : threshold_px - 1] = 1
        centroids = np.array([[0.2, 0.16], [0.7, 0.56]])
        result = filter_minimum_zone_size(zone_map, centroids, field_area_ha=12.0)
        assert 1 not in np.unique(result)

    def test_threshold_1_ha_for_small_field(self) -> None:
        # 1.0 ha = 100 pixels at 10m resolution
        threshold_px = int(1.0 / _PIXEL_AREA_HA)
        zone_map = np.zeros((200, 200), dtype=np.int8)
        zone_map[:1, : threshold_px - 1] = 1
        centroids = np.array([[0.2, 0.16], [0.7, 0.56]])
        result = filter_minimum_zone_size(zone_map, centroids, field_area_ha=5.0)
        assert 1 not in np.unique(result)

    def test_centroid_mismatch_raises(self) -> None:
        zone_map = np.zeros((10, 10), dtype=np.int8)
        zone_map[5:] = 1
        centroids = np.array([[0.2, 0.16]])  # only 1 centroid for 2 zones
        with pytest.raises(ValueError, match="centroids"):
            filter_minimum_zone_size(zone_map, centroids, field_area_ha=5.0)
