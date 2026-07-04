"""
Fener (portfolio health score) tests.
"""
from backend.services.health_score import compute_health


def test_empty_portfolio_scores_zero():
    result = compute_health({})
    assert result["overall"] == 0
    assert result["notes"]


def test_single_asset_type_scores_low_diversification():
    result = compute_health({"land": 1000000})
    assert result["components"]["diversification"] == 0
    assert result["components"]["liquidity"] == 0  # land is illiquid
    assert any("çeşitlendirme" in n.lower() for n in result["notes"])


def test_balanced_liquid_portfolio_scores_high():
    result = compute_health({
        "stock": 20000, "fund": 20000, "etf": 20000, "gold": 20000, "cash": 20000,
    })
    assert result["components"]["diversification"] == 100
    assert result["components"]["liquidity"] == 100
    assert result["overall"] == 100


def test_illiquid_heavy_portfolio_warns():
    result = compute_health({"real_estate": 800000, "stock": 200000})
    assert result["components"]["liquidity"] == 20
    assert any("nakde dönmez" in n for n in result["notes"])


def test_health_endpoint(client):
    for h in client.get("/holdings").json():
        client.delete(f"/holdings/{h['id']}")
    client.post("/holdings", json={
        "asset_type": "land", "name": "arsa", "purchase_amount": 500000,
    })
    res = client.get("/holdings/health")
    assert res.status_code == 200
    assert res.json()["components"]["liquidity"] == 0
