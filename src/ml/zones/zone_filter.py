"""Minimum zone size filter for management zone maps.

After k-means clustering produces a zone map, small disconnected patches can
appear that are too small for variable-rate application equipment to target
accurately (typical spreader positioning error ≥ 0.5 ha).

This module merges sub-threshold pixels into the zone with the closest NDVI
centroid value, ensuring every zone in the final map is large enough to be
actionable.

Threshold rule (Landwirt-Validator recommendation):
  - Field area ≥ 10 ha  →  min zone size = 0.5 ha
  - Field area < 10 ha  →  min zone size = 1.0 ha  (precision < equipment capability)
"""

from __future__ import annotations

import logging

import numpy as np

logger = logging.getLogger(__name__)

# Pixel resolution of Sentinel-2 10m bands (metres per side)
_SENTINEL2_RESOLUTION_M = 10.0
_PIXEL_AREA_HA = (_SENTINEL2_RESOLUTION_M**2) / 10_000.0  # 0.01 ha per pixel


def filter_minimum_zone_size(
    zone_map: np.ndarray,
    centroids: np.ndarray,
    field_area_ha: float,
) -> np.ndarray:
    """Merge zones smaller than the area threshold into their nearest neighbour.

    Iterates over zones in ascending size order (smallest first).  When a zone
    has fewer pixels than the threshold, all its pixels are re-assigned to the
    zone whose NDVI centroid is nearest.  The process repeats until all zones
    exceed the threshold or only one zone remains.

    Args:
        zone_map: int8 array of zone labels (0..n_zones-1, -1 for invalid),
            as produced by :func:`~ml.zones.delineation.delineate_zones`.
        centroids: (n_zones, 2) float64 array of [NDVI, NDRE] centroid values
            in zone order, as returned by
            :func:`~ml.zones.delineation.delineate_zones`.
        field_area_ha: Total field area in hectares (used to choose threshold).

    Returns:
        A copy of ``zone_map`` with sub-threshold zones merged.  The returned
        array may have fewer distinct zone labels than the input if zones were
        merged away entirely.

    Raises:
        ValueError: If ``centroids`` shape does not match the number of unique
            valid zone labels in ``zone_map``.
    """
    threshold_ha = 0.5 if field_area_ha >= 10.0 else 1.0
    threshold_pixels = int(np.ceil(threshold_ha / _PIXEL_AREA_HA))

    result = zone_map.copy()
    valid = result >= 0

    unique_zones = sorted(z for z in np.unique(result) if z >= 0)
    n_zones = len(unique_zones)

    if n_zones != len(centroids):
        raise ValueError(
            f"centroids has {len(centroids)} rows but zone_map has {n_zones} distinct zones."
        )

    # Re-map zone labels to dense 0..n-1 indices (necessary after potential prior merges)
    zone_centroids = {int(z): centroids[i] for i, z in enumerate(unique_zones)}

    for _ in range(n_zones):
        unique_active = sorted(z for z in np.unique(result) if z >= 0)
        if len(unique_active) <= 1:
            break

        zone_counts = {z: int((result == z).sum()) for z in unique_active}
        smallest = min(unique_active, key=lambda z: zone_counts[z])

        if zone_counts[smallest] >= threshold_pixels:
            break  # All zones are large enough

        # Find nearest zone by NDVI centroid distance
        candidates = [z for z in unique_active if z != smallest]
        src_centroid = zone_centroids[smallest]
        nearest = min(
            candidates,
            key=lambda z: float(np.linalg.norm(src_centroid - zone_centroids[z])),
        )

        result[result == smallest] = nearest
        logger.info(
            "Merged zone %d (%d px, %.2f ha) into zone %d — below %.1f ha threshold",
            smallest,
            zone_counts[smallest],
            zone_counts[smallest] * _PIXEL_AREA_HA,
            nearest,
            threshold_ha,
        )
        del zone_centroids[smallest]

    return result
