"""SatelliteScene ORM model for AgroLens.

Tracks each Sentinel-2 scene downloaded for a field, including the
S3 key prefix of the stored band rasters, acquisition date, and
cloud cover percentage.  Status transitions:
pending → processing → complete | failed.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from app.db.base_class import Base
from sqlalchemy import DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.dialects.postgresql import ENUM as PgEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.models.field import Field


SCENE_STATUS_ENUM = PgEnum(
    "pending",
    "processing",
    "complete",
    "failed",
    name="scenestatus",
    create_type=False,
)


class SatelliteScene(Base):
    """SQLAlchemy ORM model for a single Sentinel-2 scene download.

    Attributes:
        id: UUID primary key.
        field_id: FK to the field this scene covers (cascade delete).
        scene_id: Sentinel Hub scene identifier string.
        acquired_at: UTC acquisition timestamp of the scene.
        cloud_cover_pct: Cloud cover percentage (0–100).
        bands_s3_key: S3 key prefix; band TIFFs stored at
            ``{bands_s3_key}/{band}.tif``.
        status: Processing state: pending | processing | complete | failed.
        created_at: Row creation timestamp (UTC).
        field: Many-to-one back-reference to the parent Field.
    """

    __tablename__ = "satellite_scenes"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Auto-generated UUID primary key.",
    )
    field_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("fields.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="FK → fields.id; cascade deletes scene when field is deleted.",
    )
    scene_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Sentinel Hub scene identifier.",
    )
    acquired_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        comment="UTC acquisition time of the satellite scene.",
    )
    cloud_cover_pct: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 2),
        nullable=True,
        comment="Cloud cover percentage (0–100).",
    )
    bands_s3_key: Mapped[Optional[str]] = mapped_column(
        String(512),
        nullable=True,
        comment="S3 key prefix where band GeoTIFFs are stored.",
    )
    status: Mapped[str] = mapped_column(
        SCENE_STATUS_ENUM,
        nullable=False,
        server_default="pending",
        comment="Processing status: pending | processing | complete | failed.",
    )
    created_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Row creation timestamp (UTC).",
    )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------

    field: Mapped["Field"] = relationship(
        "Field",
        back_populates="satellite_scenes",
        lazy="selectin",
    )
