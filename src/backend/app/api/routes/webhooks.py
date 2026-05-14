"""Stripe webhook handler.

Stripe delivers signed webhook events to POST /webhooks/stripe.
The raw request body is verified against the Stripe-Signature header using
the webhook signing secret before any event data is trusted.

Registered in ``main.py`` under prefix ``/api/v1`` (no auth required —
authentication is via Stripe signature verification instead).

Supported event types:
    checkout.session.completed      — subscription activated after payment
    customer.subscription.updated  — plan/status change from Stripe dashboard
    customer.subscription.deleted  — subscription cancelled
    invoice.payment_succeeded       — successful renewal, period end updated
    invoice.payment_failed          — payment failed, status → past_due
"""

from __future__ import annotations

import logging

import stripe
from app.api.deps import get_db
from app.core.config import settings
from app.services.subscription_lifecycle import (
    handle_checkout_completed,
    handle_payment_failed,
    handle_payment_succeeded,
    handle_subscription_deleted,
    handle_subscription_updated,
)
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("/stripe", status_code=200, summary="Stripe webhook receiver")
async def stripe_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    """Receive and process a Stripe webhook event.

    Verifies the Stripe-Signature header before deserialising the payload.
    Unrecognised event types are silently ignored (logged at DEBUG level) to
    ensure forward-compatibility with new Stripe event types.

    Args:
        request: The raw FastAPI Request (body read before JSON parsing so that
            the HMAC signature over the raw bytes remains valid).
        db: Async database session injected by get_db.

    Returns:
        ``{"status": "ok"}`` on success.

    Raises:
        HTTPException: 400 if the signature is invalid or the payload is
            malformed — Stripe will retry on 4xx/5xx responses.
    """
    raw_body = await request.body()
    sig_header = request.headers.get("stripe-signature", "")

    try:
        event = stripe.Webhook.construct_event(
            raw_body, sig_header, settings.stripe_webhook_secret
        )
    except stripe.error.SignatureVerificationError:
        logger.warning("Stripe webhook: invalid signature")
        raise HTTPException(status_code=400, detail="Invalid Stripe signature.")
    except ValueError:
        logger.warning("Stripe webhook: invalid payload")
        raise HTTPException(status_code=400, detail="Invalid payload.")

    event_type: str = event["type"]
    data: dict = event["data"]["object"]

    if event_type == "checkout.session.completed":
        await handle_checkout_completed(data, db)
    elif event_type == "customer.subscription.updated":
        await handle_subscription_updated(data, db)
    elif event_type == "customer.subscription.deleted":
        await handle_subscription_deleted(data, db)
    elif event_type == "invoice.payment_succeeded":
        await handle_payment_succeeded(data, db)
    elif event_type == "invoice.payment_failed":
        await handle_payment_failed(data, db)
    else:
        logger.debug("Unhandled Stripe event type: %s", event_type)

    return {"status": "ok"}
