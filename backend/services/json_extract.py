"""
Pull a JSON object out of a language model's reply.

Models wrap JSON in markdown fences, prefix it with prose, and sometimes emit
reasoning tokens first. Every caller that reads structured output from one had
grown its own ladder of regexes for this, and they had the same flaw.

The flaw, concretely. The old ladder's second rung was `\\{[^{}]+\\}` — "a
brace block containing no braces". Against a NESTED object preceded by any
prose, that does not match the object; it matches the first INNER one:

    Here you go:
    {"age": 30, "goal": {"type": "retirement", "years": 20}}

returned `{"type": "retirement", "years": 20}`. Not a parse failure — a
confident, wrong answer, with the user's actual profile discarded. The third
rung, `\\{.*?\\}`, is non-greedy and truncates nested objects the same way.

A regex cannot match balanced braces. `raw_decode` can: it is the parser
itself, so it understands nesting, strings and escapes, and it reports where
the value ended. Scan for `{`, try to decode there, take the first one that
yields a complete object.
"""

import json
import re
from typing import Any, Optional

# Leading/trailing markdown fences, with or without a language tag.
_FENCE = re.compile(r"^```(?:json)?\s*|\s*```$", re.MULTILINE)
# Reasoning blocks some models emit before the answer. They can contain
# braces, which is exactly what misled the old ladder.
_THINK = re.compile(r"<think(?:ing)?>.*?</think(?:ing)?>", re.DOTALL | re.IGNORECASE)

_decoder = json.JSONDecoder()


def _first_value(raw: str):
    """
    The first COMPLETE JSON value in the text, with its container intact.

    Scanning for `{` and decoding there is not quite enough: against
    `[{"age": 30}]` it finds the brace INSIDE the array and returns the
    element, having silently discarded the fact that the model answered with
    a list. Decoding from whichever of `{` or `[` comes first keeps the
    top-level shape, so the caller decides what to do with it instead of this
    function quietly descending.
    """
    if not raw or not isinstance(raw, str):
        return None

    text = _THINK.sub(" ", raw)
    text = _FENCE.sub("", text.strip()).strip()

    for candidate in (text, raw):
        for index, char in enumerate(candidate):
            if char not in "{[":
                continue
            try:
                value, _ = _decoder.raw_decode(candidate, index)
            except ValueError:
                continue          # not a complete value here — keep scanning
            return value
    return None


def extract_json_object(raw: str) -> Optional[dict[str, Any]]:
    """
    The JSON OBJECT a model meant to return, or None.

    A single-element array is unwrapped: models wrap an answer in a list often
    enough, and the list IS the answer, just in a box. Anything else — a bare
    list of several items, a number, a string — is not the object the caller
    asked for, and returning something plausible from inside it is the exact
    failure this module exists to prevent.
    """
    value = _first_value(raw)
    if isinstance(value, dict):
        return value
    if isinstance(value, list) and len(value) == 1 and isinstance(value[0], dict):
        return value[0]
    return None


def extract_json_array(raw: str) -> Optional[list]:
    """The first complete JSON ARRAY, for callers that expect a list."""
    value = _first_value(raw)
    return value if isinstance(value, list) else None
