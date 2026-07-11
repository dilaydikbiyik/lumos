"""
Gemini free-tier fallback chain tests — the quota fix.

Every Gemini model has its own free-tier quota; on 429/5xx we walk down
GEMINI_MODEL_CHAIN instead of surfacing an error. These tests mock the
genai client and verify the chain order, error pass-through, and the
honest exhausted-message at the end.
"""
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException
from google.genai import errors as genai_errors

from backend.config import settings
from backend.services.ai_service import GEMINI_MODEL_CHAIN, _gemini_chat

MSGS = [{"role": "user", "content": "merhaba"}]


def _api_error(code):
    err = genai_errors.APIError.__new__(genai_errors.APIError)
    err.code = code
    err.message = f"fake {code}"
    return err


def _client_with(side_effects):
    """Fake genai client whose generate_content pops side_effects in order."""
    client = MagicMock()
    client.models.generate_content.side_effect = side_effects
    return client


def _ok_response(text="cevap"):
    resp = MagicMock()
    resp.text = text
    return resp


@pytest.fixture
def genai_client():
    # Tests assume a single key — disable the extra slots
    with patch("google.genai.Client") as cls, \
         patch.object(settings, "GEMINI_API_KEY_2", ""), \
         patch.object(settings, "GEMINI_API_KEY_3", ""), \
         patch.object(settings, "GEMINI_API_KEY_4", ""):
        yield cls


def test_primary_model_used_when_healthy(genai_client):
    client = _client_with([_ok_response("birincil")])
    genai_client.return_value = client

    assert _gemini_chat(MSGS, "sys", 100) == "birincil"
    assert client.models.generate_content.call_count == 1
    assert client.models.generate_content.call_args.kwargs["model"] == GEMINI_MODEL_CHAIN[0]


def test_quota_429_falls_back_to_next_model(genai_client):
    client = _client_with([_api_error(429), _ok_response("yedekten")])
    genai_client.return_value = client

    assert _gemini_chat(MSGS, "sys", 100) == "yedekten"
    models_called = [c.kwargs["model"] for c in client.models.generate_content.call_args_list]
    assert models_called == GEMINI_MODEL_CHAIN[:2]


def test_overload_503_falls_back_too(genai_client):
    client = _client_with([_api_error(503), _api_error(503), _ok_response("üçüncü")])
    genai_client.return_value = client

    assert _gemini_chat(MSGS, "sys", 100) == "üçüncü"
    assert client.models.generate_content.call_count == 3


def test_chain_exhausted_gives_honest_quota_message(genai_client):
    client = _client_with([_api_error(429)] * len(GEMINI_MODEL_CHAIN))
    genai_client.return_value = client

    with pytest.raises(HTTPException) as exc:
        _gemini_chat(MSGS, "sys", 100)
    assert exc.value.status_code == 503
    assert "yarın" in exc.value.detail


def test_real_errors_are_not_masked_by_chain(genai_client):
    # 400 (invalid request) must not enter the fallback — surface immediately
    client = _client_with([_api_error(400)])
    genai_client.return_value = client

    with pytest.raises(genai_errors.APIError):
        _gemini_chat(MSGS, "sys", 100)
    assert client.models.generate_content.call_count == 1


def test_multi_key_model_major_order():
    """With 4 keys: the best model is tried on ALL keys before stepping down."""
    with patch("google.genai.Client") as cls, \
         patch.object(settings, "GEMINI_API_KEY", "k1"), \
         patch.object(settings, "GEMINI_API_KEY_2", "k2"), \
         patch.object(settings, "GEMINI_API_KEY_3", ""), \
         patch.object(settings, "GEMINI_API_KEY_4", ""):
        c1, c2 = MagicMock(), MagicMock()
        # k1'in en iyi modeli kotada; k2'nin en iyi modeli cevap veriyor
        c1.models.generate_content.side_effect = [_api_error(429)]
        c2.models.generate_content.side_effect = [_ok_response("k2-flash")]
        cls.side_effect = [c1, c2]

        assert _gemini_chat(MSGS, "sys", 100) == "k2-flash"
        # Both calls went to the SAME (best) model — the key changed, quality didn't
        assert c1.models.generate_content.call_args.kwargs["model"] == GEMINI_MODEL_CHAIN[0]
        assert c2.models.generate_content.call_args.kwargs["model"] == GEMINI_MODEL_CHAIN[0]


def test_thinking_disabled_for_25_family(genai_client):
    client = _client_with([_ok_response("ok")])
    genai_client.return_value = client
    _gemini_chat(MSGS, "sys", 100)
    config = client.models.generate_content.call_args.kwargs["config"]
    assert config.thinking_config is not None
    assert config.thinking_config.thinking_budget == 0


def test_generate_text_cache_skips_second_ai_call():
    from backend.services.ai_service import generate_text

    with patch("backend.services.ai_service._dispatch", return_value="üretildi") as m, \
         patch("backend.services.cache.get", side_effect=[None, "üretildi"]), \
         patch("backend.services.cache.set"):
        first = generate_text("aynı prompt", system="s", cache=True)
        second = generate_text("aynı prompt", system="s", cache=True)
    assert first == second == "üretildi"
    assert m.call_count == 1  # second call served from cache
