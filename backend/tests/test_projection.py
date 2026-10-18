"""
Future scenario band tests — market data and EVDS mocked.
"""
import numpy as np
import pandas as pd
import pytest
from unittest.mock import patch

from backend.services.projection import project_asset, project_portfolio

# THIRTY years of daily data, steady ~12%/yr growth with noise.
#
# It was ten, which is exactly the thin case the independent-period guard
# now refuses: a five-year window over ten years of history is TWO
# non-overlapping stretches, however many overlapping ones are counted. The
# fixture was encoding the behaviour the guard was added to stop, so a test
# asking for a five-year band had to be given a record that can carry one.
_N = 252 * 30
_rng = np.random.default_rng(7)
_GROWTH = pd.Series(
    100 * np.cumprod(1 + _rng.normal(0.00045, 0.01, _N)),
    index=pd.date_range("1996-01-01", periods=_N, freq="B"),
)


def _fake_history(tickers, period="max"):
    return {t: _GROWTH for t in tickers}


def test_asset_projection_returns_ordered_band():
    with patch("backend.services.projection.fetch_price_history", side_effect=_fake_history):
        r = project_asset("SPY", amount=100000, years=5)
    assert r["available"] is True
    assert r["pessimistic"]["value"] <= r["typical"]["value"] <= r["optimistic"]["value"]
    assert r["windows_analysed"] >= 6
    assert "tahmin DEĞİL" in r["honesty_note"]


def test_asset_projection_applies_amount():
    with patch("backend.services.projection.fetch_price_history", side_effect=_fake_history):
        r = project_asset("SPY", amount=50000, years=1)
    typ = r["typical"]
    assert typ["value"] == pytest.approx(50000 * (1 + typ["return_pct"] / 100), rel=0.01)


def test_asset_projection_refuses_thin_history():
    short = {"NEW": _GROWTH.iloc[:300]}  # ~1.2 years of data
    with patch("backend.services.projection.fetch_price_history", return_value=short):
        r = project_asset("NEW", amount=10000, years=5)
    assert r["available"] is False
    assert "geçmiş veri yok" in r["reason"]


def test_portfolio_projection_combines_weighted_series():
    # Two different growth profiles — the diversified band must be narrower than a single asset's
    n = 252 * 30   # enough record for a five-year window to have independent periods
    rng2 = np.random.default_rng(11)
    calm = pd.Series(
        100 * np.cumprod(1 + rng2.normal(0.0003, 0.004, n)),
        index=pd.date_range("1996-01-01", periods=n, freq="B"),
    )

    def fake_multi(tickers, period="10y"):
        return {"SPY": _GROWTH, "GLD": calm}

    with patch("backend.services.projection.fetch_price_history", side_effect=fake_multi):
        r = project_portfolio({"SPY": 0.6, "GLD": 0.4}, amount=100000, years=5)

    assert r["available"] is True
    assert r["pessimistic"]["value"] <= r["typical"]["value"] <= r["optimistic"]["value"]
    assert set(r["tickers"]) == {"SPY", "GLD"}
    assert "tahmin DEĞİL" in r["honesty_note"]


def test_portfolio_projection_endpoint(client):
    def fake_multi(tickers, period="10y"):
        return {t: _GROWTH for t in tickers}

    with patch("backend.services.projection.fetch_price_history", side_effect=fake_multi):
        res = client.post(
            "/planning/projection/portfolio",
            json={"weights": {"SPY": 0.5, "GLD": 0.5}, "amount": 100000, "years": 5},
        )
    assert res.status_code == 200
    assert res.json()["available"] is True


def test_portfolio_projection_endpoint_rejects_bad_weights(client):
    res = client.post(
        "/planning/projection/portfolio",
        json={"weights": {"SPY": 0.5}, "amount": 100000, "years": 5},
    )
    assert res.status_code == 422


def test_asset_projection_endpoint(client):
    with patch("backend.services.projection.fetch_price_history", side_effect=_fake_history):
        res = client.post(
            "/planning/projection/asset",
            json={"ticker": "spy", "amount": 100000, "years": 5},
        )
    assert res.status_code == 200
    assert res.json()["ticker"] == "SPY"


def test_projection_endpoint_rejects_bad_years(client):
    res = client.post(
        "/planning/projection/asset",
        json={"ticker": "SPY", "amount": 100000, "years": 7},
    )
    assert res.status_code == 422


def test_the_context_sentence_never_touches_the_numbers(client):
    """
    The scenario band is the distribution of an asset's own history. A model
    that could nudge those figures would turn a measurement into a forecast,
    which is the one thing every projection in this app refuses to be — so
    the sentence travels BESIDE the band, in its own field.
    """
    from unittest.mock import patch

    payload = {"ticker": "SPY", "amount": 100000, "years": 5}

    with patch("backend.services.news_service.context_sentence",
               return_value="Markets are quiet this week."):
        with_context = client.post("/api/v1/planning/projection/asset", json=payload).json()
    with patch("backend.services.news_service.context_sentence", return_value=None):
        without = client.post("/api/v1/planning/projection/asset", json=payload).json()

    assert with_context.get("context") == "Markets are quiet this week."
    assert without.get("context") is None

    # Every other field is identical: the sentence changed nothing.
    numbers = lambda d: {k: v for k, v in d.items() if k != "context"}  # noqa: E731
    assert numbers(with_context) == numbers(without)


def test_a_failing_digest_costs_the_card_its_sentence_and_nothing_else(client):
    from unittest.mock import patch

    with patch("backend.services.news_service.context_sentence",
               side_effect=RuntimeError("feeds down")):
        res = client.post("/api/v1/planning/projection/asset",
                          json={"ticker": "SPY", "amount": 100000, "years": 5})

    assert res.status_code == 200
    assert res.json().get("context") is None


def test_a_band_needs_independent_periods_not_just_overlapping_windows():
    """
    The guard this replaced counted OVERLAPPING windows, and its comment
    claimed it stopped the app "pretending it's a distribution". Six
    overlapping windows is six steps past the horizon: a five-year band
    passed on five and a half years of history — one stretch of history
    resampled sixty-six times, drawn as a spread of outcomes.

    Twelve years cannot carry a five-year band honestly: it holds two
    non-overlapping stretches. Thirty years holds six.
    """
    from unittest.mock import patch

    def history_of(years):
        n = 252 * years
        rng = np.random.default_rng(3)
        return {"SPY": pd.Series(
            100 * np.cumprod(1 + rng.normal(0.0004, 0.01, n)),
            index=pd.date_range("1990-01-01", periods=n, freq="B"),
        )}

    with patch("backend.services.projection.fetch_price_history",
               side_effect=lambda t, period="max": history_of(12)):
        thin = project_asset("SPY", amount=10_000, years=5)
    assert thin["available"] is False, "12 years is two independent 5-year periods"

    with patch("backend.services.projection.fetch_price_history",
               side_effect=lambda t, period="max": history_of(30)):
        ok = project_asset("SPY", amount=10_000, years=5)
    assert ok["available"] is True
    assert ok["independent_periods"] >= 3
