"""Field CRUD API endpoints.

All endpoints require a valid Supabase JWT.  Ownership is checked on
every single-resource operation (returns 404 rather than 403 to avoid
leaking resource existence).

Geometry handling:
- ``POST /fields`` accepts geometry as a GeoJSON ``Polygon`` dict,
  converts it to WKB via ``ST_GeomFromGeoJSON``, and computes
  ``area_ha`` using ``ST_Area(ST_Transform(..., 3857)) / 10000``.
- ``GET /fields/{field_id}`` returns geometry serialised back to GeoJSON
  via ``ST_AsGeoJSON``.

Routes registered under prefix ``/api/v1`` in ``main.py``:
    GET    /fields           (supports ?farm_id= filter)
    POST   /fields
    GET    /fields/{field_id}
    PUT    /fields/{field_id}
    DELETE /fields/{field_id}
"""

from __future__ import annotations

import json
import logging
import uuid
from typing import List, Optional

from app.api.deps import get_current_user, get_db, get_owned_field
from app.models.farm import Farm
from app.models.field import Field
from app.models.user import User
from app.schemas.field import FieldCreate, FieldRead, FieldUpdate
from fastapi import APIRouter, Depends, HTTPException, Query, status
from geoalchemy2.functions import (
    ST_Area,
    ST_AsGeoJSON,
    ST_GeomFromGeoJSON,
    ST_Transform,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/fields",
    tags=["fields"],
)


async def _compute_area_ha(geojson_str: str, db: AsyncSession) -> float:
    """Compute field area in hectares from a GeoJSON polygon string.

    Uses PostGIS ``ST_Area(ST_Transform(ST_GeomFromGeoJSON(...), 3857)) / 10000``.

    Args:
        geojson_str: JSON string of a GeoJSON Polygon geometry.
        db: Async database session.

    Returns:
        Area in hectares as a float, rounded to 1 decimal place.
    """
    result = await db.execute(
        select(ST_Area(ST_Transform(ST_GeomFromGeoJSON(geojson_str), 3857)) / 10000)
    )
    area: Optional[float] = result.scalar_one_or_none()
    return round(area or 0.0, 1)


async def _field_to_read(field: Field, db: AsyncSession) -> FieldRead:
    """Serialise a :class:`Field` ORM object to a :class:`FieldRead` schema.

    Fetches the geometry as GeoJSON from PostGIS.

    Args:
        field: The ORM :class:`Field` instance.
        db: Async database session (used to call ``ST_AsGeoJSON``).

    Returns:
        Populated :class:`FieldRead` schema.
    """
    geometry_dict = None
    if field.geometry is not None:
        geojson_result = await db.execute(select(ST_AsGeoJSON(field.geometry)))
        geojson_str: Optional[str] = geojson_result.scalar_one_or_none()
        if geojson_str:
            geometry_dict = json.loads(geojson_str)

    return FieldRead(
        id=field.id,
        farm_id=field.farm_id,
        name=field.name,
        crop_type=field.crop_type,  # type: ignore[arg-type]
        planting_date=field.planting_date,  # type: ignore[arg-type]
        geometry=geometry_dict,
        area_ha=field.area_ha,  # type: ignore[arg-type]
        created_at=field.created_at,  # type: ignore[arg-type]
    )


async def _verify_farm_ownership(
    farm_id: uuid.UUID,
    current_user: User,
    db: AsyncSession,
) -> Farm:
    """Check that the current user owns the given farm.

    Args:
        farm_id: UUID of the farm to verify.
        current_user: The authenticated user.
        db: Async database session.

    Returns:
        The :class:`Farm` ORM object if owned.

    Raises:
        HTTPException: 404 if farm not found or not owned.
    """
    result = await db.execute(
        select(Farm).where(Farm.id == farm_id, Farm.user_id == current_user.id)
    )
    farm = result.scalar_one_or_none()
    if farm is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Farm {farm_id} not found.",
        )
    return farm


@router.get("/", response_model=List[FieldRead], summary="List all fields")
async def list_fields(
    farm_id: Optional[uuid.UUID] = Query(
        default=None,
        description="Filter fields by parent farm UUID.",
    ),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[FieldRead]:
    """Return all fields for the authenticated user.

    Optionally filter by ``?farm_id=<uuid>``.

    Args:
        farm_id: Optional farm UUID filter.
        current_user: Authenticated user from JWT dependency.
        db: Async database session.

    Returns:
        List of :class:`FieldRead` schemas.
    """
    query = (
        select(Field)
        .join(Farm, Farm.id == Field.farm_id)
        .where(Farm.user_id == current_user.id)
    )
    if farm_id is not None:
        query = query.where(Field.farm_id == farm_id)

    result = await db.execute(query)
    fields = result.scalars().all()

    return [await _field_to_read(f, db) for f in fields]


@router.post(
    "/",
    response_model=FieldRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a field",
)
async def create_field(
    payload: FieldCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> FieldRead:
    """Create a new field under the specified farm.

    Validates the GeoJSON polygon geometry (enforced by
    :class:`~app.schemas.field.FieldCreate`), computes ``area_ha`` via
    PostGIS, and stores both.

    Args:
        payload: :class:`FieldCreate` request body with geometry.
        current_user: Authenticated user from JWT dependency.
        db: Async database session.

    Returns:
        The newly created :class:`FieldRead` schema.

    Raises:
        HTTPException: 404 if the target farm is not found or not owned.
        HTTPException: 422 if the geometry is not a valid Polygon.
    """
    # Verify farm ownership
    await _verify_farm_ownership(payload.farm_id, current_user, db)

    geojson_str = json.dumps(payload.geometry)

    # Compute area via PostGIS before inserting
    area_ha = await _compute_area_ha(geojson_str, db)

    field = Field(
        id=uuid.uuid4(),
        farm_id=payload.farm_id,
        name=payload.name,
        crop_type=payload.crop_type.value if payload.crop_type else None,
        planting_date=payload.planting_date,
        geometry=ST_GeomFromGeoJSON(geojson_str),
        area_ha=area_ha,
    )
    db.add(field)
    await db.flush()
    logger.info(
        "Created field id=%s name=%r farm=%s area_ha=%s",
        field.id,
        field.name,
        field.farm_id,
        area_ha,
    )
    return await _field_to_read(field, db)


@router.get("/{field_id}", response_model=FieldRead, summary="Get a field")
async def get_field(
    field_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> FieldRead:
    """Return a single field by ID, including geometry as GeoJSON.

    Args:
        field_id: UUID of the field to retrieve.
        current_user: Authenticated user from JWT dependency.
        db: Async database session.

    Returns:
        :class:`FieldRead` schema for the requested field.

    Raises:
        HTTPException: 404 if the field does not exist or is not owned.
    """
    field = await get_owned_field(field_id, current_user, db)
    return await _field_to_read(field, db)


@router.put("/{field_id}", response_model=FieldRead, summary="Update a field")
async def update_field(
    field_id: uuid.UUID,
    payload: FieldUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> FieldRead:
    """Update one or more attributes of a field.

    If the geometry is updated, ``area_ha`` is recomputed automatically.

    Args:
        field_id: UUID of the field to update.
        payload: :class:`FieldUpdate` request body with optional fields.
        current_user: Authenticated user from JWT dependency.
        db: Async database session.

    Returns:
        Updated :class:`FieldRead` schema.

    Raises:
        HTTPException: 404 if the field does not exist or is not owned.
        HTTPException: 422 if the updated geometry is not a valid Polygon.
    """
    field = await get_owned_field(field_id, current_user, db)

    if payload.name is not None:
        field.name = payload.name
    if payload.crop_type is not None:
        field.crop_type = payload.crop_type.value
    if payload.planting_date is not None:
        field.planting_date = payload.planting_date  # type: ignore[assignment]
    if payload.geometry is not None:
        geojson_str = json.dumps(payload.geometry)
        field.geometry = ST_GeomFromGeoJSON(geojson_str)  # type: ignore[assignment]
        field.area_ha = await _compute_area_ha(geojson_str, db)  # type: ignore[assignment]

    await db.flush()
    logger.info("Updated field id=%s for user=%s", field.id, current_user.id)
    return await _field_to_read(field, db)


@router.delete(
    "/{field_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=None,
    summary="Delete a field",
)
async def delete_field(
    field_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a field.

    Args:
        field_id: UUID of the field to delete.
        current_user: Authenticated user from JWT dependency.
        db: Async database session.

    Raises:
        HTTPException: 404 if the field does not exist or is not owned.
    """
    field = await get_owned_field(field_id, current_user, db)
    await db.delete(field)
    await db.flush()
    logger.info("Deleted field id=%s for user=%s", field_id, current_user.id)
