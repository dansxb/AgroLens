"""NDVI (Normalized Difference Vegetation Index) computation.

NDVI = (NIR - Red) / (NIR + Red)

Values range from -1 to 1.  Healthy green vegetation typically shows
values above 0.3; bare soil 0–0.1; water and cloud pixels are masked
to NaN before computation.
"""

from __future__ import annotations

import numpy as np


def compute_ndvi(
    nir: np.ndarray,
    red: np.ndarray,
    mask: np.ndarray,
) -> np.ndarray:
    """Compute per-pixel NDVI from NIR and Red reflectance bands.

    Args:
        nir: NIR reflectance array (Band 8, float32, shape H×W).
        red: Red reflectance array (Band 4, float32, shape H×W).
        mask: Boolean validity mask (True = valid pixel, False = cloud/invalid).
            Shape must match ``nir`` and ``red``.

    Returns:
        Float32 array of shape H×W with NDVI values in [-1, 1].
        Masked pixels (``mask == False``) are set to ``nan``.
        Pixels where ``(nir + red) == 0`` are also set to ``nan``
        to avoid division by zero.

    Raises:
        ValueError: If ``nir``, ``red``, and ``mask`` have different shapes.
    """
    if nir.shape != red.shape or nir.shape != mask.shape:
        raise ValueError(
            f"Shape mismatch: nir={nir.shape}, red={red.shape}, mask={mask.shape}"
        )

    nir_f = nir.astype(np.float32)
    red_f = red.astype(np.float32)

    with np.errstate(invalid="ignore", divide="ignore"):
        denominator = nir_f + red_f
        ndvi = np.where(
            denominator == 0,
            np.nan,
            (nir_f - red_f) / denominator,
        ).astype(np.float32)

    # Apply cloud/invalid mask — NaN out invalid pixels
    ndvi[~mask] = np.nan

    return ndvi
