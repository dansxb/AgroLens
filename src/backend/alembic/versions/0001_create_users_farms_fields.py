"""Create users, farms, and fields tables.

Revision ID: 0001
Revises: None
Create Date: 2026-05-12

This migration:
1. Enables the PostGIS extension (idempotent via IF NOT EXISTS).
2. Creates the ``users`` table mirroring Supabase Auth user records.
3. Creates the ``farms`` table linked to users via a CASCADE FK.
4. Creates the ``fields`` table linked to farms via a CASCADE FK,
   including the PostGIS polygon geometry column and derived area_ha.
5. Creates a GIST spatial index on ``fields.geometry``.
6. Creates B-tree indexes on ``fields.farm_id`` and ``farms.user_id``.

Running ``alembic upgrade head`` twice is idempotent — the PostGIS
extension creation is guarded by ``IF NOT EXISTS``, and Alembic tracks
which migrations have been applied in the ``alembic_version`` table.
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import ENUM as PgEnum

# ---------------------------------------------------------------------------
# Revision identifiers (used by Alembic)
# ---------------------------------------------------------------------------
revision: str = "0001"
down_revision: str | None = None
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    """Apply the migration: create extensions and all three tables."""

    # ------------------------------------------------------------------
    # 1. Enable PostGIS extension (idempotent)
    # ------------------------------------------------------------------
    op.execute(sa.text("CREATE EXTENSION IF NOT EXISTS postgis"))
    op.execute(sa.text("CREATE EXTENSION IF NOT EXISTS postgis_topology"))
    op.execute(sa.text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"'))

    # ------------------------------------------------------------------
    # 2. Create croptype enum
    # ------------------------------------------------------------------
    op.execute(
        sa.text(
            "DO $$ BEGIN "
            "  CREATE TYPE croptype AS ENUM "
            "    ('wheat', 'rapeseed', 'barley', 'maize', 'soybeans'); "
            "EXCEPTION WHEN duplicate_object THEN null; "
            "END $$;"
        )
    )

    # ------------------------------------------------------------------
    # 3. Create ``users`` table
    # ------------------------------------------------------------------
    op.create_table(
        "users",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            comment="Supabase Auth user UUID.",
        ),
        sa.Column(
            "email",
            sa.String,
            nullable=False,
            unique=True,
            comment="User email address.",
        ),
        sa.Column(
            "full_name",
            sa.String,
            nullable=True,
            comment="Optional display name.",
        ),
        sa.Column(
            "farm_name",
            sa.String,
            nullable=True,
            comment="Optional farm operation name.",
        ),
        sa.Column(
            "country",
            sa.String(2),
            nullable=True,
            comment="ISO 3166-1 alpha-2 country code.",
        ),
        sa.Column(
            "phone",
            sa.String,
            nullable=True,
            comment="Optional contact phone number.",
        ),
        sa.Column(
            "stripe_customer_id",
            sa.String,
            nullable=True,
            unique=True,
            comment="Stripe Customer ID.",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )
    # Index on email for fast lookups (unique constraint already creates one,
    # but explicit for readability)
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    # ------------------------------------------------------------------
    # 4. Create ``farms`` table
    # ------------------------------------------------------------------
    op.create_table(
        "farms",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "name",
            sa.String(255),
            nullable=False,
            comment="Farm name.",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )
    # B-tree index on user_id for listing farms per user
    op.create_index("ix_farms_user_id", "farms", ["user_id"])

    # ------------------------------------------------------------------
    # 5. Create ``fields`` table
    # ------------------------------------------------------------------
    # The geometry column must be added via raw SQL because GeoAlchemy2's
    # AddGeometryColumn pattern is the most portable way to register it
    # properly with PostGIS's geometry_columns view.
    op.create_table(
        "fields",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "farm_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("farms.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "name",
            sa.String(255),
            nullable=False,
            comment="Field name.",
        ),
        sa.Column(
            "crop_type",
            PgEnum(
                "wheat",
                "rapeseed",
                "barley",
                "maize",
                "soybeans",
                name="croptype",
                create_type=False,
            ),
            nullable=True,
            comment="Crop type grown in this field.",
        ),
        sa.Column(
            "planting_date",
            sa.Date,
            nullable=True,
            comment="Date the current crop was planted.",
        ),
        sa.Column(
            "area_ha",
            sa.Numeric(12, 4),
            nullable=True,
            comment="Field area in hectares, 4 decimal places (computed from geometry).",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )

    # Add geometry column via PostGIS raw SQL for proper metadata registration
    op.execute(
        sa.text(
            "ALTER TABLE fields ADD COLUMN geometry "
            "geometry(Polygon,4326)"
        )
    )

    # ------------------------------------------------------------------
    # 6. Create GIST spatial index on fields.geometry
    # ------------------------------------------------------------------
    op.execute(
        sa.text(
            "CREATE INDEX ix_fields_geometry_gist "
            "ON fields USING GIST (geometry)"
        )
    )

    # ------------------------------------------------------------------
    # 7. Create B-tree index on fields.farm_id
    # ------------------------------------------------------------------
    op.create_index("ix_fields_farm_id", "fields", ["farm_id"])


def downgrade() -> None:
    """Reverse the migration: drop tables in reverse dependency order."""
    # Drop fields first (references farms)
    op.execute(sa.text("DROP INDEX IF EXISTS ix_fields_geometry_gist"))
    op.drop_index("ix_fields_farm_id", table_name="fields")
    op.drop_table("fields")

    # Drop farms (references users)
    op.drop_index("ix_farms_user_id", table_name="farms")
    op.drop_table("farms")

    # Drop users
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")

    # Drop the custom enum type
    op.execute(sa.text("DROP TYPE IF EXISTS croptype"))
