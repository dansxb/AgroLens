"""SprayingRecord ORM model for §67 PflSchG documentation.

German plant-protection law (§67 Pflanzenschutzgesetz) requires professional
pesticide users to document every application.  A :class:`SprayingRecord`
captures the mandatory fields for each prescription actually applied in the
field.

Required documentation fields (§67 Abs. 1 PflSchG):
  - Field identifier (field_id / FLIK-Nummer via Field.flik)
  - Date of application (applied_at)
  - Product name and registration number
  - Applied quantity (actual_rate_l_ha × field area)
  - Target pest / application purpose
  - Operator name and equipment ID

Records are created by the farmer after each application and linked to the
prescription that generated the rates.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from app.db.base_class import Base
from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.models.prescription import Prescription


class SprayingRecord(Base):
    """ORM model for a pesticide application documentation record (§67 PflSchG).

    Attributes:
        id: UUID primary key.
        prescription_id: FK → prescriptions.id (SET NULL on delete — records
            must survive prescription deletion for compliance).
        field_id: FK → fields.id (CASCADE delete).
        applied_at: UTC timestamp when the application took place.
        product_name: Commercial name of the pesticide product.
        product_reg_number: Official registration number of the pesticide.
        target_pest: Pest or disease targeted by this application.
        actual_rate_l_ha: Rate actually applied (may differ from prescribed).
        area_sprayed_ha: Total field area covered by this application.
        operator_name: Name of the person who operated the equipment.
        equipment_id: Identifier of the sprayer/spreader used.
        notes: Optional free-text remarks.
        created_at: UTC record creation timestamp.
    """

    __tablename__ = "spraying_records"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
        comment="Auto-generated UUID primary key.",
    )
    prescription_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("prescriptions.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="FK → prescriptions.id (nullable: record survives prescription deletion).",
    )
    field_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("fields.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="FK → fields.id.",
    )
    applied_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        comment="UTC timestamp when the application was performed.",
    )
    product_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Commercial product name of the pesticide applied.",
    )
    product_reg_number: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Official pesticide registration number (e.g. BVL Zulassungsnummer).",
    )
    target_pest: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="Pest, disease, or weed targeted by this application.",
    )
    actual_rate_l_ha: Mapped[Decimal] = mapped_column(
        Numeric(10, 4),
        nullable=False,
        comment="Actual application rate in L/ha (may differ from prescribed rate).",
    )
    area_sprayed_ha: Mapped[Decimal] = mapped_column(
        Numeric(12, 4),
        nullable=False,
        comment="Total area covered by this spraying pass in hectares.",
    )
    operator_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Name of the equipment operator (§67 PflSchG requirement).",
    )
    equipment_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Identifier of the sprayer / spreader used.",
    )
    notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Optional free-text remarks.",
    )
    created_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Row creation timestamp (UTC).",
    )

    prescription: Mapped[Optional["Prescription"]] = relationship(
        "Prescription", back_populates="spraying_records"
    )
