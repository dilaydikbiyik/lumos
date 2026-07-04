import httpx
from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from typing import Optional

from backend.config import settings

_security = HTTPBearer(auto_error=False)

# CLERK_JWT_ISSUER is already the full JWKS URL
_JWKS_URL = settings.CLERK_JWT_ISSUER


async def _get_jwks() -> dict:
    async with httpx.AsyncClient() as client:
        r = await client.get(_JWKS_URL, timeout=5)
        r.raise_for_status()
        return r.json()


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
        jwks = await _get_jwks()
        # jose picks the correct key by kid automatically
        payload = jwt.decode(
            token,
            jwks,
            algorithms=["RS256"],
            options={"verify_aud": False},
        )
        user_id: str = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        return user_id
    except JWTError as exc:
        raise HTTPException(status_code=401, detail=f"Token verification failed: {exc}")
