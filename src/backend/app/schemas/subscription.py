"""Pydantic schemas for Stripe billing and subscription endpoints.

Used by:
    - GET  /billing/subscription  → SubscriptionRead
    - POST /billing/checkout      → CheckoutRequest / CheckoutResponse
    - POST /billing/portal        → PortalRequest / PortalResponse
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict


class SubscriptionRead(BaseModel):
    """Serialised subscription state returned to the frontend.

    Attributes:
        plan: Active plan tier ('basis' | 'starter' | 'farmer' | 'pro').
        status: Stripe status ('trialing' | 'active' | 'past_due' | 'canceled').
        current_period_end: UTC datetime when the current billing period ends,
            or None for free-tier (basis) users.
    """

    model_config = ConfigDict(from_attributes=True)

    plan: str
    status: str
    current_period_end: Optional[datetime] = None


class CheckoutRequest(BaseModel):
    """Request body for creating a Stripe Checkout Session.

    Attributes:
        plan: Target plan tier (must be a paid tier).
        interval: Billing cadence.
        success_url: URL Stripe redirects to on successful payment.
        cancel_url: URL Stripe redirects to if the user cancels.
    """

    plan: Literal["starter", "farmer", "pro"]
    interval: Literal["monthly", "annual"]
    success_url: str
    cancel_url: str


class CheckoutResponse(BaseModel):
    """Response containing the Stripe-hosted checkout URL.

    Attributes:
        url: Redirect the user here to complete payment.
    """

    url: str


class PortalRequest(BaseModel):
    """Request body for creating a Stripe Billing Portal session.

    Attributes:
        return_url: URL Stripe redirects to when the user exits the portal.
    """

    return_url: str


class PortalResponse(BaseModel):
    """Response containing the Stripe Billing Portal URL.

    Attributes:
        url: Redirect the user here to manage their subscription.
    """

    url: str
