"""
RAG chat-context tests — market data and inflation mocked.
"""
import pandas as pd
from unittest.mock import patch

from backend.services.chat_context import build_market_context

_FAKE = {
    "XU100.IS": pd.Series([100.0, 102.0]),
    "SPY": pd.Series([500.0, 495.0]),
    "GLD": pd.Series([200.0, 200.0]),
}


def _no_cache():
    return patch("backend.services.chat_context.cache_service.get", return_value=None), \
           patch("backend.services.chat_context.cache_service.set")


def test_context_contains_prices_and_changes():
    g, s = _no_cache()
    with g, s, \
         patch("backend.services.market_data.fetch_price_history", return_value=_FAKE), \
         patch("backend.services.inflation_service.monthly_cash_erosion",
               return_value={"monthly_inflation_pct": 2.5, "erosion_amount": 2.5}):
        ctx = build_market_context()
    assert "BIST 100" in ctx and "+2.0%" in ctx
    assert "S&P 500" in ctx and "-1.0%" in ctx
    assert "%2.5" in ctx
    assert "asla tahmine çevirme" in ctx


def test_context_fails_open_when_sources_down():
    g, s = _no_cache()
    with g, s, \
         patch("backend.services.market_data.fetch_price_history", side_effect=ConnectionError), \
         patch("backend.services.inflation_service.monthly_cash_erosion", side_effect=RuntimeError):
        ctx = build_market_context()
    assert ctx == ""


def test_chat_still_works_when_context_empty(client, mock_ai):
    with patch("backend.services.ai_service.build_market_context", create=True), \
         patch("backend.services.chat_context.build_market_context", return_value=""):
        res = client.post("/chat", json={"messages": [{"role": "user", "content": "selam"}]})
    assert res.status_code == 200
