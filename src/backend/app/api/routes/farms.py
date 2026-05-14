"""Farm CRUD API endpoints.

All endpoints require a valid Supabase JWT (``Authorization: Bearer
<token>``).  Ownership is enforced on every single-resource operation:
a 404 is returned instead of 403 to avoid leaking resource existence to
other users.

Routes registered under prefix ``/api/v1`` in ``main.py``:
    GET    /farms
    POST   /farms
    GET    /farms/{farm_id}
    PUT    /farms/{farm_id}
    DELETE /farms/{farm_id}
"""

from __future__ import annotations

import uuid
import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.farm import Farm
from app.models.field import Field
from app.models.user import User
from app.schemas.farm import FarmCreate, FarmRead, FarmUpdate

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/farms",
    tags=["farms"],
)


def _to_farm_read(farm: Farm, field_count: int) -> FarmRead:
    """Construct a :class:`FarmRead` schema from an ORM instance.

    Args:
        farm: The :class:`Farm` ORM object.
        field_count: Number of fields belonging to this farm.

    Returns:
        Populated :class:`FarmRead` schema instance.
    """
    return FarmRead(
        id=farm.id,
        user_id=farm.user_id,
        name=farm.name,
        created_at=farm.created_at,
        field_count=field_count,
    )


@router.get("/", response_model=List[FarmRead], summary="List all farms")
async def list_farms(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[FarmRead]:
    """Return all farms owned by the authenticated user.

    Args:
        current_user: Authenticated user from JWT dependency.
        db: Async database session.

    Returns:
        List of :class:`FarmRead` schemas for the user's farms.
    """
    result = await db.execute(
        select(Farm).where(Farm.user_id == current_user.id)
    )
    farms = result.scalars().all()

    # Compute field counts in a single query
    if farms:
        farm_ids = [f.id for f in farms]
        count_result = await db.execute(
            select(Field.farm_id, func.count(Field.id).label("cnt"))
            .where(Field.farm_id.in_(farm_ids))
            .group_by(Field.farm_id)
        )
        counts = {row.farm_id: row.cnt for row in count_result}
    else:
        counts = {}

    return [_to_farm_read(f, counts.get(f.id, 0)) for f in farms]


@router.post(
    "/",
    response_model=FarmRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a farm",
)
async def create_farm(
    payload: FarmCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> FarmRead:
    """Create a new farm for the authenticated user.

    Args:
        payload: :class:`FarmCreate` request body.
        current_user: Authenticated user from JWT dependency.
        db: Async database session.

    Returns:
        The newly created :class:`FarmRead` schema.
    """
    farm = Farm(
        id=uuid.uuid4(),
        user_id=current_user.id,
        name=payload.name,
    )
    db.add(farm)
    await db.flush()
    logger.info(
        "Created farm id=%s name=%r for user=%s", farm.id, farm.name, current_user.id
    )
    return _to_farm_read(farm, 0)


@router.get("/{farm_id}", response_model=FarmRead, summary="Get a farm")
async def get_farm(
    farm_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> FarmRead:
    """Return a single farm by ID, checking ownership.

    Args:
        farm_id: UUID of the farm to retrieve.
        current_user: Authenticated user from JWT dependency.
        db: Async database session.

    Returns:
        :class:`FarmRead` schema for the requested farm.

    Raises:
        HTTPException: 404 if the farm does not exist or is not owned
            by the current user.
    """
    farm = await _get_owned_farm(farm_id, current_user, db)

    count_result = await db.execute(
        select(func.count(Field.id)).where(Field.farm_id == farm.id)
    )
    field_count: int = count_result.scalar_one() or 0

    return _to_farm_read(farm, field_count)


@router.put("/{farm_id}", response_model=FarmRead, summary="Update a farm")
async def update_farm(
    farm_id: uuid.UUID,
    payload: FarmUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> FarmRead:
    """Update a farm's name.

    Args:
        farm_id: UUID of the farm to update.
        payload: :class:`FarmUpdate` request body with optional fields.
        current_user: Authenticated user from JWT dependency.
        db: Async database session.

    Returns:
        Updated :class:`FarmRead` schema.

    Raises:
        HTTPException: 404 if the farm does not exist or is not owned
            by the current user.
    """
    farm = await _get_owned_farm(farm_id, current_user, db)

    if payload.name is not None:
        farm.name = payload.name

    await db.flush()
    logger.info("Updated farm id=%s for user=%s", farm.id, current_user.id)

    count_result = await db.execute(
        select(func.count(Field.id)).where(Field.farm_id == farm.id)
    )
    field_count: int = count_result.scalar_one() or 0

    return _to_farm_read(farm, field_count)


@router.delete(
    "/{farm_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a farm",
)
async def delete_farm(
    farm_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a farm and all its associated fields (cascade).

    Args:
        farm_id: UUID of the farm to delete.
        current_user: Authenticated user from JWT dependency.
        db: Async database session.

    Raises:
        HTTPException: 404 if the farm does not exist or is not owned
            by the current user.
    """
    farm = await _get_owned_farm(farm_id, current_user, db)
    await db.delete(farm)
    await db.flush()
    logger.info("Deleted farm id=%s for user=%s", farm_id, current_user.id)


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------


async def _get_owned_farm(
    farm_id: uuid.UUID,
    current_user: User,
    db: AsyncSession,
) -> Farm:
    """Fetch a farm, returning 404 if not found or not owned.

    Args:
        farm_id: UUID of the target farm.
        current_user: The authenticated user requesting the resource.
        db: Async database session.

    Returns:
        The :class:`Farm` ORM object if it exists and belongs to the user.

    Raises:
        HTTPException: 404 Not Found if the farm is absent or not owned.
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
