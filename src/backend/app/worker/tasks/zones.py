"""Celery task: compute_field_zones — zone delineation for a field.

Triggered by the daily scheduler or on-demand after new NDVI/NDRE composites
are available.  Downloads the latest composites, runs delineation, applies
minimum zone-size filter, and persists ManagementZone records.

Note: This task only creates ManagementZone records.  Prescription records
are created separately — either by the API endpoint (user-initiated) or by
a downstream task in the pipeline.
"""

from __future__ import annotations

import logging
import uuid
from decimal import Decimal

import numpy as np
from app.db.session import SessionLocal
from app.models.management_zone import ManagementZone
from app.models.vegetation_index import VegetationIndex
from app.services.s3_storage import S3StorageService
from app.worker.celery_app import celery_app

from ml.zones.delineation import delineate_zones
from ml.zones.zone_filter import filter_minimum_zone_size

logger = logging.getLogger(__name__)


@celery_app.task(
    name="zones.compute_field_zones",
    bind=True,
    max_retries=3,
    default_retry_delay=120,
)
def compute_field_zones(
    self,
    field_id: str,
    field_area_ha: float,
    n_zones: int = 3,
) -> dict:
    """Delineate management zones for a field from the latest composites.

    Downloads NDVI and NDRE composites from S3, runs k-means clustering,
    applies minimum zone-size filter, and persists ManagementZone rows.

    Args:
        field_id: UUID string of the target field.
        field_area_ha: Field area in hectares (for min-zone threshold).
        n_zones: Number of zones to delineate (2–5, default 3).

    Returns:
        Dict with keys: ``field_id``, ``n_zones_created``,
        ``composite_start``, ``composite_end``.
    """
    fid = uuid.UUID(field_id)
    s3 = S3StorageService()

    try:
        with SessionLocal() as db:
            ndvi_vi, ndre_vi = _load_latest_composites(db, fid)
            ndvi_data, _ = s3.download_geotiff(ndvi_vi.s3_key)
            ndre_data, _ = s3.download_geotiff(ndre_vi.s3_key)

            ndvi_array = ndvi_data[0].astype(np.float32)
            ndre_array = ndre_data[0].astype(np.float32)

            zone_map, zone_names, centroids = delineate_zones(
                ndvi_array, ndre_array, n_zones
            )
            zone_map = filter_minimum_zone_size(zone_map, centroids, field_area_ha)

            active_indices = sorted(z for z in np.unique(zone_map) if z >= 0)
            active_names = [zone_names[i] for i in active_indices]
            active_centroids = centroids[active_indices]

            created_zones = []
            for pos, zone_idx in enumerate(active_indices):
                centroid = active_centroids[pos]
                pixel_count = int((zone_map == zone_idx).sum())
                area_ha = Decimal(str(round(pixel_count * 0.01, 4)))

                mgmt_zone = ManagementZone(
                    id=uuid.uuid4(),
                    field_id=fid,
                    zone_index=pos,
                    zone_label=active_names[pos],
                    n_zones=len(active_indices),
                    composite_start=ndvi_vi.composite_start,
                    composite_end=ndvi_vi.composite_end,
                    ndvi_mean=Decimal(str(round(float(centroid[0]), 4))),
                    ndre_mean=Decimal(str(round(float(centroid[1]), 4))),
                    area_ha=area_ha,
                )
                db.add(mgmt_zone)
                created_zones.append(mgmt_zone)

            db.commit()

            result = {
                "field_id": field_id,
                "n_zones_created": len(created_zones),
                "composite_start": str(ndvi_vi.composite_start),
                "composite_end": str(ndvi_vi.composite_end),
            }
            logger.info(
                "Zone delineation complete: field=%s zones=%d window=%s–%s",
                field_id,
                len(created_zones),
                ndvi_vi.composite_start,
                ndvi_vi.composite_end,
            )
            return result

    except Exception as exc:
        logger.exception("Zone delineation failed for field=%s: %s", field_id, exc)
        raise self.retry(exc=exc)


def _load_latest_composites(
    db,
    field_id: uuid.UUID,
) -> tuple[VegetationIndex, VegetationIndex]:
    """Load the most recent NDVI and NDRE composites for a field.

    Args:
        db: Synchronous SQLAlchemy session.
        field_id: UUID of the target field.

    Returns:
        Tuple of (ndvi VegetationIndex, ndre VegetationIndex).

    Raises:
        ValueError: If NDVI or NDRE composite is missing.
    """
    from sqlalchemy import select

    def _latest(index_type: str) -> VegetationIndex:
        result = db.execute(
            select(VegetationIndex)
            .where(
                VegetationIndex.field_id == field_id,
                VegetationIndex.index_type == index_type,
            )
            .order_by(VegetationIndex.composite_end.desc())
            .limit(1)
        )
        vi = result.scalar_one_or_none()
        if vi is None:
            raise ValueError(
                f"No {index_type.upper()} composite found for field {field_id}. "
                "Run the imagery pipeline first."
            )
        return vi

    return _latest("ndvi"), _latest("ndre")
