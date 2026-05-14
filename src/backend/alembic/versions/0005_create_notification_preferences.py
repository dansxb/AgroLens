"""Create notification_preferences table.

Revision ID: 0005
Revises: 0004
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

revision: str = "0005"
down_revision: str | None = "0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create enum type if it does not already exist (idempotent)
    op.execute(
        """
        DO $$ BEGIN
            CREATE TYPE notificationtype AS ENUM ('new_vra_map', 'field_stress_alert');
        EXCEPTION WHEN duplicate_object THEN NULL;
        END $$;
        """
    )

    op.create_table(
        "notification_preferences",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("field_id", UUID(as_uuid=True), sa.ForeignKey("fields.id", ondelete="CASCADE"), nullable=True),
        sa.Column(
            "notification_type",
            sa.Enum("new_vra_map", "field_stress_alert", name="notificationtype", create_type=False),
            nullable=False,
        ),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True, onupdate=sa.func.now()),
    )

    op.create_index("ix_notification_preferences_user_id", "notification_preferences", ["user_id"])
    op.create_index(
        "ix_notification_preferences_user_type",
        "notification_preferences",
        ["user_id", "notification_type"],
    )


def downgrade() -> None:
    op.drop_index("ix_notification_preferences_user_type", table_name="notification_preferences")
    op.drop_index("ix_notification_preferences_user_id", table_name="notification_preferences")
    op.drop_table("notification_preferences")
    op.execute("DROP TYPE IF EXISTS notificationtype;")
