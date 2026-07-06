"""
Request-ID correlation and standard error envelope tests.
"""


def test_response_carries_request_id_header(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert len(res.headers.get("X-Request-ID", "")) >= 12


def test_client_supplied_request_id_is_echoed(client):
    res = client.get("/health", headers={"X-Request-ID": "test-rid-42"})
    assert res.headers["X-Request-ID"] == "test-rid-42"


def test_error_envelope_shape(client):
    from unittest.mock import patch
    from backend.exceptions import MarketDataError

    with patch("backend.routers.backtest.run_backtest", side_effect=MarketDataError("down")):
        res = client.post(
            "/backtest",
            json={"weights": {"SPY": 1.0}, "budget": 1000, "period": "1y"},
            headers={"X-Request-ID": "rid-err-1"},
        )
    assert res.status_code == 503
    body = res.json()
    assert body["error"]["code"] == "market_data_unavailable"
    assert body["error"]["request_id"] == "rid-err-1"
    assert body["detail"]  # frontend backward compatibility
