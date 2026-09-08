"""
FRED adapter — the US house PRICE index.

The failure this guards against is subtle: a partial or empty response that
still looks like data. A state map missing half its states must not become
the cached answer for a day, and a "." placeholder must not become 0.0.
"""

from unittest.mock import patch

import pytest

from backend.services import cache as cache_service
from backend.services import fred_service


@pytest.fixture(autouse=True)
def _clear_cache():
    cache_service.clear()
    yield
    cache_service.clear()


class _Response:
    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code
        self.text = str(payload)

    def json(self):
        return self._payload

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


def _observations(rows):
    return {"observations": [{"date": d, "value": v} for d, v in rows]}


def test_series_id_follows_the_fhfa_naming():
    assert fred_service.series_id("ca") == "CASTHPI"
    assert fred_service.series_id("NY") == "NYSTHPI"
    assert fred_service.NATIONAL_SERIES == "USSTHPI"


def test_all_fifty_states_plus_dc_are_covered():
    assert len(fred_service.STATES) == 51
    assert fred_service.STATES["DC"] == "District of Columbia"
    assert "PR" not in fred_service.STATES  # not a state, no STHPI series


def test_unconfigured_key_reports_unavailable_rather_than_guessing():
    with patch.object(fred_service.settings, "FRED_API_KEY", ""):
        assert fred_service.is_configured() is False
        assert fred_service.get_national_hpi() is None
        assert fred_service.get_all_state_hpi() == {}


def test_missing_observations_are_dropped_not_zeroed():
    """FRED writes an unavailable value as "." — reading that as 0.0 would
    show a state whose houses became worthless."""
    payload = _observations([
        ("2024-01-01", "100.0"),
        ("2024-04-01", "."),
        ("2024-07-01", "110.0"),
    ])
    with patch.object(fred_service.settings, "FRED_API_KEY", "k"), \
         patch("httpx.get", return_value=_Response(payload)):
        series = fred_service.get_national_hpi()

    assert series == {"2024-01": 100.0, "2024-07": 110.0}
    assert 0.0 not in series.values()


def test_an_empty_response_is_not_cached_as_success():
    with patch.object(fred_service.settings, "FRED_API_KEY", "k"), \
         patch("httpx.get", return_value=_Response({"observations": []})):
        assert fred_service.get_national_hpi() is None


def test_last_known_good_survives_a_later_outage():
    payload = _observations([("2024-01-01", "100.0"), ("2024-04-01", "105.0")])
    with patch.object(fred_service.settings, "FRED_API_KEY", "k"):
        with patch("httpx.get", return_value=_Response(payload)):
            first = fred_service.get_national_hpi()
        # Drop the fresh tier only; the never-expiring last-known-good copy
        # is what the next call has to fall back to.
        cache_service.delete("fred:obs:USSTHPI:2000-01-01")

        def _boom(*a, **kw):
            raise RuntimeError("network down")

        with patch("httpx.get", _boom):
            second = fred_service.get_national_hpi()

    assert first == second


def test_a_bad_key_is_not_silently_swallowed(caplog):
    """A 400 means the key is wrong. That has to reach the logs as an error,
    not look like 'the data isn't there'."""
    with patch.object(fred_service.settings, "FRED_API_KEY", "wrong"), \
         patch("httpx.get", return_value=_Response({"error_message": "Bad API key"}, 400)):
        assert fred_service.get_national_hpi() is None

    assert any(r.levelname == "ERROR" and "rejected" in r.message
               for r in caplog.records)


def test_a_mostly_failed_state_map_is_not_cached():
    """A handful of states that happened to answer must not become the
    permanent nationwide answer for the next 24 hours."""
    good = _observations([("2024-01-01", "100.0"), ("2024-04-01", "105.0")])
    calls = {"n": 0}

    def _flaky(*args, **kwargs):
        calls["n"] += 1
        if calls["n"] <= 3:
            return _Response(good)
        raise RuntimeError("network down")

    with patch.object(fred_service.settings, "FRED_API_KEY", "k"), \
         patch("httpx.get", _flaky):
        partial = fred_service.get_all_state_hpi()

    assert 0 < len(partial) < len(fred_service.STATES)
    assert cache_service.get("fred:states:2000-01-01") is None


def test_a_complete_state_map_is_cached():
    good = _observations([("2024-01-01", "100.0"), ("2024-04-01", "105.0")])
    with patch.object(fred_service.settings, "FRED_API_KEY", "k"), \
         patch("httpx.get", return_value=_Response(good)):
        full = fred_service.get_all_state_hpi()

    assert len(full) == len(fred_service.STATES)
    assert full["CA"]["name"] == "California"
    assert cache_service.get("fred:states:2000-01-01") is not None


def test_unknown_state_code_returns_nothing():
    with patch.object(fred_service.settings, "FRED_API_KEY", "k"):
        assert fred_service.get_state_hpi("XX") is None


def test_state_map_is_fetched_in_parallel():
    """51 sequential round-trips on a cold cache is the difference between a
    page that loads and one that times out on a free-tier instance."""
    import threading
    import time

    concurrent = {"peak": 0, "now": 0}
    lock = threading.Lock()
    good = _observations([("2024-01-01", "100.0"), ("2024-04-01", "105.0")])

    def _slow(*args, **kwargs):
        with lock:
            concurrent["now"] += 1
            concurrent["peak"] = max(concurrent["peak"], concurrent["now"])
        try:
            time.sleep(0.02)  # long enough for overlap to be observable
            return _Response(good)
        finally:
            with lock:
                concurrent["now"] -= 1

    with patch.object(fred_service.settings, "FRED_API_KEY", "k"), \
         patch("httpx.get", _slow):
        fred_service.get_all_state_hpi()

    assert concurrent["peak"] > 1
