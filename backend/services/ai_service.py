import anthropic
from pathlib import Path
from typing import Optional
from backend.config import settings

_client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
_SYSTEM_PROMPT = (Path(__file__).parent.parent / "prompts" / "system_prompt.txt").read_text()

CLAUDE_MODEL = "claude-sonnet-4-6"  # Anthropic API: Claude Sonnet 4.6 (released Feb 17, 2026)


def chat(messages: list[dict]) -> str:
    """
    Send a conversation history to Claude and return the assistant reply.

    Args:
        messages: List of {"role": "user"|"assistant", "content": str}

    Returns:
        The assistant's text reply.
    """
    response = _client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=1024,
        system=_SYSTEM_PROMPT,
        messages=messages,
    )
    return response.content[0].text


def generate_text(prompt: str, system: Optional[str] = None) -> str:
    """
    One-shot text generation (used for explainer / REIT prompt calls).

    Args:
        prompt:  The user-turn prompt.
        system:  Optional override system prompt.

    Returns:
        Generated text.
    """
    response = _client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=512,
        system=system or _SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text
