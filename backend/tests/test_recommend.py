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
        patch("backend.routers.recommend.build_portfolio", return_value=FAKE_PORTFOLIO.model_copy(deep=True)),
        patch("backend.routers.recommend.explain_portfolio", return_value="Sade açıklama."),
        patch("backend.routers.recommend.explain_reit_inclusion", return_value="REIT açıklaması."),
    )


def test_recommend_returns_portfolio_with_explanations(client):
    p_engine, p_explain, p_reit = _patches()
    with p_engine as m_engine, p_explain, p_reit:
        res = client.post("/recommend", json={"risk_score": 6.0, "budget": 100000})
    assert res.status_code == 200
    body = res.json()
    assert len(body["allocations"]) == 3
    assert abs(sum(a["weight"] for a in body["allocations"]) - 1.0) < 1e-9
    assert body["plain_explanation"] == "Sade açıklama."
    assert body["metadata"]["reit_explanation"] == "REIT açıklaması."
    m_engine.assert_called_once_with(risk_score=6.0, budget=100000)


def test_recommend_skips_reit_explanation_when_no_reits(client):
    no_reit = FAKE_PORTFOLIO.model_copy(deep=True)
    no_reit.includes_reits = False
    with patch("backend.routers.recommend.build_portfolio", return_value=no_reit), \
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
