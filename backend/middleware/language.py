"""
Request language — read once, threaded everywhere the backend speaks.

The device's UI language arrives as X-Lumos-Lang (set by the frontend's API
interceptor). Anything unknown or absent falls back to Turkish, the reference
locale, so an old client keeps behaving exactly as before.
"""

from fastapi import Request

SUPPORTED = {"tr", "en"}


def get_language(request: Request) -> str:
    lang = (request.headers.get("X-Lumos-Lang") or "tr").lower()[:5]
    return lang if lang in SUPPORTED else "tr"
