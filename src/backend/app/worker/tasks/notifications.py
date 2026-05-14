"""Celery tasks for email notifications."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone

import numpy as np
from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.notification_preference import NotificationPreference
from app.models.prescription import Prescription
from app.models.vegetation_index import VegetationIndex
from app.models.field import Field
from app.models.user import User
from app.services.notifications import send_email
from app.worker.celery_app import celery_app

logger = logging.getLogger(__name__)

_NEW_VRA_SUBJECT = "AgroLens: Neuer Applikationsplan verfügbar"
_STRESS_SUBJECT = "AgroLens: Stresswarnung für Ihr Feld"

_NEW_VRA_TEMPLATE = "new_vra_map.html"
_STRESS_TEMPLATE = "field_stress_alert.html"

_STRESS_DEVIATION_THRESHOLD = 0.15  # 15% rolling-average deviation triggers alert


def _render_template(template_name: str, context: dict) -> str:
    """Load and render an email HTML template with simple str.format substitution.

    Raises:
        FileNotFoundError: If the template file does not exist.
        KeyError: If a required context variable is missing from the template.
    """
    import os

    template_dir = os.path.join(os.path.dirname(__file__), "../../../../templates/email")
    template_path = os.path.normpath(os.path.join(template_dir, template_name))
    try:
        with open(template_path, encoding="utf-8") as fh:
            return fh.read().format(**context)
    except FileNotFoundError:
        logger.error("Email template not found: %s", template_path)
        raise
    except KeyError as exc:
        logger.error("Missing context variable %s for template %s", exc, template_name)
        raise


@celery_app.task(name="notifications.send_new_vra_map_notification", bind=True, max_retries=3)
def send_new_vra_map_notification(self, prescription_id: str) -> None:
    """Send an email when a new VRA prescription map is created.

    Checks the user's NotificationPreference (new_vra_map) before sending.
    """
    with SessionLocal() as db:
        prescription = db.get(Prescription, prescription_id)
        if prescription is None:
            logger.warning("Prescription %s not found — skipping notification", prescription_id)
            return

        field = db.get(Field, prescription.field_id)
        if field is None:
            return

        # Resolve user via field → farm → user
        from app.models.farm import Farm

        farm = db.get(Farm, field.farm_id)
        if farm is None:
            return

        user = db.get(User, farm.user_id)
        if user is None:
            return

        pref = db.scalar(
            select(NotificationPreference).where(
                NotificationPreference.user_id == user.id,
                NotificationPreference.notification_type == "new_vra_map",
                NotificationPreference.enabled.is_(True),
            )
        )
        if pref is None:
            logger.debug("new_vra_map notifications disabled for user %s", user.id)
            return

        try:
            html = _render_template(
                _NEW_VRA_TEMPLATE,
                {
                    "field_name": field.name,
                    "application_type": prescription.application_type,
                    "created_at": prescription.created_at.strftime("%d.%m.%Y %H:%M"),
                },
            )
        except (FileNotFoundError, KeyError) as exc:
            logger.error("send_new_vra_map_notification: template error: %s", exc)
            raise self.retry(exc=exc, countdown=60) from exc

        success = send_email(to=user.email, subject=_NEW_VRA_SUBJECT, html_body=html)
        if not success:
            logger.warning(
                "send_new_vra_map_notification: email delivery failed for user=%s prescription=%s",
                user.id, prescription_id,
            )
            raise self.retry(exc=RuntimeError("Email delivery failed"), countdown=120)


@celery_app.task(name="notifications.check_stress_alerts", bind=True)
def check_stress_alerts(self) -> None:
    """Daily task: detect fields with NDVI composite significantly below 30-day rolling mean.

    Sends a stress alert email if the latest composite deviates more than
    _STRESS_DEVIATION_THRESHOLD (15%) from the 30-day rolling average.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(days=30)

    with SessionLocal() as db:
        fields = db.scalars(select(Field)).all()

        for field in fields:
            # Fetch last 30 days of NDVI composites for this field
            rows = db.scalars(
                select(VegetationIndex)
                .where(
                    VegetationIndex.field_id == field.id,
                    VegetationIndex.index_type == "ndvi",
                    VegetationIndex.created_at >= cutoff,
                )
                .order_by(VegetationIndex.created_at.desc())
            ).all()

            if len(rows) < 2:
                continue

            values = np.array([r.mean_value for r in rows], dtype=float)
            latest = values[0]
            rolling_mean = float(np.mean(values[1:]))

            if rolling_mean == 0:
                continue

            deviation = abs(latest - rolling_mean) / rolling_mean
            if deviation < _STRESS_DEVIATION_THRESHOLD:
                continue

            # Check user preference
            from app.models.farm import Farm

            farm = db.get(Farm, field.farm_id)
            if farm is None:
                continue
            user = db.get(User, farm.user_id)
            if user is None:
                continue

            pref = db.scalar(
                select(NotificationPreference).where(
                    NotificationPreference.user_id == user.id,
                    NotificationPreference.notification_type == "field_stress_alert",
                    NotificationPreference.enabled.is_(True),
                )
            )
            if pref is None:
                continue

            try:
                html = _render_template(
                    _STRESS_TEMPLATE,
                    {
                        "field_name": field.name,
                        "ndvi_latest": f"{latest:.3f}",
                        "ndvi_mean": f"{rolling_mean:.3f}",
                        "deviation_pct": f"{deviation * 100:.1f}",
                        "date": datetime.now(timezone.utc).strftime("%d.%m.%Y"),
                    },
                )
            except (FileNotFoundError, KeyError) as exc:
                logger.error("check_stress_alerts: template error for field %s: %s", field.id, exc)
                continue

            success = send_email(to=user.email, subject=_STRESS_SUBJECT, html_body=html)
            if success:
                logger.info(
                    "Stress alert sent for field %s (deviation=%.1f%%)", field.id, deviation * 100
                )
            else:
                logger.warning(
                    "check_stress_alerts: email delivery failed for user=%s field=%s",
                    user.id, field.id,
                )
