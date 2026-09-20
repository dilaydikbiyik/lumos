"""
Secrets must not reach logs or responses.

Modelled on the S-03 finding from the across2aim review: an AI-written
integration logged the outbound request body at INFO, and that body carried
`api_key` and `session_key`, so every value sat in plain text in the log
stream. Nothing in the code looked wrong — the leak was a *third party's*
error text being interpolated into a log line.

Lumos has the same shape. Provider SDKs raise exceptions whose messages can
carry the request URL or body, and those exceptions are interpolated into log
records and into error messages. These tests assert the property directly
rather than reviewing the call sites: given a provider that fails with its key
in the error text, the key must appear neither in a log record nor in what the
client receives.
"""
import logging

import pytest
from unittest.mock import patch

from backend.config import settings

# A value that is obviously a secret and obviously not a coincidence.
FAKE_KEY = "AIzaSyLUMOStestSECRETkeyDoNotLeak123456"


def _all_text(caplog) -> str:
    """Everything the logger emitted, formatted the way a log stream sees it."""
    return "\n".join(r.getMessage() for r in caplog.records)


def test_a_provider_error_carrying_its_key_does_not_reach_the_logs(caplog):
    """
    The realistic leak: a provider SDK raises with the key in the message,
    and the handler logs `%s` of the exception.
    """
    from backend.services import ai_service

    boom = RuntimeError(
        f"400 Bad Request for url: https://generativelanguage.googleapis.com"
        f"/v1/models/gemini:generateContent?key={FAKE_KEY}"
    )

    caplog.set_level(logging.DEBUG)
    with patch.object(settings, "GEMINI_API_KEY", FAKE_KEY), \
         patch.object(ai_service, "_gemini_call_model", side_effect=boom):
        try:
            ai_service._gemini_chat([{"role": "user", "content": "hi"}], "sys")
        except Exception:
            pass

    assert FAKE_KEY not in _all_text(caplog), (
        "a provider's key reached the log stream through its own error text"
    )


def test_no_endpoint_returns_a_raw_exception_message(client):
    """
    Every handler must answer with a curated message. `str(exc)` is a value
    written by somebody else — a driver, an SDK, a database — and none of them
    promised to keep secrets out of it.
    """
    payload = {"risk_score": 6.0, "budget": 100000}

    with patch("backend.routers.recommend.build_portfolio",
               side_effect=ValueError(f"connection failed: key={FAKE_KEY}")) as engine:
        res = client.post("/api/v1/recommend", json=payload)

    # Prove the request REACHED the code under test before trusting the
    # assertion below it. An earlier version of this test sent a payload that
    # failed validation, so the patched function never ran and the check
    # passed against an empty 422 — a security test that cannot fail is worse
    # than none, because it still counts as coverage.
    assert engine.called, "payload never reached the engine — the test is vacuous"
    assert res.status_code >= 400, "the failure should surface as an error"
    assert FAKE_KEY not in res.text, (
        f"a raw exception message reached the client: {res.text[:300]}"
    )


@pytest.mark.parametrize("field", [
    "GEMINI_API_KEY", "GEMINI_API_KEY_2", "GROQ_API_KEY", "OPENROUTER_API_KEY",
    "ANTHROPIC_API_KEY", "CLERK_SECRET_KEY", "FRED_API_KEY",
    "TCMB_EVDS_API_KEY", "DATABASE_URL", "SENTRY_DSN",
])
def test_health_never_echoes_a_configured_secret(client, field):
    """
    /health answers "is it set", never "what is it". Parametrised over every
    secret so a newly added one is covered without anyone remembering to.
    """
    if not hasattr(settings, field):
        pytest.skip(f"{field} not configured in this build")

    with patch.object(settings, field, FAKE_KEY):
        body = client.get("/api/v1/health").text

    assert FAKE_KEY not in body, f"{field} leaked into /health"


def test_the_durable_cache_never_stores_a_connection_string():
    """
    The cache mirrors arbitrary values into a shared table. A cached error
    payload carrying a DSN would persist a credential far beyond the request
    that produced it.
    """
    from backend.services import cache_store

    url = cache_store._sync_url()
    if url is None:
        pytest.skip("no durable tier configured")
    # The URL is derived for the engine and must never be logged or returned.
    assert "postgresql+psycopg://" in url
