"""Pydantic schemas for the Field resource.

Defines request/response models for the Field CRUD API endpoints.
GeoJSON geometry is accepted as a plain ``dict`` on input and returned
as a plain ``dict`` on output (the serialisation to/from WKB is handled
in the route layer via PostGIS ``ST_GeomFromGeoJSON`` /
``ST_AsGeoJSON``).
"""

from __future__ import annotations

import enum
import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CropType(str, enum.Enum):
    """Valid crop types for a field.

    Values must match the ``croptype`` PostgreSQL enum defined in the
    Alembic migration.
    """

    wheat = "wheat"
    rapeseed = "rapeseed"
    barley = "barley"
    maize = "maize"
    soybeans = "soybeans"


class FieldCreate(BaseModel):
    """Schema for creating a new field.

    Geometry is supplied as a GeoJSON ``Polygon`` feature object,
    e.g. ``{"type": "Polygon", "coordinates": [[[...]]]}``).

    Attributes:
        farm_id: UUID of the parent farm.
        name: Human-readable field name.
        crop_type: Crop type (one of the ``CropType`` enum values).
        planting_date: Optional date when the current crop was planted.
        geometry: GeoJSON Polygon geometry dict.
    """

    farm_id: uuid.UUID = Field(..., description="UUID of the parent farm.")
    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Field name.",
        examples=["North Field"],
    )
    crop_type: Optional[CropType] = Field(
        default=None,
        description="Crop type planted in this field.",
    )
    planting_date: Optional[date] = Field(
        default=None,
        description="Date when the current crop was planted.",
    )
    geometry: Dict[str, Any] = Field(
        ...,
        description=(
            "GeoJSON Polygon geometry, e.g. "
            '{"type": "Polygon", "coordinates": [[[lon, lat], ...]]}.'
        ),
    )

    @field_validator("geometry")
    @classmethod
    def validate_polygon_geometry(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure the geometry is a valid GeoJSON Polygon.

        Args:
            v: The raw geometry dict from the request body.

        Returns:
            The validated geometry dict unchanged.

        Raises:
            ValueError: If the geometry type is not ``Polygon``.
        """
        geo_type = v.get("type")
        if geo_type != "Polygon":
            raise ValueError(
                f"geometry.type must be 'Polygon', got '{geo_type}'. "
                "MultiPolygon and other geometry types are not supported."
            )
        coordinates = v.get("coordinates")
        if not coordinates or not isinstance(coordinates, list):
            raise ValueError("geometry.coordinates must be a non-empty list of rings.")
        return v


class FieldUpdate(BaseModel):
    """Schema for partially updating an existing field.

    All fields are optional to support PATCH-style semantics via PUT.

    Attributes:
        name: New field name.
        crop_type: Updated crop type.
        planting_date: Updated planting date.
        geometry: Updated GeoJSON Polygon geometry.
    """

    name: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=255,
        description="Updated field name.",
    )
    crop_type: Optional[CropType] = Field(
        default=None,
        description="Updated crop type.",
    )
    planting_date: Optional[date] = Field(
        default=None,
        description="Updated planting date.",
    )
    geometry: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Updated GeoJSON Polygon geometry.",
    )

    @field_validator("geometry")
    @classmethod
    def validate_polygon_geometry(
        cls, v: Optional[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """Validate updated geometry is a Polygon if provided.

        Args:
            v: Optional geometry dict.

        Returns:
            The validated geometry dict, or None if not provided.

        Raises:
            ValueError: If provided geometry is not a Polygon.
        """
        if v is None:
            return v
        geo_type = v.get("type")
        if geo_type != "Polygon":
            raise ValueError(f"geometry.type must be 'Polygon', got '{geo_type}'.")
        return v


class FieldRead(BaseModel):
    """Schema returned by the API for field read operations.

    Geometry is returned as a GeoJSON dict (deserialised from PostGIS
    ``ST_AsGeoJSON`` output in the route layer).

    Attributes:
        id: Field UUID.
        farm_id: UUID of the parent farm.
        name: Field name.
        crop_type: Crop type enum value (or None).
        planting_date: Planting date (or None).
        geometry: GeoJSON Polygon dict (or None if not set).
        area_ha: Computed field area in hectares (or None).
        created_at: UTC creation timestamp.
    """

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    farm_id: uuid.UUID
    name: str
    crop_type: Optional[CropType] = None
    planting_date: Optional[date] = None
    geometry: Optional[Dict[str, Any]] = None
    area_ha: Optional[Decimal] = None
    created_at: datetime
