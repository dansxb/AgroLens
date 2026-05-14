"""Export endpoints for VRA prescription maps.

Routes registered under prefix ``/api/v1`` in ``main.py``:
    GET  /fields/{field_id}/prescriptions/{app_type}/export/shapefile
    GET  /fields/{field_id}/prescriptions/{app_type}/export/taskdata
    GET  /fields/{field_id}/prescriptions/{app_type}/export/pdf

All endpoints return the most recent prescription for the given application
type.  Ownership is enforced via farm → user chain.

ISOBUS Note: For tractor terminal compatibility (John Deere GreenStar, Fendt
Variotronic, CLAAS), use the ``taskdata`` endpoint which returns ISO 11783-10
TASKDATA.XML.  Shapefile is for GIS desktop use only.
"""

from __future__ import annotations

import logging
import uuid
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.farm import Farm
from app.models.field import Field
from app.models.management_zone import ManagementZone
from app.models.prescription import Prescription
from app.models.user import User
from app.services.export.pdf_report import build_prescription_pdf
from app.services.export.shapefile import build_prescription_shapefile
from app.services.export.taskdata_xml import build_taskdata_xml

logger = logging.getLogger(__name__)

ApplicationType = Literal["fungicide", "herbicide", "insecticide"]

router = APIRouter(tags=["exports"])


async def _get_owned_field(
    field_id: uuid.UUID,
    current_user: User,
    db: AsyncSession,
) -> Field:
    """Fetch a field owned by the current user or raise 404."""
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


async def _load_latest_prescription(
    field_id: uuid.UUID,
    app_type: str,
    db: AsyncSession,
) -> tuple[list[ManagementZone], list[Prescription]]:
    """Load the most recent set of prescriptions for a field + application type."""
    pres_result = await db.execute(
        select(Prescription)
        .where(
            Prescription.field_id == field_id,
            Prescription.application_type == app_type,
        )
        .order_by(Prescription.created_at.desc())
        .limit(10)
    )
    prescriptions = list(pres_result.scalars().all())
    if not prescriptions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f"No {app_type} prescription found for field {field_id}. "
                "Generate one via POST /fields/{field_id}/prescriptions."
            ),
        )

    zone_ids = [p.management_zone_id for p in prescriptions]
    zone_result = await db.execute(
        select(ManagementZone).where(ManagementZone.id.in_(zone_ids))
    )
    zones = sorted(zone_result.scalars().all(), key=lambda z: z.zone_index)
    return zones, prescriptions


@router.get(
    "/fields/{field_id}/prescriptions/{app_type}/export/shapefile",
    summary="Download prescription map as Shapefile (ZIP)",
    response_class=Response,
)
async def export_shapefile(
    field_id: uuid.UUID,
    app_type: ApplicationType,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Response:
    """Return the latest prescription map as a zipped ESRI Shapefile.

    Note: Shapefiles require a GIS desktop application for viewing.  Use the
    ``taskdata`` endpoint for direct upload to ISOBUS tractor terminals.

    Args:
        field_id: UUID of the target field.
        app_type: Application type (fungicide / herbicide / insecticide).

    Returns:
        ZIP file containing .shp/.shx/.dbf/.prj/.cpg.
    """
    field = await _get_owned_field(field_id, current_user, db)
    zones, prescriptions = await _load_latest_prescription(field_id, app_type, db)

    try:
        data = build_prescription_shapefile(
            zones=zones,
            prescriptions=prescriptions,
            field_name=field.name,
            flik=field.flik,
        )
    except ImportError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    filename = f"prescription_{field.name}_{app_type}.zip".replace(" ", "_")
    return Response(
        content=data,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get(
    "/fields/{field_id}/prescriptions/{app_type}/export/taskdata",
    summary="Download prescription map as ISO 11783-10 TASKDATA.ZIP (ISOBUS)",
    response_class=Response,
)
async def export_taskdata_xml(
    field_id: uuid.UUID,
    app_type: ApplicationType,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Response:
    """Return the latest prescription map as an ISO 11783-10 TASKDATA.ZIP.

    This format is directly compatible with ISOBUS tractor terminals including
    John Deere GreenStar, Fendt Variotronic, CLAAS, and Amazone AmaSpread.

    Args:
        field_id: UUID of the target field.
        app_type: Application type (fungicide / herbicide / insecticide).

    Returns:
        ZIP file containing TASKDATA.XML in ISO 11783-10 format.
    """
    field = await _get_owned_field(field_id, current_user, db)
    zones, prescriptions = await _load_latest_prescription(field_id, app_type, db)

    try:
        data = build_taskdata_xml(
            zones=zones,
            prescriptions=prescriptions,
            field_name=field.name,
            application_type=app_type,
            flik=field.flik,
        )
    except Exception as exc:
        logger.error(
            "export_taskdata_xml: build failed for field=%s app_type=%s: %s",
            field_id, app_type, exc,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate TASKDATA.XML.",
        ) from exc

    logger.info("export_taskdata_xml: generated for field=%s app_type=%s", field_id, app_type)
    filename = f"TASKDATA_{field.name}_{app_type}.zip".replace(" ", "_")
    return Response(
        content=data,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get(
    "/fields/{field_id}/prescriptions/{app_type}/export/pdf",
    summary="Download prescription map as PDF report",
    response_class=Response,
)
async def export_pdf(
    field_id: uuid.UUID,
    app_type: ApplicationType,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Response:
    """Return the latest prescription map as a printable PDF report.

    The report includes zone rates, area breakdown, estimated savings, and
    the mandatory agronomist disclaimer.

    Args:
        field_id: UUID of the target field.
        app_type: Application type (fungicide / herbicide / insecticide).

    Returns:
        PDF file.
    """
    field = await _get_owned_field(field_id, current_user, db)
    zones, prescriptions = await _load_latest_prescription(field_id, app_type, db)

    if not prescriptions:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No prescription found.")

    first_pres = prescriptions[0]
    first_zone = zones[0] if zones else None

    try:
        data = build_prescription_pdf(
            zones=zones,
            prescriptions=prescriptions,
            field_name=field.name,
            application_type=app_type,
            base_rate_l_ha=float(first_pres.base_rate_l_ha),
            composite_start=first_zone.composite_start if first_zone else None,  # type: ignore[arg-type]
            composite_end=first_zone.composite_end if first_zone else None,  # type: ignore[arg-type]
            flik=field.flik,
        )
    except ImportError as exc:
        logger.error("export_pdf: missing dependency for field=%s: %s", field_id, exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        logger.error("export_pdf: build failed for field=%s app_type=%s: %s", field_id, app_type, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate PDF report.",
        ) from exc

    logger.info("export_pdf: generated for field=%s app_type=%s", field_id, app_type)
    filename = f"prescription_{field.name}_{app_type}.pdf".replace(" ", "_")
    return Response(
        content=data,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
