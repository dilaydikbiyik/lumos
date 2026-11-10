"""
Holdings in the reader's currency — after a market switch, and day by day.

Found by the second sweep: a TR reader with 150,000 TL of holdings who
switched to Germany saw 151,193 under euro formatting; and the value chart
priced every day at today's exchange rate, so a dollar fund bought for
100,000 TL started the chart at 103,369 and showed -2.1% beside a list
saying +1.2%.
"""
from datetime import date, timedelta
from types import SimpleNamespace
from unittest.mock import patch

import pandas as pd
import pytest


def _holding(i, asset_type, amount, currency="TRY", **kw):
    base = dict(id=i, asset_type=asset_type, purchase_amount=amount, currency=currency,
                ticker=None, quantity=None, purchase_date=None, manual_current_value=None)
    base.update(kw)
    return SimpleNamespace(**base)


def test_a_lira_holding_is_valued_in_euros_for_a_reader_now_in_germany():
    from backend.services import holdings_valuation as hv

    cash = _holding(1, "cash", 50_000)
    with patch.object(hv.fx_service, "rate", lambda b, q, on=None: 0.02 if (b, q) == ("TRY", "EUR") else None):
        out = hv.enrich_holdings([cash], "EUR", "DE")
    assert out[1]["value"] == pytest.approx(1_000.0)
    assert out[1]["converted_from"] == "TRY"


def test_an_unknown_rate_is_never_counted_at_parity():
    from backend.services import holdings_valuation as hv

    cash = _holding(1, "cash", 50_000)
    with patch.object(hv.fx_service, "rate", lambda b, q, on=None: None):
        out = hv.enrich_holdings([cash], "EUR", "DE")
    assert out[1]["value"] == 0.0 and out[1]["rate_unknown"] is True


def test_a_holding_in_the_readers_currency_is_untouched():
    from backend.services import holdings_valuation as hv

    cash = _holding(1, "cash", 50_000)
    out = hv.enrich_holdings([cash], "TRY", "TR")
    assert 1 not in out or out[1]["value"] == 50_000


def test_the_value_chart_uses_each_days_exchange_rate():
    from backend.services import portfolio_history as ph

    days = pd.bdate_range(date.today() - timedelta(days=20), date.today())
    spy = pd.Series(100.0, index=days)                       # flat in dollars
    usdtry = pd.Series([40.0] * (len(days) - 1) + [44.0], index=days)   # lira falls 10% on the last day
    h = _holding(1, "etf", 4_000.0, ticker="SPY", quantity=1.0, purchase_date=days[0].date())

    def fake_fetch(tickers, period="3mo", adjusted=True):
        return {t: (usdtry if t == "USDTRY=X" else spy) for t in tickers}

    with patch.object(ph, "fetch_price_history", side_effect=fake_fetch), \
         patch.object(ph.fx_service, "rate", lambda b, q, on=None: 44.0 if (b, q) == ("USD", "TRY") else 1.0), \
         patch.object(ph, "enrich_holdings", return_value={}):
        out = ph.portfolio_value_history([h], days=30, user_currency="TRY", market="TR")
    values = [p["value"] for p in out["series"]]
    assert values[0] == pytest.approx(4_000.0) and values[-1] == pytest.approx(4_400.0)
    assert out["change_pct"] == pytest.approx(10.0)
