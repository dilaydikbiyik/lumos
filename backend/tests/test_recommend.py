"""
Recommend router integration tests — portfolio engine and AI explainer mocked
(no yfinance network calls, no LLM calls).
"""
from unittest.mock import patch

from backend.schemas.portfolio import AssetAllocation, PortfolioRecommendResponse

FAKE_PORTFOLIO = PortfolioRecommendResponse(
    risk_score=6.0,
    budget=100000,
    allocations=[
        AssetAllocation(ticker="SPY", name="S&P 500 ETF", weight=0.5, category="stocks"),
        AssetAllocation(ticker="VNQ", name="Vanguard REIT ETF", weight=0.3, category="reit"),
        AssetAllocation(ticker="GLD", name="Gold ETF", weight=0.2, category="gold"),
    ],
    plain_explanation="",
    includes_reits=True,
)


def _patches():
    return (
        patch("backend.services.path_portfolio.build_portfolio", return_value=FAKE_PORTFOLIO.model_copy(deep=True)),
        patch("backend.routers.recommend.explain_portfolio", return_value="Sade açıklama."),
        patch("backend.routers.recommend.explain_reit_inclusion", return_value="REIT açıklaması."),
    )


def test_recommend_returns_portfolio_with_explanations(client):
    # Pin the market explicitly. A new account now starts in the one its
    # language suggests, so "TR" is a default rather than a constant — and a
    # test that asserts the threading should set what it asserts.
    client.patch("/users/me/market", json={"market": "TR"})
    # Stocks-only: the portfolio is the budget less the emergency reserve
    # (10% when no outgoings are known), with no property fund.
    client.patch("/users/me/investment-path", json={"investment_path": "stocks"})
    p_engine, p_explain, p_reit = _patches()
    with p_engine as m_engine, p_explain, p_reit:
        res = client.post("/recommend", json={"risk_score": 6.0, "budget": 100000})
    assert res.status_code == 200
    body = res.json()
    assert len(body["allocations"]) == 3
    assert abs(sum(a["weight"] for a in body["allocations"]) - 1.0) < 1e-9
    assert body["plain_explanation"] == "Sade açıklama."
    assert body["metadata"]["reit_explanation"] == "REIT açıklaması."
    # Market and language are both part of the call and are independent: the
    # market selects the investable universe (EU users cannot legally hold the
    # US-domiciled default set), the language selects the wording of the
    # rationale. A default request is the Turkish market read in Turkish.
    m_engine.assert_called_once_with(6.0, 90000.0, "TR", "tr", include_reits=False)


def test_recommend_skips_reit_explanation_when_no_reits(client):
    no_reit = FAKE_PORTFOLIO.model_copy(deep=True)
    no_reit.includes_reits = False
    with patch("backend.services.path_portfolio.build_portfolio", return_value=no_reit), \
         patch("backend.routers.recommend.explain_portfolio", return_value="Sade açıklama."), \
         patch("backend.routers.recommend.explain_reit_inclusion") as m_reit:
        res = client.post("/recommend", json={"risk_score": 3.0, "budget": 20000})
    assert res.status_code == 200
    assert "reit_explanation" not in res.json()["metadata"]
    m_reit.assert_not_called()


def test_recommend_rejects_out_of_range_risk_score(client):
    res = client.post("/recommend", json={"risk_score": 11, "budget": 100000})
    assert res.status_code == 422


def test_recommend_rejects_zero_budget(client):
    res = client.post("/recommend", json={"risk_score": 5, "budget": 0})
    assert res.status_code == 422


# ── the recommendation survives the AI being down ───────────────────────────
#
# scripts/live_smoke.py ran out of free-tier AI quota partway through and
# /recommend began returning 503: the deterministic portfolio, which needs no
# model at all, was lost because the sentence beside it could not be written.

def test_the_portfolio_is_served_when_every_ai_provider_is_down(client):
    from unittest.mock import patch

    from fastapi import HTTPException

    down = HTTPException(status_code=503, detail="all providers down")
    with patch("backend.routers.recommend.explain_portfolio", side_effect=down), \
         patch("backend.routers.recommend.explain_reit_inclusion", side_effect=down):
        res = client.post("/recommend", json={"risk_score": 6.0, "budget": 250000})

    assert res.status_code == 200, res.text
    body = res.json()
    assert body["allocations"], "the portfolio itself must survive the outage"
    assert body["plain_explanation"] == ""


def test_the_portfolio_is_served_when_the_ai_raises_its_own_error(client):
    from unittest.mock import patch

    from backend.exceptions import AIServiceError

    with patch("backend.routers.recommend.explain_portfolio",
               side_effect=AIServiceError("quota")), \
         patch("backend.routers.recommend.explain_reit_inclusion",
               side_effect=AIServiceError("quota")):
        res = client.post("/recommend", json={"risk_score": 6.0, "budget": 250000})

    assert res.status_code == 200, res.text
    assert res.json()["allocations"]


def test_a_programming_error_in_the_explainer_still_surfaces(client):
    """Only the outage is absorbed. A bug must not hide as a missing paragraph."""
    from unittest.mock import patch

    with patch("backend.routers.recommend.explain_portfolio",
               side_effect=TypeError("broken")):
        try:
            res = client.post("/recommend", json={"risk_score": 6.0, "budget": 250000})
        except TypeError:
            return                      # raised through the test client: surfaced
    assert res.status_code == 500
