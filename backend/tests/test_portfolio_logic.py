"""
Portfolio engine v4 logic tests — keeping the realism filter alive in code:

1. The risk score GENUINELY changes the allocation (it cancelled out in v2 — bug).
2. Cautious profiles overweight calm assets (gold); aggressive ones overweight volatile.
3. Position count follows the budget logic; no dust positions survive.
4. Pruning is never silent — every drop is reported with a reason in metadata.
5. Every asset carries a rationale; risk-factor contributions sum to the score.
6. v4: a risk-sized DEFENSIVE sleeve (cash + bonds) — conservative profiles hold
   a real capital-preservation weight; it shrinks monotonically as risk rises;
   no single position exceeds the concentration cap.
"""
from unittest.mock import patch

import pytest

from backend.schemas.user_profile import RiskProfileAnswers
from backend.services.portfolio_engine import (
    MAX_POSITION_PCT,
    MIN_WEIGHT_PCT,
    build_portfolio,
)
from backend.services.risk_engine import compute_risk_score

# Fixed volatilities: XU100 very volatile, GLD calm — makes the contrast obvious
FAKE_VOLS = {"XU100.IS": 0.45, "SPY": 0.18, "QQQ": 0.28, "GLD": 0.12, "VNQ": 0.20, "SCHH": 0.22}


def _vols(tickers):
    return {t: FAKE_VOLS.get(t, 0.15) for t in tickers}


@pytest.fixture(autouse=True)
def _mock_vol():
    with patch("backend.services.portfolio_engine.compute_volatility", side_effect=_vols):
        yield


def _weight(portfolio, ticker):
    return next((a.weight for a in portfolio.allocations if a.ticker == ticker), 0.0)


def test_risk_score_actually_changes_allocation():
    cautious = build_portfolio(risk_score=2, budget=300000)
    aggressive = build_portfolio(risk_score=9, budget=300000)
    w_c = {a.ticker: a.weight for a in cautious.allocations}
    w_a = {a.ticker: a.weight for a in aggressive.allocations}
    assert w_c != w_a, "risk skoru dağılımı değiştirmiyor — v2 bug'ı geri gelmiş"


def test_cautious_profile_overweights_calm_assets():
    """
    Within the volatility blend: the calmer equity outweighs the more
    volatile one. This compared GLD with the BIST 100, which tested gold as
    a "calm asset" weighted by its volatility — the premise v5 removed: gold
    now has a fixed share whatever its volatility, so it no longer belongs in
    a test of how the blend tilts.
    """
    p = build_portfolio(risk_score=2, budget=300000)
    assert _weight(p, "SPY") > _weight(p, "XU100.IS"), (
        "muhafazakâr profilde sakin hisse fonu (SPY) oynak olandan (XU100) ağır olmalı"
    )


def test_aggressive_profile_overweights_volatile_assets():
    p = build_portfolio(risk_score=10, budget=300000)
    assert _weight(p, "XU100.IS") > _weight(p, "GLD")


def test_small_budget_gets_fewer_positions():
    small = build_portfolio(risk_score=5, budget=50000)
    large = build_portfolio(risk_score=5, budget=500000)
    assert len(small.allocations) <= 3, "50k bütçe en fazla 3 pozisyona bölünmeli"
    assert len(small.allocations) <= len(large.allocations)


def test_no_dust_positions_survive():
    p = build_portfolio(risk_score=5, budget=500000)
    for a in p.allocations:
        assert a.weight * 100 >= MIN_WEIGHT_PCT - 0.5, f"{a.ticker} kırıntı kalmış: {a.weight}"


def test_weights_sum_to_one_after_pruning():
    for risk, budget in [(1, 30000), (5, 120000), (10, 900000)]:
        p = build_portfolio(risk_score=risk, budget=budget)
        assert sum(a.weight for a in p.allocations) == pytest.approx(1.0, abs=1e-6)


def test_dropped_assets_are_reported_with_reasons():
    p = build_portfolio(risk_score=5, budget=50000)
    logic = p.metadata["allocation_logic"]
    assert logic["position_cap"] == 3
    # every dropped asset carries a reason
    for d in logic["dropped"]:
        assert d["ticker"] and d["reason"]
    # universe(4) → 3 positions: at least 1 drop must be reported
    assert len(logic["dropped"]) >= 1


def test_every_allocation_has_rationale():
    p = build_portfolio(risk_score=6, budget=200000)
    for a in p.allocations:
        assert "Rolü:" in a.explanation and "gerekçesi" in a.explanation
        assert "%" in a.explanation  # volatility and weight figures are visible


def _defensive_weight(portfolio):
    return sum(a.weight for a in portfolio.allocations if a.category in ("cash", "bond"))


def test_conservative_profile_holds_a_defensive_sleeve():
    # A cautious beginner must NOT be ~100% equities+gold — v4's core fix.
    p = build_portfolio(risk_score=2, budget=150000)
    cats = {a.category for a in p.allocations}
    assert cats & {"cash", "bond"}, "muhafazakâr profilde nakit/tahvil olmalı"
    assert _defensive_weight(p) > 0.30, "muhafazakârda savunma payı anlamlı olmalı"


def test_defensive_weight_decreases_as_risk_rises():
    weights = [_defensive_weight(build_portfolio(risk_score=r, budget=300000))
               for r in range(1, 11)]
    for earlier, later in zip(weights, weights[1:]):
        assert later <= earlier + 1e-9, f"savunma payı riskle artmamalı: {weights}"
    assert weights[0] > weights[-1] + 0.3, "muhafazakâr ≫ atılgan savunma farkı olmalı"


def test_aggressive_profile_is_growth_heavy():
    p = build_portfolio(risk_score=10, budget=300000)
    growth = sum(a.weight for a in p.allocations if a.category in ("stocks", "gold", "reit"))
    assert growth > 0.9, "en atılgan profil büyüme ağırlıklı olmalı"


def test_no_position_exceeds_concentration_cap():
    for risk in (1, 4, 7, 10):
        for budget in (50000, 150000, 600000):
            p = build_portfolio(risk_score=risk, budget=budget)
            for a in p.allocations:
                assert a.weight <= MAX_POSITION_PCT / 100.0 + 1e-9, (
                    f"{a.ticker} tek başına %{MAX_POSITION_PCT} üstünde: {a.weight}"
                )


def test_risk_factors_sum_to_score():
    answers = RiskProfileAnswers(
        budget=100000, time_horizon="long", loss_tolerance="high",
        goal="growth", experience="beginner", age=27, income_stability="variable",
    )
    r = compute_risk_score(answers)
    assert len(r.factors) >= 4
    total = sum(f.contribution for f in r.factors)
    assert total == pytest.approx(r.risk_score, abs=0.11)  # rounding tolerance
    # modifiers appear in the breakdown too
    names = " ".join(f.factor for f in r.factors)
    assert "Yaş" in names and "Gelir" in names


def test_risk_factors_expose_weights_and_answers():
    answers = RiskProfileAnswers(
        budget=100000, time_horizon="short", loss_tolerance="low",
        goal="preservation", experience="none",
    )
    r = compute_risk_score(answers)
    loss = next(f for f in r.factors if "Kayıp" in f.factor)
    assert "%30" in loss.factor            # weight is visible
    assert loss.answer == "Düşüşte satarım"  # answer in readable form
    assert loss.explanation               # has a why-explanation


# ── Growth sleeve must not stack duplicates of one exposure ─────────────────

def test_picker_prefers_a_new_category_over_a_higher_ranked_duplicate():
    """Two REIT ETFs tracking the same index are one exposure, not two."""
    from backend.services.portfolio_engine import _pick_diversified

    universe = [
        {"ticker": "VNQ", "category": "reit"},
        {"ticker": "SCHH", "category": "reit"},
        {"ticker": "GLD", "category": "gold"},
        {"ticker": "SPY", "category": "stocks"},
    ]
    ranked = ["VNQ", "SCHH", "GLD", "SPY"]      # both REITs rank top

    assert _pick_diversified(ranked, universe, 2) == ["VNQ", "GLD"]
    assert _pick_diversified(ranked, universe, 3) == ["VNQ", "GLD", "SPY"]


def test_picker_holds_fewer_positions_rather_than_a_duplicate():
    """
    `slots` is a maximum, not a target. Filling a spare slot with a second
    asset from a represented category used to pull SCHH back in beside VNQ
    for large budgets — ~44% of an aggressive portfolio in what is
    effectively one holding, which is precisely what the app tells users it
    avoids and what its own drop-reason text describes.
    """
    from backend.services.portfolio_engine import _pick_diversified

    universe = [
        {"ticker": "VNQ", "category": "reit"},
        {"ticker": "SCHH", "category": "reit"},
        {"ticker": "GLD", "category": "gold"},
    ]
    picked = _pick_diversified(["VNQ", "SCHH", "GLD"], universe, 3)
    assert picked == ["VNQ", "GLD"]


def test_no_recommended_portfolio_doubles_up_on_an_exposure():
    """
    The invariant, checked end to end rather than on the picker alone.

    It used to be "no doubled-up CATEGORY", and "stocks" was too coarse to be
    the unit: it treated the BIST 100 and the S&P 500 as the same exposure,
    so a Turkish portfolio never held a Turkish company. What must never
    happen is two funds on the same holdings — VNQ with SCHH, SPY with QQQ,
    the S&P 500 with an MSCI World that is mostly the S&P 500. That is what
    the overlap group names, and it is what this now checks, in every market.
    """
    from backend.markets import get_market_pack
    from backend.services.portfolio_engine import _overlap_group, build_portfolio

    for market in ("TR", "US", "DE"):
        pack = get_market_pack(market)
        group_of = {a["ticker"]: _overlap_group(a)
                    for a in [*pack.asset_universe, *pack.reit_assets]}
        for score in (1.0, 3.0, 5.0, 7.0, 9.0, 10.0):
            for budget in (5_000, 50_000, 200_000, 1_000_000):
                portfolio = build_portfolio(risk_score=score, budget=budget, market=market)
                groups = [group_of[a.ticker] for a in portfolio.allocations
                          if a.ticker in group_of]
                assert len(groups) == len(set(groups)), (market, score, budget, groups)


@pytest.mark.parametrize("market,home", [("TR", "XU100.IS"), ("US", "VXUS"), ("DE", "EXS1.DE")])
def test_a_second_market_reaches_the_portfolio_once_there_is_room(market, home):
    """
    What the overlap groups are for. Measured before the change: across
    every budget and risk level, a Turkish portfolio held SPY and never the
    BIST 100 below the maximum score; an American one never held VXUS, the
    international fund already in its universe; a German one held MSCI World
    without the DAX. With enough budget for a full growth sleeve, the second
    market now appears at ordinary risk levels.
    """
    from backend.services.portfolio_engine import build_portfolio

    p = build_portfolio(risk_score=5.0, budget=250_000, market=market)
    assert home in {a.ticker for a in p.allocations}, (market, [a.ticker for a in p.allocations])


def test_two_funds_on_the_same_index_still_never_appear_together():
    """The original reason for the rule must survive the change."""
    from backend.services.portfolio_engine import build_portfolio

    for market in ("TR", "US"):
        for score in (1.0, 5.0, 10.0):
            tickers = {a.ticker for a in build_portfolio(
                risk_score=score, budget=1_000_000, market=market).allocations}
            assert not {"SPY", "QQQ"} <= tickers, (market, score, tickers)
            assert not {"VNQ", "SCHH"} <= tickers, (market, score, tickers)


def test_picker_keeps_rank_order_within_a_category():
    from backend.services.portfolio_engine import _pick_diversified

    universe = [
        {"ticker": "SCHH", "category": "reit"},
        {"ticker": "VNQ", "category": "reit"},
    ]
    assert _pick_diversified(["SCHH", "VNQ"], universe, 1) == ["SCHH"]


def test_picker_never_exceeds_the_slot_count():
    from backend.services.portfolio_engine import _pick_diversified

    universe = [{"ticker": t, "category": c} for t, c in
                [("A", "stocks"), ("B", "gold"), ("C", "reit"), ("D", "bond")]]
    assert len(_pick_diversified(["A", "B", "C", "D"], universe, 2)) == 2


def test_volatility_is_measured_over_five_years_and_cached_per_window():
    """
    One year let a single unusual year reorder the assets: gold measured 29%
    over twelve months, above the BIST 100 and the Nasdaq, and the most
    aggressive portfolios — which weight growth assets BY volatility — put
    up to half their money into it. And the window was missing from the
    cache key, so changing it would have left production serving the old
    numbers.
    """
    from unittest.mock import patch

    from backend.services import volatility

    seen = {}

    def fake_history(tickers, period="1y"):
        seen["period"] = period
        return {}

    keys = []
    with patch.object(volatility, "fetch_price_history", side_effect=fake_history), \
         patch.object(volatility.cache_service, "get",
                      side_effect=lambda k: keys.append(k) or None), \
         patch.object(volatility.cache_service, "set"):
        volatility.compute_volatility(["SPY"])

    assert seen["period"] == "5y"
    assert "5y" in keys[0], keys


@pytest.mark.parametrize("category", ["gold", "reit"])
def test_diversifiers_take_a_fixed_share_of_the_growth_sleeve_in_every_scenario(category):
    """
    v5: gold takes GOLD_GROWTH_SHARE of the growth sleeve at every risk
    level, because its volatility is not a promise of growth — it earns no
    profits and pays no dividends. v6: a REIT takes REIT_GROWTH_SHARE, because
    its volatility is mostly interest-rate sensitivity; sized by the blend it
    was 16–26% of every portfolio, about as much as the S&P 500. The
    rationale card states the share, so the weight must actually BE that
    share everywhere the card is shown; the first version printed "a fixed
    15%" beside 16.4% when the concentration guard spilled a capped equity's
    excess onto gold.
    """
    from backend.services.portfolio_engine import (
        FIXED_GROWTH_SHARES,
        build_portfolio,
        effective_position_cap,
    )

    target = FIXED_GROWTH_SHARES[category]
    checked = 0
    for market in ("TR", "US", "DE"):
        for budget in (20_000, 250_000, 2_000_000):
            for score in (1.0, 3.0, 5.0, 7.0, 9.0, 10.0):
                al = build_portfolio(risk_score=score, budget=budget, market=market).allocations
                growth = [a for a in al if a.category not in ("cash", "bond")]
                held = sum(a.weight for a in growth if a.category == category)
                if not held:
                    continue
                assert len(growth) > 1, (market, budget, score, f"{category} alone in the growth sleeve")
                share = held / sum(a.weight for a in growth)
                row = next(a for a in growth if a.category == category)
                if abs(share - target) >= 0.005:
                    # Allowed ONLY where the concentration cap leaves the
                    # growth sleeve no other home for its excess: every
                    # blend-sized growth position pinned at the cap. The
                    # excess could go to cash instead, but that would make
                    # the reader more defensive than their risk score — the
                    # primary rule — so the secondary one gives, and the card
                    # must then say so instead of claiming the fixed share.
                    cap = effective_position_cap(len(al))
                    others = [a for a in growth if a.category not in FIXED_GROWTH_SHARES]
                    assert all(abs(a.weight - cap) < 0.002 for a in others), (
                        market, budget, score, round(share, 4), "off-share without the cap forcing it")
                    assert str(round(target * 100)) in row.explanation
                    assert str(round(share * 100)) in row.explanation
                    continue
                checked += 1
    # REITs are only held below each market's property entry point, so the
    # grid holds fewer of them than of gold.
    assert checked > {"gold": 20, "reit": 12}[category], (
        f"the scan found too few portfolios holding {category} to mean anything")


def test_property_is_never_the_biggest_growth_position():
    """The symptom that started v6: a REIT fund level with the S&P 500."""
    from backend.services.portfolio_engine import build_portfolio

    for market in ("TR", "US", "DE"):
        for score in (2.0, 5.5, 9.0):
            al = build_portfolio(risk_score=score, budget=20_000, market=market).allocations
            reit = [a for a in al if a.category == "reit"]
            equity = [a for a in al if a.category not in ("cash", "bond", "gold", "reit")]
            if reit and equity:
                assert max(r.weight for r in reit) < max(e.weight for e in equity), (market, score)


def test_the_most_aggressive_profile_is_led_by_equities_not_gold():
    """The symptom that started this: up to half the money in gold at risk 10."""
    from backend.services.portfolio_engine import build_portfolio

    for market in ("TR", "US", "DE"):
        al = build_portfolio(risk_score=10.0, budget=250_000, market=market).allocations
        top = max(al, key=lambda a: a.weight)
        assert top.category != "gold", (market, top.ticker, top.weight)


@pytest.mark.parametrize("lang", ["tr", "en", "de"])
def test_the_formula_shown_to_the_reader_quotes_the_engine_s_own_numbers(lang):
    """
    The recommendation page offers "show the formula", and the text it shows
    described the v4 engine after v5 shipped: every growth asset by the
    volatility blend, no word about gold's fixed share or the five-year
    window. A reader checking the arithmetic would have checked a
    calculation the app no longer performs.

    So the numbers in the text are asserted against the constants the
    engine actually uses. Change one without the other and this fails.
    """
    from backend.i18n import t
    from backend.services import volatility
    from backend.services.portfolio_engine import (
        GOLD_GROWTH_SHARE,
        REIT_GROWTH_SHARE,
        MAX_POSITION_PCT,
        MIN_WEIGHT_PCT,
    )

    text = t("formula.allocation", lang)
    window_years = int(volatility.VOLATILITY_WINDOW.rstrip("y"))
    for number, what in ((MAX_POSITION_PCT, "position cap"),
                         (MIN_WEIGHT_PCT, "dust floor"),
                         (round(GOLD_GROWTH_SHARE * 100), "gold's fixed share"),
                         (round(REIT_GROWTH_SHARE * 100), "the REIT's fixed share"),
                         (window_years, "volatility window")):
        assert str(number) in text, f"[{lang}] formula text does not state the {what} ({number})"


def test_position_bands_are_in_each_markets_own_currency(monkeypatch):
    """The bands were lira amounts applied to every market: EUR 50,000 (about
    2.5 million lira) got the three positions meant for under 75,000 lira.
    Each market now states its bands in its own currency."""
    from backend.markets import MARKET_PACKS
    from backend.services.portfolio_engine import _position_cap, MAX_POSITIONS

    tr = MARKET_PACKS["TR"].position_bands
    for code, pack in MARKET_PACKS.items():
        bands = pack.position_bands
        assert [cap for _, cap in bands] == sorted(cap for _, cap in bands)
        assert all(cap < MAX_POSITIONS for _, cap in bands)
        if pack.currency != "TRY":
            assert bands != tr, f"{code} reuses lira amounts"
    assert _position_cap(50_000, MARKET_PACKS["DE"].position_bands) == MAX_POSITIONS
    assert _position_cap(50_000, MARKET_PACKS["US"].position_bands) == MAX_POSITIONS
    assert _position_cap(50_000, MARKET_PACKS["TR"].position_bands) == 3
