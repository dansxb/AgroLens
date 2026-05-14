"""Pydantic schemas for spraying record (§67 PflSchG) endpoints."""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class SprayingRecordCreate(BaseModel):
    """Request body for logging a pesticide application (§67 PflSchG)."""

    field_id: uuid.UUID
    prescription_id: Optional[uuid.UUID] = None
    applied_at: datetime
    product_name: str = Field(min_length=1, max_length=255)
    product_reg_number: str = Field(min_length=1, max_length=50)
    target_pest: Optional[str] = Field(default=None, max_length=255)
    actual_rate_l_ha: Decimal = Field(gt=0)
    area_sprayed_ha: Decimal = Field(gt=0)
    operator_name: str = Field(min_length=1, max_length=255)
    equipment_id: str = Field(min_length=1, max_length=100)
    notes: Optional[str] = None


class SprayingRecordRead(BaseModel):
    """Response schema for a spraying record."""

    id: uuid.UUID
    prescription_id: Optional[uuid.UUID]
    field_id: uuid.UUID
    applied_at: datetime
    product_name: str
    product_reg_number: str
    target_pest: Optional[str]
    actual_rate_l_ha: Decimal
    area_sprayed_ha: Decimal
    operator_name: str
    equipment_id: str
    notes: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}
