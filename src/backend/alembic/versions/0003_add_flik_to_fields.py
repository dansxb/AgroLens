"""Add flik column to fields table.

Revision ID: 0003
Revises: 0002
Create Date: 2026-05-13

Adds the ``flik`` column (FLIK-Nummer / Feldstücks-Kennzahl) to the
``fields`` table.  This is the German InVeKoS field identifier required
for cross-compliance documentation under EU agricultural policy.

The column is nullable — existing fields without a FLIK number are valid.
Length 18 matches the official FLIK format (2-letter state code + 16 digits).
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision: str = "0003"
down_revision: str | None = "0002"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    """Add flik column to fields."""
    op.add_column(
        "fields",
        sa.Column(
            "flik",
            sa.String(18),
            nullable=True,
            comment="FLIK-Nummer (Feldstücks-Kennzahl) for German InVeKoS cross-compliance.",
        ),
    )


def downgrade() -> None:
    """Remove flik column from fields."""
    op.drop_column("fields", "flik")
