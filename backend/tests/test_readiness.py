"""
Fear check-in and readiness score tests.
"""


def test_fear_check_in_returns_reassurance(client):
    res = client.patch("/users/me/fear-check-in", json={"primary_fear": "kandirilirim"})
    assert res.status_code == 200
    body = res.json()
    assert body["primary_fear"] == "kandirilirim"
    assert "komisyon" in body["reassurance"]


def test_fear_check_in_rejects_unknown_tag(client):
    res = client.patch("/users/me/fear-check-in", json={"primary_fear": "yolo"})
    assert res.status_code == 422


def test_readiness_score_reflects_milestones(client):
    # Fresh baseline
    baseline = client.get("/users/me/readiness").json()

    client.patch("/users/me/fear-check-in", json={"primary_fear": "anlamiyorum"})
    after_fear = client.get("/users/me/readiness").json()

    assert after_fear["score"] >= baseline["score"]
    assert after_fear["milestones"]["Korkunu paylaştın"] is True


def test_readiness_not_ready_below_threshold(client):
    from backend.main import app
    from backend.middleware.verify_clerk import get_current_user

    app.dependency_overrides[get_current_user] = lambda: "user_fresh_readiness"
    res = client.get("/users/me/readiness")
    assert res.status_code == 200
    assert res.json()["ready_for_real_investing"] is False
