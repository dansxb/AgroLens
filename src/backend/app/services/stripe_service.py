"""Stripe API wrapper service.

Provides thin, testable wrappers around the Stripe SDK calls used by
the billing endpoints and webhook handler.  All functions use the
``stripe`` library configured with the secret key from application settings.

Never call stripe.* directly from route handlers — always go through this
module so that test mocks can be applied in one place.
"""

from __future__ import annotations

import logging

import stripe
from app.core.config import settings
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

# Configure the Stripe SDK once at module load time.  The secret key is
# loaded from the environment via Pydantic Settings — never hardcoded.
stripe.api_key = settings.stripe_secret_key


def _resolve_price_id(plan: str, interval: str) -> str:
    """Map a (plan, interval) pair to the corresponding Stripe Price ID.

    Args:
        plan: One of 'starter', 'farmer', 'pro'.
        interval: One of 'monthly', 'annual'.

    Returns:
        Stripe Price ID string (price_…).

    Raises:
        ValueError: If the (plan, interval) combination has no configured price.
    """
    mapping: dict[tuple[str, str], str] = {
        ("starter", "monthly"): settings.stripe_price_id_starter_monthly,
        ("starter", "annual"): settings.stripe_price_id_starter_annual,
        ("farmer", "monthly"): settings.stripe_price_id_farmer_monthly,
        ("farmer", "annual"): settings.stripe_price_id_farmer_annual,
        ("pro", "monthly"): settings.stripe_price_id_pro_monthly,
        ("pro", "annual"): settings.stripe_price_id_pro_annual,
    }
    price_id = mapping.get((plan, interval))
    if not price_id:
        raise ValueError(f"Unknown plan/interval: {plan}/{interval}")
    return price_id


def price_to_plan(price_id: str) -> str:
    """Reverse-map a Stripe Price ID to an AgroLens plan tier.

    Falls back to 'basis' for unknown price IDs so that unrecognised webhook
    events don't silently upgrade a user to an unintended tier.

    Args:
        price_id: Stripe Price ID (price_…).

    Returns:
        Plan tier string ('basis' | 'starter' | 'farmer' | 'pro').
    """
    mapping: dict[str, str] = {
        settings.stripe_price_id_starter_monthly: "starter",
        settings.stripe_price_id_starter_annual: "starter",
        settings.stripe_price_id_farmer_monthly: "farmer",
        settings.stripe_price_id_farmer_annual: "farmer",
        settings.stripe_price_id_pro_monthly: "pro",
        settings.stripe_price_id_pro_annual: "pro",
    }
    return mapping.get(price_id, "basis")


async def get_or_create_customer(user: object, db: AsyncSession) -> str:
    """Return the Stripe Customer ID for the user, creating one if needed.

    Persists the new customer ID to the user row via db.flush() so that
    subsequent calls within the same transaction see the updated value.

    Args:
        user: The authenticated User ORM object (must have .email and
            .stripe_customer_id attributes).
        db: Async database session — flushed after customer creation.

    Returns:
        Stripe Customer ID string (cus_…).
    """
    # Narrow type access via attribute lookup to stay import-free of User model
    if user.stripe_customer_id:  # type: ignore[union-attr]
        return user.stripe_customer_id  # type: ignore[union-attr]

    customer = stripe.Customer.create(
        email=user.email,  # type: ignore[union-attr]
        metadata={"user_id": str(user.id)},  # type: ignore[union-attr]
    )
    user.stripe_customer_id = customer.id  # type: ignore[union-attr]
    await db.flush()
    logger.info(
        "Created Stripe customer %s for user %s",
        customer.id,
        user.id,  # type: ignore[union-attr]
    )
    return customer.id


def create_checkout_session(
    customer_id: str,
    plan: str,
    interval: str,
    success_url: str,
    cancel_url: str,
) -> str:
    """Create a Stripe Checkout Session for a subscription upgrade.

    Args:
        customer_id: Stripe Customer ID (cus_…).
        plan: Target plan tier ('starter' | 'farmer' | 'pro').
        interval: Billing interval ('monthly' | 'annual').
        success_url: Redirect URL after successful payment.
        cancel_url: Redirect URL if the user cancels.

    Returns:
        Stripe-hosted checkout URL.

    Raises:
        ValueError: If the plan/interval combination has no configured price.
        stripe.error.StripeError: On Stripe API failure.
    """
    price_id = _resolve_price_id(plan, interval)
    session = stripe.checkout.Session.create(
        customer=customer_id,
        payment_method_types=["card"],
        mode="subscription",
        line_items=[{"price": price_id, "quantity": 1}],
        success_url=success_url,
        cancel_url=cancel_url,
    )
    return session.url


def create_portal_session(customer_id: str, return_url: str) -> str:
    """Create a Stripe Billing Portal session for self-service management.

    Args:
        customer_id: Stripe Customer ID (cus_…).
        return_url: URL Stripe redirects to when the user exits the portal.

    Returns:
        Stripe Billing Portal URL.

    Raises:
        stripe.error.StripeError: On Stripe API failure.
    """
    session = stripe.billing_portal.Session.create(
        customer=customer_id,
        return_url=return_url,
    )
    return session.url
