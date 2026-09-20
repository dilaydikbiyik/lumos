"""
Pulling JSON out of a model reply.

Modelled on BUG-005 in the across2aim review: an AI-written integration parsed
an API response with a chain of string manipulations, and the review's warning
was that a nested object or an unexpected trailing character would make it
parse the WRONG thing — silently.

Lumos had the same defect, in the code that builds a user's risk profile. The
old ladder's second rung was `\\{[^{}]+\\}`, "a brace block containing no
braces", which against a nested object preceded by prose matched the INNER
object. `extract_profile` then returned that as the user's profile: not an
error, a confident wrong answer, feeding the risk score and the whole
portfolio built from it.
"""
import pytest

from backend.services.json_extract import extract_json_array, extract_json_object


def test_the_nested_object_bug_that_returned_the_wrong_answer():
    """The exact shape that used to return the inner object."""
    raw = 'Here you go:\n{"age": 30, "goal": {"type": "retirement", "years": 20}}\ndone'

    parsed = extract_json_object(raw)

    assert parsed == {"age": 30, "goal": {"type": "retirement", "years": 20}}
    # The specific wrong answer the old code gave, named so the regression is
    # unmistakable if anyone reaches for a regex again.
    assert parsed != {"type": "retirement", "years": 20}


@pytest.mark.parametrize("raw,expected", [
    ('{"age": 30}', {"age": 30}),
    ('```json\n{"age": 30}\n```', {"age": 30}),
    ('```\n{"age": 30}\n```', {"age": 30}),
    ('Sure!\n{"age": 30}\nHope that helps.', {"age": 30}),
    ('{"a": {"b": {"c": {"d": 1}}}}', {"a": {"b": {"c": {"d": 1}}}}),
    # A brace inside a string is not structure. A regex cannot know that;
    # the parser does.
    ('{"note": "a } brace", "age": 30}', {"note": "a } brace", "age": 30}),
    ('{"note": "an escaped \\" quote", "age": 30}',
     {"note": 'an escaped " quote', "age": 30}),
    # Reasoning tokens, which contain braces of their own.
    ('<think>maybe {"a": 1}</think>\n{"age": 30, "meta": {"a": 1}}',
     {"age": 30, "meta": {"a": 1}}),
])
def test_it_finds_the_object_whatever_the_model_wrapped_it_in(raw, expected):
    assert extract_json_object(raw) == expected


@pytest.mark.parametrize("raw", [
    "", None, "no json at all", "[1, 2, 3]", '[{"a": 1}, {"b": 2}]',
    '{"age": 30, "goal": {"type":',        # truncated mid-object
    "{{{{", "}{",
])
def test_it_returns_none_rather_than_guessing(raw):
    """
    A wrong object is worse than no object: the caller can handle None, and
    it cannot detect a plausible-looking profile that is not the user's.
    """
    assert extract_json_object(raw) is None


def test_a_single_element_array_is_unwrapped_but_a_longer_one_is_not():
    """
    Models wrap an answer in a list often enough that the list IS the answer,
    just in a box. Several items is a different claim, and picking one of them
    would be the guessing this module exists to avoid.
    """
    assert extract_json_object('[{"age": 30}]') == {"age": 30}
    assert extract_json_object('[{"age": 30}, {"age": 41}]') is None
    assert extract_json_object('[1, 2, 3]') is None
    assert extract_json_array('[{"age": 30}]') == [{"age": 30}]


def test_arrays_get_the_same_treatment():
    raw = '```json\n[{"headline": "a"}, {"headline": "b"}]\n```'
    assert extract_json_array(raw) == [{"headline": "a"}, {"headline": "b"}]
    assert extract_json_array("not json") is None


def test_extract_profile_keeps_the_outer_object(client):
    """
    End to end through the real function, because the unit above would still
    pass if `extract_profile` stopped calling it.
    """
    from unittest.mock import patch

    from backend.services import ai_service

    reply = ('Certainly — here is the profile:\n'
             '{"age": 41, "budget": 250000, "goal": {"kind": "house", "years": 7}}')

    with patch.object(ai_service, "_dispatch", return_value=reply):
        parsed = ai_service.extract_profile([{"role": "user", "content": "hi"}])

    assert parsed["age"] == 41
    assert parsed["budget"] == 250000


def test_extract_profile_does_not_log_the_users_financial_details(client, caplog):
    """
    A parse failure logged `raw_output=%r` — the model's extracted profile,
    meaning the user's age, income and debts, copied into the log stream.
    """
    import logging
    from unittest.mock import patch

    from fastapi import HTTPException

    from backend.services import ai_service

    secret = "monthly_income 91000 and debts of 45000"
    caplog.set_level(logging.DEBUG)
    with patch.object(ai_service, "_dispatch", return_value=f"sorry, no JSON. {secret}"):
        with pytest.raises(HTTPException):
            ai_service.extract_profile([{"role": "user", "content": "hi"}])

    logged = "\n".join(r.getMessage() for r in caplog.records)
    assert "91000" not in logged and "45000" not in logged, logged
