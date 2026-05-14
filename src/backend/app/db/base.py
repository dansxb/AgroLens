"""Central model registry for Alembic autogenerate.

Import every ORM model here so that Alembic's ``env.py`` can detect
all tables when running ``alembic revision --autogenerate``.

This module should never be imported by application code directly —
use the individual model modules instead.  It exists solely to ensure
``Base.metadata`` contains every table definition.

Note: Model imports are wrapped in try/except blocks so that Phase 0
infrastructure (health checks, DB session, Alembic baseline) works
correctly before Phase 1+ model files are implemented.  Remove the
try/except guards as each phase is completed and the classes are defined.
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

# Re-export Base so alembic/env.py only needs to import from this module.
from app.db.base_class import Base  # noqa: F401
from app.models.api_key import ApiKey  # noqa: F401
from app.models.farm import Farm  # noqa: F401
from app.models.field import Field  # noqa: F401

# Phase 3 models
from app.models.management_zone import ManagementZone  # noqa: F401

# Phase 4 models
from app.models.notification_preference import NotificationPreference  # noqa: F401
from app.models.pipeline_run import PipelineRun  # noqa: F401
from app.models.prescription import Prescription  # noqa: F401

# Phase 2 models
from app.models.satellite_scene import SatelliteScene  # noqa: F401
from app.models.spraying_record import SprayingRecord  # noqa: F401

# Phase 1 models
from app.models.user import User  # noqa: F401
from app.models.vegetation_index import VegetationIndex  # noqa: F401

# ---------------------------------------------------------------------------
# Model imports — add every new model here
# Each block is guarded so that stub files (one-line comments, no class
# definition) do not crash the application during incremental development.
# Once a phase is complete and all classes are defined, the try/except can
# be removed for that block.
# ---------------------------------------------------------------------------


# Phase 5 models
try:
    from app.models.subscription import Subscription  # noqa: F401
except ImportError as _e:
    logger.debug("Phase 5 models not yet implemented: %s", _e)
