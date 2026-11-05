"""
The stock explorer describes and never recommends — enforced, not intended.

The explorer exists so the app can be as broad as a brokerage list while
staying an education tool. docs/legal-review-brief.md puts the line at
naming instruments PERSONALISED to someone. These tests hold the design to
it: the answer cannot depend on who asks, the order cannot reward last
year's winners, and nothing in it ranks, rates or suits.
"""
import numpy as np
import pandas as pd
import pytest

from backend.markets import MARKET_PACKS, get_market_pack
from backend.markets.base import EXPLORER_SECTORS


def _series(seed: int, years: float = 5, vol: float = 0.02):
    n = int(252 * years)
    rng = np.random.default_rng(seed)
    return pd.Series(100 * np.cumprod(1 + rng.normal(0.0003, vol, n)),
                     index=pd.date_range("2021-11-01", periods=n, freq="B"))


@pytest.fixture
def fake_prices(monkeypatch):
    """Every explorer ticker gets a deterministic five-year series."""
    from backend.services import cache as cache_service
    from backend.services import stock_explorer

    calm = {p.explorer_benchmark["ticker"] for p in MARKET_PACKS.values()}

    def history(tickers, period="5y", adjusted=True):
        return {t: _series(abs(hash(t)) % 10_000, vol=0.01 if t in calm else 0.025)
                for t in tickers}

    monkeypatch.setattr(stock_explorer, "fetch_price_history", history)
    monkeypatch.setattr(cache_service, "get", lambda k: None)
    monkeypatch.setattr(cache_service, "set", lambda k, v, ttl=None: None)
    monkeypatch.setattr(stock_explorer, "_real", lambda change, market: round(change / 2, 1))
    return stock_explorer


# ── the packs ───────────────────────────────────────────────────────────────

@pytest.mark.parametrize("market", sorted(MARKET_PACKS))
def test_every_market_has_a_real_list_with_known_sectors(market):
    pack = get_market_pack(market)
    stocks = pack.explorer_stocks
    assert len(stocks) >= 20, f"{market} explorer has only {len(stocks)} companies"
    assert pack.explorer_as_of, "a dated selection must say its date"
    tickers = [s["ticker"] for s in stocks]
    assert len(tickers) == len(set(tickers)), f"{market} lists a company twice"
    unknown = {s["sector"] for s in stocks} - EXPLORER_SECTORS
    assert not unknown, f"{market} uses sectors with no translation: {unknown}"


def test_no_company_is_listed_under_two_markets():
    seen = {}
    for code, pack in MARKET_PACKS.items():
        for s in pack.explorer_stocks:
            assert s["ticker"] not in seen, f"{s['ticker']} in {seen.get(s['ticker'])} and {code}"
            seen[s["ticker"]] = code


# ── it describes; it does not recommend ─────────────────────────────────────

@pytest.mark.parametrize("market", sorted(MARKET_PACKS))
def test_the_list_is_ordered_by_name_never_by_return(fake_prices, market):
    """Sorted by return it would be a leaderboard — a recommendation by order."""
    rows = fake_prices.explore(market)["stocks"]
    names = [r["name"] for r in rows]
    assert names == sorted(names, key=str.casefold)
    returns = [r["change_pct"] for r in rows]
    assert returns != sorted(returns, reverse=True), "ordered by return"


def test_nothing_in_the_answer_ranks_rates_or_suits(fake_prices):
    banned = {"score", "rank", "rating", "recommended", "suitable", "fit", "pick", "buy", "target"}
    body = fake_prices.explore("TR")
    keys = {k.lower() for row in body["stocks"] for k in row} | {k.lower() for k in body}
    assert not keys & banned, keys & banned


def test_the_answer_does_not_depend_on_who_asks(client, fake_prices):
    """
    Two readers on one market with opposite profiles see identical numbers.
    The endpoint reads the market and nothing else — the step that would
    turn this into advice is passing the profile in, and this fails if
    anyone does.
    """
    from backend.middleware.verify_clerk import get_current_user
    from backend.main import app

    answers = []
    for uid, profile in (("cautious", {"loss_tolerance": "low", "goal": "preservation"}),
                         ("bold", {"loss_tolerance": "high", "goal": "speculation"})):
        app.dependency_overrides[get_current_user] = lambda uid=uid: uid
        client.post("/profile", json={"budget": 100_000, "time_horizon": "long",
                                      "experience": "beginner", **profile})
        answers.append(client.get("/stocks/explore").json())
    assert answers[0] == answers[1]


def test_a_company_with_too_short_a_record_is_left_out(monkeypatch, fake_prices):
    """Compared over a shorter window it would not be like for like."""
    pack = get_market_pack("TR")
    young = pack.explorer_stocks[0]["ticker"]
    real = fake_prices.fetch_price_history

    def history(tickers, period="5y", adjusted=True):
        out = real(tickers, period, adjusted)
        out[young] = _series(1, years=2)
        return out

    monkeypatch.setattr(fake_prices, "fetch_price_history", history)
    assert young not in {r["ticker"] for r in fake_prices.explore("TR")["stocks"]}


def test_every_row_carries_the_comparison_that_is_the_lesson(fake_prices):
    body = fake_prices.explore("US")
    assert body["index"]["worst_drop_pct"] < 0
    for row in body["stocks"]:
        assert row["worst_drop_pct"] <= 0
        assert row["swing_vs_index"] > 0
        assert "real_change_pct" in row



# ── one basis for the companies and the benchmark ───────────────────────────

@pytest.mark.parametrize("market", sorted(MARKET_PACKS))
def test_every_market_declares_its_benchmark_and_basis(market):
    b = get_market_pack(market).explorer_benchmark
    assert b.get("ticker"), market
    assert isinstance(b.get("total_return"), bool), market


@pytest.mark.parametrize("market", sorted(MARKET_PACKS))
def test_companies_and_benchmark_are_measured_on_the_same_basis(monkeypatch, fake_prices, market):
    """
    Measured before this rule: the S&P 500 price index gained 56.8% over
    five years and the same index with dividends 67.6%, and Tüpraş's
    five-year return was 2,424% with dividends against 1,498% without. The
    companies came with dividends while the US and Turkish benchmarks came
    without, which flattered every company against its index. One fetch, one
    basis, chosen by what the benchmark can be measured on.
    """
    calls = []
    real = fake_prices.fetch_price_history

    def spy(tickers, period="5y", adjusted=True):
        calls.append((tuple(tickers), adjusted))
        return real(tickers, period, adjusted)

    monkeypatch.setattr(fake_prices, "fetch_price_history", spy)
    body = fake_prices.explore(market)
    bench = get_market_pack(market).explorer_benchmark
    assert len(calls) == 1, "companies and benchmark must come from one fetch"
    assert bench["ticker"] in calls[0][0]
    assert calls[0][1] is bench["total_return"]
    assert body["dividends_included"] is bench["total_return"]
