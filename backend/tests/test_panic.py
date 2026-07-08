"""
Panik Düğmesi testleri — profil-bazlı sakinleştirme + çözüm loglama.
"""


def _set_loss_tolerance(client, tolerance):
    client.post("/profile", json={
        "budget": 100000, "time_horizon": "long",
        "loss_tolerance": tolerance, "goal": "growth", "experience": "none",
    })


def test_panic_press_returns_profile_keyed_message(client):
    _set_loss_tolerance(client, "low")
    res = client.post("/coach/panic", json={})
    assert res.status_code == 200
    body = res.json()
    assert body["loss_tolerance"] == "low"
    assert len(body["facts"]) >= 3
    assert "doğal" in body["message"]  # low-tolerance mesajı endişeyi normalize eder


def test_panic_facts_contain_no_dark_patterns(client):
    res = client.post("/coach/panic", json={})
    facts = " ".join(res.json()["facts"])
    # kullanıcının özgürlüğü açıkça teslim edilmeli
    assert "geçerli bir karar" in facts


def test_panic_resolution_held(client):
    res = client.post("/coach/panic", json={"resolution": "held"})
    assert res.status_code == 200
    assert "Plana sadık" in res.json()["message"]


def test_panic_resolution_still_worried_points_to_advisor(client):
    res = client.post("/coach/panic", json={"resolution": "still_worried"})
    assert res.status_code == 200
    assert "danışman" in res.json()["message"]
