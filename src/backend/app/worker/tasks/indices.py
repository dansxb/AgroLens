"""Celery task: compute NDVI and NDRE composites for a field.

Retrieves stored satellite scenes in a compositing window, computes
per-pixel NDVI and NDRE, generates median composites, uploads them
to S3, and records the resulting VegetationIndex rows in the database.
"""

from __future__ import annotations

import logging
import uuid
from datetime import date

from celery import Task

from app.worker.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(
    bind=True,
    name="indices.compute_field_indices",
    max_retries=2,
    default_retry_delay=600,
)
def compute_field_indices(
    self: Task,
    field_id: str,
    composite_start: str,
    composite_end: str,
) -> dict[str, str]:
    """Compute NDVI and NDRE median composites for a field over a time window.

    Args:
        field_id: UUID string of the field to process.
        composite_start: Start date of the compositing window (YYYY-MM-DD).
        composite_end: End date of the compositing window (YYYY-MM-DD).

    Returns:
        Dict with ``ndvi_s3_key`` and ``ndre_s3_key`` of the uploaded
        composite rasters, or empty strings if no scenes were available.
    """
    import numpy as np
    from rasterio.crs import CRS
    from rasterio.transform import from_bounds
    from sqlalchemy import and_, select

    from app.db.session import SessionLocal
    from app.models.satellite_scene import SatelliteScene
    from app.models.vegetation_index import VegetationIndex
    from app.services.s3_storage import download_geotiff, upload_geotiff
    from ml.cloud_mask import apply_scl_cloud_mask
    from ml.indices.composite import compute_composite
    from ml.indices.ndre import compute_ndre
    from ml.indices.ndvi import compute_ndvi

    start = date.fromisoformat(composite_start)
    end = date.fromisoformat(composite_end)
    field_uuid = uuid.UUID(field_id)

    logger.info(
        "compute_field_indices: field=%s window=%s–%s", field_id, start, end
    )

    # Load all complete scenes in the compositing window
    with SessionLocal() as db:
        scenes = db.execute(
            select(SatelliteScene).where(
                and_(
                    SatelliteScene.field_id == field_uuid,
                    SatelliteScene.status == "complete",
                    SatelliteScene.acquired_at >= start,
                    SatelliteScene.acquired_at <= end,
                )
            )
        ).scalars().all()

    if not scenes:
        logger.warning(
            "compute_field_indices: no complete scenes for field=%s in %s–%s",
            field_id, start, end,
        )
        return {"ndvi_s3_key": "", "ndre_s3_key": ""}

    ndvi_arrays: list[np.ndarray] = []
    ndre_arrays: list[np.ndarray] = []
    profile_ref: dict | None = None

    for scene in scenes:
        prefix = scene.bands_s3_key
        try:
            b04, profile = download_geotiff(f"{prefix}/B04.tif")
            b05, _ = download_geotiff(f"{prefix}/B05.tif")
            b08, _ = download_geotiff(f"{prefix}/B08.tif")
            scl, _ = download_geotiff(f"{prefix}/SCL.tif")
        except RuntimeError as exc:
            logger.error(
                "compute_field_indices: failed to download bands for scene %s: %s",
                scene.scene_id, exc,
            )
            continue

        mask = apply_scl_cloud_mask(scl.astype(np.uint8))
        ndvi_arrays.append(compute_ndvi(b08.astype(np.float32), b04.astype(np.float32), mask))
        ndre_arrays.append(compute_ndre(b05.astype(np.float32), b04.astype(np.float32), mask))
        if profile_ref is None:
            profile_ref = profile

    if not ndvi_arrays:
        logger.warning("compute_field_indices: all scene band downloads failed for field=%s", field_id)
        return {"ndvi_s3_key": "", "ndre_s3_key": ""}

    ndvi_composite = compute_composite(ndvi_arrays, method="median")
    ndre_composite = compute_composite(ndre_arrays, method="median")

    window_str = f"{composite_start}_{composite_end}"
    ndvi_key = f"indices/{field_id}/ndvi/{window_str}.tif"
    ndre_key = f"indices/{field_id}/ndre/{window_str}.tif"

    upload_geotiff(ndvi_key, ndvi_composite, profile_ref)
    upload_geotiff(ndre_key, ndre_composite, profile_ref)

    # Compute summary statistics (ignoring NaN)
    def _stats(arr: np.ndarray) -> tuple[float, float, float, float]:
        valid = arr[~np.isnan(arr)]
        if valid.size == 0:
            return float("nan"), float("nan"), float("nan"), 0.0
        pct_valid = valid.size / arr.size * 100
        return float(np.mean(valid)), float(np.min(valid)), float(np.max(valid)), pct_valid

    def _save_index(
        index_type: str, s3_key: str, composite: np.ndarray
    ) -> None:
        mean, mn, mx, valid_pct = _stats(composite)
        with SessionLocal() as db:
            # Prevent duplicate (unique constraint on field + window + type)
            existing = db.execute(
                select(VegetationIndex).where(
                    and_(
                        VegetationIndex.field_id == field_uuid,
                        VegetationIndex.composite_start == start,
                        VegetationIndex.composite_end == end,
                        VegetationIndex.index_type == index_type,
                    )
                )
            ).scalar_one_or_none()
            if existing:
                existing.s3_key = s3_key
                existing.mean_value = round(mean, 4) if not np.isnan(mean) else None
                existing.min_value = round(mn, 4) if not np.isnan(mn) else None
                existing.max_value = round(mx, 4) if not np.isnan(mx) else None
                existing.valid_pixel_pct = round(valid_pct, 2)
            else:
                record = VegetationIndex(
                    field_id=field_uuid,
                    composite_start=start,
                    composite_end=end,
                    index_type=index_type,
                    s3_key=s3_key,
                    mean_value=round(mean, 4) if not np.isnan(mean) else None,
                    min_value=round(mn, 4) if not np.isnan(mn) else None,
                    max_value=round(mx, 4) if not np.isnan(mx) else None,
                    valid_pixel_pct=round(valid_pct, 2),
                )
                db.add(record)
            db.commit()

    _save_index("ndvi", ndvi_key, ndvi_composite)
    _save_index("ndre", ndre_key, ndre_composite)

    logger.info(
        "compute_field_indices: complete for field=%s; ndvi=%s ndre=%s",
        field_id, ndvi_key, ndre_key,
    )
    return {"ndvi_s3_key": ndvi_key, "ndre_s3_key": ndre_key}
