"""
The portfolio follows the reader's chosen path.

Found by the consistency sweep: a stocks-only reader was handed a property
fund, and a hybrid reader's portfolio was built on the whole budget beside a
budget split that had already set aside a reserve and a property share —
property and cash counted twice (a German hybrid reader: ~21% in property).
"""
import pytest

from backend.services.path_portfolio import build_for_path

CASES = [("TR", 250_000), ("US", 20_000), ("DE", 20_000), ("DE", 500_000)]


@pytest.mark.parametrize("market,budget", CASES)
@pytest.mark.parametrize("score", [2.0, 5.5, 9.0])
def test_stocks_only_never_holds_a_property_fund(market, budget, score):
    portfolio, plan = build_for_path("stocks", score, budget, market, "en")
    # The market part of the same split the dashboard's budget plan shows:
    # the reserve comes off the top, and nothing goes to property.
    assert plan["property_amount"] == 0 and plan["property_vehicle"] == "none"
    assert plan["reserve"] + plan["market_amount"] == pytest.approx(budget)
    assert portfolio.budget == pytest.approx(plan["market_amount"])
    assert all(a.category != "reit" for a in portfolio.allocations)


@pytest.mark.parametrize("path", ["hybrid", "undecided"])
@pytest.mark.parametrize("market,budget", CASES)
def test_a_hybrid_portfolio_is_the_market_part_of_the_split(path, market, budget):
    portfolio, plan = build_for_path(path, 6.0, budget, market, "en")
    assert portfolio.budget == pytest.approx(plan["market_amount"])
    assert plan["reserve"] + plan["property_amount"] + plan["market_amount"] == pytest.approx(budget)
    # The split's property part IS the property exposure: none inside the
    # portfolio on top of it.
    assert all(a.category != "reit" for a in portfolio.allocations)
    assert portfolio.metadata["plan"] == plan


def test_no_path_chosen_plans_like_the_budget_split_page():
    """The budget-split endpoint treats a reader with no path as hybrid;
    the portfolio must agree, or the two pages describe different plans."""
    a, plan_a = build_for_path(None, 5.0, 20_000, "DE", "en")
    b, plan_b = build_for_path("hybrid", 5.0, 20_000, "DE", "en")
    assert plan_a == plan_b
    assert [x.ticker for x in a.allocations] == [x.ticker for x in b.allocations]


def test_the_recommendation_carries_the_plan(client):
    client.patch("/users/me/market", json={"market": "DE"})
    client.patch("/users/me/investment-path", json={"investment_path": "hybrid"})
    body = client.post("/recommend", json={"risk_score": 6.0, "budget": 20_000}).json()
    plan = body["metadata"]["plan"]
    assert plan["total_budget"] == 20_000
    assert body["budget"] == pytest.approx(plan["market_amount"])
    assert body["includes_reits"] is False


@pytest.mark.parametrize("market,budget", [("DE", 500_000), ("TR", 3_000_000), ("US", 20_000)])
def test_following_the_hybrid_plan_exactly_is_in_balance(market, budget):
    """The sweep's repro: reserve as cash, the property part as a home, the
    rest exactly as recommended — the drift check said 'serious'."""
    from types import SimpleNamespace

    from backend.services.drift import compute_drift
    from backend.services.path_portfolio import plan_targets

    portfolio, plan = build_for_path("hybrid", 6.6, budget, market, "en")
    holdings, values = [], {}

    def hold(i, asset_type, ticker, value):
        holdings.append(SimpleNamespace(id=i, asset_type=asset_type, ticker=ticker))
        values[i] = value

    hold(1, "cash", None, plan["reserve"])
    hold(2, "real_estate", None, plan["property_amount"])
    for i, a in enumerate(portfolio.allocations, start=3):
        hold(i, "etf", a.ticker, a.weight * plan["market_amount"])

    result = compute_drift(holdings, values, plan_targets(portfolio, plan, market, holdings), "en")
    assert result["verdict"] == "balanced", result["rows"]


def test_a_reit_fund_bought_for_the_property_part_counts_as_property():
    """Recorded as an ETF and absent from the portfolio, it was filed under
    stocks: property 0% against a target of 8%, 'notable' drift."""
    from types import SimpleNamespace

    from backend.markets import get_market_pack
    from backend.services.drift import compute_drift
    from backend.services.path_portfolio import plan_targets

    for market in ("TR", "US", "DE"):
        budget = 20_000 if market != "TR" else 400_000
        portfolio, plan = build_for_path("hybrid", 6.6, budget, market, "en",
                                         monthly_outgoings=budget / 100)
        assert plan["property_vehicle"] == "reit"
        reit = get_market_pack(market).reit_assets[0]["ticker"]
        holdings = [SimpleNamespace(id=1, asset_type="cash", ticker=None),
                    SimpleNamespace(id=2, asset_type="etf", ticker=reit)]
        values = {1: plan["reserve"], 2: plan["property_amount"]}
        for i, a in enumerate(portfolio.allocations, start=3):
            holdings.append(SimpleNamespace(id=i, asset_type="etf", ticker=a.ticker))
            values[i] = a.weight * plan["market_amount"]
        result = compute_drift(holdings, values, plan_targets(portfolio, plan, market, holdings), "en")
        assert result["verdict"] == "balanced", (market, result["rows"])


@pytest.mark.parametrize("path", ["stocks", "hybrid"])
@pytest.mark.parametrize("market,budget", [("TR", 400_000), ("US", 20_000), ("DE", 20_000)])
def test_recording_only_the_portfolio_is_in_balance(path, market, budget):
    """What "I bought it" records — the portfolio and nothing else. The
    reserve and property targets made every such reader 'drifted'."""
    from types import SimpleNamespace

    from backend.services.drift import compute_drift
    from backend.services.path_portfolio import plan_targets

    portfolio, plan = build_for_path(path, 6.6, budget, market, "en")
    holdings, values = [], {}
    for i, a in enumerate(portfolio.allocations, start=1):
        typ = "fund" if a.category == "cash" else "etf"
        holdings.append(SimpleNamespace(id=i, asset_type=typ, ticker=a.ticker))
        values[i] = a.weight * portfolio.budget
    result = compute_drift(holdings, values, plan_targets(portfolio, plan, market, holdings), "en")
    assert result["verdict"] == "balanced", (path, market, result["rows"])
