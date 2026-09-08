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


def _h(id, asset_type, ticker=None, amount=100000, qty=None, pdate=None,
       manual=None, currency="TRY"):
    return SimpleNamespace(
        id=id, asset_type=asset_type, ticker=ticker, purchase_amount=amount,
        quantity=qty, purchase_date=pdate, manual_current_value=manual,
        currency=currency,
    )


def _series(values, start="2025-01-01"):
    return pd.Series(values, index=pd.bdate_range(start, periods=len(values)))


def test_stock_with_quantity_revalues_live():
    # 5 units, current price 240 → live value 1200; purchase 1000 → +20%.
    # A Turkish-quoted symbol keeps the arithmetic free of any FX step.
    holding = _h(1, "stock", ticker="THYAO.IS", amount=1000, qty=5)
    with patch("backend.services.holdings_valuation.fetch_price_history",
               return_value={"THYAO.IS": _series([200.0, 220.0, 240.0])}):
        e = enrich_holdings([holding], "TRY")
    assert e[1]["value"] == 1200
    assert e[1]["source"] == "live"
    assert e[1]["change_pct"] == 20.0


def test_stock_with_purchase_date_infers_units():
    # Purchase-day price 100 → 1000 TL = 10 units; today 150 → 1500 (+50%)
    holding = _h(2, "etf", ticker="XU100.IS", amount=1000, pdate=date(2025, 1, 1))
    with patch("backend.services.holdings_valuation.fetch_price_history",
               return_value={"XU100.IS": _series([100.0, 120.0, 150.0])}):
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


# ── Currency ─────────────────────────────────────────────────────────────────
#
# The app had no conversion step at all: it multiplied units by a dollar price
# and compared the result to a lira amount. A Turkish user holding two shares
# of SPY, roughly break-even, was told they had lost 97.6% of their money.

def test_foreign_asset_is_converted_into_the_users_currency():
    holding = _h(1, "stock", ticker="SPY", amount=64000, qty=2, currency="TRY")
    with patch("backend.services.holdings_valuation.fetch_price_history",
               return_value={"SPY": _series([700.0, 750.0, 770.0])}), \
         patch("backend.services.fx_service.rate", return_value=48.0):
        e = enrich_holdings([holding], "TRY")

    # 2 shares × $770 × 48 = 73,920 TRY, not $1,540 compared against 64,000 TRY
    assert e[1]["value"] == 73920.0
    assert e[1]["currency"] == "TRY"
    assert e[1]["change_pct"] == 15.5


def test_units_inferred_from_a_past_purchase_use_that_days_rate():
    """
    Using today's rate to back out units would fold every FX move since the
    purchase into the unit count, cancelling the currency gain the user
    actually made.
    """
    def rate_on(base, quote, on=None):
        return 30.0 if on else 48.0        # lira weakened since the purchase

    holding = _h(2, "stock", ticker="SPY", amount=30000, pdate=date(2025, 1, 1),
                 currency="TRY")
    with patch("backend.services.holdings_valuation.fetch_price_history",
               return_value={"SPY": _series([100.0, 100.0, 100.0])}), \
         patch("backend.services.fx_service.rate", side_effect=rate_on):
        e = enrich_holdings([holding], "TRY")

    # 30,000 TRY ÷ (price 100 × rate 30) = 10 units; today 10 × 100 × 48
    assert e[2]["value"] == 48000.0
    # The dollar price never moved, so the whole +60% is the currency
    assert e[2]["change_pct"] == 60.0


def test_a_local_asset_is_untouched_by_conversion():
    holding = _h(3, "stock", ticker="THYAO.IS", amount=25000, qty=100, currency="TRY")
    with patch("backend.services.holdings_valuation.fetch_price_history",
               return_value={"THYAO.IS": _series([250.0, 280.0, 300.0])}):
        e = enrich_holdings([holding], "TRY")
    assert e[3]["value"] == 30000.0


def test_an_unknown_rate_means_no_valuation_not_an_assumed_one():
    """Assuming parity is how a 48x error gets presented as a fact."""
    holding = _h(4, "stock", ticker="SPY", amount=64000, qty=2, currency="TRY")
    with patch("backend.services.holdings_valuation.fetch_price_history",
               return_value={"SPY": _series([700.0, 770.0])}), \
         patch("backend.services.fx_service.rate", return_value=None):
        e = enrich_holdings([holding], "TRY")
    assert 4 not in e          # falls back to purchase basis, shows no change


def test_ticker_currency_is_read_from_the_listing_venue():
    from backend.services.holdings_valuation import ticker_currency

    assert ticker_currency("THYAO.IS") == "TRY"
    assert ticker_currency("EUNL.DE") == "EUR"
    assert ticker_currency("XU100.IS") == "TRY"


def test_currency_of_a_recommended_asset_needs_no_network():
    """
    ticker_currency ran a rate-limited lookup inside the valuation loop. When
    it stalled in production, a holding stopped being valued and silently
    reverted to showing its purchase price as if nothing had moved.
    """
    from unittest.mock import patch

    from backend.services.holdings_valuation import ticker_currency

    def explode(_):
        raise AssertionError("no lookup should be needed for a known symbol")

    with patch("backend.services.ticker_lookup.lookup", side_effect=explode):
        for symbol in ("SPY", "VNQ", "BND", "BIL", "GLD", "QQQ", "SCHH"):
            assert ticker_currency(symbol) == "USD", symbol
        assert ticker_currency("EUNL.DE") == "EUR"
        assert ticker_currency("XU100.IS") == "TRY"


def test_fx_history_is_fetched_once_for_many_dates():
    """One network call per purchase date is how a portfolio stops valuing."""
    from datetime import date
    from unittest.mock import patch

    from backend.services import fx_service

    series = {"2026-06-01": 40.0, "2026-06-22": 46.0, "2026-09-04": 48.0}
    with patch.object(fx_service, "_series", return_value=series) as m:
        assert fx_service.rate("USD", "TRY") == 48.0
        assert fx_service.rate("USD", "TRY", date(2026, 6, 22)) == 46.0
        # A non-trading day snaps back to the last known close
        assert fx_service.rate("USD", "TRY", date(2026, 6, 23)) == 46.0
        # Older than the series: the earliest rate beats refusing to value
        assert fx_service.rate("USD", "TRY", date(2000, 1, 1)) == 40.0
    assert m.call_count == 4  # one lookup each, all served from one cached series
