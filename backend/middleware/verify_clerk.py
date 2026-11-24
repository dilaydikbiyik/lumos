"""
Clerk session tokens, verified on every authenticated request.

PyJWT against Clerk's published keys (JWKS), RS256 only — a token signed with
any other algorithm, or with a key that is not in the set, is refused before
its claims are read. python-jose did this job until 2026-11-25; it is
unmaintained and one of its advisories has no fixed release.

Two properties beyond "the signature is valid":

  * The keys are fetched at most once an hour, and a failed verification
    triggers a refetch (a key may have rotated) only if the last fetch is at
    least a minute old. Refetching on every failure let anyone with a forged
    token make this server call Clerk on every request.
  * The reason a token failed is logged, never returned: the response says
    only that verification failed.
"""
import logging
import time
from typing import Optional

import httpx
import jwt
from fastapi import HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import PyJWK, PyJWKSet

from backend.config import settings

logger = logging.getLogger("lumos.verify_clerk")

_security = HTTPBearer(auto_error=False)

# CLERK_JWT_ISSUER is already the full JWKS URL
_JWKS_URL = settings.CLERK_JWT_ISSUER

_JWKS_TTL_SECONDS = 3600
_JWKS_MIN_REFETCH_SECONDS = 60
_jwks_cache: dict | None = None
_jwks_fetched_at: float = 0.0


async def _get_jwks(force: bool = False) -> dict:
    global _jwks_cache, _jwks_fetched_at
    now = time.monotonic()
    fresh = _jwks_cache is not None and now - _jwks_fetched_at < _JWKS_TTL_SECONDS
    recently = _jwks_cache is not None and now - _jwks_fetched_at < _JWKS_MIN_REFETCH_SECONDS
    if (fresh and not force) or (force and recently):
        return _jwks_cache
    async with httpx.AsyncClient() as client:
        r = await client.get(_JWKS_URL, timeout=5)
        r.raise_for_status()
        _jwks_cache = r.json()
        _jwks_fetched_at = now
        return _jwks_cache


def _decode(token: str, jwks: dict) -> dict:
    """Verify `token` against the key its header names. RS256 only."""
    kid = jwt.get_unverified_header(token).get("kid")
    key: Optional[PyJWK] = None
    for candidate in PyJWKSet.from_dict(jwks).keys:
        if candidate.key_id == kid:
            key = candidate
            break
    if key is None:
        raise jwt.InvalidTokenError("no matching signing key")
    return jwt.decode(token, key.key, algorithms=["RS256"],
                      options={"verify_aud": False, "require": ["exp", "sub"]})


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
        except jwt.InvalidTokenError as exc:
            # The signing key may have rotated since we cached the JWKS —
            # refresh (at most once a minute) before rejecting. Log the reason
            # only: the token itself must never reach a log stream.
            logger.info("jwt verification failed (%s) — retrying with fresh JWKS", type(exc).__name__)
            payload = _decode(token, await _get_jwks(force=True))
        user_id: str = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        return user_id
    except jwt.InvalidTokenError as exc:
        logger.info("jwt rejected (%s)", type(exc).__name__)
        raise HTTPException(status_code=401, detail="Token verification failed")
