"""Create satellite_scenes, vegetation_indices, and pipeline_runs tables.

Revision ID: 0002
Revises: 0001
Create Date: 2026-05-12

This migration:
1. Creates three PostgreSQL native enum types:
   - ``scenestatus``:    pending / processing / complete / failed
   - ``indextype``:      ndvi / ndre
   - ``pipelinestatus``: running / complete / failed
2. Creates the ``satellite_scenes`` table tracking raw downloaded Sentinel-2
   scenes per field, with status lifecycle and S3 key reference.
3. Creates the ``vegetation_indices`` table tracking computed NDVI/NDRE
   composites per field per time window, with aggregate statistics and a
   unique constraint preventing duplicate computations.
4. Creates the ``pipeline_runs`` table recording daily scheduler executions.
5. Creates appropriate indexes for all three tables per the development plan.

Running ``alembic upgrade head`` twice is idempotent — enum creation is
guarded by ``DO $$ ... EXCEPTION WHEN duplicate_object THEN null; END $$;``
and Alembic tracks applied revisions in ``alembic_version``.
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import ENUM as PgEnum, UUID

# ---------------------------------------------------------------------------
# Revision identifiers
# ---------------------------------------------------------------------------
revision: str = "0002"
down_revision: str | None = "0001"
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
    """Create satellite_scenes, vegetation_indices, and pipeline_runs tables."""

    # ------------------------------------------------------------------
    # 1. Create enum types (idempotent guards)
    # ------------------------------------------------------------------
    _create_enum("scenestatus", "pending", "processing", "complete", "failed")
    _create_enum("indextype", "ndvi", "ndre")
    _create_enum("pipelinestatus", "running", "complete", "failed")

    # ------------------------------------------------------------------
    # 2. Create ``satellite_scenes`` table
    # ------------------------------------------------------------------
    op.create_table(
        "satellite_scenes",
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
            "scene_id",
            sa.String(255),
            nullable=False,
            comment="Sentinel Hub scene identifier.",
        ),
        sa.Column(
            "acquired_at",
            sa.DateTime(timezone=True),
            nullable=False,
            comment="UTC acquisition time of the satellite scene.",
        ),
        sa.Column(
            "cloud_cover_pct",
            sa.Numeric(5, 2),
            nullable=True,
            comment="Cloud cover percentage (0–100).",
        ),
        sa.Column(
            "bands_s3_key",
            sa.String(512),
            nullable=True,
            comment="S3 key prefix for stored band GeoTIFFs.",
        ),
        sa.Column(
            "status",
            PgEnum(
                "pending", "processing", "complete", "failed",
                name="scenestatus",
                create_type=False,
            ),
            nullable=False,
            server_default="pending",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    # Composite index for time-range queries per field
    op.create_index(
        "ix_satellite_scenes_field_id_acquired_at",
        "satellite_scenes",
        ["field_id", "acquired_at"],
    )

    # ------------------------------------------------------------------
    # 3. Create ``vegetation_indices`` table
    # ------------------------------------------------------------------
    op.create_table(
        "vegetation_indices",
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
            "composite_start",
            sa.Date,
            nullable=False,
            comment="First date of the compositing window.",
        ),
        sa.Column(
            "composite_end",
            sa.Date,
            nullable=False,
            comment="Last date of the compositing window.",
        ),
        sa.Column(
            "index_type",
            PgEnum("ndvi", "ndre", name="indextype", create_type=False),
            nullable=False,
        ),
        sa.Column(
            "s3_key",
            sa.String(512),
            nullable=False,
            comment="S3 key of the COG GeoTIFF composite raster.",
        ),
        sa.Column("mean_value", sa.Numeric(6, 4), nullable=True),
        sa.Column("min_value", sa.Numeric(6, 4), nullable=True),
        sa.Column("max_value", sa.Numeric(6, 4), nullable=True),
        sa.Column(
            "valid_pixel_pct",
            sa.Numeric(5, 2),
            nullable=True,
            comment="Percentage of cloud-free valid pixels.",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        # Unique constraint prevents duplicate computations
        sa.UniqueConstraint(
            "field_id",
            "composite_start",
            "composite_end",
            "index_type",
            name="uq_vegetation_indices_field_window_type",
        ),
    )
    # Index for "latest composite per field" queries (DESC on composite_end)
    op.execute(
        sa.text(
            "CREATE INDEX ix_vegetation_indices_field_composite_end "
            "ON vegetation_indices (field_id, composite_end DESC)"
        )
    )

    # ------------------------------------------------------------------
    # 4. Create ``pipeline_runs`` table
    # ------------------------------------------------------------------
    op.create_table(
        "pipeline_runs",
        sa.Column(
            "id",
            UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "run_at",
            sa.DateTime(timezone=True),
            nullable=False,
            comment="UTC timestamp when the pipeline run started.",
        ),
        sa.Column(
            "fields_processed",
            sa.Integer,
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "fields_failed",
            sa.Integer,
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "status",
            PgEnum(
                "running", "complete", "failed",
                name="pipelinestatus",
                create_type=False,
            ),
            nullable=False,
            server_default="running",
        ),
        sa.Column("error_message", sa.Text, nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index("ix_pipeline_runs_run_at", "pipeline_runs", ["run_at"])


def downgrade() -> None:
    """Drop satellite_scenes, vegetation_indices, and pipeline_runs tables."""
    op.execute(sa.text("DROP INDEX IF EXISTS ix_vegetation_indices_field_composite_end"))
    op.drop_index("ix_pipeline_runs_run_at", table_name="pipeline_runs")
    op.drop_index("ix_satellite_scenes_field_id_acquired_at", table_name="satellite_scenes")

    op.drop_table("pipeline_runs")
    op.drop_table("vegetation_indices")
    op.drop_table("satellite_scenes")

    op.execute(sa.text("DROP TYPE IF EXISTS pipelinestatus"))
    op.execute(sa.text("DROP TYPE IF EXISTS indextype"))
    op.execute(sa.text("DROP TYPE IF EXISTS scenestatus"))
