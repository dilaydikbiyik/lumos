"""
Provider-agnostic AI service.

Exposes chat() and generate_text() backed by the provider selected via
settings.AI_PROVIDER ("gemini" or "anthropic"). Gemini's free tier is the
development default; Anthropic can be enabled by switching the env var.
"""
from pathlib import Path
from typing import Optional

from fastapi import HTTPException

from backend.config import settings

_SYSTEM_PROMPT = (Path(__file__).parent.parent / "prompts" / "system_prompt.txt").read_text()

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


# ── Gemini adapter ────────────────────────────────────────────────────────────

def _gemini_chat(messages: list[dict], system: str, max_tokens: int) -> str:
    import google.generativeai as genai
    from google.api_core import exceptions as gexc

    genai.configure(api_key=settings.GEMINI_API_KEY)
    model = genai.GenerativeModel(GEMINI_MODEL, system_instruction=system)

    # Convert OpenAI/Anthropic-style messages to Gemini history format
    history = [
        {"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]}
        for m in messages[:-1]
    ]
    last = messages[-1]["content"]

    try:
        session = model.start_chat(history=history)
        response = session.send_message(
            last,
            generation_config={"max_output_tokens": max_tokens},
        )
        return response.text
    except gexc.ResourceExhausted:
        raise HTTPException(
            status_code=503,
            detail="Daily free AI quota reached. Please try again tomorrow.",
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
    return adapter(messages, system, max_tokens)


# ── Public API (unchanged signatures) ─────────────────────────────────────────

def chat(messages: list[dict]) -> str:
    """
    Send a conversation history to the configured AI provider.

    Args:
        messages: List of {"role": "user"|"assistant", "content": str}

    Returns:
        The assistant's text reply.
    """
    return _dispatch(messages, _SYSTEM_PROMPT, max_tokens=1024)


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
