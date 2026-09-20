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


# ── Upstream cooldown ────────────────────────────────────────────────────────
# When a source is down, every request re-attempts it. With a 25-second
# timeout on a single-worker free instance, a provider outage stops being
# "some stale numbers" and becomes a hung app, because requests pile up
# waiting on a socket that is never going to answer.
#
# `ticker_lookup` already solved this for itself by caching a miss for 60
# seconds. The official-statistics adapters did not, which is the same
# inconsistency in error handling that lets one bad afternoon look like an
# outage. One helper, applied the same way in each.
#
# The cooldown suppresses the NETWORK CALL only. Fresh and last-known-good
# data are still served throughout — a cooldown must never turn a degraded
# answer into no answer.
COOLDOWN_SECONDS = 120


class UpstreamInCooldown(RuntimeError):
    """
    Raised INSIDE an adapter's try block when its source is cooling down.

    Raising rather than returning early is deliberate: it routes through the
    adapter's existing `except`, so the whole fallback chain it already has —
    last-known-good, then a bundled static snapshot — runs exactly as it does
    during a real outage. An early return skipped the bundled snapshot and
    turned a degraded answer into no answer, which is the opposite of what a
    cooldown is for.
    """


def _cooldown_key(name: str) -> str:
    return f"cooldown:{name}"


def in_cooldown(name: str) -> bool:
    """Whether this upstream failed recently enough to leave alone."""
    return _cache.get(_cooldown_key(name)) is not None


def start_cooldown(name: str, seconds: int = COOLDOWN_SECONDS) -> None:
    """Record that an upstream just failed. Local-only: an outage is per-host."""
    _cache.set(_cooldown_key(name), True, expire=seconds)


def clear_cooldown(name: str) -> None:
    _cache.delete(_cooldown_key(name))
