"""VegetationIndex ORM model for AgroLens.

Stores the result of a vegetation index (NDVI or NDRE) composite
computation for a specific field and time window.  The raster itself
lives in S3; this record holds aggregate statistics and the S3 key.
"""

from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from app.db.base_class import Base
from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.dialects.postgresql import ENUM as PgEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.models.field import Field


INDEX_TYPE_ENUM = PgEnum(
    "ndvi",
    "ndre",
    name="indextype",
    create_type=False,
)


class VegetationIndex(Base):
    """ORM model for a computed vegetation index composite.

    Attributes:
        id: UUID primary key.
        field_id: FK to the field this composite covers.
        composite_start: First date of the compositing window.
        composite_end: Last date of the compositing window.
        index_type: Which index was computed: ndvi or ndre.
        s3_key: S3 key of the COG GeoTIFF storing the composite raster.
        mean_value: Spatial mean of valid (cloud-free) pixels.
        min_value: Spatial minimum of valid pixels.
        max_value: Spatial maximum of valid pixels.
        valid_pixel_pct: Percentage of cloud-free valid pixels (0–100).
        created_at: Row creation timestamp (UTC).
        field: Many-to-one back-reference to the parent Field.
    """

    __tablename__ = "vegetation_indices"

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
        comment="FK → fields.id.",
    )
    composite_start: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        comment="First date of the compositing window (inclusive).",
    )
    composite_end: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        comment="Last date of the compositing window (inclusive).",
    )
    index_type: Mapped[str] = mapped_column(
        INDEX_TYPE_ENUM,
        nullable=False,
        comment="Index type: ndvi or ndre.",
    )
    s3_key: Mapped[str] = mapped_column(
        String(512),
        nullable=False,
        comment="S3 key of the COG GeoTIFF raster.",
    )
    mean_value: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(6, 4),
        nullable=True,
        comment="Spatial mean of cloud-free pixels.",
    )
    min_value: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(6, 4),
        nullable=True,
        comment="Spatial minimum of cloud-free pixels.",
    )
    max_value: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(6, 4),
        nullable=True,
        comment="Spatial maximum of cloud-free pixels.",
    )
    valid_pixel_pct: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 2),
        nullable=True,
        comment="Percentage of cloud-free pixels (0–100).",
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
        back_populates="vegetation_indices",
        lazy="selectin",
    )
