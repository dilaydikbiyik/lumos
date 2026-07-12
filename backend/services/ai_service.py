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
_ADVISOR_PROMPT = (Path(__file__).parent.parent / "prompts" / "advisor_prompt.txt").read_text()

# Short content hash — lets logs tie a response to the exact prompt version
PROMPT_VERSION = hashlib.sha1(_SYSTEM_PROMPT.encode()).hexdigest()[:8]

ANTHROPIC_MODEL = "claude-sonnet-4-6"

# Free-quota strategy: every Gemini model has its OWN free-tier quota.
# On 429 (quota) or 503 (overload) we fall to the next model — the user
# gets an answer from a slightly lighter model instead of an error.
# Order: quality ↓, free limit ↑ (flash-lite and 2.0-flash are more generous).
GEMINI_MODEL_CHAIN = [
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
]
GEMINI_MODEL = GEMINI_MODEL_CHAIN[0]  # backwards compatibility (tests/logs)


# ── Anthropic adapter ──────────────────────────────────────────────────────────────────────

def _anthropic_chat(
    messages: list[dict], system: str, max_tokens: int,
    model_chain: Optional[list[str]] = None,
) -> str:
    import anthropic
    from anthropic import Anthropic
    from anthropic.types import Message, MessageParam
    from typing import cast as tcast

    chain = model_chain or [ANTHROPIC_MODEL]
    client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    typed_messages: list[MessageParam] = [
        {"role": m["role"], "content": m["content"]} for m in messages
    ]

    last_exc: Optional[Exception] = None
    for i, model in enumerate(chain):
        try:
            # cast: create() returns Message|Stream union; we never pass stream=True so it's always Message
            response = tcast(Message, client.messages.create(
                model=model,
                max_tokens=max_tokens,
                system=system,
                messages=typed_messages,
            ))
            if i > 0:
                logger.info("anthropic_fallback served_by=%s", model)
            block = response.content[0]
            return block.text if hasattr(block, "text") else ""
        except anthropic.RateLimitError as exc:
            logger.warning("anthropic model=%s rate-limited — trying next", model)
            last_exc = exc
            continue
        except anthropic.BadRequestError as exc:
            if "credit balance" in str(exc):
                logger.warning("anthropic model=%s credit exhausted — trying next", model)
                last_exc = exc
                continue
            raise

    logger.error("anthropic_chain_exhausted models=%s last=%s", chain, last_exc)
    raise HTTPException(
        status_code=503,
        detail="AI service is temporarily unavailable (provider quota). Please try again later.",
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
            # The 2.5 family burns invisible "thinking" tokens — turning it
            # off cuts token usage substantially and speeds up replies.
            # (The 2.0 family doesn't support thinking; sending it returns 400.)
            thinking_config=(
                genai_types.ThinkingConfig(thinking_budget=0)
                if model.startswith("gemini-2.5") else None
            ),
        ),
    )
    if response.text is None:
        raise HTTPException(
            status_code=503,
            detail="AI returned an empty response. Please try again.",
        )
    return response.text


def _gemini_chat(
    messages: list[dict], system: str, max_tokens: int,
    model_chain: Optional[list[str]] = None,
) -> str:
    from google import genai
    from google.genai import errors as genai_errors
    from google.genai import types as genai_types

    chain = model_chain or GEMINI_MODEL_CHAIN

    # Multiple API keys — each with its own free-tier quota
    keys = [k for k in [
        settings.GEMINI_API_KEY,
        settings.GEMINI_API_KEY_2,
        settings.GEMINI_API_KEY_3,
        settings.GEMINI_API_KEY_4,
    ] if k]

    # Convert messages once
    contents = [
        genai_types.Content(
            role="user" if m["role"] == "user" else "model",
            parts=[genai_types.Part(text=m["content"])],
        )
        for m in messages
    ]

    # MODEL-major order: the best model is tried on ALL keys before
    # stepping down a model. When one key's quota runs out the user
    # sacrifices a key, not quality.
    clients = [genai.Client(api_key=k) for k in keys]
    last_exc: Optional[Exception] = None
    for model_idx, model in enumerate(chain):
        for key_idx, client in enumerate(clients):
            try:
                reply = _gemini_call_model(client, model, contents, system, max_tokens)
                if key_idx > 0 or model_idx > 0:
                    logger.info(
                        "gemini_fallback served_by=%s key_slot=%d", model, key_idx + 1
                    )
                return reply
            except genai_errors.APIError as exc:
                code = getattr(exc, "code", None)
                if code == 429 or (isinstance(code, int) and code >= 500):
                    logger.warning(
                        "gemini key=%d model=%s unavailable (code=%s) — trying next",
                        key_idx + 1, model, code,
                    )
                    last_exc = exc
                    continue
                raise  # real errors (400 etc.) are not masked

    # every key and model exhausted
    logger.error("gemini_all_keys_exhausted keys=%d models=%s last=%s", len(keys), chain, last_exc)
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


def _resolve_tier(tier_name: Optional[str]) -> tuple[str, dict]:
    """
    Tier name → (name, config). Without a tier the legacy behaviour holds:
    free (gemini) or pro (anthropic) according to settings.AI_PROVIDER.
    """
    from backend.services.ai_tiers import get_tier

    if tier_name is None:
        tier_name = "pro" if settings.AI_PROVIDER == "anthropic" else "free"
    return tier_name, get_tier(tier_name)


def _dispatch(
    messages: list[dict], system: str, max_tokens: int,
    tier: Optional[str] = None,
) -> str:
    tier_name, tier_cfg = _resolve_tier(tier)
    adapter = _ADAPTERS.get(tier_cfg["provider"])
    if adapter is None:
        raise HTTPException(
            status_code=500,
            detail=f"Unknown AI provider '{tier_cfg['provider']}' for tier '{tier_name}'.",
        )

    started = time.monotonic()
    try:
        reply = adapter(messages, system, max_tokens, model_chain=tier_cfg["model_chain"])
    except Exception as exc:
        logger.error(
            "ai_call tier=%s provider=%s prompt_version=%s messages=%d max_tokens=%d "
            "latency_ms=%d status=error error=%s",
            tier_name, tier_cfg["provider"], PROMPT_VERSION, len(messages), max_tokens,
            (time.monotonic() - started) * 1000, type(exc).__name__,
        )
        raise

    logger.info(
        "ai_call tier=%s provider=%s prompt_version=%s messages=%d max_tokens=%d "
        "latency_ms=%d status=ok reply_chars=%d",
        tier_name, tier_cfg["provider"], PROMPT_VERSION, len(messages), max_tokens,
        (time.monotonic() - started) * 1000, len(reply),
    )
    return reply


# ── Public API (unchanged signatures) ─────────────────────────────────────────

def chat(
    messages: list[dict],
    tier: Optional[str] = None,
    mode: str = "profiling",
    context: str = "",
) -> str:
    """
    Send a conversation history to the AI provider resolved from the
    user's plan tier (None = legacy default from settings.AI_PROVIDER).

    Args:
        messages: List of {"role": "user"|"assistant", "content": str}
        tier: plan name from ai_tiers (free/plus/pro)
        mode: "profiling" runs the 9-question risk quiz; "advisor" is the
              free-form education assistant reachable from anywhere.
        context: optional "USER CONTEXT" block appended in advisor mode so
                 answers reference the user's real profile/holdings.

    Returns:
        The assistant's text reply.
    """
    # RAG: today's market summary is appended to the system prompt (fail-open — skipped when empty)
    from backend.services.ai_tiers import get_tier
    from backend.services.chat_context import build_market_context

    base = _ADVISOR_PROMPT if mode == "advisor" else _SYSTEM_PROMPT
    system = base + (context or "") + build_market_context()

    # Generous budget: gemini-2.5-flash spends "thinking" tokens from the same
    # pool, and the final profile summary must not be truncated before the
    # [PROFILE_COMPLETE] marker.
    max_tokens = get_tier(tier)["max_tokens"] if tier else 4096
    return _dispatch(messages, system, max_tokens=max_tokens, tier=tier)


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


def generate_text(prompt: str, system: Optional[str] = None, cache: bool = False) -> str:
    """
    One-shot text generation (used for explainer / REIT prompt calls).

    Args:
        prompt:  The user-turn prompt.
        system:  Optional override system prompt.
        cache:   Daily cache for deterministic calls — quota isn't burned
                 again and again for the same portfolio explanation.

    Returns:
        Generated text.
    """
    cache_key = None
    if cache:
        from backend.services import cache as cache_service

        cache_key = "ai_text:" + hashlib.sha1(
            (prompt + "||" + (system or "")).encode()
        ).hexdigest()
        hit = cache_service.get(cache_key)
        if hit is not None:
            logger.info("ai_text_cache_hit key=%s", cache_key[:20])
            return hit

    reply = _dispatch(
        [{"role": "user", "content": prompt}],
        system or _SYSTEM_PROMPT,
        max_tokens=512,
    )
    if cache_key:
        from backend.services import cache as cache_service

        cache_service.set(cache_key, reply, ttl=60 * 60 * 24)
    return reply
