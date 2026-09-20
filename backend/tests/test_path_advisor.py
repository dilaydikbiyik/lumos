"""
The path suggestion for someone who answered "not sure yet".

Rule-based on purpose. The point of these tests is that the suggestion is
DEFENSIBLE — every output traceable to an input the user gave — because the
product promise is that a beginner is never told what to do without being
told why.
"""
import pytest

from backend.services import path_advisor
from backend.services.path_advisor import suggest

TR_THRESHOLD = 1_000_000.0


def test_a_short_horizon_keeps_someone_out_of_property():
    """
    Purchase costs are paid up front and amortise over years. Under five, the
    honest answer is "not yet" — not "buy a cheaper flat".
    """
    result = suggest(horizon="kisa", budget=5_000_000, entry_threshold=TR_THRESHOLD)

    assert result.path == "stocks"
    assert "path.reason.short_horizon" in result.reasons


def test_a_big_budget_does_not_override_a_short_horizon():
    """
    Being able to afford it is not the same as it being the right instrument.
    Budget must not be allowed to outvote the horizon.
    """
    result = suggest(horizon=2, budget=50_000_000, entry_threshold=TR_THRESHOLD)
    assert result.path == "stocks"


def test_a_long_horizon_with_the_means_opens_both_worlds():
    result = suggest(horizon="uzun", budget=3_000_000, entry_threshold=TR_THRESHOLD)

    assert result.path == "hybrid"
    assert "path.reason.long_horizon" in result.reasons
    assert "path.reason.above_entry" in result.reasons


def test_below_the_entry_bar_property_is_not_offered_as_if_it_were_available():
    """
    Suggesting property to someone who cannot reach the entry bar wastes their
    time and reads as the app not listening.
    """
    result = suggest(horizon="uzun", budget=50_000, entry_threshold=TR_THRESHOLD)

    assert result.path == "stocks"
    assert "path.reason.below_entry" in result.reasons


def test_the_entry_bar_comes_from_the_market_not_from_a_constant():
    """
    "Enough to buy a flat" is a fact about a country. The same budget must be
    able to clear the bar in one market and miss it in another.
    """
    from backend.markets import get_market_pack

    budget = 90_000.0
    us = suggest(horizon="uzun", budget=budget,
                 entry_threshold=get_market_pack("US").property_entry_threshold)
    de = suggest(horizon="uzun", budget=budget,
                 entry_threshold=get_market_pack("DE").property_entry_threshold)

    assert us.path == "hybrid"          # 90k clears the US bar (80k)
    assert de.path == "stocks"          # and misses Germany's (100k)


def test_not_understanding_it_steers_away_from_the_harder_world_to_learn_in():
    """
    Deeds, notaries and transfer taxes are a harder first classroom than a
    single fund purchase. The fear someone named is real information.
    """
    result = suggest(horizon="uzun", budget=5_000_000,
                     primary_fear="anlamiyorum", entry_threshold=TR_THRESHOLD)

    assert result.path == "stocks"
    assert "path.reason.fear_complexity" in result.reasons


def test_an_inflation_fear_is_acknowledged_even_when_the_answer_is_stocks():
    """
    Property is what people reach for against inflation. Ignoring that named
    fear would read as the app not having heard it.
    """
    result = suggest(horizon="kisa", budget=5_000_000,
                     primary_fear="param_eriyor", entry_threshold=TR_THRESHOLD)

    assert result.path == "stocks"
    assert "path.reason.fear_inflation" in result.reasons


def test_no_signal_says_so_instead_of_inventing_a_rationale():
    result = suggest()

    assert result.confident is False
    assert result.reasons == ["path.reason.no_signal"]


def test_every_suggestion_carries_at_least_one_reason():
    """
    A suggestion with no reason is an instruction. The whole design is that a
    beginner can disagree with the reasoning rather than obey the output.
    """
    for horizon in (None, "kisa", "orta", "uzun", 1, 7, 30):
        for budget in (None, 0, 50_000, 5_000_000):
            for fear in (None, "anlamiyorum", "param_eriyor", "batiririm"):
                result = suggest(horizon=horizon, budget=budget,
                                 primary_fear=fear, entry_threshold=TR_THRESHOLD)
                assert result.reasons, (horizon, budget, fear)
                assert result.path in {"stocks", "real_estate", "hybrid"}


@pytest.mark.parametrize("raw,expected", [
    ("kisa", 2), ("kısa", 2), ("short", 2),
    ("orta", 6), ("medium", 6),
    ("uzun", 15), ("long", 15),
    (7, 7.0), ("7", 7.0),
    (None, None), ("whenever", None), ("", None),
])
def test_horizon_is_read_in_whatever_shape_the_profile_stored_it(raw, expected):
    """The quiz has stored horizons as words and as numbers over time."""
    assert path_advisor._years(raw) == expected


def test_the_endpoint_answers_in_the_readers_language(client):
    """
    The reasons are sentences, not keys — the engine writes prose here the way
    every other engine in the app does.
    """
    turkish = client.get("/api/v1/users/me/path-suggestion",
                         headers={"X-Lumos-Lang": "tr"}).json()
    english = client.get("/api/v1/users/me/path-suggestion",
                         headers={"X-Lumos-Lang": "en"}).json()

    assert turkish["path"] in {"stocks", "real_estate", "hybrid"}
    assert turkish["reasons"] and english["reasons"]
    # Sentences, not i18n keys leaking through.
    assert not any(r.startswith("path.reason.") for r in turkish["reasons"])
    assert turkish["reasons"] != english["reasons"]
