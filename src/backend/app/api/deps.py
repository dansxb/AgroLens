"""FastAPI shared dependencies.

Provides reusable ``Depends()`` callables for:
- ``get_db`` — database session per request (async).
- ``get_current_user`` — authenticated user from Supabase JWT.
- ``get_current_user_payload`` — raw JWT payload (used by API-key auth path).
- ``get_current_user_or_key`` — JWT-first, falls back to API key Bearer token.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from uuid import UUID

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user_payload
from app.db.session import get_db

logger = logging.getLogger(__name__)

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
_bearer = HTTPBearer(auto_error=False)


async def get_current_user(
    payload: Dict[str, Any] = Depends(get_current_user_payload),
    db: AsyncSession = Depends(get_db),
) -> "User":  # type: ignore[name-defined]  # noqa: F821
    """Return the authenticated User ORM object for the current request.

    Validates the Supabase JWT via :func:`get_current_user_payload`,
    then looks up or lazily creates the corresponding :class:`User`
    record in the local database.

    Args:
        payload: Decoded JWT payload dictionary.
        db: Async database session from :func:`get_db`.

    Returns:
        The :class:`~app.models.user.User` ORM instance for the
        authenticated caller.

    Raises:
        HTTPException: 401 if the JWT is invalid.
        HTTPException: 401 if the user ID cannot be extracted from the payload.
    """
    # Import here to avoid circular imports at module load time.
    from app.models.user import User  # noqa: PLC0415

    user_id_str: Optional[str] = payload.get("sub")
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: missing user identifier.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_uuid = UUID(user_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: malformed user identifier.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Look up existing user record
    result = await db.execute(select(User).where(User.id == user_uuid))
    user: Optional[User] = result.scalar_one_or_none()

    if user is None:
        # Lazily provision the user record on first authenticated request.
        # Supabase is the authoritative identity source; we mirror the user
        # here for relational integrity and profile data storage.
        email: str = payload.get("email", "")
        user = User(
            id=user_uuid,
            email=email,
        )
        db.add(user)
        await db.flush()  # Assign PK without committing the transaction
        logger.info("Provisioned new user record for sub=%s", user_id_str)

    return user


async def get_current_user_or_key(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer),
    db: AsyncSession = Depends(get_db),
) -> "User":  # type: ignore[name-defined]  # noqa: F821
    """Authenticate via JWT first, then fall back to API key Bearer token.

    On successful API key auth, stores the key prefix in ``request.state``
    so the rate limiter can bucket by key rather than IP.
    """
    from app.models.api_key import ApiKey  # noqa: PLC0415
    from app.models.user import User  # noqa: PLC0415

    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials

    # --- Try JWT first ---
    try:
        from app.core.security import verify_supabase_jwt  # noqa: PLC0415

        payload = verify_supabase_jwt(token)
        user_id_str = payload.get("sub")
        if user_id_str:
            user_uuid = UUID(user_id_str)
            result = await db.execute(select(User).where(User.id == user_uuid))
            user: Optional[User] = result.scalar_one_or_none()
            if user:
                return user
    except Exception:  # noqa: BLE001
        pass

    # --- Fall back to API key lookup ---
    if not token.startswith("agro_sk_"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    key_prefix = token[:8]
    result = await db.execute(
        select(ApiKey).where(
            ApiKey.key_prefix == key_prefix,
            ApiKey.revoked.is_(False),
        )
    )
    candidates = result.scalars().all()

    matched_key: Optional[ApiKey] = None
    for candidate in candidates:
        if _pwd_context.verify(token, candidate.key_hash):
            matched_key = candidate
            break

    if matched_key is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or revoked API key.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Update last_used_at and store prefix for rate limiter
    matched_key.last_used_at = datetime.now(timezone.utc)
    await db.commit()

    request.state.api_key_prefix = key_prefix

    result2 = await db.execute(select(User).where(User.id == matched_key.user_id))
    user = result2.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found.")

    return user
