"""
The two-tier cache.

Tier 1 is diskcache on an ephemeral container disk; tier 2 is a Postgres table
that outlives a deploy. The tier that matters is last-known-good (`ttl=None`),
which exists so a provider outage has something to fall back on and which was
previously discarded on every deploy.

These tests run with the durable tier stubbed, not connected: pointing a test
suite at a real database is how 125 rows of fixture data ended up in
production the first time this module ran.
"""
import sys
from unittest.mock import patch

import pytest

from backend.services import cache as cache_service
from backend.services import cache_store


@pytest.fixture(autouse=True)
def _clean():
    cache_service.clear()
    yield
    cache_service.clear()


def test_the_durable_tier_refuses_to_wake_up_under_pytest():
    """
    The guard that matters most, because a developer's .env holds the real
    DATABASE_URL. Without it the suite writes cache rows into production —
    which is not hypothetical; it is what happened.
    """
    cache_store._reset_for_tests()
    assert "pytest" in sys.modules
    assert cache_store.is_enabled() is False
    assert cache_store.get("anything") is None
    assert cache_store.set("anything", {"a": 1}, ttl=None) is False


def test_a_value_survives_the_local_tier_being_wiped():
    """
    A deploy wipes the container disk. The whole point of tier 2 is that the
    answer is still there afterwards.
    """
    durable = {}

    with patch.object(cache_store, "set",
                      side_effect=lambda k, v, ttl: durable.__setitem__(k, v) or True), \
         patch.object(cache_store, "get", side_effect=durable.get):
        cache_service.set("lkg:tcmb:cpi", {"2026-08": 1234.5}, ttl=None)
        assert cache_service.get("lkg:tcmb:cpi") == {"2026-08": 1234.5}

        # The deploy.
        cache_service.clear()

        assert cache_service.get("lkg:tcmb:cpi") == {"2026-08": 1234.5}


def test_a_durable_hit_warms_the_local_tier():
    """The second read should be local again, not another database round-trip."""
    durable = {"fred:obs:USSTHPI": {"2026-01": 100.0}}
    calls = []

    def _get(key):
        calls.append(key)
        return durable.get(key)

    with patch.object(cache_store, "get", side_effect=_get), \
         patch.object(cache_store, "set", return_value=True):
        assert cache_service.get("fred:obs:USSTHPI") == {"2026-01": 100.0}
        assert cache_service.get("fred:obs:USSTHPI") == {"2026-01": 100.0}

    assert len(calls) == 1, f"durable tier was consulted {len(calls)} times"


def test_a_cached_none_is_not_mistaken_for_a_miss():
    """
    Some callers cache an empty answer deliberately — chat_context writes "".
    "Found, and it was falsy" and "not found" have to stay distinguishable, or
    a negative result gets refetched forever.
    """
    with patch.object(cache_store, "get", return_value=None), \
         patch.object(cache_store, "set", return_value=True):
        cache_service.set("empty", "", ttl=600)
        assert cache_service.get("empty") == ""


def test_the_durable_tier_never_raises_into_a_caller():
    """
    A cache that can fail the request it exists to speed up is worse than no
    cache. A database that is down must produce a miss, not an exception —
    tested against the real error handling, with the engine itself broken.
    """
    class _BrokenEngine:
        def connect(self):
            raise RuntimeError("connection refused")

        def begin(self):
            raise RuntimeError("connection refused")

    with patch.object(cache_store, "_get_engine", return_value=_BrokenEngine()):
        assert cache_store.get("k") is None
        assert cache_store.set("k", {"a": 1}, ttl=60) is False
        cache_store.delete("k")            # must not raise either
        assert cache_store.sweep() == -1

    # And through the facade, the local tier keeps working regardless.
    with patch.object(cache_store, "_get_engine", return_value=_BrokenEngine()):
        cache_service.set("k", "v", ttl=60)
        assert cache_service.get("k") == "v"


def test_clear_is_local_only():
    """
    `clear()` is container-local maintenance. Wiping the shared last-known-good
    data for every instance is not what any caller of it means.
    """
    with patch.object(cache_store, "delete") as durable_delete:
        cache_service.clear()
        durable_delete.assert_not_called()


def test_a_sync_url_is_derived_for_postgres_and_refused_for_sqlite():
    """
    The durable tier needs libpq's spelling back: `normalize_db_url` rewrites
    Neon's string for asyncpg, including renaming sslmode to ssl.
    """
    with patch.object(cache_store.settings, "DATABASE_URL",
                      "postgresql+asyncpg://u:p@host/db?ssl=require"):
        url = cache_store._sync_url()
    assert url.startswith("postgresql+psycopg://")
    assert "sslmode=require" in url
    assert "asyncpg" not in url

    # Anything that isn't Postgres simply has no durable tier.
    for other in ("sqlite+aiosqlite:///./lumos.db", "", None):
        with patch.object(cache_store.settings, "DATABASE_URL", other):
            assert cache_store._sync_url() is None
