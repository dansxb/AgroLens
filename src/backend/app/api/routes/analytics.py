"""Analytics API endpoints — NDVI time-series and field health summaries.

Routes registered under prefix ``/api/v1`` in ``main.py``:
    GET  /fields/{field_id}/ndvi-series
    GET  /fields/{field_id}/health-summary

All endpoints require a valid Supabase JWT.
"""

from __future__ import annotations

import logging
import uuid
from datetime import date
from decimal import Decimal
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.farm import Farm
from app.models.field import Field
from app.models.user import User
from app.models.vegetation_index import VegetationIndex

logger = logging.getLogger(__name__)

router = APIRouter(tags=["analytics"])


# ---------------------------------------------------------------------------
# Response schemas (inline — simple enough to not warrant a separate file)
# ---------------------------------------------------------------------------


class NdviDataPoint(BaseModel):
    """Single data point in the NDVI time series."""

    composite_start: date
    composite_end: date
    mean_value: Optional[Decimal]
    min_value: Optional[Decimal]
    max_value: Optional[Decimal]
    valid_pixel_pct: Optional[Decimal]


class NdviSeriesResponse(BaseModel):
    """NDVI or NDRE time series for a field."""

    field_id: uuid.UUID
    index_type: str
    data_points: List[NdviDataPoint]


class HealthSummary(BaseModel):
    """Current health snapshot for a field."""

    field_id: uuid.UUID
    latest_ndvi: Optional[Decimal]
    latest_ndre: Optional[Decimal]
    composite_end: Optional[date]
    days_since_composite: Optional[int]
    composite_stale: bool


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


async def _get_owned_field(
    field_id: uuid.UUID,
    current_user: User,
    db: AsyncSession,
) -> Field:
    """Fetch a field owned by the authenticated user or raise 404."""
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


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.get(
    "/fields/{field_id}/ndvi-series",
    response_model=NdviSeriesResponse,
    summary="NDVI or NDRE time series for a field",
)
async def get_ndvi_series(
    field_id: uuid.UUID,
    index_type: str = Query(default="ndvi", pattern="^(ndvi|ndre)$"),
    limit: int = Query(default=52, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> NdviSeriesResponse:
    """Return historical NDVI or NDRE values for a field.

    Args:
        field_id: UUID of the target field.
        index_type: "ndvi" or "ndre" (default: "ndvi").
        limit: Maximum number of data points to return (default 52 ≈ 1 year
            of 10-day composites).
        current_user: Authenticated user from JWT.
        db: Async database session.

    Returns:
        :class:`NdviSeriesResponse` with ordered time-series data points.
    """
    await _get_owned_field(field_id, current_user, db)
    logger.debug("get_ndvi_series: field=%s index=%s limit=%d", field_id, index_type, limit)

    result = await db.execute(
        select(VegetationIndex)
        .where(
            VegetationIndex.field_id == field_id,
            VegetationIndex.index_type == index_type,
        )
        .order_by(VegetationIndex.composite_end.desc())
        .limit(limit)
    )
    indices = list(result.scalars().all())
    logger.info("get_ndvi_series: field=%s returned %d data points", field_id, len(indices))

    data_points = [
        NdviDataPoint(
            composite_start=vi.composite_start,
            composite_end=vi.composite_end,
            mean_value=vi.mean_value,
            min_value=vi.min_value,
            max_value=vi.max_value,
            valid_pixel_pct=vi.valid_pixel_pct,
        )
        for vi in reversed(indices)  # chronological order
    ]

    return NdviSeriesResponse(
        field_id=field_id,
        index_type=index_type,
        data_points=data_points,
    )


@router.get(
    "/fields/{field_id}/health-summary",
    response_model=HealthSummary,
    summary="Current vegetation health snapshot for a field",
)
async def get_health_summary(
    field_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> HealthSummary:
    """Return the latest NDVI/NDRE values and composite freshness for a field.

    ``composite_stale`` is True when the most recent composite is older than
    14 days — indicating that new satellite data should be requested.

    Args:
        field_id: UUID of the target field.
        current_user: Authenticated user from JWT.
        db: Async database session.

    Returns:
        :class:`HealthSummary` with latest index values and staleness flag.
    """
    await _get_owned_field(field_id, current_user, db)
    logger.debug("get_health_summary: field=%s user=%s", field_id, current_user.id)

    async def _latest(index_type: str) -> Optional[VegetationIndex]:
        r = await db.execute(
            select(VegetationIndex)
            .where(
                VegetationIndex.field_id == field_id,
                VegetationIndex.index_type == index_type,
            )
            .order_by(VegetationIndex.composite_end.desc())
            .limit(1)
        )
        return r.scalar_one_or_none()

    latest_ndvi = await _latest("ndvi")
    latest_ndre = await _latest("ndre")

    from datetime import datetime, timezone

    today = date.today()
    composite_end: Optional[date] = latest_ndvi.composite_end if latest_ndvi else None
    days_since: Optional[int] = (
        (today - composite_end).days if composite_end else None
    )

    stale = days_since is not None and days_since > 14
    logger.info(
        "get_health_summary: field=%s ndvi=%s days_since=%s stale=%s",
        field_id, latest_ndvi.mean_value if latest_ndvi else None, days_since, stale,
    )
    return HealthSummary(
        field_id=field_id,
        latest_ndvi=latest_ndvi.mean_value if latest_ndvi else None,
        latest_ndre=latest_ndre.mean_value if latest_ndre else None,
        composite_end=composite_end,
        days_since_composite=days_since,
        composite_stale=stale,
    )
