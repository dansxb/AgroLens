"""Unit tests for NDVI, NDRE, cloud masking, and temporal compositing."""

from __future__ import annotations

import numpy as np
import pytest

from ml.cloud_mask import apply_scl_cloud_mask
from ml.indices.composite import compute_composite
from ml.indices.ndre import compute_ndre
from ml.indices.ndvi import compute_ndvi


class TestComputeNdvi:
    def test_correct_formula(self) -> None:
        nir = np.array([[0.6, 0.8]], dtype=np.float32)
        red = np.array([[0.2, 0.2]], dtype=np.float32)
        mask = np.array([[True, True]])

        result = compute_ndvi(nir, red, mask)

        expected = (nir - red) / (nir + red)
        np.testing.assert_allclose(result, expected, rtol=1e-5)

    def test_values_in_minus_one_to_one(self) -> None:
        rng = np.random.default_rng(42)
        nir = rng.random((50, 50)).astype(np.float32)
        red = rng.random((50, 50)).astype(np.float32)
        mask = np.ones((50, 50), dtype=bool)

        result = compute_ndvi(nir, red, mask)
        valid = result[~np.isnan(result)]

        assert np.all(valid >= -1.0)
        assert np.all(valid <= 1.0)

    def test_masked_pixels_are_nan(self) -> None:
        nir = np.ones((3, 3), dtype=np.float32) * 0.5
        red = np.ones((3, 3), dtype=np.float32) * 0.2
        mask = np.array([
            [True,  False, True],
            [False, True,  False],
            [True,  True,  True],
        ])

        result = compute_ndvi(nir, red, mask)

        assert np.isnan(result[0, 1])
        assert np.isnan(result[1, 0])
        assert not np.isnan(result[0, 0])

    def test_zero_denominator_is_nan(self) -> None:
        nir = np.zeros((2, 2), dtype=np.float32)
        red = np.zeros((2, 2), dtype=np.float32)
        mask = np.ones((2, 2), dtype=bool)

        result = compute_ndvi(nir, red, mask)

        assert np.all(np.isnan(result))

    def test_shape_mismatch_raises(self) -> None:
        nir = np.ones((3, 3), dtype=np.float32)
        red = np.ones((4, 3), dtype=np.float32)
        mask = np.ones((3, 3), dtype=bool)

        with pytest.raises(ValueError, match="Shape mismatch"):
            compute_ndvi(nir, red, mask)

    def test_output_is_float32(self) -> None:
        nir = np.array([[0.5]], dtype=np.float32)
        red = np.array([[0.3]], dtype=np.float32)
        mask = np.array([[True]])

        result = compute_ndvi(nir, red, mask)
        assert result.dtype == np.float32


class TestComputeNdre:
    def test_correct_formula(self) -> None:
        re = np.array([[0.5, 0.7]], dtype=np.float32)
        red = np.array([[0.2, 0.3]], dtype=np.float32)
        mask = np.array([[True, True]])

        result = compute_ndre(re, red, mask)
        expected = (re - red) / (re + red)

        np.testing.assert_allclose(result, expected, rtol=1e-5)

    def test_masked_pixels_are_nan(self) -> None:
        re = np.ones((2, 2), dtype=np.float32) * 0.5
        red = np.ones((2, 2), dtype=np.float32) * 0.2
        mask = np.array([[True, False], [False, True]])

        result = compute_ndre(re, red, mask)

        assert np.isnan(result[0, 1])
        assert np.isnan(result[1, 0])

    def test_shape_mismatch_raises(self) -> None:
        with pytest.raises(ValueError, match="Shape mismatch"):
            compute_ndre(
                np.ones((3, 3), dtype=np.float32),
                np.ones((4, 3), dtype=np.float32),
                np.ones((3, 3), dtype=bool),
            )


class TestApplySclCloudMask:
    def test_valid_pixels_are_true(self) -> None:
        # Class 4 = Vegetation (valid), Class 5 = Not-vegetated (valid)
        scl = np.array([[4, 5, 6, 7]], dtype=np.uint8)
        mask = apply_scl_cloud_mask(scl)
        assert np.all(mask)

    def test_invalid_pixels_are_false(self) -> None:
        invalid_classes = [0, 1, 3, 8, 9, 10, 11]
        scl = np.array([invalid_classes], dtype=np.uint8)
        mask = apply_scl_cloud_mask(scl)
        assert not np.any(mask)

    def test_mixed_scene(self) -> None:
        # Row 0: valid (4=veg, 5=soil)  Row 1: invalid (8=cloud, 9=cloud)
        scl = np.array([[4, 5], [8, 9]], dtype=np.uint8)
        mask = apply_scl_cloud_mask(scl)

        assert mask[0, 0] is np.bool_(True)
        assert mask[0, 1] is np.bool_(True)
        assert mask[1, 0] is np.bool_(False)
        assert mask[1, 1] is np.bool_(False)

    def test_output_shape_matches_input(self) -> None:
        scl = np.zeros((10, 20), dtype=np.uint8)
        mask = apply_scl_cloud_mask(scl)
        assert mask.shape == (10, 20)
        assert mask.dtype == bool


class TestComputeComposite:
    def test_median_two_scenes(self) -> None:
        a = np.array([[0.2, 0.4], [0.6, 0.8]], dtype=np.float32)
        b = np.array([[0.4, 0.6], [0.8, 1.0]], dtype=np.float32)
        result = compute_composite([a, b], method="median")

        expected = np.median(np.stack([a, b], axis=0), axis=0)
        np.testing.assert_allclose(result, expected, rtol=1e-5)

    def test_mean_method(self) -> None:
        a = np.array([[0.2, 0.6]], dtype=np.float32)
        b = np.array([[0.4, 0.8]], dtype=np.float32)
        result = compute_composite([a, b], method="mean")

        np.testing.assert_allclose(result, [[0.3, 0.7]], rtol=1e-5)

    def test_nan_pixels_ignored(self) -> None:
        a = np.array([[np.nan, 0.5]], dtype=np.float32)
        b = np.array([[0.4, 0.7]], dtype=np.float32)
        result = compute_composite([a, b], method="median")

        # First pixel: only b contributes (a is NaN)
        assert abs(result[0, 0] - 0.4) < 1e-5
        # Second pixel: median of 0.5 and 0.7
        assert abs(result[0, 1] - 0.6) < 1e-4

    def test_all_nan_stays_nan(self) -> None:
        a = np.full((2, 2), np.nan, dtype=np.float32)
        b = np.full((2, 2), np.nan, dtype=np.float32)
        result = compute_composite([a, b])
        assert np.all(np.isnan(result))

    def test_output_is_float32(self) -> None:
        a = np.ones((3, 3), dtype=np.float32)
        result = compute_composite([a])
        assert result.dtype == np.float32

    def test_empty_list_raises(self) -> None:
        with pytest.raises(ValueError, match="must not be empty"):
            compute_composite([])

    def test_invalid_method_raises(self) -> None:
        a = np.ones((2, 2), dtype=np.float32)
        with pytest.raises(ValueError, match="Unsupported method"):
            compute_composite([a], method="max")

    def test_shape_mismatch_raises(self) -> None:
        a = np.ones((3, 3), dtype=np.float32)
        b = np.ones((4, 3), dtype=np.float32)
        with pytest.raises(ValueError, match="same shape"):
            compute_composite([a, b])
