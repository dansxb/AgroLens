"""Pydantic schemas for the User resource.

Defines request/response models for the user profile API endpoints
(``GET /api/v1/users/me``, ``PUT /api/v1/users/me``,
``DELETE /api/v1/users/me``).
"""

from __future__ import annotations

import re
import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class UserRead(BaseModel):
    """Schema returned by the API for user profile reads.

    Attributes:
        id: User UUID (matches Supabase Auth user ID).
        email: User email address.
        full_name: Optional display name.
        farm_name: Optional farm operation name.
        country: ISO 3166-1 alpha-2 country code.
        phone: Optional phone number.
        created_at: UTC account creation timestamp.
    """

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    full_name: Optional[str] = None
    farm_name: Optional[str] = None
    country: Optional[str] = None
    phone: Optional[str] = None
    created_at: datetime


class UserUpdate(BaseModel):
    """Schema for updating the current user's profile.

    All fields are optional — only supplied fields are updated.

    Attributes:
        full_name: Updated display name (1–255 chars).
        farm_name: Updated farm name (1–255 chars).
        country: ISO 3166-1 alpha-2 country code (exactly 2 uppercase letters).
        phone: Optional phone number.
    """

    full_name: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=255,
        description="Updated display name.",
    )
    farm_name: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=255,
        description="Updated farm operation name.",
    )
    country: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=2,
        description="ISO 3166-1 alpha-2 country code (e.g. 'DE', 'GB').",
    )
    phone: Optional[str] = Field(
        default=None,
        description="Optional contact phone number.",
    )

    @field_validator("country")
    @classmethod
    def validate_iso_country(cls, v: Optional[str]) -> Optional[str]:
        """Validate that the country code is a valid ISO 3166-1 alpha-2 value.

        Args:
            v: Two-character country code string (or None).

        Returns:
            Upper-cased country code.

        Raises:
            ValueError: If the code is not two ASCII letters.
        """
        if v is None:
            return v
        upper = v.upper()
        if not re.match(r"^[A-Z]{2}$", upper):
            raise ValueError(
                f"'{v}' is not a valid ISO 3166-1 alpha-2 country code. "
                "Must be exactly two ASCII letters (e.g. 'DE', 'GB', 'FR')."
            )
        return upper
