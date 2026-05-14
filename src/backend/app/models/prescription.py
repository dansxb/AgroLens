"""Prescription ORM model for AgroLens.

A :class:`Prescription` stores the computed application rate for a single
management zone within a field.  Multiple prescriptions from the same
delineation run together form a Variable Rate Application (VRA) prescription
map that can be exported as Shapefile, TASKDATA.XML, or PDF report.

The ``application_type`` enum matches the keys in
``ml.prescription.engine._MULTIPLIERS``.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import ENUM as PgEnum, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base

if TYPE_CHECKING:
    from app.models.field import Field
    from app.models.management_zone import ManagementZone
    from app.models.spraying_record import SprayingRecord


APPLICATION_TYPE_ENUM = PgEnum(
    "fungicide",
    "herbicide",
    "insecticide",
    name="applicationtype",
    create_type=False,
)


class Prescription(Base):
    """ORM model for a single zone's prescription rate.

    Attributes:
        id: UUID primary key.
        field_id: FK → fields.id (CASCADE delete).
        management_zone_id: FK → management_zones.id (CASCADE delete).
        application_type: Type of pesticide application.
        base_rate_l_ha: Farmer's base application rate in L/ha.
        multiplier: Zone multiplier applied to base_rate_l_ha.
        rate_l_ha: Computed prescription rate in L/ha.
        below_minimum_floor: True when rate is below 50% of base rate.
        disclaimer: Mandatory agronomist disclaimer (German text).
        created_at: UTC creation timestamp.
    """

    __tablename__ = "prescriptions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
        comment="Auto-generated UUID primary key.",
    )
    field_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("fields.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="FK → fields.id.",
    )
    management_zone_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("management_zones.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="FK → management_zones.id.",
    )
    application_type: Mapped[str] = mapped_column(
        APPLICATION_TYPE_ENUM,
        nullable=False,
        comment="Type of pesticide application.",
    )
    base_rate_l_ha: Mapped[Decimal] = mapped_column(
        Numeric(10, 4),
        nullable=False,
        comment="Farmer-supplied base application rate in L/ha.",
    )
    multiplier: Mapped[Decimal] = mapped_column(
        Numeric(5, 4),
        nullable=False,
        comment="Zone multiplier applied to base_rate_l_ha.",
    )
    rate_l_ha: Mapped[Decimal] = mapped_column(
        Numeric(10, 4),
        nullable=False,
        comment="Computed prescription rate in L/ha.",
    )
    below_minimum_floor: Mapped[bool] = mapped_column(
        nullable=False,
        server_default="false",
        comment="True when rate < 50% of base_rate — possible registration minimum conflict.",
    )
    disclaimer: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Mandatory agronomist disclaimer text (German).",
    )
    created_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Row creation timestamp (UTC).",
    )

    field: Mapped["Field"] = relationship("Field", back_populates="prescriptions")
    management_zone: Mapped["ManagementZone"] = relationship(
        "ManagementZone", back_populates="prescriptions"
    )
    spraying_records: Mapped[list["SprayingRecord"]] = relationship(
        "SprayingRecord",
        back_populates="prescription",
        cascade="all, delete-orphan",
    )
