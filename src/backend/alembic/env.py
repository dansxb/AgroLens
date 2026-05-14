"""Alembic migration environment configuration.

Supports both offline (SQL script generation) and online (direct DB)
migration modes.  The async SQLAlchemy engine is wrapped with
``run_sync`` so that Alembic's synchronous API works transparently.

The database URL is read from the ``DATABASE_SYNC_URL`` environment
variable at runtime — credentials are never stored in ``alembic.ini``.
"""

from __future__ import annotations

import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

# ---------------------------------------------------------------------------
# Alembic Config object — provides access to alembic.ini values
# ---------------------------------------------------------------------------
config = context.config

# Set up Python logging from the [loggers] section of alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ---------------------------------------------------------------------------
# Import all models so Alembic detects them during autogenerate
# ---------------------------------------------------------------------------
# app.db.base imports every model and re-exports Base.metadata
from app.db.base import Base  # noqa: E402

target_metadata = Base.metadata

# ---------------------------------------------------------------------------
# Resolve database URL from environment variable
# ---------------------------------------------------------------------------
# We read DATABASE_SYNC_URL (psycopg2 driver) rather than the async URL.
# This avoids Alembic needing to depend on asyncpg.
_database_url = os.environ.get("DATABASE_SYNC_URL") or os.environ.get("DATABASE_URL")

if not _database_url:
    raise RuntimeError(
        "Neither DATABASE_SYNC_URL nor DATABASE_URL is set. "
        "Set DATABASE_SYNC_URL in your environment before running Alembic."
    )

# Strip async driver prefix if accidentally passed the async URL
if _database_url.startswith("postgresql+asyncpg://"):
    _database_url = _database_url.replace("postgresql+asyncpg://", "postgresql://", 1)

config.set_main_option("sqlalchemy.url", _database_url)


# ---------------------------------------------------------------------------
# Migration helpers
# ---------------------------------------------------------------------------


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    Generates a SQL script without connecting to the database.
    Useful for reviewing migrations or applying them via a DBA.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode against a live database.

    Creates a synchronous connection from the configured URL and
    executes the pending migrations directly.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,  # Use NullPool for migration runs
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
            # Include PostGIS-specific schema objects during autogenerate
            include_schemas=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
