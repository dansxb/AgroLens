"""Prescription API endpoints.

Routes registered under prefix ``/api/v1`` in ``main.py``:
    POST   /fields/{field_id}/prescriptions
    GET    /fields/{field_id}/prescriptions
    GET    /fields/{field_id}/prescriptions/latest
    POST   /fields/{field_id}/spraying-records
    GET    /fields/{field_id}/spraying-records

All endpoints require a valid Supabase JWT.  Field ownership is verified on
every request — a 404 is returned instead of 403 to prevent resource enumeration.
"""

from __future__ import annotations

import logging
import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.field import Field
from app.models.farm import Farm
from app.models.management_zone import ManagementZone
from app.models.prescription import Prescription
from app.models.spraying_record import SprayingRecord
from app.models.user import User
from app.schemas.prescription import (
    PrescriptionCreate,
    PrescriptionRead,
    PrescriptionZoneRead,
)
from app.schemas.spraying_record import SprayingRecordCreate, SprayingRecordRead
from app.services.prescription_service import PrescriptionService
from app.services.s3_storage import S3StorageService

logger = logging.getLogger(__name__)

router = APIRouter(tags=["prescriptions"])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


async def _get_owned_field(
    field_id: uuid.UUID,
    current_user: User,
    db: AsyncSession,
) -> Field:
    """Fetch a field that belongs to the authenticated user.

    Raises:
        HTTPException: 404 if not found or not owned.
    """
    result = await db.execute(
        select(Field)
        .join(Farm, Farm.id == Field.farm_id)
        .where(Field.id == field_id, Farm.user_id == current_user.id)
    )
    field = result.scalar_one_or_none()
    if field is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Field {field_id} not found.",
        )
    return field


def _build_prescription_read(
    field_id: uuid.UUID,
    application_type: str,
    base_rate_l_ha: float,
    zones: list[ManagementZone],
    prescriptions: list[Prescription],
) -> PrescriptionRead:
    """Assemble a :class:`PrescriptionRead` from ORM objects."""
    from decimal import Decimal

    pres_map = {p.management_zone_id: p for p in prescriptions}
    zone_reads: list[PrescriptionZoneRead] = []
    for zone in sorted(zones, key=lambda z: z.zone_index):
        pres = pres_map.get(zone.id)
        if pres is None:
            continue
        zone_reads.append(
            PrescriptionZoneRead(
                id=pres.id,
                management_zone_id=zone.id,
                zone_label=zone.zone_label,
                zone_index=zone.zone_index,
                multiplier=pres.multiplier,
                rate_l_ha=pres.rate_l_ha,
                below_minimum_floor=pres.below_minimum_floor,
            )
        )

    mean_rate = (
        sum(float(z.rate_l_ha) for z in zone_reads) / len(zone_reads)
        if zone_reads
        else base_rate_l_ha
    )
    savings_pct = Decimal(
        str(round((1.0 - mean_rate / base_rate_l_ha) * 100.0, 2))
        if base_rate_l_ha > 0
        else 0.0
    )

    first_pres = prescriptions[0] if prescriptions else None
    first_zone = zones[0] if zones else None

    return PrescriptionRead(
        field_id=field_id,
        application_type=application_type,  # type: ignore[arg-type]
        base_rate_l_ha=Decimal(str(base_rate_l_ha)),
        mean_rate_l_ha=Decimal(str(round(mean_rate, 4))),
        savings_pct=savings_pct,
        disclaimer=first_pres.disclaimer if first_pres else "",
        composite_start=first_zone.composite_start if first_zone else None,
        composite_end=first_zone.composite_end if first_zone else None,
        zones=zone_reads,
        created_at=first_pres.created_at if first_pres else None,  # type: ignore[arg-type]
    )


# ---------------------------------------------------------------------------
# Prescription endpoints
# ---------------------------------------------------------------------------


@router.post(
    "/fields/{field_id}/prescriptions",
    response_model=PrescriptionRead,
    status_code=status.HTTP_201_CREATED,
    summary="Generate a prescription map for a field",
)
async def create_prescription(
    field_id: uuid.UUID,
    payload: PrescriptionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PrescriptionRead:
    """Generate and persist a VRA prescription map.

    Triggers zone delineation on the latest NDVI/NDRE composites and
    returns per-zone application rates.

    Args:
        field_id: UUID of the target field.
        payload: Application type, base rate, and desired zone count.
        current_user: Authenticated user from JWT.
        db: Async database session.

    Returns:
        :class:`PrescriptionRead` with per-zone rates and disclaimer.

    Raises:
        HTTPException: 404 if field not found / not owned.
        HTTPException: 422 if no composite imagery exists for the field.
    """
    field = await _get_owned_field(field_id, current_user, db)

    s3 = S3StorageService()
    service = PrescriptionService(db, s3)

    try:
        prescriptions = await service.generate_prescription(
            field_id=field_id,
            field_area_ha=float(field.area_ha or 0),
            application_type=payload.application_type,
            base_rate_l_ha=float(payload.base_rate_l_ha),
            n_zones=payload.n_zones,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    zone_ids = [p.management_zone_id for p in prescriptions]
    zone_result = await db.execute(
        select(ManagementZone).where(ManagementZone.id.in_(zone_ids))
    )
    zones = list(zone_result.scalars().all())

    logger.info(
        "Created prescription for field=%s type=%s zones=%d",
        field_id,
        payload.application_type,
        len(prescriptions),
    )
    return _build_prescription_read(
        field_id,
        payload.application_type,
        float(payload.base_rate_l_ha),
        zones,
        prescriptions,
    )


@router.get(
    "/fields/{field_id}/prescriptions",
    response_model=List[PrescriptionRead],
    summary="List all prescriptions for a field",
)
async def list_prescriptions(
    field_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[PrescriptionRead]:
    """Return all prescription maps for the specified field.

    Args:
        field_id: UUID of the target field.
        current_user: Authenticated user from JWT.
        db: Async database session.

    Returns:
        List of :class:`PrescriptionRead` schemas.
    """
    await _get_owned_field(field_id, current_user, db)

    pres_result = await db.execute(
        select(Prescription)
        .where(Prescription.field_id == field_id)
        .order_by(Prescription.created_at.desc())
    )
    all_pres = list(pres_result.scalars().all())
    if not all_pres:
        return []

    # Group by (application_type, management_zone_id's composite window)
    # For simplicity, return one PrescriptionRead per unique (type, created_at bucket).
    # More fine-grained grouping can be added in Phase 4.
    zone_ids = list({p.management_zone_id for p in all_pres})
    zone_result = await db.execute(
        select(ManagementZone).where(ManagementZone.id.in_(zone_ids))
    )
    zones_by_id = {z.id: z for z in zone_result.scalars().all()}

    # Group by application_type + composite window
    from collections import defaultdict

    groups: dict[tuple, tuple[list, list]] = defaultdict(lambda: ([], []))
    for pres in all_pres:
        zone = zones_by_id.get(pres.management_zone_id)
        if zone is None:
            continue
        key = (pres.application_type, zone.composite_start, zone.composite_end)
        groups[key][0].append(zone)
        groups[key][1].append(pres)

    reads = []
    for (app_type, _, _), (grp_zones, grp_pres) in groups.items():
        reads.append(
            _build_prescription_read(
                field_id,
                app_type,
                float(grp_pres[0].base_rate_l_ha),
                grp_zones,
                grp_pres,
            )
        )
    return reads


# ---------------------------------------------------------------------------
# Spraying record endpoints
# ---------------------------------------------------------------------------


@router.post(
    "/fields/{field_id}/spraying-records",
    response_model=SprayingRecordRead,
    status_code=status.HTTP_201_CREATED,
    summary="Log a pesticide application (§67 PflSchG)",
)
async def create_spraying_record(
    field_id: uuid.UUID,
    payload: SprayingRecordCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SprayingRecordRead:
    """Create a pesticide application documentation record.

    Required by §67 Pflanzenschutzgesetz for all professional users.

    Args:
        field_id: UUID of the target field.
        payload: Application details.
        current_user: Authenticated user from JWT.
        db: Async database session.

    Returns:
        :class:`SprayingRecordRead` with the created record.

    Raises:
        HTTPException: 404 if field not found / not owned.
    """
    await _get_owned_field(field_id, current_user, db)

    if payload.field_id != field_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="field_id in body must match URL parameter.",
        )

    record = SprayingRecord(
        id=uuid.uuid4(),
        field_id=field_id,
        prescription_id=payload.prescription_id,
        applied_at=payload.applied_at,
        product_name=payload.product_name,
        product_reg_number=payload.product_reg_number,
        target_pest=payload.target_pest,
        actual_rate_l_ha=payload.actual_rate_l_ha,
        area_sprayed_ha=payload.area_sprayed_ha,
        operator_name=payload.operator_name,
        equipment_id=payload.equipment_id,
        notes=payload.notes,
    )
    db.add(record)
    await db.flush()
    logger.info("Logged spraying record id=%s for field=%s", record.id, field_id)
    return SprayingRecordRead.model_validate(record)


@router.get(
    "/fields/{field_id}/spraying-records",
    response_model=List[SprayingRecordRead],
    summary="List pesticide application records for a field",
)
async def list_spraying_records(
    field_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[SprayingRecordRead]:
    """Return all §67 PflSchG application records for the specified field.

    Args:
        field_id: UUID of the target field.
        current_user: Authenticated user from JWT.
        db: Async database session.

    Returns:
        List of :class:`SprayingRecordRead` schemas ordered by application date.
    """
    await _get_owned_field(field_id, current_user, db)

    result = await db.execute(
        select(SprayingRecord)
        .where(SprayingRecord.field_id == field_id)
        .order_by(SprayingRecord.applied_at.desc())
    )
    return [SprayingRecordRead.model_validate(r) for r in result.scalars().all()]
