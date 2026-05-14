"""Celery task: fetch Sentinel-2 imagery for a field.

Downloads available scenes from the Sentinel Hub API for the past 30 days,
stores the raw band GeoTIFFs in S3, and records each scene in the
``satellite_scenes`` table.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timedelta, timezone

from app.worker.celery_app import celery_app
from celery import Task

logger = logging.getLogger(__name__)

# Bands required for NDVI (B04, B08), NDRE (B05), and cloud masking (SCL)
_REQUIRED_BANDS = ["B04", "B05", "B08", "SCL"]
_CLOUD_COVER_THRESHOLD = 80.0
_LOOKBACK_DAYS = 30


@celery_app.task(
    bind=True,
    name="imagery.fetch_field_imagery",
    max_retries=3,
    default_retry_delay=300,
)
def fetch_field_imagery(self: Task, field_id: str) -> dict[str, int]:
    """Download Sentinel-2 scenes for a field and store them in S3.

    Args:
        field_id: UUID string of the field to process.

    Returns:
        Dict with ``scenes_downloaded`` and ``scenes_failed`` counts.
    """
    from app.core.config import settings
    from app.db.session import SessionLocal
    from app.models.field import Field
    from app.models.satellite_scene import SatelliteScene
    from app.services.s3_storage import upload_geotiff

    from ml.sentinel.client import SentinelHubClient, SentinelHubError

    logger.info("fetch_field_imagery: starting for field_id=%s", field_id)

    client = SentinelHubClient(
        client_id=settings.sentinel_hub_client_id,
        client_secret=settings.sentinel_hub_client_secret,
        instance_id=settings.sentinel_hub_instance_id,
    )

    date_to = datetime.now(tz=timezone.utc).date()
    date_from = date_to - timedelta(days=_LOOKBACK_DAYS)

    with SessionLocal() as db:
        field = db.get(Field, uuid.UUID(field_id))
        if field is None:
            logger.error("fetch_field_imagery: field %s not found", field_id)
            return {"scenes_downloaded": 0, "scenes_failed": 0}

        # Extract bounding box from PostGIS geometry
        from geoalchemy2.shape import to_shape

        geom = to_shape(field.geometry)
        bbox = list(geom.bounds)  # [minx, miny, maxx, maxy]

    try:
        scenes = client.search_scenes(
            bbox=bbox,
            date_from=date_from,
            date_to=date_to,
            max_cloud_cover=_CLOUD_COVER_THRESHOLD,
        )
    except SentinelHubError as exc:
        logger.error(
            "fetch_field_imagery: scene search failed for field %s: %s", field_id, exc
        )
        raise self.retry(exc=exc)

    downloaded = 0
    failed = 0

    for scene in scenes:
        scene_id: str = scene["id"]
        scene_dt: str = scene.get("properties", {}).get("datetime", "")
        cloud_cover = scene.get("properties", {}).get("eo:cloud_cover")

        with SessionLocal() as db:
            # Skip if already downloaded
            from sqlalchemy import select

            existing = db.execute(
                select(SatelliteScene).where(
                    SatelliteScene.field_id == uuid.UUID(field_id),
                    SatelliteScene.scene_id == scene_id,
                )
            ).scalar_one_or_none()
            if existing:
                logger.debug(
                    "fetch_field_imagery: scene %s already stored, skipping", scene_id
                )
                continue

            # Create a pending record
            record = SatelliteScene(
                field_id=uuid.UUID(field_id),
                scene_id=scene_id,
                acquired_at=datetime.fromisoformat(scene_dt.replace("Z", "+00:00")),
                cloud_cover_pct=cloud_cover,
                status="processing",
            )
            db.add(record)
            db.commit()
            db.refresh(record)
            record_id = record.id

        try:
            bands_data = client.download_bands(
                scene_datetime=scene_dt,
                bbox=bbox,
                bands=_REQUIRED_BANDS,
            )
        except SentinelHubError as exc:
            logger.error(
                "fetch_field_imagery: download failed for scene %s: %s", scene_id, exc
            )
            with SessionLocal() as db:
                rec = db.get(SatelliteScene, record_id)
                if rec:
                    rec.status = "failed"
                    db.commit()
            failed += 1
            continue

        # Upload each band to S3
        s3_prefix = f"imagery/{field_id}/{scene_id}"
        try:
            from rasterio.crs import CRS
            from rasterio.transform import from_bounds

            first_band = next(iter(bands_data.values()))
            h, w = first_band.shape
            transform = from_bounds(*bbox, width=w, height=h)
            profile = {
                "crs": CRS.from_epsg(4326),
                "transform": transform,
                "width": w,
                "height": h,
            }

            for band_name, arr in bands_data.items():
                band_key = f"{s3_prefix}/{band_name}.tif"
                upload_geotiff(band_key, arr, profile)
        except Exception as exc:
            logger.error(
                "fetch_field_imagery: S3 upload failed for scene %s: %s", scene_id, exc
            )
            with SessionLocal() as db:
                rec = db.get(SatelliteScene, record_id)
                if rec:
                    rec.status = "failed"
                    db.commit()
            failed += 1
            continue

        with SessionLocal() as db:
            rec = db.get(SatelliteScene, record_id)
            if rec:
                rec.status = "complete"
                rec.bands_s3_key = s3_prefix
                db.commit()

        downloaded += 1
        logger.info(
            "fetch_field_imagery: stored scene %s for field %s", scene_id, field_id
        )

    logger.info(
        "fetch_field_imagery: field=%s downloaded=%d failed=%d",
        field_id,
        downloaded,
        failed,
    )
    return {"scenes_downloaded": downloaded, "scenes_failed": failed}
