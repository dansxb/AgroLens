"""Pydantic schemas for notification preference endpoints."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel

NotificationType = Literal["new_vra_map", "field_stress_alert"]


class NotificationPreferenceRead(BaseModel):
    """Response schema for a notification preference."""

    id: uuid.UUID
    user_id: uuid.UUID
    field_id: Optional[uuid.UUID]
    notification_type: NotificationType
    enabled: bool
    updated_at: Optional[datetime]

    model_config = {"from_attributes": True}


class NotificationPreferenceUpdate(BaseModel):
    """Request body for toggling a notification preference."""

    enabled: bool
