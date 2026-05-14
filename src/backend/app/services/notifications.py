"""SendGrid email delivery service."""

from __future__ import annotations

import logging

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from app.core.config import settings

logger = logging.getLogger(__name__)


def send_email(to: str, subject: str, html_body: str, from_email: str | None = None) -> bool:
    """Send an HTML email via SendGrid.

    Retries once on 5xx transient errors. Returns True on success.
    """
    sender = from_email or settings.sendgrid_from_email
    message = Mail(
        from_email=sender,
        to_emails=to,
        subject=subject,
        html_content=html_body,
    )
    client = SendGridAPIClient(settings.sendgrid_api_key)

    for attempt in range(2):
        try:
            response = client.send(message)
            if response.status_code < 400:
                logger.info("Email sent to %s (status=%s)", to, response.status_code)
                return True
            if response.status_code < 500 or attempt == 1:
                logger.error(
                    "SendGrid error sending to %s: status=%s body=%s",
                    to,
                    response.status_code,
                    response.body,
                )
                return False
            # 5xx on first attempt — retry
            logger.warning("SendGrid 5xx, retrying (attempt %d)", attempt + 1)
        except Exception as exc:  # noqa: BLE001
            logger.exception("SendGrid exception on attempt %d: %s", attempt + 1, exc)
            if attempt == 1:
                return False

    return False
