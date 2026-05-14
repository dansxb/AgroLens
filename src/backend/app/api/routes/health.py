"""Health check endpoints.

Provides two endpoints:

- ``GET /health`` — returns application status and version.  Always
  responds with HTTP 200 (used by load balancers and docker HEALTHCHECK).
- ``GET /health/db`` — verifies PostgreSQL connectivity.  Returns 503
  if the database is unreachable.
"""

from __future__ import annotations

import logging
from typing import Any, Dict

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_db

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    summary="Application health check",
    response_description="Application status, environment, and version.",
)
async def health_check() -> Dict[str, Any]:
    """Return the application health status.

    This endpoint does **not** check database connectivity — it is
    designed to respond immediately for load-balancer liveness probes.

    Returns:
        A JSON object with ``status``, ``environment``, and ``version``.
    """
    return {
        "status": "ok",
        "environment": settings.environment,
        "version": settings.app_version,
    }


@router.get(
    "/health/db",
    summary="Database connectivity check",
    response_description="Database connectivity status.",
)
async def health_db(
    db: AsyncSession = Depends(get_db),
) -> JSONResponse:
    """Verify that the application can reach PostgreSQL.

    Executes a trivial ``SELECT 1`` query and checks the PostGIS
    extension version to confirm the spatial extension is active.

    Args:
        db: Injected async database session.

    Returns:
        HTTP 200 with ``{"status": "ok", "database": "connected"}`` on
        success, or HTTP 503 with ``{"status": "error", "database":
        "unreachable"}`` if the database cannot be reached.
    """
    try:
        result = await db.execute(text("SELECT PostGIS_Version()"))
        postgis_version: str = result.scalar_one()
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": "ok",
                "database": "connected",
                "postgis_version": postgis_version,
            },
        )
    except Exception as exc:
        logger.error("Database health check failed: %s", exc)
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "error", "database": "unreachable"},
        )
