"""
Market data fallback tests — yfinance mocked, cache mocked.
"""
import pandas as pd
import pytest
from unittest.mock import patch

from backend.exceptions import MarketDataError
from backend.services.market_data import fetch_price_history

FAKE_SERIES = {"SPY": pd.Series([100.0, 101.0, 102.0])}


def test_fresh_cache_short_circuits():
    with patch("backend.services.market_data.cache_service.get", return_value=FAKE_SERIES), \
         patch("backend.services.market_data.yf.download") as m_dl:
        result = fetch_price_history(["SPY"])
    assert result == FAKE_SERIES
    m_dl.assert_not_called()


def test_download_failure_serves_stale_copy():
    def cache_get(key):
        return FAKE_SERIES if key.startswith("stale:") else None

    with patch("backend.services.market_data.cache_service.get", side_effect=cache_get), \
         patch("backend.services.market_data.yf.download", side_effect=ConnectionError("rate limited")):
        result = fetch_price_history(["SPY"])
    assert result == FAKE_SERIES


def test_download_failure_without_stale_raises():
    with patch("backend.services.market_data.cache_service.get", return_value=None), \
         patch("backend.services.market_data.yf.download", side_effect=ConnectionError("down")):
        with pytest.raises(MarketDataError):
            fetch_price_history(["SPY"])


def test_empty_download_without_stale_raises():
    with patch("backend.services.market_data.cache_service.get", return_value=None), \
         patch("backend.services.market_data.yf.download", return_value=pd.DataFrame()):
        with pytest.raises(MarketDataError):
            fetch_price_history(["SPY"])


def test_successful_download_writes_fresh_and_stale():
    df = pd.DataFrame({"Close": [100.0, 101.0]})
    written = {}

    def cache_set(key, value, ttl=None):
        written[key] = ttl

    with patch("backend.services.market_data.cache_service.get", return_value=None), \
         patch("backend.services.market_data.cache_service.set", side_effect=cache_set), \
         patch("backend.services.market_data.yf.download", return_value=df):
        fetch_price_history(["SPY"])

    keys = list(written)
    assert any(k.startswith("stale:") for k in keys)
    assert any(not k.startswith("stale:") for k in keys)


def test_a_partial_batch_is_never_remembered_as_last_known_good():
    """
    One missing symbol in a batch used to be cached — including into the
    never-expiring copy — so a real holding sat frozen at its purchase price
    while another symbol from the same request tracked live.
    """
    from unittest.mock import patch

    import pandas as pd

    from backend.services import cache as cache_service
    from backend.services import market_data

    idx = pd.bdate_range("2026-01-01", periods=5)
    only_spy = pd.DataFrame(
        {("Close", "SPY"): [1.0] * 5},
        index=idx,
    )
    only_spy.columns = pd.MultiIndex.from_tuples(only_spy.columns)

    writes = {}
    with patch.object(market_data.yf, "download", return_value=only_spy), \
         patch.object(cache_service, "get", return_value=None), \
         patch.object(cache_service, "set",
                      side_effect=lambda k, v, ttl=...: writes.setdefault(k, ttl)):
        result = market_data.fetch_price_history(["SPY", "VNQ"], period="1y")

    assert "SPY" in result and "VNQ" not in result
    # The incomplete answer is usable now, but must expire soon...
    assert any(k.startswith("price_history:") for k in writes)
    # ...and must NOT become the permanent fallback.
    assert not any(k.startswith("lkg:") for k in writes), writes
    assert not any(k.startswith("stale:") for k in writes), writes
