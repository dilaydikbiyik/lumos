"""
"Is this listing a fair price?"

The tests are mostly about REFUSING. A price index and a price level are
different data products, and only a level can answer this question — so in
two of three markets the correct output is "cannot say", and producing a
number there would cost somebody a fair property or an unfair price.
"""
from unittest.mock import patch

import pytest

from backend.services import listing_eval


def _level(name="İstanbul", per_m2=50_000.0):
    return lambda code, market, lang: (name, per_m2)


def test_a_market_with_only_an_index_refuses_rather_than_inventing_a_verdict():
    """
    Dividing an asking price by an index number produces a number that means
    nothing. The US and German area data are indices.
    """
    for market in ("US", "DE"):
        result = listing_eval.evaluate(
            area_code="TX", size_m2=120, asking_price=400_000,
            market=market, lang="en")
        assert result["available"] is False, market
        assert "INDEX" in result["reason"] or "index" in result["reason"]


def test_the_refusal_explains_why_rather_than_saying_no_data():
    """
    "No data" and "the data we have cannot answer this" are different, and
    only one of them is fixable by waiting.
    """
    result = listing_eval.evaluate(area_code="TX", size_m2=100,
                                   asking_price=100_000, market="US", lang="en")
    assert "moved" in result["reason"]


@pytest.mark.parametrize("price,expected", [
    (50_000 * 100 * 0.70, "below"),        # 30% under
    (50_000 * 100 * 1.00, "fair"),
    (50_000 * 100 * 1.10, "fair"),         # inside the noise band
    (50_000 * 100 * 1.25, "above"),
    (50_000 * 100 * 1.60, "well_above"),
])
def test_the_verdict_follows_the_gap(price, expected):
    with patch.object(listing_eval, "_area_average_per_m2", side_effect=_level()):
        result = listing_eval.evaluate(area_code="IST", size_m2=100,
                                       asking_price=price, market="TR", lang="en")
    assert result["verdict"] == expected, result["delta_pct"]


def test_being_slightly_under_the_average_is_not_called_a_bargain():
    """
    Within a fifth of the average is noise between one street and the next.
    Calling that a deal is how an app talks somebody into a purchase.
    """
    with patch.object(listing_eval, "_area_average_per_m2", side_effect=_level()):
        result = listing_eval.evaluate(area_code="IST", size_m2=100,
                                       asking_price=50_000 * 100 * 0.90,
                                       market="TR", lang="en")
    assert result["verdict"] == "fair"


def test_a_cheap_listing_is_treated_as_a_question_not_a_win():
    with patch.object(listing_eval, "_area_average_per_m2", side_effect=_level()):
        result = listing_eval.evaluate(area_code="IST", size_m2=100,
                                       asking_price=50_000 * 100 * 0.60,
                                       market="TR", lang="en")
    assert result["verdict"] == "below"
    assert "reason" in result["verdict_text"].lower()


def test_the_caveat_travels_with_the_verdict():
    """
    A province average against one property is the weakness of this whole
    comparison. It belongs beside the number, not in a footnote.
    """
    with patch.object(listing_eval, "_area_average_per_m2", side_effect=_level()):
        result = listing_eval.evaluate(area_code="IST", size_m2=100,
                                       asking_price=5_000_000, market="TR", lang="en")
    assert result["caveat"]
    assert "İstanbul" in result["caveat"]


def test_missing_numbers_are_asked_for_rather_than_assumed():
    for size, price in ((0, 100), (100, 0), (None, 100), (100, None)):
        result = listing_eval.evaluate(area_code="IST", size_m2=size,
                                       asking_price=price, market="TR", lang="en")
        assert result["available"] is False


def test_every_verdict_ships_with_the_questions_to_ask():
    with patch.object(listing_eval, "_area_average_per_m2", side_effect=_level()):
        result = listing_eval.evaluate(area_code="IST", size_m2=100,
                                       asking_price=5_000_000, market="TR", lang="en")
    assert len(result["questions"]) >= 5
    assert all(q and not q.startswith("listing.") for q in result["questions"])


@pytest.mark.parametrize("lang", ["tr", "en", "de"])
def test_it_answers_in_the_readers_language(lang):
    with patch.object(listing_eval, "_area_average_per_m2", side_effect=_level()):
        result = listing_eval.evaluate(area_code="IST", size_m2=100,
                                       asking_price=8_000_000, market="TR", lang=lang)
    assert not result["verdict_text"].startswith("listing.")
    assert not result["caveat"].startswith("listing.")
