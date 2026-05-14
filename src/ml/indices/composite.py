"""Temporal compositing for vegetation index rasters.

Aggregates a stack of per-scene index arrays into a single representative
composite by computing the pixel-wise median (or mean) while ignoring
NaN values (masked by cloud or no-data pixels).
"""

from __future__ import annotations

import numpy as np


def compute_composite(
    index_arrays: list[np.ndarray],
    method: str = "median",
) -> np.ndarray:
    """Compute a pixel-wise temporal composite from a list of index arrays.

    Args:
        index_arrays: List of float32 arrays each with shape H×W.
            NaN values (masked pixels) are ignored in the aggregation.
            All arrays must have the same shape.
        method: Aggregation method — ``"median"`` (default) or ``"mean"``.
            Median is preferred for vegetation indices because it is robust
            to residual cloud contamination.

    Returns:
        Float32 array of shape H×W.  Pixels that are NaN in *all* input
        scenes remain NaN in the output (indicating persistent cloud cover
        or no-data throughout the compositing period).

    Raises:
        ValueError: If ``index_arrays`` is empty, arrays have mismatched
            shapes, or ``method`` is not ``"median"`` or ``"mean"``.
    """
    if not index_arrays:
        raise ValueError("index_arrays must not be empty.")

    if method not in {"median", "mean"}:
        raise ValueError(f"Unsupported method {method!r}. Use 'median' or 'mean'.")

    shapes = {arr.shape for arr in index_arrays}
    if len(shapes) > 1:
        raise ValueError(f"All index arrays must have the same shape; got {shapes}.")

    stack = np.stack(index_arrays, axis=0).astype(np.float32)  # (T, H, W)

    if method == "median":
        composite = np.nanmedian(stack, axis=0).astype(np.float32)
    else:
        composite = np.nanmean(stack, axis=0).astype(np.float32)

    return composite
