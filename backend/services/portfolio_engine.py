"""
Risk-blended portfolio engine — v4 (glide-path + defensive sleeve).

WHY v4 (2026-07-13): v3 blended every asset with an inverse-/direct-volatility
mix keyed on the risk score. Two realism gaps surfaced in an end-to-end audit:
  1. The universe had no cash/bond, so even the most conservative profile was
     ~100% equities+gold — irresponsible for a cautious/older/irregular-income
     beginner.
  2. The risk score barely moved the allocation (a risk-2 and a risk-9 portfolio
     looked almost identical).

v4 splits the portfolio into two sleeves whose SIZES are set by the risk score,
so the profile genuinely shapes the result:

    defensive_target = clamp(0.60 − 0.055·risk, 0, 0.60)   (→0 for aggressive)
    growth_target    = 1 − defensive_target

  • DEFENSIVE sleeve (cash + bonds): capital-preservation weight. Cash is the
    safest; bonds a low-volatility buffer. cash_share falls as risk rises.
  • GROWTH sleeve (equities + gold + REIT): the existing volatility blend
    (α = risk/10) decides the mix WITHIN this sleeve, then it's scaled to
    growth_target.

A per-position cap (MAX_POSITION_PCT) prevents any single asset from dominating
a small portfolio, and a small-weight floor removes dust. The result: defensive
weight decreases monotonically with the risk score, and every weight is still
explainable in one sentence.

Cash/bond are sized directly (not fetched), so compute_volatility is only ever
called on the real, fetchable growth tickers.
"""

import json
from pathlib import Path

from backend.schemas.portfolio import AssetAllocation, PortfolioRecommendResponse
from backend.services.hybrid_basket import get_reit_assets, should_include_reits
from backend.services.volatility import compute_volatility

_ASSET_UNIVERSE_PATH = Path(__file__).parent.parent / "data" / "asset_universe.json"

MIN_WEIGHT_PCT = 5          # below this is "dust" — pruned and reported
MAX_POSITION_PCT = 45       # no single asset may exceed this (concentration guard)
_BUDGET_POSITION_CAPS = [   # (budget upper bound, max positions)
    (75_000, 3),
    (200_000, 4),
    (float("inf"), 6),
]

# Defensive sleeve — sized by the glide path, but REAL fetchable tickers so
# every downstream feature (projection, time-machine, backtest, what-if) can
# pull their history. BIL = 1-3 month T-bills (cash-like), BND = total bond.
_CASH_ASSET = {"ticker": "BIL", "name": "Nakit / Kısa Vade", "category": "cash"}
_BOND_ASSET = {"ticker": "BND", "name": "Tahvil Fonu (geniş tabanlı)", "category": "bond"}

# Category → role in the portfolio (core of the per-asset rationale)
_CATEGORY_ROLES = {
    "stocks": "büyüme motoru — uzun vadeli getiri buradan gelir",
    "gold": "dengeleyici — hisseler düşerken genellikle farklı davranır, portföyü yumuşatır",
    "reit": "gayrimenkul penceresi — mülk almadan emlak getirisine ortaklık",
    "bond": "sabit getirili tampon — hisse dalgalanmasını yumuşatır, düzenli faiz üretir",
    "cash": "güvenlik yastığı — düşüşte değer kaybetmez, fırsat ve acil durum likiditesi",
    "fund": "hazır sepet — tek kalemde çeşitlendirme",
}


def _load_universe() -> list[dict]:
    with open(_ASSET_UNIVERSE_PATH) as f:
        return json.load(f)


def _pick_diversified(ranked: list[str], universe: list[dict], slots: int) -> list[str]:
    """
    Take the top `slots` assets, but never two from one category while another
    category is still unrepresented.

    Ranking alone produced portfolios whose entire growth sleeve sat in two
    REIT ETFs tracking the same index — four slices on the chart, one real
    exposure underneath. Order within a category is untouched, so the choice
    stays deterministic and explainable; only redundant picks are deferred.
    """
    category_of = {a["ticker"]: a["category"] for a in universe}
    kept: list[str] = []
    used: set[str] = set()

    for ticker in ranked:                       # first pass: one per category
        if len(kept) >= slots:
            break
        category = category_of.get(ticker)
        if category not in used:
            kept.append(ticker)
            used.add(category)

    for ticker in ranked:                       # then fill, best-ranked first
        if len(kept) >= slots:
            break
        if ticker not in kept:
            kept.append(ticker)

    return kept


def _position_cap(budget: float) -> int:
    for limit, cap in _BUDGET_POSITION_CAPS:
        if budget < limit:
            return cap
    return _BUDGET_POSITION_CAPS[-1][1]


def _clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def _apply_max_position(weights: dict[str, float]) -> dict[str, float]:
    """Cap any position at MAX_POSITION_PCT, redistributing the excess
    proportionally onto the uncapped positions (iterated to convergence)."""
    cap = MAX_POSITION_PCT / 100.0
    w = dict(weights)
    for _ in range(40):
        over = [t for t, x in w.items() if x > cap + 1e-9]
        if not over:
            break
        excess = sum(w[t] - cap for t in over)
        for t in over:
            w[t] = cap
        under = [t for t in w if w[t] < cap - 1e-9]
        under_sum = sum(w[t] for t in under)
        if under_sum <= 0:
            break
        for t in under:
            w[t] += excess * (w[t] / under_sum)
    return w


def _growth_rationale(category: str, vol: float, weight: float, alpha: float) -> str:
    role = _CATEGORY_ROLES.get(category, "çeşitlendirici")
    vol_pct = round(vol * 100)
    if alpha < 0.45:
        tilt = f"profilin temkinli olduğu için düşük oynaklık (%{vol_pct}) ağırlığı artırdı"
    elif alpha > 0.7:
        tilt = f"yüksek risk iştahın oynaklığı (%{vol_pct}) getiri motoruna çevirdi"
    else:
        tilt = f"dengeli profilinde %{vol_pct} oynaklık orta ağırlık aldı"
    return f"Rolü: {role}. Ağırlığın gerekçesi: {tilt} → %{round(weight * 100, 1)}."


def _defensive_rationale(category: str, weight: float, defensive_target: float) -> str:
    role = _CATEGORY_ROLES.get(category, "koruma")
    return (
        f"Rolü: {role}. Ağırlığın gerekçesi: risk profilin portföyün ~%{round(defensive_target * 100)}'ünü "
        f"savunmaya (nakit/tahvil) ayırmayı gerektiriyor → %{round(weight * 100, 1)}."
    )


def build_portfolio(risk_score: float, budget: float) -> PortfolioRecommendResponse:
    """
    Compute a glide-path portfolio: a risk-sized defensive sleeve (cash + bonds)
    plus a volatility-blended growth sleeve (equities + gold + REIT).

    Args:
        risk_score: 1-10 score from the risk engine
        budget:     Investment budget in TRY

    Returns:
        PortfolioRecommendResponse with per-asset weights, per-asset rationale,
        and fully transparent allocation logic in metadata.
    """
    include_reits = should_include_reits(budget)
    growth_universe = _load_universe()
    if include_reits:
        growth_universe = growth_universe + get_reit_assets()

    # Fetch volatility ONLY for the real, fetchable growth tickers
    growth_tickers = [a["ticker"] for a in growth_universe]
    volatilities = compute_volatility(growth_tickers)

    alpha = _clamp(risk_score / 10.0, 0.1, 1.0)

    # ── Sleeve sizing (glide path) — the risk score sets the split ──
    defensive_target = _clamp(0.60 - 0.055 * risk_score, 0.0, 0.60)
    if defensive_target < 0.10:            # aggressive: a clean, cash-free growth mix
        defensive_target = 0.0
    growth_target = 1.0 - defensive_target
    cash_share = _clamp(0.75 - 0.05 * risk_score, 0.30, 0.75)

    cap = _position_cap(budget)
    n_defensive = 0 if defensive_target == 0 else min(2, max(cap - 2, 1))
    growth_slots = max(cap - n_defensive, 1)

    # ── Growth sleeve: volatility blend, keep the top `growth_slots` ──
    raw: dict[str, float] = {}
    for asset in growth_universe:
        t = asset["ticker"]
        vol = max(volatilities.get(t, 0.15), 0.01)
        raw[t] = (1 - alpha) * (1.0 / vol) + alpha * vol
    total_raw = sum(raw.values())
    growth_w = {t: v / total_raw for t, v in raw.items()}

    ranked = sorted(growth_w, key=growth_w.get, reverse=True)
    kept = _pick_diversified(ranked, growth_universe, growth_slots)

    category_of = {a["ticker"]: a["category"] for a in growth_universe}
    kept_categories = {category_of[t] for t in kept}
    dropped: list[dict] = []
    for t in growth_w:
        if t not in kept:
            # Two funds tracking the same market are one exposure wearing two
            # names. Say which, so a dropped-but-higher-ranked asset doesn't
            # look arbitrary.
            if category_of[t] in kept_categories:
                reason = (
                    f"Aynı kategoriden ({category_of[t]}) bir varlık zaten seçildi — "
                    "aynı şeyi izleyen iki fonu birlikte tutmak çeşitlendirme "
                    "görüntüsü verir ama riski azaltmaz"
                )
            else:
                reason = (
                    f"{budget:,.0f} TL bütçe için azami {cap} pozisyon hedeflendi — "
                    "küçük bütçeyi çok parçaya bölmek pratik değil"
                )
            dropped.append({
                "ticker": t,
                "weight_pct": round(growth_w[t] * 100, 1),
                "reason": reason,
            })
    growth_w = {t: growth_w[t] for t in kept}
    gsum = sum(growth_w.values()) or 1.0
    weights = {t: (v / gsum) * growth_target for t, v in growth_w.items()}

    # ── Defensive sleeve: sized directly, split cash/bond by risk ──
    defensive_categories: dict[str, str] = {}
    if n_defensive == 1:
        weights[_CASH_ASSET["ticker"]] = defensive_target
        defensive_categories[_CASH_ASSET["ticker"]] = "cash"
    elif n_defensive == 2:
        weights[_CASH_ASSET["ticker"]] = defensive_target * cash_share
        weights[_BOND_ASSET["ticker"]] = defensive_target * (1 - cash_share)
        defensive_categories[_CASH_ASSET["ticker"]] = "cash"
        defensive_categories[_BOND_ASSET["ticker"]] = "bond"

    # ── Dust floor first, then the concentration guard as the LAST step so no
    #    position can exceed the cap after the final re-normalisation ──
    min_w = MIN_WEIGHT_PCT / 100.0
    dust = [t for t, w in weights.items() if w < min_w]
    for t in dust:
        dropped.append({
            "ticker": t,
            "weight_pct": round(weights[t] * 100, 1),
            "reason": f"%{MIN_WEIGHT_PCT} altı kırıntı pozisyon — takip yükü ve işlem maliyeti katkısını aşar",
        })
        weights.pop(t)

    total = sum(weights.values()) or 1.0
    weights = {t: w / total for t, w in weights.items()}
    weights = _apply_max_position(weights)  # sum-preserving; final cap wins

    # ── Assemble allocations with per-asset rationale ──
    by_ticker = {a["ticker"]: a for a in growth_universe}
    by_ticker[_CASH_ASSET["ticker"]] = _CASH_ASSET
    by_ticker[_BOND_ASSET["ticker"]] = _BOND_ASSET

    allocations = []
    for t, weight in sorted(weights.items(), key=lambda kv: -kv[1]):
        asset = by_ticker[t]
        category = asset.get("category", "other")
        if t in defensive_categories:
            explanation = _defensive_rationale(category, weight, defensive_target)
        else:
            vol = volatilities.get(t, 0.15)
            explanation = _growth_rationale(category, vol, weight, alpha)
        allocations.append(
            AssetAllocation(
                ticker=t,
                name=asset.get("name", t),
                weight=round(weight, 4),
                category=category,
                explanation=explanation,
            )
        )

    # add the rounding remainder to the largest position → sum is exactly 1.0
    rounding_gap = round(1.0 - sum(a.weight for a in allocations), 4)
    if allocations and abs(rounding_gap) > 0:
        allocations[0].weight = round(allocations[0].weight + rounding_gap, 4)

    return PortfolioRecommendResponse(
        risk_score=risk_score,
        budget=budget,
        allocations=allocations,
        plain_explanation="",  # filled by explainer service
        includes_reits=include_reits and any(a.category == "reit" for a in allocations),
        formula_used="glide-path-defensive-sleeve-v4",
        metadata={
            "volatilities": {k: round(v, 4) for k, v in volatilities.items()},
            "allocation_logic": {
                "alpha": round(alpha, 2),
                "defensive_target_pct": round(defensive_target * 100, 1),
                "growth_target_pct": round(growth_target * 100, 1),
                "formula": (
                    "Güvenli pay = 60 − (5,5 × risk skoru), en az %0 en fazla %60 "
                    "(nakit + tahvil). Kalan pay büyüme varlıklarına dağıtılır: "
                    "her varlığın ağırlığı = (1 − α) × (1 / oynaklık) + α × oynaklık. "
                    "α risk skorunun onda biridir; yani α büyüdükçe oynak varlıklar "
                    "daha fazla, küçüldükçe sakin varlıklar daha fazla pay alır."
                ),
                "position_cap": cap,
                "max_position_pct": MAX_POSITION_PCT,
                "min_weight_pct": MIN_WEIGHT_PCT,
                "dropped": dropped,
            },
        },
    )
