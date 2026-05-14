"""Unit tests for JWT authentication utilities.

Covers:
- :func:`~app.core.security.verify_supabase_jwt` with a valid token.
- :func:`~app.core.security.verify_supabase_jwt` with an expired token.
- :func:`~app.core.security.verify_supabase_jwt` with a malformed token.
- :func:`~app.api.deps.get_current_user` lazy-provisions a new User record.
- :func:`~app.api.deps.get_current_user` returns existing User record.

All database interactions are mocked so these tests run without a
PostgreSQL instance.
"""

from __future__ import annotations

import uuid
from typing import Any, Dict
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException
from jose.exceptions import ExpiredSignatureError, JWTError

from app.core.security import verify_supabase_jwt


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def valid_payload() -> Dict[str, Any]:
    """Return a minimal valid Supabase JWT payload."""
    return {
        "sub": str(uuid.uuid4()),
        "email": "farmer@example.com",
        "role": "authenticated",
        "exp": 9999999999,  # Far future — won't expire during test run
    }


# ---------------------------------------------------------------------------
# verify_supabase_jwt — positive case
# ---------------------------------------------------------------------------


def test_verify_supabase_jwt_valid(valid_payload: Dict[str, Any]) -> None:
    """A valid JWT returns the decoded payload including the sub claim.

    The ``jose.jwt.decode`` call is mocked so no real secret is needed.
    """
    with patch("app.core.security.jwt.decode", return_value=valid_payload):
        result = verify_supabase_jwt("any.valid.token")

    assert result["sub"] == valid_payload["sub"]
    assert result["email"] == valid_payload["email"]


# ---------------------------------------------------------------------------
# verify_supabase_jwt — expired token
# ---------------------------------------------------------------------------


def test_verify_supabase_jwt_expired() -> None:
    """An expired JWT raises HTTPException with status 401."""
    with patch(
        "app.core.security.jwt.decode",
        side_effect=ExpiredSignatureError("Token expired"),
    ):
        with pytest.raises(HTTPException) as exc_info:
            verify_supabase_jwt("expired.token.here")

    assert exc_info.value.status_code == 401
    assert "expired" in exc_info.value.detail.lower()


# ---------------------------------------------------------------------------
# verify_supabase_jwt — malformed token
# ---------------------------------------------------------------------------


def test_verify_supabase_jwt_malformed() -> None:
    """A malformed/invalid JWT raises HTTPException with status 401."""
    with patch(
        "app.core.security.jwt.decode",
        side_effect=JWTError("Signature verification failed"),
    ):
        with pytest.raises(HTTPException) as exc_info:
            verify_supabase_jwt("not.a.valid.jwt")

    assert exc_info.value.status_code == 401


# ---------------------------------------------------------------------------
# verify_supabase_jwt — missing sub claim
# ---------------------------------------------------------------------------


def test_verify_supabase_jwt_missing_sub() -> None:
    """A JWT payload without a 'sub' claim raises HTTPException 401."""
    payload_no_sub: Dict[str, Any] = {"email": "nosubject@example.com"}
    with patch("app.core.security.jwt.decode", return_value=payload_no_sub):
        with pytest.raises(HTTPException) as exc_info:
            verify_supabase_jwt("token.without.sub")

    assert exc_info.value.status_code == 401


# ---------------------------------------------------------------------------
# get_current_user — lazy provision new user
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_current_user_creates_new_user() -> None:
    """get_current_user creates a new User record when none exists in DB."""
    from app.api.deps import get_current_user
    from app.core.security import get_current_user_payload

    user_uuid = uuid.uuid4()
    test_email = "newfarmer@example.com"
    jwt_payload: Dict[str, Any] = {
        "sub": str(user_uuid),
        "email": test_email,
    }

    # Mock database session
    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None  # No existing user
    mock_db.execute = AsyncMock(return_value=mock_result)
    mock_db.add = MagicMock()
    mock_db.flush = AsyncMock()

    # get_current_user is a plain async def (no @functools.wraps decorator),
    # so __wrapped__ does not exist.  Call the function directly with the
    # positional arguments that FastAPI would inject via Depends().
    user = await get_current_user(payload=jwt_payload, db=mock_db)

    # A new User object was added to the session
    mock_db.add.assert_called_once()
    added_user = mock_db.add.call_args[0][0]
    assert str(added_user.id) == str(user_uuid)
    assert added_user.email == test_email


@pytest.mark.asyncio
async def test_get_current_user_returns_existing_user() -> None:
    """get_current_user returns an existing User without creating a new one."""
    from app.api.deps import get_current_user
    from app.models.user import User

    user_uuid = uuid.uuid4()
    jwt_payload: Dict[str, Any] = {
        "sub": str(user_uuid),
        "email": "existing@example.com",
    }

    existing_user = User(id=user_uuid, email="existing@example.com")

    # Mock database session — returns existing user
    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing_user
    mock_db.execute = AsyncMock(return_value=mock_result)
    mock_db.add = MagicMock()

    user = await get_current_user(payload=jwt_payload, db=mock_db)

    # db.add must NOT have been called for an existing user
    mock_db.add.assert_not_called()
    assert user is existing_user
