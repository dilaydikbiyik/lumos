"""
Provider-agnostic AI service.

Exposes chat() and generate_text() backed by the provider selected via
settings.AI_PROVIDER ("gemini" or "anthropic"). Gemini's free tier is the
development default; Anthropic can be enabled by switching the env var.
"""
import hashlib
import logging
import time
from pathlib import Path
from typing import Optional

from fastapi import HTTPException

from backend.config import settings

logger = logging.getLogger("lumos.ai")

_SYSTEM_PROMPT = (Path(__file__).parent.parent / "prompts" / "system_prompt.txt").read_text()

# Short content hash — lets logs tie a response to the exact prompt version
PROMPT_VERSION = hashlib.sha1(_SYSTEM_PROMPT.encode()).hexdigest()[:8]

ANTHROPIC_MODEL = "claude-sonnet-4-6"

# Ücretsiz kota stratejisi: her Gemini modelinin AYRI free-tier kotası var.
# 429 (kota) veya 503 (aşırı yük) yediğimizde sıradaki modele düşeriz —
# kullanıcı hata yerine bir tık daha hafif bir modelden cevap alır.
# Sıralama: kalite ↓, ücretsiz limit ↑ (flash-lite ve 2.0-flash daha cömert).
GEMINI_MODEL_CHAIN = [
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
    "gemini-2.0-flash",
]
GEMINI_MODEL = GEMINI_MODEL_CHAIN[0]  # geriye dönük uyumluluk (testler/loglar)


# ── Anthropic adapter ──────────────────────────────────────────────────────────────────────

def _anthropic_chat(messages: list[dict], system: str, max_tokens: int) -> str:
    import anthropic
    from anthropic import Anthropic
    from anthropic.types import Message, MessageParam
    from typing import cast as tcast

    client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    typed_messages: list[MessageParam] = [
        {"role": m["role"], "content": m["content"]} for m in messages
    ]
    try:
        # cast: create() returns Message|Stream union; we never pass stream=True so it's always Message
        response = tcast(Message, client.messages.create(
            model=ANTHROPIC_MODEL,
            max_tokens=max_tokens,
            system=system,
            messages=typed_messages,
        ))
        block = response.content[0]
        return block.text if hasattr(block, "text") else ""
    except anthropic.BadRequestError as exc:
        if "credit balance" in str(exc):
            raise HTTPException(
                status_code=503,
                detail="AI service is temporarily unavailable (provider quota). Please try again later.",
            )
        raise
    except anthropic.RateLimitError:
        raise HTTPException(
            status_code=503,
            detail="AI service is busy right now. Please try again in a moment.",
        )


# ── Gemini adapter (google-genai SDK) ─────────────────────────────────────────

def _gemini_call_model(client, model: str, contents, system: str, max_tokens: int) -> str:
    """Single model call — raises APIError upward for the fallback chain."""
    from google.genai import types as genai_types

    response = client.models.generate_content(
        model=model,
        contents=contents,
        config=genai_types.GenerateContentConfig(
            system_instruction=system,
            max_output_tokens=max_tokens,
        ),
    )
    if response.text is None:
        raise HTTPException(
            status_code=503,
            detail="AI returned an empty response. Please try again.",
        )
    return response.text


def _gemini_chat(messages: list[dict], system: str, max_tokens: int) -> str:
    from google import genai
    from google.genai import errors as genai_errors

    from google.genai import types as genai_types

    client = genai.Client(api_key=settings.GEMINI_API_KEY)

    # Convert OpenAI/Anthropic-style messages to Gemini content format
    contents = [
        genai_types.Content(
            role="user" if m["role"] == "user" else "model",
            parts=[genai_types.Part(text=m["content"])],
        )
        for m in messages
    ]

    # Fallback zinciri: kota (429) veya geçici yük (5xx) → sıradaki model.
    # Her model ayrı free-tier kotaya sahip olduğu için bu, ücretsiz
    # kapasiteyi fiilen ~3 katına çıkarır ve kullanıcıya hata göstermez.
    last_exc: Optional[Exception] = None
    for i, model in enumerate(GEMINI_MODEL_CHAIN):
        try:
            reply = _gemini_call_model(client, model, contents, system, max_tokens)
            if i > 0:
                logger.info("gemini_fallback served_by=%s (primary quota/load)", model)
            return reply
        except genai_errors.APIError as exc:
            code = getattr(exc, "code", None)
            if code == 429 or (isinstance(code, int) and code >= 500):
                logger.warning("gemini model=%s unavailable (code=%s) — trying next", model, code)
                last_exc = exc
                continue
            raise  # 400 vb. gerçek hatalar zincir boyunca maskelenmez

    # Zincirin tamamı tükendi
    logger.error("gemini_chain_exhausted models=%s last=%s", GEMINI_MODEL_CHAIN, last_exc)
    raise HTTPException(
        status_code=503,
        detail=(
            "Günlük ücretsiz AI kotası doldu — yarın otomatik yenilenir. / "
            "Daily free AI quota reached across all models; resets tomorrow."
        ),
    )


_ADAPTERS = {
    "anthropic": _anthropic_chat,
    "gemini": _gemini_chat,
}


def _dispatch(messages: list[dict], system: str, max_tokens: int) -> str:
    adapter = _ADAPTERS.get(settings.AI_PROVIDER)
    if adapter is None:
        raise HTTPException(
            status_code=500,
            detail=f"Unknown AI_PROVIDER '{settings.AI_PROVIDER}' — use 'gemini' or 'anthropic'.",
        )

    started = time.monotonic()
    try:
        reply = adapter(messages, system, max_tokens)
    except Exception as exc:
        logger.error(
            "ai_call provider=%s prompt_version=%s messages=%d max_tokens=%d "
            "latency_ms=%d status=error error=%s",
            settings.AI_PROVIDER, PROMPT_VERSION, len(messages), max_tokens,
            (time.monotonic() - started) * 1000, type(exc).__name__,
        )
        raise

    logger.info(
        "ai_call provider=%s prompt_version=%s messages=%d max_tokens=%d "
        "latency_ms=%d status=ok reply_chars=%d",
        settings.AI_PROVIDER, PROMPT_VERSION, len(messages), max_tokens,
        (time.monotonic() - started) * 1000, len(reply),
    )
    return reply


# ── Public API (unchanged signatures) ─────────────────────────────────────────

def chat(messages: list[dict]) -> str:
    """
    Send a conversation history to the configured AI provider.

    Args:
        messages: List of {"role": "user"|"assistant", "content": str}

    Returns:
        The assistant's text reply.
    """
    # RAG: bugünün piyasa özeti system prompt'a eklenir (fail-open — boşsa eklenmez)
    from backend.services.chat_context import build_market_context

    system = _SYSTEM_PROMPT + build_market_context()

    # Generous budget: gemini-2.5-flash spends "thinking" tokens from the same
    # pool, and the final profile summary must not be truncated before the
    # [PROFILE_COMPLETE] marker.
    return _dispatch(messages, system, max_tokens=4096)


def extract_profile(messages: list[dict]) -> dict:
    """
    Extract structured risk-profile answers from a completed profiling
    conversation. Returns a dict matching RiskProfileAnswers fields.

    Raises HTTPException(422) if the AI output cannot be parsed as JSON.
    """
    import json
    import re

    extract_system = (
        Path(__file__).parent.parent / "prompts" / "profile_extract_prompt.txt"
    ).read_text()
    transcript = "\n".join(f"{m['role'].upper()}: {m['content']}" for m in messages)

    raw = _dispatch(
        [{"role": "user", "content": f"CONVERSATION:\n{transcript}"}],
        extract_system,
        max_tokens=512,
    )

    # Strategy 1: strip markdown fences and try direct parse
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw.strip(), flags=re.MULTILINE).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # Strategy 2: find the first {...} block in the response (handles thinking tokens / prose)
    match = re.search(r"\{[^{}]+\}", cleaned, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass

    # Strategy 3: find any {...} block including nested
    match = re.search(r"\{.*?\}", raw, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass

    logger.warning(
        "extract_profile failed to parse JSON. raw_output=%r",
        raw[:300],
    )
    raise HTTPException(
        status_code=422,
        detail="Sohbet tamamlanmadı — lütfen tüm soruları yanıtla ve tekrar dene.",
    )


def generate_text(prompt: str, system: Optional[str] = None) -> str:
    """
    One-shot text generation (used for explainer / REIT prompt calls).

    Args:
        prompt:  The user-turn prompt.
        system:  Optional override system prompt.

    Returns:
        Generated text.
    """
    return _dispatch(
        [{"role": "user", "content": prompt}],
        system or _SYSTEM_PROMPT,
        max_tokens=512,
    )
