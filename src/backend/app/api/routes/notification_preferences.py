"""Notification preference endpoints."""

from __future__ import annotations

import logging
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.notification_preference import NotificationPreference
from app.models.user import User
from app.schemas.notification_preference import NotificationPreferenceRead, NotificationPreferenceUpdate

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/notification-preferences", tags=["notifications"])

CurrentUser = Annotated[User, Depends(get_current_user)]
AsyncDB = Annotated[AsyncSession, Depends(get_db)]


@router.get("", response_model=list[NotificationPreferenceRead])
async def list_notification_preferences(
    current_user: CurrentUser,
    db: AsyncDB,
) -> list[NotificationPreference]:
    """Return all notification preferences for the authenticated user."""
    logger.debug("list_notification_preferences: user=%s", current_user.id)
    result = await db.execute(
        select(NotificationPreference).where(
            NotificationPreference.user_id == current_user.id
        )
    )
    prefs = list(result.scalars().all())
    logger.debug("list_notification_preferences: returning %d preferences", len(prefs))
    return prefs


@router.put("/{preference_id}", response_model=NotificationPreferenceRead)
async def update_notification_preference(
    preference_id: uuid.UUID,
    body: NotificationPreferenceUpdate,
    current_user: CurrentUser,
    db: AsyncDB,
) -> NotificationPreference:
    """Toggle a notification preference on or off."""
    pref = await db.get(NotificationPreference, preference_id)
    if pref is None or pref.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Preference not found")

    prev_enabled = pref.enabled
    pref.enabled = body.enabled
    try:
        await db.commit()
        await db.refresh(pref)
    except SQLAlchemyError as exc:
        await db.rollback()
        logger.error(
            "update_notification_preference: db error for pref=%s user=%s: %s",
            preference_id, current_user.id, exc,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update notification preference.",
        ) from exc

    logger.info(
        "update_notification_preference: pref=%s user=%s enabled=%s→%s",
        preference_id, current_user.id, prev_enabled, pref.enabled,
    )
    return pref
