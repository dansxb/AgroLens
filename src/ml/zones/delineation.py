"""Management zone delineation via k-means clustering on NDVI/NDRE composites.

Pixels are clustered in 2-D [NDVI, NDRE] feature space using scikit-learn
k-means.  The resulting zones are labelled Low / Medium / High (/ Very High
for k>3) ordered by mean NDVI centroid value so that:

  - **Low**:   lowest NDVI → most stressed area  → lowest application rate
  - **Medium** / intermediate zones: baseline range
  - **High**:  highest NDVI → most vigorous growth → highest attention (fungal risk)

The function accepts *any* k in [2, 5], defaulting to 3.  Only valid (non-NaN)
pixels are used for fitting; the cluster labels array preserves NaN positions.
"""

from __future__ import annotations

import logging
from typing import Literal

import numpy as np
from sklearn.cluster import KMeans

logger = logging.getLogger(__name__)

# Ordered zone labels for k=2..5
_ZONE_LABELS: dict[int, list[str]] = {
    2: ["Low", "High"],
    3: ["Low", "Medium", "High"],
    4: ["Low", "Medium", "High", "Very High"],
    5: ["Low", "Medium-Low", "Medium", "Medium-High", "High"],
}


def delineate_zones(
    ndvi: np.ndarray,
    ndre: np.ndarray,
    n_zones: int = 3,
    random_state: int = 42,
) -> tuple[np.ndarray, list[str], np.ndarray]:
    """Cluster field pixels into management zones using k-means on [NDVI, NDRE].

    Only pixels that are valid in *both* index arrays (no NaN) are used for
    fitting.  The returned label array has the same shape as the inputs; pixels
    that were NaN in either input are assigned -1 (invalid / no-data).

    Args:
        ndvi: 2-D float32 array of NDVI values (-1..1), NaN for masked pixels.
        ndre: 2-D float32 array of NDRE values (-1..1), NaN for masked pixels.
        n_zones: Number of clusters to produce.  Must be in [2, 5].
        random_state: Seed for reproducible k-means initialisation.

    Returns:
        A tuple of:
          - ``zone_map``: int8 array with same shape as inputs.  Values are
            0..n_zones-1 ordered from lowest to highest NDVI centroid.
            Invalid pixels are -1.
          - ``zone_names``: list of human-readable zone names in centroid order,
            length == n_zones (e.g. ["Low", "Medium", "High"]).
          - ``centroids``: (n_zones, 2) float64 array of [NDVI, NDRE] centroid
            values in zone order (useful for debugging / reporting).

    Raises:
        ValueError: If ``n_zones`` is outside [2, 5].
        ValueError: If ``ndvi`` and ``ndre`` do not have the same shape.
        ValueError: If fewer than ``n_zones`` valid pixels exist.
    """
    if not (2 <= n_zones <= 5):
        raise ValueError(f"n_zones must be between 2 and 5, got {n_zones}")
    if ndvi.shape != ndre.shape:
        raise ValueError(
            f"ndvi and ndre must have the same shape: "
            f"{ndvi.shape} vs {ndre.shape}"
        )

    valid_mask = ~(np.isnan(ndvi) | np.isnan(ndre))
    n_valid = int(valid_mask.sum())
    if n_valid < n_zones:
        raise ValueError(
            f"Only {n_valid} valid pixels — need at least {n_zones} to form zones."
        )

    features = np.column_stack(
        [ndvi[valid_mask].astype(np.float64), ndre[valid_mask].astype(np.float64)]
    )

    kmeans = KMeans(n_clusters=n_zones, random_state=random_state, n_init="auto")
    raw_labels = kmeans.fit_predict(features)

    # Re-order clusters by ascending NDVI centroid value
    ndvi_centroids = kmeans.cluster_centers_[:, 0]
    order = np.argsort(ndvi_centroids)
    remap = np.empty(n_zones, dtype=np.int8)
    remap[order] = np.arange(n_zones, dtype=np.int8)
    ordered_labels = remap[raw_labels]

    zone_map = np.full(ndvi.shape, -1, dtype=np.int8)
    zone_map[valid_mask] = ordered_labels

    centroids_ordered = kmeans.cluster_centers_[order]
    zone_names = _ZONE_LABELS[n_zones]

    logger.info(
        "Zone delineation complete: n_zones=%d, valid_pixels=%d, "
        "centroids(NDVI)=%s",
        n_zones,
        n_valid,
        np.round(centroids_ordered[:, 0], 3).tolist(),
    )

    return zone_map, zone_names, centroids_ordered
