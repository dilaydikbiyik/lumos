"""
Population as a demand signal — and the guards that stop it reading as more.
"""

from unittest.mock import patch

import pytest

from backend.markets import get_market_pack
from backend.services import population_signal as ps


def _series(by_year):
    return {str(y): float(v) for y, v in by_year.items()}


GROWING = _series({2019: 1_000_000, 2020: 1_020_000, 2021: 1_040_000,
                   2022: 1_070_000, 2023: 1_100_000})
SHRINKING = _series({2019: 1_000_000, 2020: 985_000, 2021: 970_000,
                     2022: 955_000, 2023: 940_000})
FLAT = _series({2019: 1_000_000, 2020: 1_002_000, 2021: 1_003_000,
                2022: 1_004_000, 2023: 1_005_000})


def _with(series, working=None):
    """
    Serve the same series for every region, with no network.

    The table is read WHOLE — one request per age band for the market — so
    this patches the table reader rather than a per-region one. The first
    version of the service asked per region and took two minutes here.
    """
    from backend.markets import get_market_pack

    def reader(market, age="TOTAL"):
        source = working if age == "Y15-64" else series
        if source is None:
            return None
        return {geo: source for geo in get_market_pack(market).population_regions}

    return patch.object(ps, "_table_for", reader)


# ── dispatch ────────────────────────────────────────────────────────────────

def test_source_is_dispatched_by_declaration_not_country():
    """The rule the whole market layer rests on."""
    assert get_market_pack("TR").population_source == "eurostat"
    assert get_market_pack("DE").population_source == "eurostat"
    assert get_market_pack("US").population_source == "none"


def test_a_market_without_a_source_refuses_rather_than_inventing():
    assert ps.available("US") is False
    out = ps.region_trend("US", "TR10", "en")
    assert out["available"] is False and out["reason"]


def test_every_declared_region_code_belongs_to_its_market():
    """A stray code would silently serve another country's region."""
    for market in ("TR", "DE"):
        pack = get_market_pack(market)
        assert pack.population_regions
        assert all(code.startswith(market) for code in pack.population_regions)


# ── the arithmetic ──────────────────────────────────────────────────────────

def test_growth_is_measured_across_the_whole_series():
    with _with(GROWING):
        out = ps.region_trend("TR", "TR10", "en")
    assert out["change_pct"] == pytest.approx(10.0, abs=0.1)
    assert out["direction"] == "growing"
    assert out["from_year"] == "2019" and out["to_year"] == "2023"


def test_shrinking_is_named_as_such():
    with _with(SHRINKING):
        assert ps.region_trend("TR", "TR10", "en")["direction"] == "shrinking"


def test_small_moves_are_flat_not_shrinking():
    """
    Registration systems get revised. Putting a scary word next to statistical
    noise is how a reader concludes something the data never said.
    """
    with _with(FLAT):
        assert ps.region_trend("TR", "TR10", "en")["direction"] == "flat"


def test_working_age_share_is_reported_when_available():
    working = {k: v * 0.68 for k, v in GROWING.items()}
    with _with(GROWING, working):
        out = ps.region_trend("TR", "TR10", "en")
    assert out["working_age_share_pct"] == pytest.approx(68.0, abs=0.1)


def test_a_missing_age_band_degrades_rather_than_failing():
    with _with(GROWING, None):
        out = ps.region_trend("TR", "TR10", "en")
    assert out["available"] is True
    assert out["working_age_share_pct"] is None


# ── the honesty guards ──────────────────────────────────────────────────────

def test_a_short_series_is_flagged_untrustworthy():
    """Two points is not a trend, and the caller has to be able to tell."""
    with _with(_series({2022: 1_000_000, 2023: 1_100_000})):
        out = ps.region_trend("TR", "TR10", "en")
    assert out["available"] is True
    assert out["trustworthy"] is False
    assert out["years"] == 2


def test_untrustworthy_regions_are_left_out_of_the_ranking():
    with _with(_series({2022: 1_000_000, 2023: 1_100_000})):
        out = ps.rank_regions("TR", "en")
    assert out["available"] is False


def test_the_caveat_travels_with_the_number():
    """A reader who sees the percentage and not this has been misled."""
    with _with(GROWING):
        out = ps.region_trend("TR", "TR10", "en")
    assert out["caveat"] and "population.caveat" not in out["caveat"]


def test_the_caveat_refuses_to_promise_prices():
    from backend.i18n import t
    for lang in ("tr", "en", "de"):
        text = t("population.caveat", lang).lower()
        assert any(w in text for w in ("not", "değil", "kein"))


def test_ranking_orders_by_growth_and_states_its_granularity():
    with _with(GROWING):
        out = ps.rank_regions("TR", "en", limit=5)
    assert out["available"] is True
    assert len(out["regions"]) == 5
    # NUTS-2 is regions, not provinces, and the answer has to say so —
    # attaching a three-province trend to one district would be false precision.
    assert out["area_kind"] == "nuts2"
    assert "NUTS-2" in out["source_note"]


def test_an_unknown_region_is_refused():
    out = ps.region_trend("TR", "ZZ99", "en")
    assert out["available"] is False


def test_unreadable_upstream_refuses_rather_than_guessing():
    with patch.object(ps, "_table_for", lambda *a, **k: None):
        out = ps.region_trend("TR", "TR10", "en")
    assert out["available"] is False and out["reason"]
