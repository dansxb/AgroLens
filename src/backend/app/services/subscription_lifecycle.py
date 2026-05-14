"""Stripe webhook event handlers for subscription lifecycle transitions.

Each handler corresponds to a single Stripe event type and updates the
Subscription row in the database accordingly.  All handlers accept the raw
Stripe event data dict and an async database session.

Handlers call db.flush() — the caller (webhook route) is responsible for the
final commit via the session context manager injected by get_db().

Event coverage:
    checkout.session.completed      → handle_checkout_completed
    customer.subscription.updated   → handle_subscription_updated
    customer.subscription.deleted   → handle_subscription_deleted
    invoice.payment_succeeded       → handle_payment_succeeded
    invoice.payment_failed          → handle_payment_failed
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


async def _get_or_create_subscription(
    stripe_customer_id: str, db: AsyncSession
) -> object | None:
    """Return the Subscription row for the given Stripe customer, creating it
    if it does not yet exist.

    Looks up the User by stripe_customer_id first; returns None and logs a
    warning if no matching user is found (e.g. test webhook events).

    Args:
        stripe_customer_id: Stripe Customer ID (cus_…).
        db: Async database session.

    Returns:
        The Subscription ORM instance, or None if no matching user found.
    """
    from app.models.subscription import Subscription  # avoid circular imports
    from app.models.user import User  # avoid circular imports

    user_result = await db.execute(
        select(User).where(User.stripe_customer_id == stripe_customer_id)
    )
    user = user_result.scalar_one_or_none()
    if user is None:
        logger.warning(
            "Webhook: no user found for stripe_customer_id=%s", stripe_customer_id
        )
        return None

    sub_result = await db.execute(
        select(Subscription).where(Subscription.user_id == user.id)
    )
    sub = sub_result.scalar_one_or_none()
    if sub is None:
        sub = Subscription(user_id=user.id, plan="basis", status="active")
        db.add(sub)
        await db.flush()

    return sub


async def handle_checkout_completed(data: dict, db: AsyncSession) -> None:
    """Handle checkout.session.completed — activate the chosen subscription.

    Retrieves the Stripe Subscription object to get the current price ID and
    period end, then updates the local Subscription row.

    Args:
        data: Stripe CheckoutSession object dict.
        db: Async database session.
    """
    import stripe  # import here so tests can mock without top-level side effect
    from app.services.stripe_service import price_to_plan  # avoid circular import

    customer_id: str | None = data.get("customer")
    sub_id: str | None = data.get("subscription")
    if not customer_id or not sub_id:
        logger.debug("checkout.session.completed missing customer or subscription id")
        return

    sub = await _get_or_create_subscription(customer_id, db)
    if sub is None:
        return

    stripe_sub = stripe.Subscription.retrieve(sub_id)
    price_id: str = stripe_sub["items"]["data"][0]["price"]["id"]
    plan = price_to_plan(price_id)
    period_end = stripe_sub.get("current_period_end")

    sub.stripe_subscription_id = sub_id  # type: ignore[union-attr]
    sub.plan = plan  # type: ignore[union-attr]
    sub.status = "active"  # type: ignore[union-attr]
    sub.current_period_end = (  # type: ignore[union-attr]
        datetime.fromtimestamp(period_end, tz=timezone.utc) if period_end else None
    )
    await db.flush()
    logger.info("Checkout completed: customer=%s plan=%s", customer_id, plan)


async def handle_subscription_updated(data: dict, db: AsyncSession) -> None:
    """Handle customer.subscription.updated — sync plan, status, and period end.

    Args:
        data: Stripe Subscription object dict.
        db: Async database session.
    """
    from app.services.stripe_service import price_to_plan  # avoid circular import

    sub_id: str | None = data.get("id")
    customer_id: str | None = data.get("customer")
    if not sub_id or not customer_id:
        return

    sub = await _get_or_create_subscription(customer_id, db)
    if sub is None:
        return

    price_id: str = data["items"]["data"][0]["price"]["id"]
    plan = price_to_plan(price_id)
    stripe_status: str = data.get("status", "active")

    # Only persist known statuses; default to 'active' for forward-compat.
    valid_statuses = {"trialing", "active", "past_due", "canceled"}
    resolved_status = stripe_status if stripe_status in valid_statuses else "active"

    period_end = data.get("current_period_end")

    sub.plan = plan  # type: ignore[union-attr]
    sub.status = resolved_status  # type: ignore[union-attr]
    sub.current_period_end = (  # type: ignore[union-attr]
        datetime.fromtimestamp(period_end, tz=timezone.utc) if period_end else None
    )
    await db.flush()
    logger.info(
        "Subscription updated: customer=%s plan=%s status=%s",
        customer_id,
        plan,
        resolved_status,
    )


async def handle_subscription_deleted(data: dict, db: AsyncSession) -> None:
    """Handle customer.subscription.deleted — downgrade user to basis plan.

    Args:
        data: Stripe Subscription object dict.
        db: Async database session.
    """
    customer_id: str | None = data.get("customer")
    if not customer_id:
        return

    sub = await _get_or_create_subscription(customer_id, db)
    if sub is None:
        return

    sub.status = "canceled"  # type: ignore[union-attr]
    sub.plan = "basis"  # type: ignore[union-attr]
    await db.flush()
    logger.info("Subscription canceled: customer=%s downgraded to basis", customer_id)


async def handle_payment_succeeded(data: dict, db: AsyncSession) -> None:
    """Handle invoice.payment_succeeded — mark subscription active and update period end.

    Args:
        data: Stripe Invoice object dict.
        db: Async database session.
    """
    customer_id: str | None = data.get("customer")
    if not customer_id:
        return

    sub = await _get_or_create_subscription(customer_id, db)
    if sub is None:
        return

    # Extract period end from the first invoice line item.
    period_end = data.get("lines", {}).get("data", [{}])[0].get("period", {}).get("end")
    sub.status = "active"  # type: ignore[union-attr]
    if period_end:
        sub.current_period_end = datetime.fromtimestamp(  # type: ignore[union-attr]
            period_end, tz=timezone.utc
        )
    await db.flush()
    logger.info("Payment succeeded: customer=%s subscription reactivated", customer_id)


async def handle_payment_failed(data: dict, db: AsyncSession) -> None:
    """Handle invoice.payment_failed — set subscription status to past_due.

    Args:
        data: Stripe Invoice object dict.
        db: Async database session.
    """
    customer_id: str | None = data.get("customer")
    if not customer_id:
        return

    sub = await _get_or_create_subscription(customer_id, db)
    if sub is None:
        return

    sub.status = "past_due"  # type: ignore[union-attr]
    await db.flush()
    logger.warning("Payment failed: customer=%s status=past_due", customer_id)
