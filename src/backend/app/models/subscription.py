"""Subscription ORM model.

Tracks each user's billing plan, Stripe identifiers, and subscription
status.  One row per user (enforced by the UNIQUE constraint on user_id).

Plan tiers:
    basis   — free tier, limited to 1 field / 15 ha
    starter — up to 5 fields / 100 ha, prescriptions enabled
    farmer  — up to 50 fields / 500 ha, prescriptions enabled
    pro     — unlimited, prescriptions enabled
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from app.db.base_class import Base
from sqlalchemy import DateTime, String, func
from sqlalchemy.dialects.postgresql import ENUM as PgEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

# ---------------------------------------------------------------------------
# Enum type objects — create_type=False because the types are created by the
# Alembic migration (0007) and must not be re-created at ORM load time.
# ---------------------------------------------------------------------------

PLAN_ENUM = PgEnum(
    "basis",
    "starter",
    "farmer",
    "pro",
    name="plantype",
    create_type=False,
)

STATUS_ENUM = PgEnum(
    "trialing",
    "active",
    "past_due",
    "canceled",
    name="subscriptionstatus",
    create_type=False,
)


class Subscription(Base):
    """Billing subscription record for a single user.

    Attributes:
        id: Primary key UUID, generated server-side via gen_random_uuid().
        user_id: FK to users.id; CASCADE delete removes the subscription when
            the user is deleted.
        plan: Active plan tier ('basis' | 'starter' | 'farmer' | 'pro').
        status: Stripe subscription status ('trialing' | 'active' |
            'past_due' | 'canceled').
        stripe_customer_id: Stripe Customer object ID (cus_…).
        stripe_subscription_id: Stripe Subscription object ID (sub_…).
        current_period_end: UTC datetime when the current billing period ends.
        created_at: Row creation timestamp (set by DB).
        updated_at: Row last-updated timestamp (set by SQLAlchemy onupdate).
    """

    __tablename__ = "subscriptions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        unique=True,
        index=True,
    )
    plan: Mapped[str] = mapped_column(
        PLAN_ENUM,
        nullable=False,
        server_default="basis",
    )
    status: Mapped[str] = mapped_column(
        STATUS_ENUM,
        nullable=False,
        server_default="active",
    )
    stripe_customer_id: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        unique=True,
    )
    stripe_subscription_id: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        unique=True,
    )
    current_period_end: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        onupdate=func.now(),
    )
