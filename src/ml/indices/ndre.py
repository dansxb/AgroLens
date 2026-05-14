"""NDRE (Normalized Difference Red-Edge Index) computation.

NDRE = (RedEdge - Red) / (RedEdge + Red)

Uses Sentinel-2 Band 5 (Red-Edge 1, 705 nm) and Band 4 (Red, 665 nm).
NDRE is more sensitive than NDVI to chlorophyll content in moderate-to-high
biomass canopies, making it valuable for in-season crop stress detection.
"""

from __future__ import annotations

import numpy as np


def compute_ndre(
    red_edge: np.ndarray,
    red: np.ndarray,
    mask: np.ndarray,
) -> np.ndarray:
    """Compute per-pixel NDRE from Red-Edge and Red reflectance bands.

    Args:
        red_edge: Red-Edge reflectance array (Band 5, float32, shape H×W).
        red: Red reflectance array (Band 4, float32, shape H×W).
        mask: Boolean validity mask (True = valid pixel, False = cloud/invalid).
            Shape must match ``red_edge`` and ``red``.

    Returns:
        Float32 array of shape H×W with NDRE values in [-1, 1].
        Masked pixels (``mask == False``) are set to ``nan``.
        Pixels where ``(red_edge + red) == 0`` are set to ``nan``.

    Raises:
        ValueError: If ``red_edge``, ``red``, and ``mask`` have different shapes.
    """
    if red_edge.shape != red.shape or red_edge.shape != mask.shape:
        raise ValueError(
            f"Shape mismatch: red_edge={red_edge.shape}, "
            f"red={red.shape}, mask={mask.shape}"
        )

    re_f = red_edge.astype(np.float32)
    red_f = red.astype(np.float32)

    with np.errstate(invalid="ignore", divide="ignore"):
        denominator = re_f + red_f
        ndre = np.where(
            denominator == 0,
            np.nan,
            (re_f - red_f) / denominator,
        ).astype(np.float32)

    # Apply cloud/invalid mask
    ndre[~mask] = np.nan

    return ndre
