"""
Holdings router tests — CRUD, wealth summary, remaining-budget math.
"""

LAND = {
    "asset_type": "land",
    "name": "Ankara Gölbaşı arsa",
    "purchase_amount": 600000,
    "manual_current_value": 750000,
    "note": "tapu alındı",
}
STOCK = {
    "asset_type": "stock",
    "name": "S&P 500 ETF",
    "ticker": "SPY",
    "purchase_amount": 100000,
    "quantity": 5,
}


def test_create_and_list_holdings(client):
    created = client.post("/holdings", json=LAND)
    assert created.status_code == 201
    assert created.json()["asset_type"] == "land"

    listed = client.get("/holdings")
    assert listed.status_code == 200
    assert any(h["name"] == LAND["name"] for h in listed.json())


def test_exchange_asset_requires_ticker(client):
    bad = dict(STOCK)
    del bad["ticker"]
    res = client.post("/holdings", json=bad)
    assert res.status_code == 422


def test_off_exchange_asset_needs_no_ticker(client):
    res = client.post("/holdings", json=LAND)
    assert res.status_code == 201
    assert res.json()["ticker"] is None


def test_update_holding_valuation(client):
    created = client.post("/holdings", json=LAND).json()
    res = client.patch(f"/holdings/{created['id']}", json={"manual_current_value": 800000})
    assert res.status_code == 200
    assert res.json()["manual_current_value"] == 800000


def test_delete_holding(client):
    created = client.post("/holdings", json=STOCK).json()
    res = client.delete(f"/holdings/{created['id']}")
    assert res.status_code == 204
    remaining_ids = [h["id"] for h in client.get("/holdings").json()]
    assert created["id"] not in remaining_ids


def test_update_missing_holding_404(client):
    res = client.patch("/holdings/999999", json={"purchase_amount": 1})
    assert res.status_code == 404


def test_summary_math(client):
    # Clean slate for deterministic math: delete existing holdings
    for h in client.get("/holdings").json():
        client.delete(f"/holdings/{h['id']}")

    # Declare a budget via profile
    client.post("/profile", json={
        "budget": 1000000, "time_horizon": "long", "loss_tolerance": "medium",
        "goal": "growth", "experience": "beginner",
    })
    client.post("/holdings", json=LAND)    # invested 600k, now worth 750k
    client.post("/holdings", json=STOCK)   # invested 100k, no valuation → 100k

    s = client.get("/holdings/summary").json()
    assert s["total_budget"] == 1000000
    assert s["total_invested"] == 700000
    assert s["remaining_budget"] == 300000
    assert s["total_current_value"] == 850000
    assert s["holdings_count"] == 2
    assert s["by_type"] == {"land": 750000, "stock": 100000}
    # remaining_budget (300k) is idle cash — erosion card should be populated
    assert s["cash_erosion"] is not None
    assert s["cash_erosion"]["erosion_amount"] > 0


def test_summary_no_erosion_when_fully_invested(client):
    for h in client.get("/holdings").json():
        client.delete(f"/holdings/{h['id']}")
    client.post("/profile", json={
        "budget": 100000, "time_horizon": "long", "loss_tolerance": "medium",
        "goal": "growth", "experience": "beginner",
    })
    client.post("/holdings", json=dict(STOCK, purchase_amount=100000))
    s = client.get("/holdings/summary").json()
    assert s["remaining_budget"] == 0
    assert s["cash_erosion"] is None
