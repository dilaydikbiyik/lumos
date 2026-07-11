"""
Risk-blended volatility portfolio engine — v3.

REALISM FIX (2026-07-10): the v2 formula was `RiskScore × Vol(asset)`; the
risk score multiplied every asset equally, so it CANCELLED OUT during
normalisation — the allocation was independent of the risk profile, and
higher volatility always got more weight (the exact opposite of what a
conservative profile needs). v3 fixes this:

    α = risk_score / 10                       (risk appetite, 0.1–1.0)
    raw(asset) = (1-α)·(1/vol) + α·vol        (defensive ↔ aggressive blend)
    weight     = raw / Σ raw

  - Low score → inverse-volatility weighting: calm assets (gold etc.) rise.
  - High score → volatility weighting: growth engines rise.
  Every weight can be explained in one sentence — no logical gaps.

POSITION-COUNT LOGIC: a reasoned number, not pie-chart decoration:
  - "Dust" positions below MIN_WEIGHT_PCT% are pruned (they add tracking
    burden and transaction costs without measurable portfolio impact).
  - Small budgets are split into fewer pieces (75k → ≤3, 200k → ≤4).
  Every dropped asset and its reason is reported in metadata — no silent
  pruning.
"""

import json
from pathlib import Path

from backend.schemas.portfolio import AssetAllocation, PortfolioRecommendResponse
from backend.services.hybrid_basket import get_reit_assets, should_include_reits
from backend.services.volatility import compute_volatility

_ASSET_UNIVERSE_PATH = Path(__file__).parent.parent / "data" / "asset_universe.json"

MIN_WEIGHT_PCT = 8          # below this is "dust" — pruned and reported
_BUDGET_POSITION_CAPS = [   # (budget upper bound, max positions)
    (75_000, 3),
    (200_000, 4),
    (float("inf"), 6),
]

# Category → role in the portfolio (core of the per-asset rationale)
_CATEGORY_ROLES = {
    "stocks": "büyüme motoru — uzun vadeli getiri buradan gelir",
    "gold": "dengeleyici — hisseler düşerken genellikle farklı davranır, portföyü yumuşatır",
    "reit": "gayrimenkul penceresi — mülk almadan emlak getirisine ortaklık",
    "fund": "hazır sepet — tek kalemde çeşitlendirme",
    "cash": "güvenlik yastığı — fırsat ve acil durum likiditesi",
}


def _load_universe() -> list[dict]:
    with open(_ASSET_UNIVERSE_PATH) as f:
        return json.load(f)


def _position_cap(budget: float) -> int:
    for limit, cap in _BUDGET_POSITION_CAPS:
        if budget < limit:
            return cap
    return _BUDGET_POSITION_CAPS[-1][1]


def _asset_rationale(category: str, vol: float, weight: float, alpha: float) -> str:
    role = _CATEGORY_ROLES.get(category, "çeşitlendirici")
    vol_pct = round(vol * 100)
    if alpha < 0.45:
        tilt = f"profilin temkinli olduğu için düşük oynaklık (%{vol_pct}) ağırlığı artırdı"
    elif alpha > 0.7:
        tilt = f"yüksek risk iştahın oynaklığı (%{vol_pct}) getiri motoruna çevirdi"
    else:
        tilt = f"dengeli profilinde %{vol_pct} oynaklık orta ağırlık aldı"
    return f"Rolü: {role}. Ağırlığın gerekçesi: {tilt} → %{round(weight * 100, 1)}."


def build_portfolio(risk_score: float, budget: float) -> PortfolioRecommendResponse:
    """
    Compute a risk-blended, volatility-aware portfolio allocation.

    Args:
        risk_score: 1-10 score from the risk engine
        budget:     Investment budget in TRY

    Returns:
        PortfolioRecommendResponse with per-asset weights, per-asset
        rationale, and fully transparent allocation logic in metadata.
    """
    universe = _load_universe()
    include_reits = should_include_reits(budget)
    if include_reits:
        universe = universe + get_reit_assets()

    tickers = [a["ticker"] for a in universe]
    volatilities = compute_volatility(tickers)

    # ── v3 blend: risk appetite GENUINELY shapes the allocation ──
    alpha = min(max(risk_score / 10.0, 0.1), 1.0)
    raw_weights: dict[str, float] = {}
    for asset in universe:
        t = asset["ticker"]
        vol = max(volatilities.get(t, 0.15), 0.01)
        raw_weights[t] = (1 - alpha) * (1.0 / vol) + alpha * vol

    # normalise (first pass)
    total = sum(raw_weights.values())
    weights = {t: w / total for t, w in raw_weights.items()}

    # ── position-count logic: dust pruning + budget cap ──
    dropped: list[dict] = []
    min_w = MIN_WEIGHT_PCT / 100.0

    dust = [t for t, w in weights.items() if w < min_w]
    for t in dust:
        dropped.append({
            "ticker": t,
            "weight_pct": round(weights[t] * 100, 1),
            "reason": f"%{MIN_WEIGHT_PCT} altı kırıntı pozisyon — takip yükü ve işlem maliyeti katkısını aşar",
        })
        weights.pop(t)

    cap = _position_cap(budget)
    if len(weights) > cap:
        ranked = sorted(weights, key=weights.get)  # ascending
        for t in ranked[: len(weights) - cap]:
            dropped.append({
                "ticker": t,
                "weight_pct": round(weights[t] * 100, 1),
                "reason": f"{budget:,.0f} TL bütçe için azami {cap} pozisyon hedeflendi — küçük bütçeyi çok parçaya bölmek pratik değil",
            })
            weights.pop(t)

    # re-normalise (second pass)
    total = sum(weights.values())
    weights = {t: w / total for t, w in weights.items()}

    by_ticker = {a["ticker"]: a for a in universe}
    allocations = []
    for t, weight in sorted(weights.items(), key=lambda kv: -kv[1]):
        asset = by_ticker[t]
        vol = volatilities.get(t, 0.15)
        allocations.append(
            AssetAllocation(
                ticker=t,
                name=asset.get("name", t),
                weight=round(weight, 4),
                category=asset.get("category", "other"),
                explanation=_asset_rationale(asset.get("category", "other"), vol, weight, alpha),
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
        formula_used="risk-blended-volatility-v3",
        metadata={
            "volatilities": {k: round(v, 4) for k, v in volatilities.items()},
            "allocation_logic": {
                "alpha": round(alpha, 2),
                "formula": "ağırlık ∝ (1-α)·(1/oynaklık) + α·oynaklık — α senin risk iştahın (skor/10)",
                "position_cap": cap,
                "min_weight_pct": MIN_WEIGHT_PCT,
                "dropped": dropped,
            },
        },
    )
