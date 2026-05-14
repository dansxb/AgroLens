"""JWT security utilities for AgroLens backend.

Provides Supabase JWT verification using the HS256 algorithm with the
``SUPABASE_JWT_SECRET``, and a FastAPI dependency ``get_current_user``
that validates the Bearer token and returns the authenticated user.

Supabase JWTs use HS256 (HMAC-SHA256) with the project-level JWT
secret found at Supabase Dashboard → Settings → API → JWT Secret.
"""

from __future__ import annotations

import logging
from typing import Any, Dict

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from jose.exceptions import ExpiredSignatureError

from app.core.config import settings

logger = logging.getLogger(__name__)

# FastAPI dependency that extracts the Bearer token from the
# ``Authorization: Bearer <token>`` header.
_bearer_scheme = HTTPBearer(auto_error=True)

# Algorithm used by Supabase for JWT signing.
_ALGORITHM = "HS256"


def verify_supabase_jwt(token: str) -> Dict[str, Any]:
    """Verify a Supabase-issued JWT and return its decoded payload.

    Validates the token signature using ``SUPABASE_JWT_SECRET``, checks
    expiry, and returns the decoded claims dictionary.

    Args:
        token: Raw JWT string (without the ``Bearer `` prefix).

    Returns:
        Decoded JWT payload as a dictionary.  Useful keys include
        ``sub`` (Supabase user UUID), ``email``, ``role``, and ``exp``.

    Raises:
        HTTPException: 401 Unauthorized if the token is missing,
            expired, or has an invalid signature.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload: Dict[str, Any] = jwt.decode(
            token,
            settings.supabase_jwt_secret,
            algorithms=[_ALGORITHM],
            # Supabase JWTs include an audience claim; we accept both
            # "authenticated" (logged-in users) and no audience restriction.
            options={"verify_aud": False},
        )
    except ExpiredSignatureError:
        logger.warning("JWT verification failed: token expired.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError as exc:
        logger.warning("JWT verification failed: %s", exc)
        raise credentials_exception

    user_id: str | None = payload.get("sub")
    if not user_id:
        logger.warning("JWT payload missing 'sub' claim.")
        raise credentials_exception

    return payload


async def get_current_user_payload(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
) -> Dict[str, Any]:
    """FastAPI dependency that validates the Bearer token.

    Extracts the token from the ``Authorization`` header, verifies it,
    and returns the decoded payload.  Inject this dependency into any
    route that requires authentication.

    Args:
        credentials: Parsed HTTP Authorization credentials.

    Returns:
        Decoded JWT payload dictionary.

    Raises:
        HTTPException: 401 if the token is invalid or expired.
    """
    return verify_supabase_jwt(credentials.credentials)
