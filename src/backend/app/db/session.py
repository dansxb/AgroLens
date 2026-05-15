"""SQLAlchemy database session management.

Provides:
- ``engine`` — async SQLAlchemy engine bound to ``DATABASE_URL``.
- ``AsyncSessionLocal`` — async session factory for FastAPI route handlers.
- ``SessionLocal`` — synchronous session factory for Celery background tasks.
- ``get_db`` — FastAPI dependency that yields an ``AsyncSession`` and
  commits/rolls back automatically.
"""

from __future__ import annotations

import logging
from typing import AsyncGenerator

from app.core.config import settings
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import Session, sessionmaker

logger = logging.getLogger(__name__)

# -------------------------------------------------------------------
# Async engine (used by FastAPI route handlers)
# -------------------------------------------------------------------

engine = create_async_engine(
    settings.database_url,
    pool_pre_ping=True,  # Test connections before using them
    pool_size=10,  # Maximum number of connections in the pool
    max_overflow=20,  # Extra connections allowed above pool_size
    pool_timeout=30,  # Seconds to wait for a connection from pool
    echo=settings.is_development,  # Log SQL statements in development
)

#: Async session factory bound to the async engine.
AsyncSessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)

# -------------------------------------------------------------------
# Sync engine (used by Alembic and Celery tasks)
# -------------------------------------------------------------------

sync_engine = create_engine(
    settings.database_sync_url,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    echo=settings.is_development,
)

#: Synchronous session factory for background tasks and migrations.
SessionLocal: sessionmaker[Session] = sessionmaker(
    bind=sync_engine,
    autoflush=False,
    autocommit=False,
)


# -------------------------------------------------------------------
# FastAPI dependency
# -------------------------------------------------------------------


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that provides a database session per request.

    Yields an :class:`AsyncSession`, commits on success, and rolls back
    on any unhandled exception before closing the session.

    Yields:
        An open :class:`AsyncSession` for the duration of the request.

    Example::

        @router.get("/example")
        async def example(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(Model))
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
