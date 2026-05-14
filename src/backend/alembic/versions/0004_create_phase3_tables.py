"""Create management_zones, prescriptions, and spraying_records tables.

Revision ID: 0004
Revises: 0003
Create Date: 2026-05-13

This migration:
1. Creates three PostgreSQL native enum types:
   - ``zonelabel``:      Low / Medium-Low / Medium / Medium-High / High / Very High
   - ``applicationtype``: fungicide / herbicide / insecticide
2. Creates the ``management_zones`` table (zone delineation results per field
   and composite window) with PostGIS MULTIPOLYGON geometry.
3. Creates the ``prescriptions`` table linking zones to per-zone application rates.
4. Creates the ``spraying_records`` table for §67 PflSchG documentation.
5. Creates all required indexes.

All enum types are guarded by idempotent ``DO $$ BEGIN ... EXCEPTION WHEN
duplicate_object THEN null; END $$;`` blocks for safe re-runs.
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import ENUM as PgEnum, UUID


revision: str = "0004"
down_revision: str | None = "0003"
branch_labels: str | None = None
depends_on: str | None = None


def _create_enum(name: str, *values: str) -> None:
    """Create a PostgreSQL native enum type idempotently."""
    values_sql = ", ".join(f"'{v}'" for v in values)
    op.execute(
        sa.text(
            f"DO $$ BEGIN "
            f"  CREATE TYPE {name} AS ENUM ({values_sql}); "
            f"EXCEPTION WHEN duplicate_object THEN null; "
            f"END $$;"
        )
    )


def upgrade() -> None:
    """Create Phase 3 tables: management_zones, prescriptions, spraying_records."""

    op.execute(sa.text("CREATE EXTENSION IF NOT EXISTS postgis"))

    # ------------------------------------------------------------------
    # 1. Enum types
    # ------------------------------------------------------------------
    _create_enum(
        "zonelabel",
        "Low", "Medium-Low", "Medium", "Medium-High", "High", "Very High",
    )
    _create_enum("applicationtype", "fungicide", "herbicide", "insecticide")

    # ------------------------------------------------------------------
    # 2. management_zones
    # ------------------------------------------------------------------
    op.create_table(
        "management_zones",
        sa.Column(
            "id",
            UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "field_id",
            UUID(as_uuid=True),
            sa.ForeignKey("fields.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("zone_index", sa.Integer, nullable=False),
        sa.Column(
            "zone_label",
            PgEnum(
                "Low", "Medium-Low", "Medium", "Medium-High", "High", "Very High",
                name="zonelabel",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("n_zones", sa.Integer, nullable=False, server_default="3"),
        sa.Column("composite_start", sa.Date, nullable=False),
        sa.Column("composite_end", sa.Date, nullable=False),
        sa.Column("ndvi_mean", sa.Numeric(6, 4), nullable=True),
        sa.Column("ndre_mean", sa.Numeric(6, 4), nullable=True),
        sa.Column("area_ha", sa.Numeric(12, 4), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    # Add PostGIS MULTIPOLYGON column via PostGIS function (Alembic generic types cannot express it)
    op.execute(
        sa.text(
            "SELECT AddGeometryColumn('management_zones', 'geometry', 4326, 'MULTIPOLYGON', 2)"
        )
    )

    op.create_index(
        "ix_management_zones_field_id",
        "management_zones",
        ["field_id"],
    )
    op.execute(
        sa.text(
            "CREATE INDEX ix_management_zones_geometry "
            "ON management_zones USING GIST (geometry)"
        )
    )
    # Composite index for "latest zones per field" queries
    op.execute(
        sa.text(
            "CREATE INDEX ix_management_zones_field_composite_end "
            "ON management_zones (field_id, composite_end DESC)"
        )
    )

    # ------------------------------------------------------------------
    # 3. prescriptions
    # ------------------------------------------------------------------
    op.create_table(
        "prescriptions",
        sa.Column(
            "id",
            UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "field_id",
            UUID(as_uuid=True),
            sa.ForeignKey("fields.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "management_zone_id",
            UUID(as_uuid=True),
            sa.ForeignKey("management_zones.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "application_type",
            PgEnum("fungicide", "herbicide", "insecticide", name="applicationtype", create_type=False),
            nullable=False,
        ),
        sa.Column("base_rate_l_ha", sa.Numeric(10, 4), nullable=False),
        sa.Column("multiplier", sa.Numeric(5, 4), nullable=False),
        sa.Column("rate_l_ha", sa.Numeric(10, 4), nullable=False),
        sa.Column(
            "below_minimum_floor",
            sa.Boolean,
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column("disclaimer", sa.Text, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index("ix_prescriptions_field_id", "prescriptions", ["field_id"])
    op.create_index(
        "ix_prescriptions_management_zone_id", "prescriptions", ["management_zone_id"]
    )

    # ------------------------------------------------------------------
    # 4. spraying_records
    # ------------------------------------------------------------------
    op.create_table(
        "spraying_records",
        sa.Column(
            "id",
            UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "prescription_id",
            UUID(as_uuid=True),
            sa.ForeignKey("prescriptions.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "field_id",
            UUID(as_uuid=True),
            sa.ForeignKey("fields.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("applied_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("product_name", sa.String(255), nullable=False),
        sa.Column("product_reg_number", sa.String(50), nullable=False),
        sa.Column("target_pest", sa.String(255), nullable=True),
        sa.Column("actual_rate_l_ha", sa.Numeric(10, 4), nullable=False),
        sa.Column("area_sprayed_ha", sa.Numeric(12, 4), nullable=False),
        sa.Column("operator_name", sa.String(255), nullable=False),
        sa.Column("equipment_id", sa.String(100), nullable=False),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index("ix_spraying_records_field_id", "spraying_records", ["field_id"])
    op.create_index(
        "ix_spraying_records_prescription_id", "spraying_records", ["prescription_id"]
    )
    op.create_index(
        "ix_spraying_records_applied_at", "spraying_records", ["applied_at"]
    )


def downgrade() -> None:
    """Drop Phase 3 tables and enum types."""
    op.drop_index("ix_spraying_records_applied_at", table_name="spraying_records")
    op.drop_index("ix_spraying_records_prescription_id", table_name="spraying_records")
    op.drop_index("ix_spraying_records_field_id", table_name="spraying_records")
    op.drop_table("spraying_records")

    op.drop_index("ix_prescriptions_management_zone_id", table_name="prescriptions")
    op.drop_index("ix_prescriptions_field_id", table_name="prescriptions")
    op.drop_table("prescriptions")

    op.execute(sa.text("DROP INDEX IF EXISTS ix_management_zones_field_composite_end"))
    op.execute(sa.text("DROP INDEX IF EXISTS ix_management_zones_geometry"))
    op.drop_index("ix_management_zones_field_id", table_name="management_zones")
    op.drop_table("management_zones")

    op.execute(sa.text("DROP TYPE IF EXISTS applicationtype"))
    op.execute(sa.text("DROP TYPE IF EXISTS zonelabel"))
