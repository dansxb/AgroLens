"""API key management endpoints."""

from __future__ import annotations

import secrets
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.api_key import ApiKey
from app.models.user import User
from app.schemas.api_key import ApiKeyCreate, ApiKeyCreated, ApiKeyRead

router = APIRouter(prefix="/api-keys", tags=["api-keys"])

CurrentUser = Annotated[User, Depends(get_current_user)]
AsyncDB = Annotated[AsyncSession, Depends(get_db)]

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

_KEY_PREFIX = "agro_sk_"
_KEY_RANDOM_BYTES = 24  # 32 base64url chars


def _generate_key() -> tuple[str, str, str]:
    """Return (full_key, key_prefix_8, key_hash)."""
    random_part = secrets.token_urlsafe(_KEY_RANDOM_BYTES)
    full_key = f"{_KEY_PREFIX}{random_part}"
    key_prefix = full_key[:8]
    key_hash = _pwd_context.hash(full_key)
    return full_key, key_prefix, key_hash


@router.post("", response_model=ApiKeyCreated, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    body: ApiKeyCreate,
    current_user: CurrentUser,
    db: AsyncDB,
) -> dict:
    """Create a new API key. Returns the full key exactly once."""
    full_key, key_prefix, key_hash = _generate_key()

    api_key = ApiKey(
        user_id=current_user.id,
        name=body.name,
        key_hash=key_hash,
        key_prefix=key_prefix,
    )
    db.add(api_key)
    await db.commit()
    await db.refresh(api_key)

    return {
        "id": api_key.id,
        "name": api_key.name,
        "key_prefix": api_key.key_prefix,
        "created_at": api_key.created_at,
        "last_used_at": api_key.last_used_at,
        "revoked": api_key.revoked,
        "key": full_key,
    }


@router.get("", response_model=list[ApiKeyRead])
async def list_api_keys(
    current_user: CurrentUser,
    db: AsyncDB,
) -> list[ApiKey]:
    """List all non-revoked API keys for the authenticated user."""
    result = await db.execute(
        select(ApiKey).where(
            ApiKey.user_id == current_user.id,
            ApiKey.revoked.is_(False),
        )
    )
    return list(result.scalars().all())


@router.delete("/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_api_key(
    key_id: uuid.UUID,
    current_user: CurrentUser,
    db: AsyncDB,
) -> None:
    """Revoke (soft-delete) an API key."""
    api_key = await db.get(ApiKey, key_id)
    if api_key is None or api_key.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="API key not found")

    api_key.revoked = True
    await db.commit()


# ---------------------------------------------------------------------------
# Account usage — placed here as it relates to the API / plan management area.
# Phase 5 will populate plan_limit from the Subscription model.
# ---------------------------------------------------------------------------

_account_router = APIRouter(prefix="/account", tags=["account"])


@_account_router.get("/usage")
async def get_account_usage(
    current_user: CurrentUser,
    db: AsyncDB,
) -> dict:
    """Return hectares used vs plan limit for the current user.

    Phase 5 will read the actual limit from the Subscription model.
    Until then, plan_limit is null and usage_pct is 0.
    """
    from sqlalchemy import func as sa_func  # noqa: PLC0415

    from app.models.farm import Farm  # noqa: PLC0415
    from app.models.field import Field  # noqa: PLC0415

    result = await db.execute(
        select(sa_func.coalesce(sa_func.sum(Field.area_ha), 0.0)).join(
            Farm, Farm.id == Field.farm_id
        ).where(Farm.user_id == current_user.id)
    )
    hectares_used: float = float(result.scalar() or 0.0)

    return {
        "hectares_used": round(hectares_used, 4),
        "plan_limit": None,
        "usage_pct": 0.0,
    }
