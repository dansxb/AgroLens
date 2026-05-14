"""Pydantic schemas for the Farm resource.

Defines request/response models for the Farm CRUD API endpoints.
All schemas use Pydantic v2 model configuration.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class FarmCreate(BaseModel):
    """Schema for creating a new farm.

    Attributes:
        name: Human-readable farm name (1–255 characters).
    """

    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Farm name.",
        examples=["Riverside Farm"],
    )


class FarmUpdate(BaseModel):
    """Schema for partially updating an existing farm.

    All fields are optional to support PATCH-style semantics via PUT.

    Attributes:
        name: New farm name (1–255 characters).
    """

    name: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=255,
        description="Updated farm name.",
    )


class FarmRead(BaseModel):
    """Schema returned by the API for farm read operations.

    Attributes:
        id: Farm UUID.
        user_id: UUID of the owning user.
        name: Farm name.
        created_at: UTC creation timestamp.
        field_count: Number of fields belonging to this farm.
    """

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    name: str
    created_at: datetime
    field_count: int = Field(
        default=0,
        description="Number of fields associated with this farm.",
    )
