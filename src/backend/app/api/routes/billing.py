"""Stripe billing endpoints.

Routes registered under prefix ``/api/v1`` in ``main.py``:
    GET  /billing/subscription  — return the current user's plan and status
    POST /billing/checkout      — create a Stripe Checkout Session
    POST /billing/portal        — create a Stripe Billing Portal session

All endpoints require a valid Supabase JWT.
"""

from __future__ import annotations

import logging
from typing import Annotated

from app.api.deps import get_current_user, get_db
from app.models.subscription import Subscription
from app.models.user import User
from app.schemas.subscription import (
    CheckoutRequest,
    CheckoutResponse,
    PortalRequest,
    PortalResponse,
    SubscriptionRead,
)
from app.services.stripe_service import (
    create_checkout_session,
    create_portal_session,
    get_or_create_customer,
)
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/billing", tags=["billing"])

# Annotated dependency aliases keep route signatures concise.
CurrentUser = Annotated[User, Depends(get_current_user)]
AsyncDB = Annotated[AsyncSession, Depends(get_db)]


@router.get(
    "/subscription",
    response_model=SubscriptionRead,
    summary="Get current billing subscription",
)
async def get_subscription(user: CurrentUser, db: AsyncDB) -> SubscriptionRead:
    """Return the authenticated user's active plan and Stripe status.

    If the user has no Subscription row (free tier, never paid), a synthetic
    basis/active response is returned without touching the database further.

    Args:
        user: Authenticated user from JWT dependency.
        db: Async database session.

    Returns:
        :class:`SubscriptionRead` with plan, status, and period end date.
    """
    result = await db.execute(
        select(Subscription).where(Subscription.user_id == user.id)
    )
    sub = result.scalar_one_or_none()
    if sub is None:
        # User is on the implicit free tier — no DB row needed.
        return SubscriptionRead(plan="basis", status="active", current_period_end=None)
    return SubscriptionRead.model_validate(sub)


@router.post(
    "/checkout",
    response_model=CheckoutResponse,
    summary="Create a Stripe Checkout Session",
)
async def create_checkout(
    body: CheckoutRequest, user: CurrentUser, db: AsyncDB
) -> CheckoutResponse:
    """Generate a Stripe-hosted checkout URL for a subscription upgrade.

    Creates a Stripe Customer for the user if one does not yet exist, then
    opens a Checkout Session for the requested plan and billing interval.

    Args:
        body: Desired plan tier, billing interval, and redirect URLs.
        user: Authenticated user from JWT dependency.
        db: Async database session.

    Returns:
        :class:`CheckoutResponse` containing the Stripe checkout URL.

    Raises:
        stripe.error.StripeError: Propagated as HTTP 500 by FastAPI exception
            handler if Stripe is unavailable.
    """
    customer_id = await get_or_create_customer(user, db)
    url = create_checkout_session(
        customer_id,
        body.plan,
        body.interval,
        body.success_url,
        body.cancel_url,
    )
    return CheckoutResponse(url=url)


@router.post(
    "/portal",
    response_model=PortalResponse,
    summary="Create a Stripe Billing Portal session",
)
async def create_portal(
    body: PortalRequest, user: CurrentUser, db: AsyncDB
) -> PortalResponse:
    """Generate a Stripe Billing Portal URL for self-service subscription management.

    The portal allows users to update payment methods, view invoices, and
    cancel or upgrade their subscription directly via Stripe's hosted UI.

    Args:
        body: Return URL to redirect to after the user exits the portal.
        user: Authenticated user from JWT dependency.
        db: Async database session.

    Returns:
        :class:`PortalResponse` containing the Stripe portal URL.

    Raises:
        HTTPException: 400 if the user has no Stripe customer account yet.
    """
    if not user.stripe_customer_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Kein Billing-Konto gefunden.",
        )
    url = create_portal_session(user.stripe_customer_id, body.return_url)
    return PortalResponse(url=url)
