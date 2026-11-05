"""
The store builds can reach the API.

A Capacitor app serves its bundled UI from its own origin —
capacitor://localhost on iOS, https://localhost on Android — not from the
website. Production CORS allowed only FRONTEND_URL, so every request from
the App Store and Play Store builds would have been refused while the web
build worked: a blank app on a reviewer's phone.

Checked against a real CORS preflight through Starlette's own middleware,
built with the production rule, rather than by reading the list back.
"""
import pytest
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.testclient import TestClient

from backend.config import settings
from backend.main import NATIVE_APP_ORIGINS, production_origins


# A fixed production value, not whatever this machine's .env says. The first
# version read settings.FRONTEND_URL as found: on the author's machine that
# was the Vercel URL and every case passed; in CI it is the default,
# http://localhost:5173, which this file then asserted must be REFUSED. A
# CORS test whose verdict depends on the laptop it runs on tests the laptop.
PROD_FRONTEND = "https://lumos.example.app"


@pytest.fixture(autouse=True)
def _production_frontend(monkeypatch):
    monkeypatch.setattr(settings, "FRONTEND_URL", PROD_FRONTEND)


@pytest.fixture
def prod_app():
    app = FastAPI()
    app.add_middleware(CORSMiddleware, allow_origins=production_origins(),
                       allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

    @app.get("/ping")
    def ping():
        return {"ok": True}

    return TestClient(app)


def _preflight(client, origin):
    return client.options("/ping", headers={
        "Origin": origin, "Access-Control-Request-Method": "GET",
    })


@pytest.mark.parametrize("origin", [*NATIVE_APP_ORIGINS, PROD_FRONTEND])
def test_the_web_and_both_store_builds_are_admitted(prod_app, origin):
    res = _preflight(prod_app, origin)
    assert res.status_code == 200, origin
    assert res.headers.get("access-control-allow-origin") == origin


@pytest.mark.parametrize("origin", [
    # The development convenience must not leak into production: a dev
    # server on some port is not the store build.
    "http://localhost:5173",
    "https://localhost:8443",
    "http://localhost",
    "https://evil.example.com",
])
def test_nothing_else_is(prod_app, origin):
    res = _preflight(prod_app, origin)
    assert res.headers.get("access-control-allow-origin") != origin, origin
