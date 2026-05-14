"""Pydantic schemas for prescription and management zone endpoints."""

from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator

ApplicationType = Literal["fungicide", "herbicide", "insecticide"]


# ---------------------------------------------------------------------------
# Management zone schemas
# ---------------------------------------------------------------------------


class ManagementZoneRead(BaseModel):
    """Read schema for a management zone."""

    id: uuid.UUID
    field_id: uuid.UUID
    zone_index: int
    zone_label: str
    n_zones: int
    composite_start: date
    composite_end: date
    ndvi_mean: Optional[Decimal]
    ndre_mean: Optional[Decimal]
    area_ha: Optional[Decimal]

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Prescription schemas
# ---------------------------------------------------------------------------


class PrescriptionZoneRead(BaseModel):
    """Per-zone prescription rate, as returned by the API."""

    id: uuid.UUID
    management_zone_id: uuid.UUID
    zone_label: str
    zone_index: int
    multiplier: Decimal
    rate_l_ha: Decimal
    below_minimum_floor: bool

    model_config = {"from_attributes": False}


class PrescriptionRead(BaseModel):
    """Full prescription result for a field, as returned by the API."""

    field_id: uuid.UUID
    application_type: ApplicationType
    base_rate_l_ha: Decimal
    mean_rate_l_ha: Decimal
    savings_pct: Decimal
    disclaimer: str
    composite_start: date
    composite_end: date
    zones: list[PrescriptionZoneRead]
    created_at: datetime

    model_config = {"from_attributes": False}


class PrescriptionCreate(BaseModel):
    """Request body for creating a prescription map."""

    application_type: ApplicationType
    base_rate_l_ha: Decimal = Field(gt=0, description="Base application rate in L/ha.")
    n_zones: int = Field(
        default=3, ge=2, le=5, description="Number of management zones (2–5)."
    )

    @field_validator("base_rate_l_ha")
    @classmethod
    def validate_rate(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("base_rate_l_ha must be greater than 0")
        return v
