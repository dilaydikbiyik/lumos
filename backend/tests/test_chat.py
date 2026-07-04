"""
Chat router integration tests — AI provider mocked, auth bypassed.
"""


def test_chat_returns_reply(client, mock_ai):
    res = client.post(
        "/chat",
        json={"messages": [{"role": "user", "content": "10.000 TL bütçem var"}]},
    )
    assert res.status_code == 200
    assert res.json()["reply"] == "Mocked AI reply ⚠️ educational purposes only"
    mock_ai.assert_called_once()


def test_chat_passes_full_history(client, mock_ai):
    history = [
        {"role": "assistant", "content": "Merhaba! Bütçen nedir?"},
        {"role": "user", "content": "20.000 TL"},
    ]
    res = client.post("/chat", json={"messages": history})
    assert res.status_code == 200
    sent_messages = mock_ai.call_args[0][0]
    assert sent_messages == history


def test_chat_rejects_invalid_body(client, mock_ai):
    res = client.post("/chat", json={"messages": [{"role": "user"}]})  # content eksik
    assert res.status_code == 422
    mock_ai.assert_not_called()


def test_chat_requires_auth(mock_ai):
    """Without the auth override, a tokenless request must be rejected."""
    from fastapi.testclient import TestClient
    from backend.main import app

    app.dependency_overrides.clear()
    with TestClient(app) as raw_client:
        res = raw_client.post(
            "/chat",
            json={"messages": [{"role": "user", "content": "merhaba"}]},
        )
    assert res.status_code == 401
    mock_ai.assert_not_called()
