import time

import httpx
from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from typing import Optional

from backend.config import settings

_security = HTTPBearer(auto_error=False)

# CLERK_JWT_ISSUER is already the full JWKS URL
_JWKS_URL = settings.CLERK_JWT_ISSUER

# JWKS keys rotate rarely; fetching them per request added an extra HTTP
# round-trip to Clerk on EVERY authenticated call (latency + rate-limit risk
# in production). Cache for an hour; on verification failure we refetch once
# in case a key rotated.
_JWKS_TTL_SECONDS = 3600
_jwks_cache: dict | None = None
_jwks_fetched_at: float = 0.0


async def _get_jwks(force: bool = False) -> dict:
    global _jwks_cache, _jwks_fetched_at
    now = time.monotonic()
    if not force and _jwks_cache is not None and now - _jwks_fetched_at < _JWKS_TTL_SECONDS:
        return _jwks_cache
    async with httpx.AsyncClient() as client:
        r = await client.get(_JWKS_URL, timeout=5)
        r.raise_for_status()
        _jwks_cache = r.json()
        _jwks_fetched_at = now
        return _jwks_cache


def _decode(token: str, jwks: dict) -> dict:
    # jose picks the correct key by kid automatically
    return jwt.decode(token, jwks, algorithms=["RS256"], options={"verify_aud": False})


async def get_current_user(request: Request) -> str:
    """
    FastAPI dependency.
    Verifies the Clerk JWT from the Authorization header.
    Returns the Clerk user_id (sub claim) on success.
    Raises HTTP 401 on failure.
    """
    credentials: Optional[HTTPAuthorizationCredentials] = await _security(request)

    if not credentials:
        raise HTTPException(status_code=401, detail="Missing authentication token")

    token = credentials.credentials

    try:
        try:
            payload = _decode(token, await _get_jwks())
        except JWTError:
            # The signing key may have rotated since we cached the JWKS —
            # refresh once before rejecting the token.
            payload = _decode(token, await _get_jwks(force=True))
        user_id: str = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        return user_id
    except JWTError as exc:
        raise HTTPException(status_code=401, detail=f"Token verification failed: {exc}")
