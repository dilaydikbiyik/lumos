"""
Live holding valuation tests — "my stock doubled, will I see it?"

yfinance and EVDS mocked; verifies the priority chain
(manual > live/index > purchase) and the fail-open behaviour.
"""
from datetime import date
from types import SimpleNamespace
from unittest.mock import patch

import pandas as pd

from backend.services.holdings_valuation import current_value, enrich_holdings


def _h(id, asset_type, ticker=None, amount=100000, qty=None, pdate=None, manual=None):
    return SimpleNamespace(
        id=id, asset_type=asset_type, ticker=ticker, purchase_amount=amount,
        quantity=qty, purchase_date=pdate, manual_current_value=manual,
    )


def _series(values, start="2025-01-01"):
    return pd.Series(values, index=pd.bdate_range(start, periods=len(values)))


def test_stock_with_quantity_revalues_live():
    # 5 units, current price 240 → live value 1200; purchase 1000 → +20%
    holding = _h(1, "stock", ticker="SPY", amount=1000, qty=5)
    with patch("backend.services.holdings_valuation.fetch_price_history",
               return_value={"SPY": _series([200.0, 220.0, 240.0])}):
        e = enrich_holdings([holding])
    assert e[1]["value"] == 1200
    assert e[1]["source"] == "live"
    assert e[1]["change_pct"] == 20.0


def test_stock_with_purchase_date_infers_units():
    # Purchase-day price 100 → 1000 TL = 10 units; today 150 → 1500 (+50%)
    holding = _h(2, "etf", ticker="GLD", amount=1000, pdate=date(2025, 1, 1))
    with patch("backend.services.holdings_valuation.fetch_price_history",
               return_value={"GLD": _series([100.0, 120.0, 150.0])}):
        e = enrich_holdings([holding])
    assert e[2]["value"] == 1500
    assert e[2]["change_pct"] == 50.0


def test_stock_without_qty_or_date_stays_on_purchase_basis():
    holding = _h(3, "stock", ticker="SPY", amount=1000)
    with patch("backend.services.holdings_valuation.fetch_price_history",
               return_value={"SPY": _series([100.0, 150.0])}):
        e = enrich_holdings([holding])
    assert 3 not in e
    assert current_value(holding, e) == 1000


def test_real_estate_revalues_by_national_index():
    # Index 100 in the purchase month, 150 today → 600k home ≈ 900k estimate (+50%)
    holding = _h(4, "real_estate", amount=600000, pdate=date(2025, 1, 15))
    with patch("backend.services.holdings_valuation.evds_service.fetch_series",
               return_value={"2025-01": 100.0, "2025-06": 130.0, "2026-01": 150.0}):
        e = enrich_holdings([holding])
    assert e[4]["value"] == 900000
    assert e[4]["source"] == "index"
    assert e[4]["change_pct"] == 50.0


def test_manual_valuation_overrides_everything():
    holding = _h(5, "stock", ticker="SPY", amount=1000, qty=5, manual=7777)
    with patch("backend.services.holdings_valuation.fetch_price_history",
               return_value={"SPY": _series([200.0, 240.0])}):
        e = enrich_holdings([holding])
    assert e[5]["value"] == 7777
    assert e[5]["source"] == "manual"


def test_fail_open_when_sources_down():
    holdings = [
        _h(6, "stock", ticker="SPY", amount=1000, qty=5),
        _h(7, "land", amount=500000, pdate=date(2025, 1, 1)),
    ]
    with patch("backend.services.holdings_valuation.fetch_price_history",
               side_effect=ConnectionError), \
         patch("backend.services.holdings_valuation.evds_service.fetch_series",
               side_effect=ConnectionError):
        e = enrich_holdings(holdings)
    assert e == {}
    assert current_value(holdings[0], e) == 1000  # falls back to purchase basis


def test_list_endpoint_carries_valuation_fields(client):
    res = client.post("/holdings", json={
        "asset_type": "stock", "name": "SPY ETF", "ticker": "SPY",
        "purchase_amount": 1000, "quantity": 5,
    })
    assert res.status_code == 201
    listed = client.get("/holdings").json()
    mine = next(h for h in listed if h["name"] == "SPY ETF")
    # conftest kills the network → purchase basis; fields still present
    assert mine["current_value"] == 1000
    assert mine["value_source"] == "purchase"
