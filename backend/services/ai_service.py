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
GEMINI_MODEL = "gemini-2.5-flash"


# ── Anthropic adapter ─────────────────────────────────────────────────────────

def _anthropic_chat(messages: list[dict], system: str, max_tokens: int) -> str:
    import anthropic

    client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    try:
        response = client.messages.create(
            model=ANTHROPIC_MODEL,
            max_tokens=max_tokens,
            system=system,
            messages=messages,
        )
        return response.content[0].text
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

    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
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
    except genai_errors.APIError as exc:
        if exc.code == 429:
            raise HTTPException(
                status_code=503,
                detail="Daily free AI quota reached. Please try again tomorrow.",
            )
        raise


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
    # Generous budget: gemini-2.5-flash spends "thinking" tokens from the same
    # pool, and the final profile summary must not be truncated before the
    # [PROFILE_COMPLETE] marker.
    return _dispatch(messages, _SYSTEM_PROMPT, max_tokens=4096)


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
        max_tokens=256,
    )

    # Tolerate accidental markdown fences around the JSON
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw.strip())
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=422,
            detail="Could not extract a structured profile from the conversation.",
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
