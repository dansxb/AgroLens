"""JWT security utilities for AgroLens backend.

Supabase signs JWTs with ES256 (ECDSA P-256).  Public keys are fetched
from the Supabase JWKS endpoint and cached in memory.  HS256 with the
project JWT secret is tried as a fallback for any edge-case tokens.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List

import httpx
from app.core.config import settings
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwk, jwt
from jose.exceptions import ExpiredSignatureError

logger = logging.getLogger(__name__)

_bearer_scheme = HTTPBearer(auto_error=True)

# In-process cache of the Supabase JWKS key list.
_JWKS_CACHE: List[Dict[str, Any]] = []


def _fetch_jwks() -> List[Dict[str, Any]]:
    url = f"{settings.supabase_url}/auth/v1/.well-known/jwks.json"
    try:
        r = httpx.get(url, timeout=5.0)
        r.raise_for_status()
        return r.json().get("keys", [])
    except Exception as exc:
        logger.warning("JWKS fetch failed (%s) — falling back to HS256.", exc)
        return []


def _get_jwks() -> List[Dict[str, Any]]:
    global _JWKS_CACHE
    if not _JWKS_CACHE:
        _JWKS_CACHE = _fetch_jwks()
    return _JWKS_CACHE


def verify_supabase_jwt(token: str) -> Dict[str, Any]:
    """Verify a Supabase-issued JWT and return its decoded payload.

    Tries ES256 verification against each key in the Supabase JWKS, then
    falls back to HS256 with the project JWT secret.

    Args:
        token: Raw JWT string (without the ``Bearer `` prefix).

    Returns:
        Decoded JWT payload dictionary.

    Raises:
        HTTPException: 401 if the token is missing, expired, or invalid.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # ── ES256 via JWKS ────────────────────────────────────────────────────────
    for key_data in _get_jwks():
        alg = key_data.get("alg", "ES256")
        try:
            public_key = jwk.construct(key_data, algorithm=alg)
            payload: Dict[str, Any] = jwt.decode(
                token,
                public_key,
                algorithms=[alg],
                options={"verify_aud": False},
            )
            if not payload.get("sub"):
                continue
            return payload
        except ExpiredSignatureError:
            logger.warning("JWT verification failed: token expired.")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except JWTError:
            continue  # try next key

    # ── HS256 fallback ────────────────────────────────────────────────────────
    try:
        payload = jwt.decode(
            token,
            settings.supabase_jwt_secret,
            algorithms=["HS256"],
            options={"verify_aud": False},
        )
        if payload.get("sub"):
            return payload
    except ExpiredSignatureError:
        logger.warning("JWT verification failed: token expired.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError:
        pass

    logger.warning("JWT verification failed: no algorithm succeeded.")
    raise credentials_exception


async def get_current_user_payload(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
) -> Dict[str, Any]:
    """FastAPI dependency that validates the Bearer token.

    Args:
        credentials: Parsed HTTP Authorization credentials.

    Returns:
        Decoded JWT payload dictionary.

    Raises:
        HTTPException: 401 if the token is invalid or expired.
    """
    return verify_supabase_jwt(credentials.credentials)
