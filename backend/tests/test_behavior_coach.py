"""
Behavioral coach tests — templates + endpoints.
"""
from backend.services.behavior_coach import behavior_mirror, drop_message


def test_drop_message_varies_by_tolerance():
    low = drop_message("low")
    high = drop_message("high")
    assert low != high
    assert "tedirgin" in low.lower() or "doğal" in low.lower()


def test_unknown_tolerance_falls_back_to_medium():
    assert drop_message("unknown") == drop_message("medium")


def test_behavior_mirror_flags_courage_on_dip_buy():
    note = behavior_mirror("low", "bought_dip")
    assert note is not None
    assert "cesaret" in note.lower()


def test_behavior_mirror_no_note_when_consistent():
    assert behavior_mirror("medium", "bought_dip") is None


def test_market_move_endpoint(client):
    res = client.post("/coach/market-move", json={"direction": "drop", "drawdown_pct": -12.0})
    assert res.status_code == 200
    body = res.json()
    assert body["loss_tolerance"] in ("low", "medium", "high")
    assert len(body["message"]) > 0


def test_behavior_mirror_endpoint(client):
    for h in client.get("/holdings").json():
        client.delete(f"/holdings/{h['id']}")
    client.post("/holdings", json={
        "asset_type": "stock", "name": "SPY", "ticker": "SPY",
        "purchase_amount": 10000, "emotion_tag": "fomo",
    })
    res = client.get("/coach/behavior-mirror")
    assert res.status_code == 200
    assert res.json()["by_emotion"]["fomo"] == 1
