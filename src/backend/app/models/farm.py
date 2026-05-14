"""Farm ORM model for AgroLens.

A :class:`Farm` is a named collection of :class:`~app.models.field.Field`
records owned by a single :class:`~app.models.user.User`.  The farm is the
organisational unit — every field must belong to a farm.

Cascade delete is enabled so that deleting a farm automatically removes
all child fields via the database foreign-key constraint.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from app.db.base_class import Base
from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.models.field import Field
    from app.models.user import User


class Farm(Base):
    """SQLAlchemy ORM model representing an agricultural farm.

    Attributes:
        id: UUID primary key (auto-generated).
        user_id: Foreign key referencing the owning :class:`~app.models.user.User`.
        name: Human-readable farm name (required, max 255 chars).
        created_at: UTC creation timestamp set by the database server.
        updated_at: UTC last-update timestamp maintained by the database.
        user: Many-to-one relationship back to the owning :class:`~app.models.user.User`.
        fields: One-to-many relationship to child :class:`~app.models.field.Field` records.
    """

    __tablename__ = "farms"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Auto-generated UUID primary key.",
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="FK → users.id; cascade deletes farm when user is deleted.",
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Farm name (required).",
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

    user: Mapped["User"] = relationship(
        "User",
        back_populates="farms",
        lazy="selectin",
    )
    fields: Mapped[List["Field"]] = relationship(
        "Field",
        back_populates="farm",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
