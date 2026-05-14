"""User ORM model for AgroLens.

Mirrors the Supabase Auth user record using the Supabase user UUID as
the primary key.  Profile fields (full_name, farm_name, country, phone)
are stored here; authentication itself is fully delegated to Supabase.

The ``stripe_customer_id`` column links this record to the Stripe
billing system (populated during the first checkout session creation).
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base

if TYPE_CHECKING:
    from app.models.api_key import ApiKey
    from app.models.farm import Farm


class User(Base):
    """SQLAlchemy ORM model representing an AgroLens user.

    The ``id`` column is the Supabase user UUID, ensuring a 1-to-1 mapping
    between the Supabase Auth identity and the local profile record.

    Attributes:
        id: UUID primary key — matches the Supabase ``auth.users.id``.
        email: User's email address (unique, from Supabase).
        full_name: Optional display name.
        farm_name: Optional name of the user's farm operation.
        country: ISO 3166-1 alpha-2 country code (2 characters).
        phone: Optional phone number (E.164 or free-form).
        stripe_customer_id: Stripe Customer ID, set on first checkout.
        created_at: UTC timestamp set by the database server on insert.
        updated_at: UTC timestamp updated by the database on every row update.
        farms: Relationship back-ref to all :class:`~app.models.farm.Farm`
            records owned by this user.
    """

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Supabase Auth user UUID — used as primary key.",
    )
    email: Mapped[str] = mapped_column(
        String,
        unique=True,
        nullable=False,
        index=True,
        comment="User email address (sourced from Supabase Auth).",
    )
    full_name: Mapped[Optional[str]] = mapped_column(
        String,
        nullable=True,
        comment="Optional display name.",
    )
    farm_name: Mapped[Optional[str]] = mapped_column(
        String,
        nullable=True,
        comment="Name of the user's farm operation.",
    )
    country: Mapped[Optional[str]] = mapped_column(
        String(2),
        nullable=True,
        comment="ISO 3166-1 alpha-2 country code (e.g. 'DE', 'GB').",
    )
    phone: Mapped[Optional[str]] = mapped_column(
        String,
        nullable=True,
        comment="Optional contact phone number.",
    )
    stripe_customer_id: Mapped[Optional[str]] = mapped_column(
        String,
        nullable=True,
        unique=True,
        comment="Stripe Customer ID — set during the first checkout session.",
    )
    created_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Row creation timestamp (UTC, set by database server).",
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        onupdate=func.now(),
        nullable=True,
        comment="Last update timestamp (UTC, maintained by database on UPDATE).",
    )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------

    farms: Mapped[List["Farm"]] = relationship(
        "Farm",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    api_keys: Mapped[List["ApiKey"]] = relationship(
        "ApiKey",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
