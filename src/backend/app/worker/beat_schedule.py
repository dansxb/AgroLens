"""Celery Beat periodic task schedule for AgroLens.

Defines the cron-based schedule for all recurring background tasks.
This module is loaded by ``celery_app.config_from_object()`` so that
the schedule is applied automatically when the beat process starts.
"""

from __future__ import annotations

from celery.schedules import crontab

beat_schedule: dict = {
    # Daily imagery pipeline: runs at 02:00 UTC every day.
    # Finds all fields with stale vegetation index data and enqueues
    # fetch + compute tasks for each.
    "daily-imagery-pipeline": {
        "task": "scheduler.trigger_daily_imagery_pipeline",
        "schedule": crontab(hour=2, minute=0),
        "options": {"expires": 3600},  # Drop the task if not picked up within 1 hour
    },
    # Daily NDVI stress check: runs at 07:00 UTC.
    # Compares latest composite against 30-day rolling mean; sends alert emails
    # to users with field_stress_alert notifications enabled when deviation > 15%.
    "daily-stress-alerts": {
        "task": "notifications.check_stress_alerts",
        "schedule": crontab(hour=7, minute=0),
        "options": {"expires": 3600},
    },
}
