"""Create subscriptions table.

Revision ID: 0007
Revises: 0006
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

revision: str = "0007"
down_revision: str | None = "0006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create the subscriptions table with plantype and subscriptionstatus enums."""
    # Create enum types idempotently (same pattern as migration 0004)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE plantype AS ENUM ('basis', 'starter', 'farmer', 'pro');
        EXCEPTION WHEN duplicate_object THEN null;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE subscriptionstatus AS ENUM ('trialing', 'active', 'past_due', 'canceled');
        EXCEPTION WHEN duplicate_object THEN null;
        END $$;
    """)
    op.create_table(
        "subscriptions",
        sa.Column(
            "id",
            UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "user_id",
            UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column(
            "plan",
            sa.Enum(
                "basis",
                "starter",
                "farmer",
                "pro",
                name="plantype",
                create_existing_type=False,
            ),
            nullable=False,
            server_default="basis",
        ),
        sa.Column(
            "status",
            sa.Enum(
                "trialing",
                "active",
                "past_due",
                "canceled",
                name="subscriptionstatus",
                create_existing_type=False,
            ),
            nullable=False,
            server_default="active",
        ),
        sa.Column("stripe_customer_id", sa.String(255), nullable=True, unique=True),
        sa.Column("stripe_subscription_id", sa.String(255), nullable=True, unique=True),
        sa.Column("current_period_end", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_subscriptions_user_id", "subscriptions", ["user_id"])
    op.create_index(
        "ix_subscriptions_stripe_customer_id",
        "subscriptions",
        ["stripe_customer_id"],
    )
    op.create_index(
        "ix_subscriptions_stripe_subscription_id",
        "subscriptions",
        ["stripe_subscription_id"],
    )


def downgrade() -> None:
    """Drop the subscriptions table and associated enum types."""
    op.drop_index("ix_subscriptions_stripe_subscription_id", table_name="subscriptions")
    op.drop_index("ix_subscriptions_stripe_customer_id", table_name="subscriptions")
    op.drop_index("ix_subscriptions_user_id", table_name="subscriptions")
    op.drop_table("subscriptions")
    op.execute("DROP TYPE IF EXISTS subscriptionstatus;")
    op.execute("DROP TYPE IF EXISTS plantype;")
