"""
Portfolio engine v3 logic tests — keeping the realism filter alive in code:

1. The risk score GENUINELY changes the allocation (it cancelled out in v2 — bug).
2. Cautious profiles overweight calm assets (gold); aggressive ones overweight volatile.
3. Position count follows the budget logic; no dust positions survive.
4. Pruning is never silent — every drop is reported with a reason in metadata.
5. Every asset carries a rationale; risk-factor contributions sum to the score.
"""
from unittest.mock import patch

import pytest

from backend.schemas.user_profile import RiskProfileAnswers
from backend.services.portfolio_engine import MIN_WEIGHT_PCT, build_portfolio
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
    p = build_portfolio(risk_score=2, budget=300000)
    assert _weight(p, "GLD") > _weight(p, "XU100.IS"), (
        "muhafazakâr profilde sakin varlık (GLD) oynak varlıktan (XU100) ağır olmalı"
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
