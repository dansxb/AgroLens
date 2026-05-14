"""Plan-based usage limits enforcement.

Each plan tier has a maximum field count, a maximum total area in hectares,
and a flag indicating whether prescription generation is available.

If a user has no Subscription row (e.g. just signed up), they are treated as
a 'basis' user — the most restrictive tier.

Raises HTTP 402 Payment Required when a limit is exceeded so that the
frontend can surface an upgrade prompt.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class PlanLimits:
    """Immutable descriptor of per-plan usage limits.

    Attributes:
        max_fields: Maximum number of fields, or None for unlimited.
        max_ha: Maximum total cultivated area in hectares, or None for unlimited.
        prescriptions_allowed: Whether VRA prescription generation is permitted.
    """

    max_fields: Optional[int]
    max_ha: Optional[float]
    prescriptions_allowed: bool


# Canonical plan limit table — single source of truth for all enforcement logic.
PLAN_LIMITS: dict[str, PlanLimits] = {
    "basis": PlanLimits(
        max_fields=1,
        max_ha=15.0,
        prescriptions_allowed=False,
    ),
    "starter": PlanLimits(
        max_fields=5,
        max_ha=100.0,
        prescriptions_allowed=True,
    ),
    "farmer": PlanLimits(
        max_fields=50,
        max_ha=500.0,
        prescriptions_allowed=True,
    ),
    "pro": PlanLimits(
        max_fields=None,
        max_ha=None,
        prescriptions_allowed=True,
    ),
}


async def _get_user_plan(user_id: object, db: AsyncSession) -> str:
    """Resolve the active plan for a user.

    Falls back to 'basis' if no Subscription row exists.

    Args:
        user_id: UUID of the user.
        db: Async database session.

    Returns:
        Plan tier string ('basis' | 'starter' | 'farmer' | 'pro').
    """
    from app.models.subscription import Subscription  # avoid circular imports

    result = await db.execute(
        select(Subscription.plan).where(Subscription.user_id == user_id)
    )
    plan = result.scalar_one_or_none()
    return plan or "basis"


async def check_field_count_limit(user: object, db: AsyncSession) -> None:
    """Raise HTTP 402 if the user has reached their plan's field count limit.

    Args:
        user: The authenticated user ORM object (must have .id attribute).
        db: Async database session.

    Raises:
        HTTPException: 402 if the field limit for the current plan is reached.
    """
    from app.models.farm import Farm  # avoid circular imports
    from app.models.field import Field  # avoid circular imports

    plan = await _get_user_plan(user.id, db)  # type: ignore[union-attr]
    limits = PLAN_LIMITS[plan]

    if limits.max_fields is None:
        return  # unlimited — skip the count query

    result = await db.execute(
        select(func.count(Field.id))
        .join(Farm, Farm.id == Field.farm_id)
        .where(Farm.user_id == user.id)  # type: ignore[union-attr]
    )
    count = result.scalar_one()

    if count >= limits.max_fields:
        logger.warning(
            "Field limit reached for user=%s plan=%s count=%d limit=%d",
            user.id,  # type: ignore[union-attr]
            plan,
            count,
            limits.max_fields,
        )
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=(
                f"Feldlimit erreicht ({limits.max_fields} Felder). "
                "Bitte upgraden Sie Ihren Plan."
            ),
        )


async def check_ha_limit(user: object, new_area_ha: float, db: AsyncSession) -> None:
    """Raise HTTP 402 if adding new_area_ha would exceed the plan's hectare cap.

    Args:
        user: The authenticated user ORM object (must have .id attribute).
        new_area_ha: Area of the field being created, in hectares.
        db: Async database session.

    Raises:
        HTTPException: 402 if the cumulative area would exceed the plan limit.
    """
    from app.models.farm import Farm  # avoid circular imports
    from app.models.field import Field  # avoid circular imports

    plan = await _get_user_plan(user.id, db)  # type: ignore[union-attr]
    limits = PLAN_LIMITS[plan]

    if limits.max_ha is None:
        return  # unlimited — skip the sum query

    result = await db.execute(
        select(func.coalesce(func.sum(Field.area_ha), 0.0))
        .join(Farm, Farm.id == Field.farm_id)
        .where(Farm.user_id == user.id)  # type: ignore[union-attr]
    )
    existing_ha = float(result.scalar_one() or 0.0)

    if existing_ha + new_area_ha > limits.max_ha:
        logger.warning(
            "Ha limit reached for user=%s plan=%s existing=%.2f new=%.2f limit=%.1f",
            user.id,  # type: ignore[union-attr]
            plan,
            existing_ha,
            new_area_ha,
            limits.max_ha,
        )
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=(
                f"Flächenlimit erreicht ({limits.max_ha} ha). "
                "Bitte upgraden Sie Ihren Plan."
            ),
        )


async def check_prescription_limit(user: object, db: AsyncSession) -> None:
    """Raise HTTP 402 if prescription generation is not available on this plan.

    Args:
        user: The authenticated user ORM object (must have .id attribute).
        db: Async database session.

    Raises:
        HTTPException: 402 if the plan does not permit prescriptions.
    """
    plan = await _get_user_plan(user.id, db)  # type: ignore[union-attr]
    limits = PLAN_LIMITS[plan]

    if not limits.prescriptions_allowed:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Ausbringungskarten erfordern mindestens den Starter-Plan.",
        )
