"""
Request language — read once, threaded everywhere the backend speaks.

The device's UI language arrives as X-Lumos-Lang (set by the frontend's API
interceptor). Anything unknown or absent falls back to Turkish, the reference
locale, so an old client keeps behaving exactly as before.
"""

from fastapi import Request

SUPPORTED = {"tr", "en", "de"}


def get_language(request: Request) -> str:
    lang = (request.headers.get("X-Lumos-Lang") or "tr").lower()[:5]
    return lang if lang in SUPPORTED else "tr"


# Same reader, spelled as a dependency: `lang: str = Depends(language)` keeps
# routers from having to take a Request just to learn what to speak.
language = get_language
