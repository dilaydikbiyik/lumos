"""
API-level end-to-end journeys — the 5 persona scenarios from
tests/e2e/scenarios.json walked through the real HTTP surface:

  path selection -> fear check-in -> risk profile -> recommendation ->
  "Aldım" (holdings) -> wealth summary -> readiness score

External boundaries (AI provider, yfinance) are mocked; everything else
(routing, validation, DB, business logic) runs for real.
"""
import json
from pathlib import Path
from unittest.mock import patch

import pytest

from backend.schemas.portfolio import AssetAllocation, PortfolioRecommendResponse

SCENARIOS = json.loads(
    (Path(__file__).parent.parent.parent / "tests" / "e2e" / "scenarios.json").read_text()
)["scenarios"]


def _fake_portfolio(risk_score, budget):
    return PortfolioRecommendResponse(
        risk_score=risk_score, budget=budget,
        allocations=[
            AssetAllocation(ticker="SPY", name="S&P 500 ETF", weight=0.6, category="stocks"),
            AssetAllocation(ticker="GLD", name="Gold ETF", weight=0.4, category="gold"),
        ],
        plain_explanation="", includes_reits=False,
    )


@pytest.mark.parametrize("scenario", SCENARIOS, ids=[s["name"] for s in SCENARIOS])
def test_full_journey(client, scenario):
    from backend.main import app
    from backend.middleware.verify_clerk import get_current_user

    # each persona gets its own user — no quota/holdings collisions
    app.dependency_overrides[get_current_user] = lambda: f"user_e2e_{scenario['name']}"

    # 1) Path selection (Flow 0)
    res = client.patch("/users/me/investment-path", json={"investment_path": "hybrid"})
    assert res.status_code == 200

    # 2) Korku check-in'i
    res = client.patch("/users/me/fear-check-in", json={"primary_fear": "param_eriyor"})
    assert res.status_code == 200

    # 3) Risk profili
    res = client.post("/profile", json=scenario["answers"])
    assert res.status_code == 200
    profile = res.json()
    score = profile["risk_score"]
    assert profile["label"] in scenario["expected_label_in"], (
        f"{scenario['name']}: beklenmedik etiket {profile['label']} (skor {score})"
    )
    if "max_risk_score" in scenario:
        assert score <= scenario["max_risk_score"]
    if "min_risk_score" in scenario:
        assert score >= scenario["min_risk_score"]

    # 4) Portfolio recommendation (engine + mocked explainer)
    with patch("backend.routers.recommend.build_portfolio",
               return_value=_fake_portfolio(score, scenario["answers"]["budget"])), \
         patch("backend.routers.recommend.explain_portfolio", return_value="Açıklama."):
        res = client.post("/recommend", json={
            "risk_score": score, "budget": scenario["answers"]["budget"],
        })
    assert res.status_code == 200
    allocations = res.json()["allocations"]
    assert abs(sum(a["weight"] for a in allocations) - 1.0) < 1e-9

    # 5) "I bought it" — record the allocation into holdings
    for a in allocations:
        res = client.post("/holdings", json={
            "asset_type": "stock" if a["category"] == "stocks" else "gold",
            "name": a["name"], "ticker": a["ticker"],
            "purchase_amount": round(a["weight"] * scenario["answers"]["budget"]),
        })
        assert res.status_code == 201

    # 6) Wealth summary: remaining budget should be ~0 (fully invested)
    res = client.get("/holdings/summary")
    assert res.status_code == 200
    summary = res.json()
    assert summary["holdings_count"] == 2
    assert summary["remaining_budget"] == pytest.approx(0, abs=1)

    # 7) Readiness score: profile + path + holdings done -> serious progress
    res = client.get("/users/me/readiness")
    assert res.status_code == 200
    assert res.json()["score"] >= 60
