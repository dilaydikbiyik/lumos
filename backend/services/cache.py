"""
Two-tier cache for market data.

Tier 1 — diskcache, on the container's local disk: fast, and wiped on every
deploy, because Render's filesystem is ephemeral.

Tier 2 — a small Postgres table (`cache_store`), which is not. Optional: with
no Postgres configured, tier 2 is a no-op and this module behaves exactly as
the single-tier version always did.

The tier that matters is the LAST-KNOWN-GOOD one. Callers write it with
`ttl=None` so it never expires, on purpose: when TCMB or Eurostat is down, it
is the only thing standing between a user and an empty screen. Keeping that on
ephemeral disk meant it was discarded several times a week, and usually right
when it was most needed — a deploy is frequently the response to something
already being wrong.

Reads check tier 1 first and fall back to tier 2, warming tier 1 on the way
past so the second read is local again.
"""

import logging
from pathlib import Path
from typing import Optional

import diskcache

from backend.services import cache_store

logger = logging.getLogger("lumos.cache")

_CACHE_DIR = Path(__file__).parent.parent / ".cache"
_cache = diskcache.Cache(str(_CACHE_DIR), size_limit=200 * 1024 * 1024)  # 200 MB

TTL_SECONDS = 60 * 60 * 24  # 24 hours

# A sentinel, because None is a legitimate cached value and "not found" and
# "found, and it was None" must stay distinguishable.
_MISS = object()


def get(key: str):
    local = _cache.get(key, default=_MISS)
    if local is not _MISS:
        return local

    durable = cache_store.get(key)
    if durable is not None:
        # Warm the local tier so the next read costs nothing. The TTL is not
        # recoverable from here, so it gets the default — the durable row
        # keeps the authoritative expiry either way.
        try:
            _cache.set(key, durable, expire=TTL_SECONDS)
        except Exception:  # a full or read-only disk must not fail the read
            pass
        return durable
    return None


def set(key: str, value, ttl: Optional[int] = TTL_SECONDS):
    _cache.set(key, value, expire=ttl)
    # Mirrored best-effort: the durable tier never fails a caller, and a value
    # that will not serialise simply stays local.
    cache_store.set(key, value, ttl)


def delete(key: str):
    _cache.delete(key)
    cache_store.delete(key)


def clear():
    _cache.clear()
    # Deliberately NOT clearing the durable tier: `clear()` is a local
    # maintenance action, and wiping every instance's shared last-known-good
    # data is not what any caller of it means.
