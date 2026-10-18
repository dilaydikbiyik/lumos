"""
"A 500,000 plot, or a 500,000 portfolio?"

The screen most able to mislead, so the tests are about honesty rather than
arithmetic: it must refuse to compare unequal windows, it must charge the
property side the costs only property pays, and it must answer in real terms
on both sides.
"""
from unittest.mock import patch

import pytest

from backend.services import property_vs_portfolio as compare_service

WEIGHTS = {"XU100.IS": 0.6, "GLD": 0.4}


def _fake_backtest(total_return_pct=50.0):
    # Takes **kwargs so the fake cannot silently reject an argument the real
    # function gained. It lagged behind `market` and the resulting TypeError
    # was swallowed by compare()'s `except Exception`, which reported the
    # portfolio side as "unavailable" — a signature mismatch arriving as a
    # plausible-looking empty result rather than an error.
    return lambda weights, budget, period="5y", **kwargs: {
        "total_return_pct": total_return_pct,
    }


def test_it_refuses_to_compare_two_different_windows():
    """
    The failure this prevents: a region with three years of history set
    beside a five-year portfolio backtest, presented as one answer. The
    shorter side is not a smaller number, it is a different question.
    """
    with patch.object(compare_service, "_region_growth_pct",
                      return_value=(30.0, 2.0)):          # only 2 of 5 years
        result = compare_service.compare(
            amount=500_000, region_code="34", weights=WEIGHTS,
            period="5y", market="TR", lang="en")

    assert result["available"] is False
    assert "5" in result["reason"] and "2" in result["reason"]


def test_an_unknown_region_says_so_rather_than_guessing():
    with patch.object(compare_service, "_region_growth_pct", return_value=None):
        result = compare_service.compare(
            amount=500_000, region_code="ZZ", weights=WEIGHTS, market="TR", lang="en")
    assert result["available"] is False


def test_a_missing_portfolio_side_shows_nothing_rather_than_one_side():
    """
    A one-sided comparison is worse than no comparison.

    The simulated failure is a MarketDataError, because that is what "market
    data down" actually raises: market_data raises it when the provider
    returns nothing usable, portfolio_series when the tickers share no
    history. It used to be a RuntimeError, which production never produces
    here — the old `except Exception` was broad enough that the test could
    be wrong about the real system and still pass.
    """
    from backend.exceptions import MarketDataError

    with patch.object(compare_service, "_region_growth_pct", return_value=(60.0, 5.0)), \
         patch("backend.services.backtest.run_backtest",
               side_effect=MarketDataError("yfinance returned no usable data")):
        result = compare_service.compare(
            amount=500_000, region_code="34", weights=WEIGHTS, market="TR", lang="en")

    assert result["available"] is False


def test_the_property_side_pays_the_costs_only_it_pays():
    """
    Transfer tax, commission and upkeep come off property and not off the
    portfolio. Leaving them out is how property wins an argument it might
    not deserve.
    """
    with patch.object(compare_service, "_region_growth_pct", return_value=(60.0, 5.0)), \
         patch("backend.services.backtest.run_backtest", _fake_backtest(60.0)):
        result = compare_service.compare(
            amount=500_000, region_code="34", weights=WEIGHTS,
            period="5y", market="TR", lang="en")

    assert result["available"] is True
    prop, folio = result["property"], result["portfolio"]

    assert prop["entry_costs"] > 0
    assert prop["upkeep_paid"] > 0
    assert prop["rent_received"] > 0
    # Identical headline growth, but property carried costs the portfolio did
    # not — so it cannot come out ahead on price appreciation alone.
    assert prop["index_growth_pct"] == folio["nominal_return_pct"] == 60.0
    assert result["assumptions"]["transfer_tax_pct"] > 0


def test_both_sides_are_reported_in_real_terms():
    """
    In a high-inflation market, nominal numbers make both sides look like
    wins. Deflating only one of them would be worse than deflating neither.
    """
    with patch.object(compare_service, "_region_growth_pct", return_value=(60.0, 5.0)), \
         patch("backend.services.backtest.run_backtest", _fake_backtest(60.0)), \
         patch("backend.services.assumptions.annual_inflation_pct", return_value=30.0):
        result = compare_service.compare(
            amount=500_000, region_code="34", weights=WEIGHTS,
            period="5y", market="TR", lang="en")

    for side in ("property", "portfolio"):
        assert result[side]["real_return_pct"] < result[side]["return_pct"], side
        assert result[side]["real_value"] < result[side]["value"], side


def test_the_rent_yield_offered_for_comparison_is_net_not_gross():
    """
    A gross rental yield beside a dividend yield is not like for like, and
    gross is the figure agents quote.
    """
    for market in ("TR", "US", "DE"):
        result = compare_service.yield_comparison(market=market, lang="en")
        assert result["net_rental_yield_pct"] == pytest.approx(
            result["gross_rental_yield_pct"] - result["annual_upkeep_pct"], abs=0.01)
        assert result["net_rental_yield_pct"] < result["gross_rental_yield_pct"]
        assert "NET" in result["note"] or "net" in result["note"]


def test_the_yield_note_names_the_upkeep_it_deducted():
    result = compare_service.yield_comparison(market="US", lang="en")
    assert str(result["annual_upkeep_pct"]) in result["note"]


def test_a_broken_call_crashes_instead_of_claiming_missing_data():
    """
    The handler used to be `except Exception`, which could not tell "the
    provider has no history" from "this code is broken" — and answered both
    with a calm, plausible "the portfolio side is unavailable".

    It was found the honest way: the fake in this file lagged behind
    run_backtest gaining a `market` argument, and the resulting TypeError
    came back as missing data. A programming mistake in the costume of an
    empty provider is the hardest kind to find, because nothing looks
    wrong on the screen.

    So anything that is not a MarketDataError must now propagate.
    """
    def broken(*args, **kwargs):
        raise TypeError("run_backtest() got an unexpected keyword argument")

    with patch.object(compare_service, "_region_growth_pct", return_value=(60.0, 5.0)), \
         patch("backend.services.backtest.run_backtest", broken):
        with pytest.raises(TypeError):
            compare_service.compare(
                amount=500_000, region_code="34", weights=WEIGHTS,
                period="5y", market="TR", lang="en")
