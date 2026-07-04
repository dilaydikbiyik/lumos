"""
Daily message quota tests — chat blocks at the configured limit.
"""
from unittest.mock import patch


def test_quota_exhaustion_returns_429(client, mock_ai):
    # Fresh user — other tests share FAKE_USER_ID and may have used quota
    from backend.main import app
    from backend.middleware.verify_clerk import get_current_user

    app.dependency_overrides[get_current_user] = lambda: "user_quota_test"
    with patch("backend.routers.chat.settings.DAILY_MESSAGE_QUOTA", 3):
        for _ in range(3):
            ok = client.post(
                "/chat", json={"messages": [{"role": "user", "content": "merhaba"}]}
            )
            assert ok.status_code == 200

        blocked = client.post(
            "/chat", json={"messages": [{"role": "user", "content": "bir daha"}]}
        )
    assert blocked.status_code == 429
    assert "yarın" in blocked.json()["detail"] or "tomorrow" in blocked.json()["detail"]
    assert mock_ai.call_count == 3  # blocked message never reached the AI


def test_users_me_and_investment_path(client):
    me = client.get("/users/me")
    assert me.status_code == 200

    res = client.patch("/users/me/investment-path", json={"investment_path": "hybrid"})
    assert res.status_code == 200
    assert res.json()["investment_path"] == "hybrid"

    bad = client.patch("/users/me/investment-path", json={"investment_path": "yolo"})
    assert bad.status_code == 422
