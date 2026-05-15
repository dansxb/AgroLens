"""Field ORM model for AgroLens.

A :class:`Field` represents a single agricultural plot with a PostGIS
polygon geometry stored in EPSG:4326 (WGS84).  Each field belongs to a
:class:`~app.models.farm.Farm`.

The ``area_ha`` column is computed from the geometry using PostGIS
``ST_Area(ST_Transform(geometry, 3857)) / 10000`` and is populated at
insert/update time by the API layer before committing to the database.

The ``crop_type`` column is backed by a PostgreSQL native enum type
``croptype`` to enforce valid values at the database level.
"""

from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING, List, Optional

from app.db.base_class import Base
from geoalchemy2 import Geometry, WKBElement
from sqlalchemy import (
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Numeric,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.models.farm import Farm
    from app.models.management_zone import ManagementZone
    from app.models.prescription import Prescription
    from app.models.satellite_scene import SatelliteScene
    from app.models.vegetation_index import VegetationIndex


# PostgreSQL native ENUM for crop type — kept as a module-level constant so
# the Alembic migration can reference the same definition.
CROP_TYPE_ENUM = Enum(
    "wheat",
    "rapeseed",
    "barley",
    "maize",
    "soybeans",
    name="croptype",
)


class Field(Base):
    """SQLAlchemy ORM model representing an agricultural field (plot).

    Attributes:
        id: UUID primary key (auto-generated).
        farm_id: Foreign key referencing the parent :class:`~app.models.farm.Farm`.
        name: Human-readable field name (required, max 255 chars).
        crop_type: Crop grown in this field; one of the ``croptype`` enum values.
        planting_date: Optional date when the current crop was planted.
        geometry: PostGIS polygon geometry in EPSG:4326 (WGS84).
        area_ha: Field area in hectares (computed via PostGIS, stored as
            ``Numeric(10, 1)``).
        created_at: UTC creation timestamp set by the database server.
        updated_at: UTC last-update timestamp maintained by the database.
        farm: Many-to-one relationship to the parent :class:`~app.models.farm.Farm`.
    """

    __tablename__ = "fields"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Auto-generated UUID primary key.",
    )
    farm_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("farms.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="FK → farms.id; cascade deletes field when farm is deleted.",
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Field name (required).",
    )
    crop_type: Mapped[Optional[str]] = mapped_column(
        CROP_TYPE_ENUM,
        nullable=True,
        comment="Crop type planted in this field.",
    )
    planting_date: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True,
        comment="Date when the current crop was planted (nullable).",
    )
    geometry: Mapped[Optional[WKBElement]] = mapped_column(
        Geometry("POLYGON", srid=4326),
        nullable=True,
        comment="Field boundary as a PostGIS polygon in EPSG:4326.",
    )
    area_ha: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 4),
        nullable=True,
        comment=(
            "Field area in hectares, 4 decimal places "
            "(computed via ST_Area(ST_Transform(geometry, 3857)) / 10000)."
        ),
    )
    flik: Mapped[Optional[str]] = mapped_column(
        String(18),
        nullable=True,
        comment="FLIK-Nummer (Feldstücks-Kennzahl) for German InVeKoS cross-compliance.",
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

    farm: Mapped["Farm"] = relationship(
        "Farm",
        back_populates="fields",
        lazy="selectin",
    )
    satellite_scenes: Mapped[List["SatelliteScene"]] = relationship(
        "SatelliteScene",
        back_populates="field",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    vegetation_indices: Mapped[List["VegetationIndex"]] = relationship(
        "VegetationIndex",
        back_populates="field",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    management_zones: Mapped[List["ManagementZone"]] = relationship(
        "ManagementZone",
        back_populates="field",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    prescriptions: Mapped[List["Prescription"]] = relationship(
        "Prescription",
        back_populates="field",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
