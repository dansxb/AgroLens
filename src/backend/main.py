"""AgroLens FastAPI application entrypoint.

Creates the :class:`~fastapi.FastAPI` application, registers all
routers, configures CORS middleware, and wires up the Sentry error
tracking SDK when running in staging or production.

Run locally::

    uvicorn main:app --reload --host 0.0.0.0 --port 8000

The ``PYTHONPATH`` must include the ``backend/`` directory so that
``app.*`` imports resolve correctly.  This is handled automatically by
the ``Dockerfile`` and the ``docker-compose.yml``.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import sentry_sdk
from app.core.config import settings
from app.core.rate_limiting import limiter
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Sentry initialisation
# ---------------------------------------------------------------------------


def _init_sentry() -> None:
    """Initialise Sentry SDK if a DSN is configured and not in development."""
    if settings.sentry_dsn and not settings.is_development:
        sentry_sdk.init(
            dsn=settings.sentry_dsn,
            environment=settings.environment,
            release=f"agrolens-backend@{settings.app_version}",
            traces_sample_rate=0.1,
            integrations=[
                FastApiIntegration(),
                SqlalchemyIntegration(),
            ],
        )
        logger.info("Sentry SDK initialised (environment=%s).", settings.environment)


# ---------------------------------------------------------------------------
# Application lifespan
# ---------------------------------------------------------------------------


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage application startup and shutdown lifecycle.

    Runs setup logic (logging, Sentry) on startup and tears down
    resources (e.g. connection pool) on shutdown.

    Args:
        app: The FastAPI application instance.
    """
    # --- Startup ---
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    logger.info(
        "Starting AgroLens backend v%s (environment=%s).",
        settings.app_version,
        settings.environment,
    )
    _init_sentry()
    yield
    # --- Shutdown ---
    from app.db.session import engine  # noqa: PLC0415

    await engine.dispose()
    logger.info("AgroLens backend shut down cleanly.")


# ---------------------------------------------------------------------------
# FastAPI application factory
# ---------------------------------------------------------------------------


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Returns:
        Fully configured :class:`~fastapi.FastAPI` instance.
    """
    application = FastAPI(
        title="AgroLens API",
        description=(
            "Precision pesticide intelligence platform — satellite-driven "
            "Variable Rate Application maps for arable farming."
        ),
        version=settings.app_version,
        docs_url="/docs" if not settings.is_production else None,
        redoc_url="/redoc" if not settings.is_production else None,
        openapi_url="/v1/openapi.json",
        lifespan=lifespan,
    )

    # -------------------------------------------------------------------
    # SlowAPI rate limiting middleware
    # -------------------------------------------------------------------
    application.state.limiter = limiter
    application.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    application.add_middleware(SlowAPIMiddleware)

    # -------------------------------------------------------------------
    # CORS middleware
    # Origins are loaded from ALLOWED_ORIGINS env var (comma-separated).
    # Never use allow_origins=["*"] in production.
    # -------------------------------------------------------------------
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )

    # -------------------------------------------------------------------
    # Routers
    # -------------------------------------------------------------------
    from app.api.routes.health import router as health_router  # noqa: PLC0415

    application.include_router(health_router)

    # Phase 1 routers (farms, fields, users) — imported lazily so that
    # missing Phase 1+ model files do not break the Phase 0 health check.
    try:
        from app.api.routes.farms import router as farms_router  # noqa: PLC0415
        from app.api.routes.fields import router as fields_router  # noqa: PLC0415
        from app.api.routes.users import router as users_router  # noqa: PLC0415

        application.include_router(farms_router, prefix="/api/v1")
        application.include_router(fields_router, prefix="/api/v1")
        application.include_router(users_router, prefix="/api/v1")
    except ImportError as exc:
        logger.warning("Phase 1 routers not yet available: %s", exc)

    try:
        from app.api.routes.analytics import router as analytics_router  # noqa: PLC0415
        from app.api.routes.exports import router as exports_router  # noqa: PLC0415
        from app.api.routes.prescriptions import (  # noqa: PLC0415
            router as prescriptions_router,
        )

        application.include_router(prescriptions_router, prefix="/api/v1")
        application.include_router(analytics_router, prefix="/api/v1")
        application.include_router(exports_router, prefix="/api/v1")
    except ImportError as exc:
        logger.warning("Phase 3 routers not yet available: %s", exc)

    try:
        from app.api.routes.api_keys import _account_router
        from app.api.routes.api_keys import router as api_keys_router  # noqa: PLC0415
        from app.api.routes.billing import router as billing_router  # noqa: PLC0415
        from app.api.routes.monitoring import (  # noqa: PLC0415
            router as monitoring_router,
        )
        from app.api.routes.notification_preferences import (  # noqa: PLC0415
            router as notif_router,
        )
        from app.api.routes.webhooks import router as webhooks_router  # noqa: PLC0415

        application.include_router(notif_router, prefix="/api/v1")
        application.include_router(api_keys_router, prefix="/api/v1")
        application.include_router(_account_router, prefix="/api/v1")
        application.include_router(billing_router, prefix="/api/v1")
        application.include_router(webhooks_router, prefix="/api/v1")
        application.include_router(monitoring_router)
    except ImportError as exc:
        logger.warning("Phase 4/5 routers not yet available: %s", exc)

    return application


#: Module-level ASGI application instance used by uvicorn.
app: FastAPI = create_app()
