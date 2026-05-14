"""Celery application factory for AgroLens background task workers.

Configures Celery with Redis as both the broker and result backend.
All configuration is read from the application settings (``app.core.config``)
so that no secrets or URLs are hardcoded here.

Usage::

    celery -A app.worker.celery_app:celery_app worker --loglevel=info
    celery -A app.worker.celery_app:celery_app beat  --loglevel=info
"""

from __future__ import annotations

from celery import Celery

from app.core.config import settings

celery_app: Celery = Celery(
    "agrolens",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=[
        "app.worker.tasks.imagery",
        "app.worker.tasks.indices",
        "app.worker.tasks.scheduler",
        "app.worker.tasks.billing",
        "app.worker.tasks.notifications",
        "app.worker.tasks.zones",
    ],
)

celery_app.conf.update(
    # Serialization
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    # Timezone
    timezone="UTC",
    enable_utc=True,
    # Task behavior
    task_track_started=True,
    task_acks_late=True,
    # Prevent one slow task from blocking the worker
    worker_prefetch_multiplier=1,
    # Result expiry: keep results for 24 hours then discard
    result_expires=86400,
    # Beat schedule is defined in beat_schedule.py
    beat_schedule_filename="/tmp/celerybeat-schedule",
)

# Load the periodic schedule
celery_app.config_from_object("app.worker.beat_schedule")
