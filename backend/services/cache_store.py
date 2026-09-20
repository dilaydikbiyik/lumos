"""
Durable cache tier — the half of the cache that survives a deploy.

diskcache is fast and local, and on Render it is also *ephemeral*: the
container's filesystem is rebuilt on every deploy and on every restart of a
sleeping free instance. That is survivable for the 24-hour tier, which simply
refetches. It is not survivable for the last-known-good tier, which is written
with `ttl=None` precisely so that a source outage has something to fall back
on — and which was being thrown away several times a week. The one moment the
fallback exists for is a provider being down, and a deploy happening to land
near that moment is not unlikely; it is the normal case, because a deploy is
often the response to something being wrong.

So: values are mirrored into a small Postgres table. Reads try the local tier
first and fall back here, warming the local tier on the way past.

Deliberately SYNCHRONOUS, with its own engine. The cache is called from
`_observations`-style functions that are themselves sync and run inside a
thread pool; making it async would mean rewriting every data adapter and
every thread-pool fan-out to no benefit.

Entirely optional. Without Postgres — local SQLite, tests, a fresh clone —
every function here is a no-op and the cache behaves exactly as it always
did. It never raises into a caller: a cache that can fail the request it was
meant to speed up is worse than no cache.
"""

import json
import logging
import re
import sys
import threading
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from backend.config import settings

logger = logging.getLogger("lumos.cache_store")

_TABLE = "cache_entries"
# A value big enough to be a problem is a bug upstream, not something to
# quietly persist: the whole point is a small, fast lookup table.
_MAX_VALUE_BYTES = 1_000_000

_engine = None
_ready = False
_lock = threading.Lock()
_disabled = False


def _sync_url() -> Optional[str]:
    """
    The same database, through a synchronous driver.

    `normalize_db_url` targets asyncpg; psycopg needs the libpq spelling back,
    including the `sslmode` that asyncpg wanted renamed to `ssl`.
    """
    url = settings.DATABASE_URL or ""
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://"):]
    if not url.startswith(("postgresql://", "postgresql+")):
        return None          # SQLite and friends: no durable tier, by design
    url = re.sub(r"^postgresql\+\w+://", "postgresql://", url)
    url = url.replace("postgresql://", "postgresql+psycopg://", 1)
    # asyncpg's spelling, if it is in the env, back to libpq's.
    url = re.sub(r"([?&])ssl=", r"\1sslmode=", url)
    return url


def _get_engine():
    """The engine, created once, or None when there is no durable tier."""
    global _engine, _ready, _disabled
    if _ready or _disabled:
        return _engine

    with _lock:
        if _ready or _disabled:
            return _engine
        # NEVER under pytest. A developer's .env normally holds the real
        # DATABASE_URL, so without this the suite connects to the production
        # database and writes cache rows into it — which is exactly what
        # happened the first time this module ran: 125 rows, including test
        # fixtures that then leaked back into a later assertion. Tests get the
        # local tier only, which is what they were always written against.
        if "pytest" in sys.modules:
            _disabled = True
            return None

        url = _sync_url()
        if not url:
            _disabled = True
            return None
        try:
            from sqlalchemy import create_engine, text

            # Small pool: this is a side channel, not the request path, and it
            # must never be the reason the app runs out of connections.
            engine = create_engine(url, pool_size=2, max_overflow=2,
                                   pool_pre_ping=True, pool_recycle=300)
            with engine.begin() as conn:
                conn.execute(text(f"""
                    CREATE TABLE IF NOT EXISTS {_TABLE} (
                        key         TEXT PRIMARY KEY,
                        value       JSONB NOT NULL,
                        expires_at  TIMESTAMPTZ,
                        updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
                    )
                """))
                # Sweeping expired rows needs this; the table stays small.
                conn.execute(text(
                    f"CREATE INDEX IF NOT EXISTS {_TABLE}_expires_idx "
                    f"ON {_TABLE} (expires_at)"))
            _engine = engine
            _ready = True
            logger.info("durable cache tier ready")
        except Exception as exc:
            # A missing driver or an unreachable database must not stop the
            # app booting. Log once and stay out of the way.
            logger.warning("durable cache tier unavailable (%s) — "
                           "local cache only", type(exc).__name__)
            _disabled = True
        return _engine


def is_enabled() -> bool:
    return _get_engine() is not None


def get(key: str) -> Any:
    """The stored value, or None when absent, expired or unreadable."""
    engine = _get_engine()
    if engine is None:
        return None
    try:
        from sqlalchemy import text

        with engine.connect() as conn:
            row = conn.execute(
                text(f"SELECT value, expires_at FROM {_TABLE} WHERE key = :k"),
                {"k": key},
            ).first()
        if not row:
            return None
        value, expires_at = row
        if expires_at is not None and expires_at <= datetime.now(timezone.utc):
            return None
        # Stored as {"v": ...} so that a cached scalar, list or None round-trips
        # through a JSONB column that would otherwise flatten them.
        return value.get("v") if isinstance(value, dict) and "v" in value else value
    except Exception as exc:
        logger.warning("durable cache read failed (%s)", type(exc).__name__)
        return None


def set(key: str, value: Any, ttl: Optional[int]) -> bool:
    """Mirror a value. True when it was stored. ttl=None means never expires."""
    engine = _get_engine()
    if engine is None:
        return False
    try:
        payload = json.dumps({"v": value})
    except (TypeError, ValueError):
        # Not everything cached locally is JSON — pickled objects stay local
        # rather than failing the write that was only ever a nice-to-have.
        return False
    if len(payload) > _MAX_VALUE_BYTES:
        logger.debug("durable cache skip: %s is %d bytes", key, len(payload))
        return False

    expires_at = (datetime.now(timezone.utc) + timedelta(seconds=ttl)) if ttl else None
    try:
        from sqlalchemy import text

        with engine.begin() as conn:
            conn.execute(text(f"""
                INSERT INTO {_TABLE} (key, value, expires_at, updated_at)
                VALUES (:k, CAST(:v AS JSONB), :e, NOW())
                ON CONFLICT (key) DO UPDATE
                   SET value = EXCLUDED.value,
                       expires_at = EXCLUDED.expires_at,
                       updated_at = NOW()
            """), {"k": key, "v": payload, "e": expires_at})
        return True
    except Exception as exc:
        logger.warning("durable cache write failed (%s)", type(exc).__name__)
        return False


def delete(key: str) -> None:
    engine = _get_engine()
    if engine is None:
        return
    try:
        from sqlalchemy import text

        with engine.begin() as conn:
            conn.execute(text(f"DELETE FROM {_TABLE} WHERE key = :k"), {"k": key})
    except Exception as exc:
        logger.warning("durable cache delete failed (%s)", type(exc).__name__)


def sweep() -> int:
    """Drop expired rows. Returns how many went; -1 when the tier is off."""
    engine = _get_engine()
    if engine is None:
        return -1
    try:
        from sqlalchemy import text

        with engine.begin() as conn:
            result = conn.execute(text(
                f"DELETE FROM {_TABLE} WHERE expires_at IS NOT NULL "
                f"AND expires_at <= NOW()"))
        return result.rowcount or 0
    except Exception as exc:
        logger.warning("durable cache sweep failed (%s)", type(exc).__name__)
        return -1


def _reset_for_tests() -> None:
    global _engine, _ready, _disabled
    with _lock:
        _engine, _ready, _disabled = None, False, False
