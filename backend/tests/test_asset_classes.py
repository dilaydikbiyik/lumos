"""
Every kind of investment, compared on one footing — and the footing tested.

The comparison is worth nothing unless every row is measured the same way.
Each test here pins one of the ways it can quietly stop being so: a dollar
return reported to a lira saver, a window that is not the deflator's
window, a weekend-trading asset annualised on the wrong calendar.
"""
import numpy as np
import pandas as pd
import pytest

from backend.markets import MARKET_PACKS, get_market_pack
from backend.markets.base import ASSET_CLASS_KEYS


def _bdays(start, end, values):
    idx = pd.bdate_range(start, end)
    return pd.Series(np.linspace(values[0], values[1], len(idx)), index=idx)


@pytest.fixture
def svc(monkeypatch):
    from backend.services import asset_classes
    from backend.services import cache as cache_service

    monkeypatch.setattr(cache_service, "get", lambda k: None)
    monkeypatch.setattr(cache_service, "set", lambda k, v, ttl=None: None)
    monkeypatch.setattr(asset_classes, "_real", lambda change, market: round(change / 2, 1))
    return asset_classes


def _feed(monkeypatch, svc, series_for):
    def history(tickers, period="1y", adjusted=True):
        return {t: series_for(t) for t in tickers}
    monkeypatch.setattr(svc, "fetch_price_history", history)


# ── the packs ───────────────────────────────────────────────────────────────

@pytest.mark.parametrize("market", sorted(MARKET_PACKS))
def test_every_market_declares_a_full_ladder(market):
    classes = get_market_pack(market).asset_classes
    keys = [c["key"] for c in classes]
    assert set(keys) <= set(ASSET_CLASS_KEYS), set(keys) - set(ASSET_CLASS_KEYS)
    assert "cash" in keys, "doing nothing is the comparison most savers make"
    assert "crypto" in keys and "gold" in keys
    assert any(k.startswith("equity") for k in keys)
    assert any(k.endswith("bond") or k in ("bonds", "tbill", "money_market") for k in keys)
    assert keys == sorted(keys, key=ASSET_CLASS_KEYS.index), "rows must follow the teaching order"


# ── one footing ─────────────────────────────────────────────────────────────

def test_a_dollar_asset_is_measured_in_the_reader_s_currency(monkeypatch, svc):
    """
    A Turkish reader holding a dollar fund earned its return AND the lira's
    fall. Flat in dollars while the dollar doubles in lira must read +100%.
    """
    end = pd.Timestamp.today().normalize()
    start = end - pd.DateOffset(years=6)

    def series_for(t):
        if t == "USDTRY=X":
            return _bdays(start, end, (10, 20))
        return _bdays(start, end, (100, 100))      # every asset flat in its own currency

    _feed(monkeypatch, svc, series_for)
    rows = {r["key"]: r for r in svc.compare("TR")["classes"]}
    tbill = rows["tbill"]                           # BIL, a dollar fund
    assert tbill["change_pct"] > 50, tbill          # the lira's fall is in it
    home = rows["equity_home"]                      # BIST, already in lira
    assert abs(home["change_pct"]) < 0.5, home


def test_a_foreign_asset_without_an_fx_series_is_left_out_not_shown_as_local(monkeypatch, svc):
    end = pd.Timestamp.today().normalize()
    start = end - pd.DateOffset(years=6)

    def series_for(t):
        return None if t.endswith("=X") else _bdays(start, end, (100, 150))

    _feed(monkeypatch, svc, series_for)
    keys = {r["key"] for r in svc.compare("TR")["classes"]}
    assert "tbill" not in keys and "crypto" not in keys
    assert "equity_home" in keys and "cash" in keys


def test_the_window_is_exactly_five_years_by_date(monkeypatch, svc):
    """
    The first version cut the last 252×5 rows of a business-day calendar —
    4.8 years — while inflation was taken over five. Here the price is flat
    until exactly five years ago and doubles after; a 4.8-year window would
    miss the start and misreport the change.
    """
    end = pd.Timestamp.today().normalize()
    five = end - pd.DateOffset(years=5)
    idx = pd.bdate_range(end - pd.DateOffset(years=6), end)
    s = pd.Series(np.where(idx < five, 100.0, 100.0), index=idx)
    s[idx >= five] = np.linspace(100, 200, int((idx >= five).sum()))

    _feed(monkeypatch, svc, lambda t: 1.0 + 0 * s if t.endswith("=X") else s)
    row = next(r for r in svc.compare("US")["classes"] if r["key"] == "equity_home")
    assert abs(row["change_pct"] - 100.0) < 1.0, row


def test_a_weekend_trading_asset_is_put_on_the_same_calendar(monkeypatch, svc):
    """
    Bitcoin trades every day. Annualising its calendar-day returns with a
    business-day factor understates volatility; aligned first, a series with
    identical weekday prices must give identical volatility whether or not
    it also had weekend rows.
    """
    end = pd.Timestamp.today().normalize()
    days = pd.date_range(end - pd.DateOffset(years=6), end, freq="D")
    rng = np.random.default_rng(4)
    every_day = pd.Series(100 * np.cumprod(1 + rng.normal(0, 0.03, len(days))), index=days)
    weekdays_only = every_day[every_day.index.dayofweek < 5]

    def run(series):
        _feed(monkeypatch, svc, lambda t: series if t == "BTC-USD" else _bdays(days[0], end, (100, 110)))
        return next(r for r in svc.compare("US")["classes"] if r["key"] == "crypto")

    assert run(every_day)["volatility_pct"] == run(weekdays_only)["volatility_pct"]


def test_cash_is_a_row_and_inflation_is_its_whole_story(monkeypatch, svc):
    end = pd.Timestamp.today().normalize()
    _feed(monkeypatch, svc, lambda t: _bdays(end - pd.DateOffset(years=6), end, (100, 120)))
    cash = next(r for r in svc.compare("DE")["classes"] if r["key"] == "cash")
    assert cash["change_pct"] == 0.0 and cash["worst_drop_pct"] == 0.0
    assert cash["real_change_pct"] == 0.0     # the fake deflator halves; real code returns −inflation


def test_the_answer_does_not_depend_on_who_asks(client, monkeypatch, svc):
    from backend.main import app
    from backend.middleware.verify_clerk import get_current_user

    end = pd.Timestamp.today().normalize()
    _feed(monkeypatch, svc, lambda t: _bdays(end - pd.DateOffset(years=6), end, (100, 140)))
    answers = []
    for uid, tol in (("calm", "low"), ("bold", "high")):
        app.dependency_overrides[get_current_user] = lambda uid=uid: uid
        client.post("/profile", json={"budget": 100_000, "time_horizon": "long",
                                      "loss_tolerance": tol, "goal": "growth",
                                      "experience": "beginner"})
        answers.append(client.get("/stocks/asset-classes").json())
    assert answers[0] == answers[1]


def test_every_asset_class_has_its_copy_in_every_language():
    """A class the backend can return must have a name, a description and a
    lesson on the page, in all three languages — otherwise the reader sees a
    raw key where the teaching should be."""
    import json
    from pathlib import Path
    from backend.markets.base import ASSET_CLASS_KEYS

    locales = Path(__file__).resolve().parents[2] / "frontend" / "src" / "locales"
    for lang in ("tr", "en", "de"):
        copy = json.loads((locales / f"{lang}.json").read_text())["assetClasses"]["k"]
        assert set(copy) == set(ASSET_CLASS_KEYS), lang
        for key in ASSET_CLASS_KEYS:
            assert all(copy[key].get(f) for f in ("name", "what", "lesson")), (lang, key)
