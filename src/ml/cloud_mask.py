"""Cloud masking using the Sentinel-2 Scene Classification Layer (SCL).

The SCL band produced by the Sen2Cor processor assigns a class label
to every pixel.  This module converts the SCL raster into a boolean
validity mask suitable for NDVI/NDRE computation.
"""

from __future__ import annotations

import numpy as np

# SCL class values that indicate invalid (cloud, shadow, snow, water) pixels.
_INVALID_SCL_CLASSES: frozenset[int] = frozenset(
    {
        0,   # No data
        1,   # Saturated / defective
        3,   # Cloud shadow
        8,   # Cloud, medium probability
        9,   # Cloud, high probability
        10,  # Thin cirrus
        11,  # Snow / ice
    }
)


def apply_scl_cloud_mask(scl: np.ndarray) -> np.ndarray:
    """Convert a Sentinel-2 SCL raster to a boolean validity mask.

    Args:
        scl: Integer array of SCL class values, shape H×W (uint8 or int).

    Returns:
        Boolean array of shape H×W where:
        - ``True``  → valid, cloud-free land pixel
        - ``False`` → cloud, shadow, snow, ice, no-data, or saturated pixel

    Masked classes: 0 (No data), 1 (Saturated), 3 (Cloud shadow),
    8 (Cloud medium), 9 (Cloud high), 10 (Thin cirrus), 11 (Snow/ice).
    """
    mask = np.ones(scl.shape, dtype=bool)
    for cls in _INVALID_SCL_CLASSES:
        mask &= scl != cls
    return mask
