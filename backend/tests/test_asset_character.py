"""
"Does this asset match your patience?"

The backtest already measured how far each asset fell, how long it took to
come back and how long it went nowhere — and none of it was ever shown. The
judgment here is about BEHAVIOUR rather than returns, because the way people
lose money in a good asset is selling it during the part nobody warned them
about.
"""
import pytest

from backend.services.asset_character import describe_all, fit

STEADY = {"max_drawdown_pct": -8.0, "longest_stagnation_months": 3.0,
          "recovery_trading_days": 20}
DEEP = {"max_drawdown_pct": -55.0, "longest_stagnation_months": 6.0,
        "recovery_trading_days": 300}
FLAT = {"max_drawdown_pct": -12.0, "longest_stagnation_months": 26.0,
        "recovery_trading_days": 40}
SLOW = {"max_drawdown_pct": -30.0, "longest_stagnation_months": 4.0,
        "recovery_trading_days": 1200}      # ~57 months


def test_a_fall_deeper_than_the_reader_said_they_could_take_is_a_mismatch():
    result = fit(DEEP, loss_tolerance="low", time_horizon="long", lang="en")
    assert result["verdict"] == "mismatch"
    assert "55" in result["reason"] and "20" in result["reason"]


def test_the_same_asset_can_suit_a_different_reader():
    """
    The verdict is about the PERSON, not the asset. A blanket "risky" label
    would be the horoscope version of this.
    """
    cautious = fit(DEEP, loss_tolerance="low", time_horizon="long", lang="en")
    bold = fit(DEEP, loss_tolerance="high", time_horizon="long", lang="en")
    assert cautious["verdict"] == "mismatch"
    assert bold["verdict"] != "mismatch"


def test_a_recovery_longer_than_the_horizon_is_a_mismatch():
    """
    Needing the money before the price comes back is what turns a paper loss
    into a real one.
    """
    result = fit(SLOW, loss_tolerance="high", time_horizon="short", lang="en")
    assert result["verdict"] == "mismatch"
    assert result["recovery_months"] == pytest.approx(57.1, abs=0.5)


def test_a_long_flat_stretch_is_called_out_even_when_the_fall_was_mild():
    """
    The number nobody quotes. A crash is frightening and brief; years of
    going nowhere is what actually makes people give up, and it looks like
    nothing on a chart.
    """
    result = fit(FLAT, loss_tolerance="high", time_horizon="long", lang="en")
    assert result["verdict"] == "demanding"
    assert "26" in result["reason"]


def test_a_steady_asset_is_said_to_be_steady():
    result = fit(STEADY, loss_tolerance="low", time_horizon="medium", lang="en")
    assert result["verdict"] == "comfortable"


def test_missing_history_says_so_instead_of_guessing():
    result = fit({"max_drawdown_pct": None}, lang="en")
    assert result["verdict"] == "unknown"


def test_an_asset_that_never_recovered_is_not_treated_as_instant_recovery():
    """
    `recovery_trading_days: None` means "never came back inside the window".
    Reading that as zero would make the worst case look like the best one.
    """
    never = {"max_drawdown_pct": -25.0, "longest_stagnation_months": 5.0,
             "recovery_trading_days": None}
    result = fit(never, loss_tolerance="high", time_horizon="short", lang="en")
    assert result["recovery_months"] is None
    assert result["verdict"] != "comfortable"


@pytest.mark.parametrize("lang", ["tr", "en", "de"])
def test_every_verdict_speaks_the_readers_language(lang):
    for metrics in (STEADY, DEEP, FLAT, SLOW):
        result = fit(metrics, loss_tolerance="medium", time_horizon="medium", lang=lang)
        assert result["reason"], (lang, metrics)
        assert not result["reason"].startswith("character."), result["reason"]


def test_describe_all_keeps_the_original_metrics():
    """The card shows the numbers as well as the verdict."""
    enriched = describe_all({"SPY": STEADY}, loss_tolerance="low",
                            time_horizon="medium", lang="en")
    assert enriched["SPY"]["max_drawdown_pct"] == STEADY["max_drawdown_pct"]
    assert enriched["SPY"]["character"]["verdict"] == "comfortable"
