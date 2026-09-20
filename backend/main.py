from contextlib import asynccontextmanager
from typing import Callable, cast

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded


from backend.config import settings
from backend.limiter import limiter

# Error monitoring — activates only when SENTRY_DSN is configured; a fresh
# clone without an account runs exactly as before.
if settings.SENTRY_DSN:
    import sentry_sdk

    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.APP_ENV,
        traces_sample_rate=0.1,
        send_default_pii=False,  # never ship user content to a third party
    )
from backend.middleware.error_handler import register_error_handlers
from backend.middleware.language import LanguageMiddleware
from backend.middleware.request_id import RequestIDMiddleware
from backend.routers import admin, backtest, chat, coach, feedback, health, holdings, news, planning, practice, profile, recommend, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown lifecycle.

    Schema is owned by Alembic — run `alembic upgrade head` before starting
    (the Dockerfile CMD does this automatically).
    """
    # Admin bootstrap: promote any IDs listed in ADMIN_CLERK_IDS to admin.
    # Safe to run on every start (idempotent — won't downgrade existing admins).
    if settings.ADMIN_CLERK_IDS:
        import logging
        from backend.db.database import AsyncSessionLocal
        from backend.repositories import user_repository

        _log = logging.getLogger("lumos.startup")
        ids = [uid.strip() for uid in settings.ADMIN_CLERK_IDS.split(",") if uid.strip()]
        async with AsyncSessionLocal() as db:
            for clerk_id in ids:
                try:
                    user = await user_repository.get_or_create(db, clerk_id)
                    if user.role != "admin":
                        user.role = "admin"
                        await db.flush()
                        _log.info("Admin promoted: %s", clerk_id)
                    await db.commit()
                except Exception as exc:
                    _log.warning("Admin bootstrap failed for %s: %s", clerk_id, exc)
                    await db.rollback()

    # Warm the daily news digest in the background. Building it costs an RSS
    # fetch plus an LLM call — around 15 seconds — and the cache is wiped by
    # every deploy because Render's disk is ephemeral. Without this, the first
    # visitor after each deploy pays that entire cost while staring at a
    # dashboard that looks broken. Fire-and-forget: never blocks startup, and
    # a failure just means the first reader warms it the old way.
    # Production only: the warm exists to protect the first real visitor after
    # a deploy. In tests and local dev there is no such visitor, and firing it
    # everywhere spent a live LLM call on every app start — including inside
    # CI, where it also broke a test that asserts the model is never called.
    # Drop expired rows from the durable cache. They are dead weight the
    # moment they expire, and nothing else removes them — without this the
    # table grows for the life of the deployment. Cheap (one indexed DELETE),
    # synchronous-but-fast, and a failure is logged rather than fatal.
    try:
        from backend.services import cache_store

        if cache_store.is_enabled():
            import logging as _sweep_logging

            removed = cache_store.sweep()
            _sweep_logging.getLogger("lumos.startup").info(
                "durable cache: swept %s expired rows", removed)
    except Exception:  # never let cache maintenance stop the app booting
        pass

    import asyncio as _asyncio
    import logging as _logging

    warm_task = None
    housing_task = None
    if settings.APP_ENV == "production":
        _warm_log = _logging.getLogger("lumos.startup")

        async def _warm_news_digest():
            from backend.services.news_service import get_daily_digest

            # Only the default market and language are warmed. The digest is
            # now cached per path x market x language, and warming all 27
            # combinations would mean 27 AI calls on every cold start to save
            # a handful of readers a few seconds.
            for path in ("hybrid", "stocks", "real_estate"):
                try:
                    await _asyncio.to_thread(get_daily_digest, path, "TR", "tr")
                    _warm_log.info("News digest warmed: %s", path)
                except Exception as exc:
                    _warm_log.warning("News digest warm failed (%s): %s", path, type(exc).__name__)

        async def _warm_housing_indices():
            """
            The US state table needs 51 FRED series. On a cold cache that is
            51 round-trips before the page can render anything, which on a
            free instance that also has to wake up reads as "Explore doesn't
            load for other markets". Free and keyless work is done here once,
            off the request path.
            """
            from backend.services import fred_service

            if not fred_service.is_configured():
                return
            try:
                states = await _asyncio.to_thread(fred_service.get_all_state_hpi)
                _warm_log.info("US housing index warmed: %d states", len(states))
            except Exception as exc:
                _warm_log.warning("US housing warm failed: %s", type(exc).__name__)

        warm_task = _asyncio.create_task(_warm_news_digest())
        housing_task = _asyncio.create_task(_warm_housing_indices())

    yield

    for task in (warm_task, housing_task):
        if task is not None:
            task.cancel()


app = FastAPI(
    title="Lumos — Smart Investment Assistant",
    description="AI-powered portfolio recommendation API",
    version="1.0.0",
    lifespan=lifespan,
)

# ── Rate Limiting ─────────────────────────────────────────────────────────────
app.state.limiter = limiter
# cast: slowapi's handler signature is narrower than the generic
# (Request, Exception) Starlette expects — cast sidesteps the type check
app.add_exception_handler(
    RateLimitExceeded,
    cast(Callable[[Request, Exception], Response], _rate_limit_exceeded_handler),
)

# ── Request ID (correlation) ──────────────────────────────────────────────────
app.add_middleware(RequestIDMiddleware)
app.add_middleware(LanguageMiddleware)

# ── CORS ──────────────────────────────────────────────────────────────────────
_dev_origins = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:5175",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
]
_allowed_origins = _dev_origins if settings.APP_ENV == "development" else [settings.FRONTEND_URL]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Global error handlers ─────────────────────────────────────────────────────
register_error_handlers(app)

# ── Routers ───────────────────────────────────────────────────────────────────
#
# Every router is mounted TWICE: once under /api/v1 and once at the bare path
# it has always been served from.
#
# The version prefix is the point — it is what lets a breaking change ship as
# /api/v2 while existing clients keep working. The unprefixed mount is the
# migration path, not a second API: the frontend and the backend deploy
# independently (Vercel and Render), so for a window after either one ships
# there is an old client talking to a new server. Removing the legacy mount in
# the same release that adds the prefix would make that window an outage.
#
# The legacy mount is deprecated. It can go once the deployed frontend has
# been on /api/v1 long enough that no cached bundle is still calling the old
# paths — a week is generous, since the service worker updates on next load.
API_V1 = "/api/v1"

_ROUTERS = [
    (health.router, "", ["Health"]),
    (chat.router, "/chat", ["Chat"]),
    (profile.router, "/profile", ["Profile"]),
    (recommend.router, "/recommend", ["Recommend"]),
    (users.router, "/users", ["Users"]),
    (holdings.router, "/holdings", ["Holdings"]),
    (backtest.router, "/backtest", ["Backtest"]),
    (news.router, "/news", ["News"]),
    (coach.router, "/coach", ["Coach"]),
    (planning.router, "/planning", ["Planning"]),
    (practice.router, "/practice", ["Practice"]),
    (admin.router, "/admin", ["Admin"]),
    (feedback.router, "/feedback", ["Feedback"]),
]

for _router, _prefix, _tags in _ROUTERS:
    app.include_router(_router, prefix=f"{API_V1}{_prefix}", tags=_tags)
    # Hidden from the schema so the docs describe ONE API rather than showing
    # every endpoint twice and leaving a reader to guess which to use.
    app.include_router(_router, prefix=_prefix, tags=_tags, include_in_schema=False)
