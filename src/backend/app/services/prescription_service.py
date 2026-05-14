"""Prescription creation orchestration service.

Orchestrates the full prescription pipeline for a field:
1. Loads the latest NDVI and NDRE composite rasters from S3.
2. Runs k-means zone delineation (configurable n_zones).
3. Applies minimum zone-size filter.
4. Calls the prescription engine for per-zone rates.
5. Persists ManagementZone and Prescription records to the database.

This service is called from both the Celery task (background) and the
REST API endpoint (synchronous, for on-demand generation).
"""

from __future__ import annotations

import logging
import uuid
from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Optional

import numpy as np
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.management_zone import ManagementZone
from app.models.prescription import Prescription
from app.models.vegetation_index import VegetationIndex
from app.services.s3_storage import S3StorageService
from ml.prescription.engine import DISCLAIMER_DE, compute_prescription
from ml.zones.delineation import delineate_zones
from ml.zones.zone_filter import filter_minimum_zone_size

logger = logging.getLogger(__name__)


class PrescriptionService:
    """Orchestrates zone delineation and prescription generation for a field.

    Args:
        db: Async SQLAlchemy session.
        s3: S3 storage service instance.
    """

    def __init__(self, db: AsyncSession, s3: S3StorageService) -> None:
        self._db = db
        self._s3 = s3

    async def generate_prescription(
        self,
        field_id: uuid.UUID,
        field_area_ha: float,
        application_type: str,
        base_rate_l_ha: float,
        n_zones: int = 3,
    ) -> list[Prescription]:
        """Generate and persist a prescription map for a field.

        Fetches the most recent NDVI + NDRE composites, delineates zones,
        filters sub-threshold zones, and persists the results.

        Args:
            field_id: UUID of the target field.
            field_area_ha: Field area in hectares (for min-zone threshold).
            application_type: One of "fungicide", "herbicide", "insecticide".
            base_rate_l_ha: Farmer's base application rate in L/ha.
            n_zones: Desired number of management zones (2–5).

        Returns:
            List of :class:`Prescription` ORM objects created (one per zone).

        Raises:
            ValueError: If fewer than 2 valid composites are found.
        """
        ndvi_array, composite_start, composite_end = await self._load_latest_composite(
            field_id, "ndvi"
        )
        ndre_array, _, _ = await self._load_latest_composite(field_id, "ndre")

        zone_map, zone_names, centroids = delineate_zones(ndvi_array, ndre_array, n_zones)
        zone_map = filter_minimum_zone_size(zone_map, centroids, field_area_ha)

        # Re-derive actual zone names after filtering (some may have been merged)
        active_zone_indices = sorted(z for z in np.unique(zone_map) if z >= 0)
        active_zone_names = [zone_names[i] for i in active_zone_indices]
        active_centroids = centroids[active_zone_indices]

        prescription_result = compute_prescription(
            application_type=application_type,  # type: ignore[arg-type]
            base_rate_l_ha=base_rate_l_ha,
            zone_names=active_zone_names,
        )

        prescriptions: list[Prescription] = []
        for zone_presc in prescription_result.zones:
            zone_idx = active_zone_indices[zone_presc.zone_index]
            centroid = active_centroids[zone_presc.zone_index]
            pixel_count = int((zone_map == zone_idx).sum())
            area_ha = Decimal(str(round(pixel_count * 0.01, 4)))

            mgmt_zone = ManagementZone(
                id=uuid.uuid4(),
                field_id=field_id,
                zone_index=zone_presc.zone_index,
                zone_label=zone_presc.zone_name,
                n_zones=len(active_zone_names),
                composite_start=composite_start,
                composite_end=composite_end,
                ndvi_mean=Decimal(str(round(float(centroid[0]), 4))),
                ndre_mean=Decimal(str(round(float(centroid[1]), 4))),
                area_ha=area_ha,
            )
            self._db.add(mgmt_zone)
            await self._db.flush()

            pres = Prescription(
                id=uuid.uuid4(),
                field_id=field_id,
                management_zone_id=mgmt_zone.id,
                application_type=application_type,
                base_rate_l_ha=Decimal(str(base_rate_l_ha)),
                multiplier=Decimal(str(zone_presc.multiplier)),
                rate_l_ha=Decimal(str(zone_presc.rate_l_ha)),
                below_minimum_floor=zone_presc.below_minimum_floor,
                disclaimer=DISCLAIMER_DE,
            )
            self._db.add(pres)
            prescriptions.append(pres)

        await self._db.flush()
        logger.info(
            "Generated %d prescription zones for field=%s (%s)",
            len(prescriptions),
            field_id,
            application_type,
        )
        return prescriptions

    async def _load_latest_composite(
        self,
        field_id: uuid.UUID,
        index_type: str,
    ) -> tuple[np.ndarray, date, date]:
        """Load the most recent composite raster for a field from S3.

        Args:
            field_id: UUID of the field.
            index_type: "ndvi" or "ndre".

        Returns:
            Tuple of (raster array, composite_start, composite_end).

        Raises:
            ValueError: If no composite exists for this field and index type.
        """
        result = await self._db.execute(
            select(VegetationIndex)
            .where(
                VegetationIndex.field_id == field_id,
                VegetationIndex.index_type == index_type,
            )
            .order_by(VegetationIndex.composite_end.desc())
            .limit(1)
        )
        vi: Optional[VegetationIndex] = result.scalar_one_or_none()
        if vi is None:
            raise ValueError(
                f"No {index_type.upper()} composite found for field {field_id}. "
                "Run the imagery pipeline first."
            )

        data, _ = self._s3.download_geotiff(vi.s3_key)
        return data[0], vi.composite_start, vi.composite_end
