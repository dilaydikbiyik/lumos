"""
Rate limiting, per READER.

It was keyed by the connecting address, and behind Render's proxy that is
the proxy: every reader shared one bucket, so about ten active people on a
10/minute endpoint locked each other out. The key is the signed-in account
(the token's subject, read without verifying — verification happens in the
route, and a forged subject only chooses which bucket a request that will
be rejected anyway counts against). Unauthenticated calls fall back to the
forwarded client address.
"""
import base64
import json

from slowapi import Limiter
from starlette.requests import Request


def _subject(token: str) -> str | None:
    try:
        payload = token.split(".")[1]
        payload += "=" * (-len(payload) % 4)
        return json.loads(base64.urlsafe_b64decode(payload)).get("sub")
    except Exception:
        return None


def reader_key(request: Request) -> str:
    auth = request.headers.get("authorization", "")
    if auth.lower().startswith("bearer "):
        subject = _subject(auth[7:])
        if subject:
            return f"user:{subject}"
    forwarded = request.headers.get("x-forwarded-for", "")
    if forwarded:
        return f"ip:{forwarded.split(',')[0].strip()}"
    return f"ip:{request.client.host if request.client else 'unknown'}"


limiter = Limiter(key_func=reader_key)
