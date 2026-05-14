"""Database engine and session factory — convenience re-export.

This module exists for backwards compatibility with code that imports
from ``app.core.database``.  All database objects live in
``app.db.session``; this module simply re-exports them.

Usage::

    from app.core.database import engine, get_db, AsyncSessionLocal
"""

from __future__ import annotations

# Re-export everything from the canonical location
from app.db.session import (  # noqa: F401
    AsyncSessionLocal,
    SessionLocal,
    engine,
    get_db,
    sync_engine,
)
