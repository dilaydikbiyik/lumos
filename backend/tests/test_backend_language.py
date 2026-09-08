"""
The backend speaks the reader's language.

A user who picks English used to get an English shell around Turkish
sentences: the risk factors, the asset roles, the drift verdict and the
panic facts all came from the backend as Turkish literals. These tests pin
the contract that closed that gap — X-Lumos-Lang in, that language out.

Language and market stay independent throughout: the market decides WHAT is
recommended, the language decides how it is WORDED.
"""

import pytest

from backend.i18n import _C, FALLBACK, t
from backend.services.drift import compute_drift
from backend.services.health_score import compute_health
from backend.services.portfolio_engine import build_portfolio
from backend.services.risk_engine import compute_risk_score
from backend.schemas.user_profile import RiskProfileAnswers

LANGS = ("tr", "en", "de")

ANSWERS = RiskProfileAnswers(
    budget=100_000,
    time_horizon="medium",
    loss_tolerance="medium",
    goal="growth",
    experience="beginner",
)


def test_catalogue_is_complete_in_every_language():
    """A missing key is invisible in production — it just falls back."""
    missing = {
        lang: sorted(k for k, v in _C.items() if lang not in v)
        for lang in LANGS
    }
    assert missing == {lang: [] for lang in LANGS}


def test_catalogue_placeholders_match_across_languages():
    """A translation that drops {score} renders a sentence with a hole in it."""
    import re

    for key, entry in _C.items():
        reference = set(re.findall(r"\{(\w+)\}", entry["tr"]))
        for lang in ("en", "de"):
            assert set(re.findall(r"\{(\w+)\}", entry[lang])) == reference, key


def test_unknown_key_returns_the_key_rather_than_raising():
    assert t("no.such.key", "en") == "no.such.key"


def test_fallback_chain_prefers_english_over_turkish_for_german():
    assert FALLBACK["de"] == ("en", "tr")


@pytest.mark.parametrize("lang", LANGS)
def test_risk_summary_and_factors_follow_the_language(lang):
    profile = compute_risk_score(ANSWERS, lang)
    assert profile.label == t(f"risk.label.{'balanced'}", lang)
    # German capitalises nouns, so the goal appears as written in the
    # catalogue there; Turkish and English lowercase it mid-sentence.
    goal = t("risk.goal.growth", lang)
    assert (goal if lang == "de" else goal.lower()) in profile.summary
    for factor in profile.factors:
        assert factor.explanation
        assert factor.factor


def test_risk_score_itself_is_language_independent():
    """Wording changes; the number must not."""
    scores = {compute_risk_score(ANSWERS, lang).risk_score for lang in LANGS}
    assert len(scores) == 1


@pytest.mark.parametrize("lang", LANGS)
def test_portfolio_rationale_follows_the_language(lang):
    portfolio = build_portfolio(risk_score=5.0, budget=100_000, market="TR", lang=lang)
    assert portfolio.allocations
    for allocation in portfolio.allocations:
        assert allocation.explanation
    formula = portfolio.metadata["allocation_logic"]["formula"]
    assert formula == t("formula.allocation", lang)


def test_defensive_asset_name_is_translated_not_a_key():
    """The cash sleeve carries a key internally; the reader must never see it."""
    for lang in LANGS:
        portfolio = build_portfolio(risk_score=2.0, budget=100_000, market="TR", lang=lang)
        names = [a.name for a in portfolio.allocations]
        assert not any(n.startswith("asset.") for n in names), names
        assert t("asset.cash.name", lang) in names


def test_weights_are_identical_across_languages():
    """Translation is presentation. If it moves a weight, something is wrong."""
    weights = {
        lang: {
            a.ticker: a.weight
            for a in build_portfolio(risk_score=6.0, budget=50_000,
                                     market="TR", lang=lang).allocations
        }
        for lang in LANGS
    }
    assert weights["tr"] == weights["en"] == weights["de"]


@pytest.mark.parametrize("lang", LANGS)
def test_health_notes_follow_the_language(lang):
    assert compute_health({}, lang)["notes"] == [t("health.none", lang)]

    concentrated = compute_health({"stock": 100.0}, lang)
    assert t("health.concentrated", lang) in concentrated["notes"]


@pytest.mark.parametrize("lang", LANGS)
def test_drift_verdict_follows_the_language(lang):
    empty = compute_drift([], {}, [], lang)
    assert empty == {"available": False, "reason": t("drift.none", lang)}


@pytest.mark.parametrize("lang,expected", [
    ("tr", "Muhafazakâr"), ("en", "Conservative"), ("de", "Konservativ"),
])
def test_risk_label_wording(lang, expected):
    assert compute_risk_score(
        ANSWERS.model_copy(update={"time_horizon": "short",
                                   "loss_tolerance": "low",
                                   "goal": "preservation",
                                   "experience": "none"}),
        lang,
    ).label == expected


def test_profile_endpoint_honours_the_language_header(client):
    body = {
        "budget": 100_000,
        "time_horizon": "medium",
        "loss_tolerance": "medium",
        "goal": "growth",
        "experience": "beginner",
    }
    english = client.post("/profile", json=body, headers={"X-Lumos-Lang": "en"}).json()
    german = client.post("/profile", json=body, headers={"X-Lumos-Lang": "de"}).json()
    turkish = client.post("/profile", json=body).json()

    assert english["label"] == "Balanced"
    assert german["label"] == "Ausgewogen"
    assert turkish["label"] == "Dengeli"
    assert english["risk_score"] == german["risk_score"] == turkish["risk_score"]


def test_unknown_language_header_falls_back_to_turkish(client):
    body = {
        "budget": 100_000,
        "time_horizon": "medium",
        "loss_tolerance": "medium",
        "goal": "growth",
        "experience": "beginner",
    }
    res = client.post("/profile", json=body, headers={"X-Lumos-Lang": "fr"})
    assert res.json()["label"] == "Dengeli"


def test_fear_reassurance_follows_the_language(client):
    english = client.patch("/users/me/fear-check-in",
                           json={"primary_fear": "kandirilirim"},
                           headers={"X-Lumos-Lang": "en"}).json()
    assert english["reassurance"] == t("fear.kandirilirim", "en")
    assert "komisyon" not in english["reassurance"]


def test_readiness_milestones_are_keys_not_sentences(client):
    """The client owns the wording, so the checklist can be translated."""
    milestones = client.get("/users/me/readiness").json()["milestones"]
    assert set(milestones) == {
        "risk_profile", "path_chosen", "fear_shared",
        "first_holding", "three_holdings",
    }
