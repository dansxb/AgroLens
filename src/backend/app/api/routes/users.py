"""User profile API endpoints.

Provides the three self-service endpoints for the authenticated user's
own profile record:
    GET    /api/v1/users/me   — read current profile
    PUT    /api/v1/users/me   — update profile fields
    DELETE /api/v1/users/me   — delete account (local DB record + Supabase user)

All three endpoints require a valid Supabase JWT in the ``Authorization:
Bearer <token>`` header.

Account deletion calls the Supabase Admin API (``supabase_service_role_key``)
to delete the user from Supabase Auth, then deletes the local record
(which cascades to farms → fields via the FK constraints).
"""

from __future__ import annotations

import logging

import httpx
from app.api.deps import get_current_user, get_db
from app.core.config import settings
from app.models.user import User
from app.schemas.user import UserRead, UserUpdate
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.get("/me", response_model=UserRead, summary="Get current user profile")
async def get_me(
    current_user: User = Depends(get_current_user),
) -> UserRead:
    """Return the authenticated user's profile.

    Args:
        current_user: Authenticated user from JWT dependency.

    Returns:
        :class:`UserRead` schema populated from the current user record.
    """
    return UserRead.model_validate(current_user)


@router.put("/me", response_model=UserRead, summary="Update current user profile")
async def update_me(
    payload: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserRead:
    """Update one or more profile fields for the authenticated user.

    Only the fields explicitly supplied in the request body are updated.
    The ``country`` field is validated as an ISO 3166-1 alpha-2 code by
    the :class:`~app.schemas.user.UserUpdate` schema.

    Args:
        payload: :class:`UserUpdate` request body with optional fields.
        current_user: Authenticated user from JWT dependency.
        db: Async database session.

    Returns:
        Updated :class:`UserRead` schema.
    """
    if payload.full_name is not None:
        current_user.full_name = payload.full_name
    if payload.farm_name is not None:
        current_user.farm_name = payload.farm_name
    if payload.country is not None:
        current_user.country = payload.country
    if payload.phone is not None:
        current_user.phone = payload.phone

    await db.flush()
    logger.info("Updated profile for user=%s", current_user.id)
    return UserRead.model_validate(current_user)


@router.delete(
    "/me",
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=None,
    summary="Delete current user account",
)
async def delete_me(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete the authenticated user's account.

    Performs the following steps atomically (within the request
    transaction):
    1. Calls the Supabase Admin API to delete the user from Supabase Auth.
    2. Deletes the local ``User`` record (cascades to farms → fields).

    The caller (frontend) is expected to sign the user out after receiving
    the 204 response and redirect them to the homepage.

    Args:
        current_user: Authenticated user from JWT dependency.
        db: Async database session.

    Raises:
        HTTPException: 502 Bad Gateway if the Supabase Admin API call fails.
    """
    user_id_str = str(current_user.id)

    # ------------------------------------------------------------------
    # 1. Delete from Supabase Auth via Admin API
    # ------------------------------------------------------------------
    supabase_admin_url = f"{settings.supabase_url}/auth/v1/admin/users/{user_id_str}"
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.delete(
                supabase_admin_url,
                headers={
                    "apikey": settings.supabase_service_role_key,
                    "Authorization": f"Bearer {settings.supabase_service_role_key}",
                },
            )
            if response.status_code not in (200, 204):
                logger.error(
                    "Supabase Admin delete failed for user=%s: %s %s",
                    user_id_str,
                    response.status_code,
                    response.text,
                )
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail="Failed to delete user from authentication provider.",
                )
        except httpx.RequestError as exc:
            logger.error(
                "Network error calling Supabase Admin for user=%s: %s",
                user_id_str,
                exc,
            )
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Authentication provider unreachable.",
            )

    # ------------------------------------------------------------------
    # 2. Delete local record (cascades to farms/fields)
    # ------------------------------------------------------------------
    await db.delete(current_user)
    await db.flush()
    logger.info("Deleted account for user=%s", user_id_str)
