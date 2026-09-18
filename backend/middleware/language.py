"""
Request language — read once, threaded everywhere the backend speaks.

The device's UI language arrives as X-Lumos-Lang (set by the frontend's API
interceptor). Anything unknown or absent falls back to Turkish, the reference
locale, so an old client keeps behaving exactly as before.
"""

from contextvars import ContextVar

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

SUPPORTED = {"tr", "en", "de"}

# The request's language, for the few places that need it without being able
# to declare a dependency — chiefly user creation, which happens inside the
# repository layer on whichever endpoint the new account happens to hit first.
language_var: ContextVar[str] = ContextVar("request_language", default="tr")


class LanguageMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # Reset on the way out. Without the token a value can outlive its
        # request, and the one thing reading this is user creation — so a
        # leaked "en" would have started someone else's account in the wrong
        # market. Caught by the suite the moment it was introduced.
        token = language_var.set(get_language(request))
        try:
            return await call_next(request)
        finally:
            language_var.reset(token)


def get_language(request: Request) -> str:
    lang = (request.headers.get("X-Lumos-Lang") or "tr").lower()[:5]
    return lang if lang in SUPPORTED else "tr"


# Same reader, spelled as a dependency: `lang: str = Depends(language)` keeps
# routers from having to take a Request just to learn what to speak.
language = get_language


def current_language() -> str:
    """The language of the request being handled, or the default outside one."""
    return language_var.get()
