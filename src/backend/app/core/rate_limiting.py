"""SlowAPI Redis sliding-window rate limiter.

Provides a shared limiter instance and the key function used to
identify callers by API key prefix (falling back to IP address).
"""

from __future__ import annotations

from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address


def _key_func(request: Request) -> str:
    """Identify rate-limit bucket by API key prefix or remote IP."""
    # API key bearer token is resolved in deps.py; the prefix is stored
    # on request.state by get_current_user_or_key after successful auth.
    prefix: str | None = getattr(request.state, "api_key_prefix", None)
    if prefix:
        return f"apikey:{prefix}"
    return get_remote_address(request)


limiter = Limiter(key_func=_key_func)

# Default limit applied to all API key-authenticated endpoints.
DEFAULT_RATE_LIMIT = "100/minute"
