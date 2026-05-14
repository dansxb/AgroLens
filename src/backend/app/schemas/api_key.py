"""Pydantic schemas for API key endpoints."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ApiKeyCreate(BaseModel):
    """Request body for creating a new API key."""

    name: str = Field(..., min_length=1, max_length=100)


class ApiKeyRead(BaseModel):
    """Response schema for a listed API key (no secret, prefix only)."""

    id: uuid.UUID
    name: str
    key_prefix: str
    created_at: datetime
    last_used_at: Optional[datetime]
    revoked: bool

    model_config = {"from_attributes": True}


class ApiKeyCreated(ApiKeyRead):
    """Response schema returned once on creation — includes the full key."""

    key: str = Field(..., description="Full API key — shown only once, store securely.")
