"""
The risk quiz served as data.

The property that matters is that the quiz and the SCHEMA cannot drift. The
nine questions used to live in a prompt file as prose; nothing connected
them to `RiskProfileAnswers` except somebody remembering. Now an answer set
built from the questions has to be a valid profile, and a required field
with no question would mean a quiz that cannot be completed.
"""
import pytest

from backend.schemas.user_profile import RiskProfileAnswers
from backend.services import quiz_questions


def _schema_fields():
    return RiskProfileAnswers.model_fields


def test_every_schema_field_has_a_question():
    """
    A field the profile needs and the quiz never asks for is a field that
    silently stays empty — and the risk score is computed from these.
    """
    asked = {q["field"] for q in quiz_questions.questions("en")}
    missing = set(_schema_fields()) - asked
    assert not missing, f"the quiz never asks for: {sorted(missing)}"


def test_no_question_asks_for_something_the_schema_rejects():
    asked = {q["field"] for q in quiz_questions.questions("en")}
    extra = asked - set(_schema_fields())
    assert not extra, f"asked but unusable: {sorted(extra)}"


def test_required_on_screen_matches_required_in_the_schema():
    """
    A question the schema lets you skip must be skippable on screen, or the
    form is stricter than the model it feeds — and people abandon forms that
    demand things they do not have.
    """
    fields = _schema_fields()
    for question in quiz_questions.questions("en"):
        schema_required = fields[question["field"]].is_required()
        assert question["required"] == schema_required, question["field"]


def test_every_choice_offers_only_values_the_schema_accepts():
    """
    An option the schema rejects means a completed quiz that fails to save,
    discovered by the user at the last step.
    """
    import typing

    def literal_values(annotation) -> set:
        """Every Literal value in an annotation, through Optional[...] too."""
        if typing.get_origin(annotation) is typing.Literal:
            return set(typing.get_args(annotation))
        found = set()
        for arg in typing.get_args(annotation):
            found |= literal_values(arg)
        return found

    fields = _schema_fields()
    for question in quiz_questions.questions("en"):
        if question["type"] != "choice":
            continue
        allowed = literal_values(fields[question["field"]].annotation)
        assert allowed, f"{question['field']} is a choice but the schema has no Literal"
        offered = {o["value"] for o in question["options"]}
        assert offered <= allowed, (question["field"], offered - allowed)


def test_a_completed_quiz_validates_as_a_profile():
    """End to end: answer every question, get a valid profile."""
    answers = {}
    for question in quiz_questions.questions("en"):
        if question["type"] == "choice":
            answers[question["field"]] = question["options"][0]["value"]
        elif question["field"] == "age":
            answers[question["field"]] = 34
        else:
            answers[question["field"]] = 100_000

    profile = RiskProfileAnswers(**answers)
    assert profile.budget == 100_000


def test_only_the_required_answers_are_needed():
    answers = {}
    for question in quiz_questions.questions("en"):
        if not question["required"]:
            continue
        answers[question["field"]] = (
            question["options"][0]["value"] if question["type"] == "choice" else 50_000
        )
    assert RiskProfileAnswers(**answers).budget == 50_000


@pytest.mark.parametrize("lang", ["tr", "en", "de"])
def test_every_question_speaks_the_readers_language(lang):
    for question in quiz_questions.questions(lang):
        assert question["title"] and not question["title"].startswith("quiz.q."), question["field"]
        assert question["help"] and not question["help"].startswith("quiz.q."), question["field"]
        for option in question.get("options", []):
            assert option["label"] and not option["label"].startswith("risk."), option
            assert option["help"] and not option["help"].startswith("quiz.q."), option


def test_option_labels_are_the_risk_engines_own():
    """
    The score breakdown prints "your answer" from `risk.*`. A quiz that
    worded the options differently would show somebody one phrase while
    asking and another while explaining the score it produced.
    """
    from backend.i18n import t

    for question in quiz_questions.questions("tr"):
        for option in question.get("options", []):
            prefix = quiz_questions._LABEL_PREFIX.get(
                question["field"], f"risk.{question['field']}")
            assert option["label"] == t(f"{prefix}.{option['value']}", "tr")


def test_the_endpoint_returns_the_markets_currency(client):
    body = client.get("/api/v1/profile/questions").json()
    assert body["questions"] and body["currency"]
    assert len(body["questions"]) == len(_schema_fields())
