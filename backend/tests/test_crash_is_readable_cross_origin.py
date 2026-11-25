"""
A 500 carries CORS and the request id, so the browser can read it.

Without them a cross-origin crash looks like a network failure: the client
retries a GET five times over ~37 seconds and never shows the translated
message. See UnhandledErrorMiddleware.
"""
from fastapi.testclient import TestClient

from backend.config import settings
from backend.main import app


def test_an_unhandled_error_is_a_readable_500():
    @app.get("/api/v1/__boom_for_test")
    async def boom():
        raise RuntimeError("boom")

    try:
        origin = settings.FRONTEND_URL
        with TestClient(app, raise_server_exceptions=False) as c:
            res = c.get("/api/v1/__boom_for_test",
                        headers={"Origin": origin, "X-Request-ID": "abc123",
                                 "Accept-Language": "tr"})
        assert res.status_code == 500
        assert res.headers.get("access-control-allow-origin") == origin
        assert res.headers.get("x-request-id") == "abc123"
        body = res.json()
        assert body["error"]["code"] == "internal_error"
        assert body["error"]["request_id"] == "abc123"
        assert "boom" not in res.text
    finally:
        app.router.routes[:] = [r for r in app.router.routes
                                if getattr(r, "path", "") != "/api/v1/__boom_for_test"]
