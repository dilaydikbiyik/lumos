"""
Debt answer survives the full round trip: POST /profile -> DB -> GET /profile.
The score is recomputed on read, so the debt check must be recomputed too.
"""


def test_debt_survives_save_and_reload(client):
    body = {
        "budget": 100000, "time_horizon": "long", "loss_tolerance": "medium",
        "goal": "growth", "experience": "none", "high_interest_debt": 40000,
    }
    res = client.post("/profile", json=body)
    assert res.status_code == 200, res.text
    assert res.json()["debt_check"]["advantage"] > 0

    again = client.get("/profile")
    assert again.status_code == 200
    assert again.json()["debt_check"]["debt"] == 40000
    assert again.json()["answers"]["high_interest_debt"] == 40000
