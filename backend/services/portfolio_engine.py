"""
Volatility-weighted portfolio engine — Phase 3 (v2 formula).

Formula:
    Allocation(asset) = (RiskScore × Volatility(asset)) / SUM(RiskScore × Volatility(i))

After computing raw weights, they are normalised so the total = 1.0.

Assets:
    - Base universe: XU100.IS, SPY, QQQ, GLD
    - REIT layer (Phase 3.5): VNQ, SCHH  (included if budget < threshold)
"""

from backend.schemas.portfolio import AssetAllocation, PortfolioRecommendResponse
from backend.services.volatility import compute_volatility
from backend.services.hybrid_basket import should_include_reits, get_reit_assets
import json
from pathlib import Path

_ASSET_UNIVERSE_PATH = Path(__file__).parent.parent / "data" / "asset_universe.json"


def _load_universe() -> list[dict]:
    with open(_ASSET_UNIVERSE_PATH) as f:
        return json.load(f)


def build_portfolio(risk_score: float, budget: float) -> PortfolioRecommendResponse:
    """
    Compute a volatility-weighted portfolio allocation.

    Args:
        risk_score: 1-10 score from the risk engine
        budget:     Investment budget in TRY

    Returns:
        PortfolioRecommendResponse with per-asset weights
    """
    universe = _load_universe()
    include_reits = should_include_reits(budget)

    # Add REIT assets conditionally
    if include_reits:
        universe = universe + get_reit_assets()

    tickers = [a["ticker"] for a in universe]
    volatilities = compute_volatility(tickers)

    # Compute raw weights: RiskScore × Volatility(asset)
    raw_weights: dict[str, float] = {}
    for asset in universe:
        t = asset["ticker"]
        vol = volatilities.get(t, 0.15)  # 15% fallback
        raw_weights[t] = risk_score * vol

    total = sum(raw_weights.values())

    allocations = []
    for asset in universe:
        t = asset["ticker"]
        weight = raw_weights[t] / total if total > 0 else 1 / len(universe)
        allocations.append(
            AssetAllocation(
                ticker=t,
                name=asset.get("name", t),
                weight=round(weight, 4),
                category=asset.get("category", "other"),
            )
        )

    return PortfolioRecommendResponse(
        risk_score=risk_score,
        budget=budget,
        allocations=allocations,
        plain_explanation="",  # filled by explainer service
        includes_reits=include_reits,
        metadata={"volatilities": {k: round(v, 4) for k, v in volatilities.items()}},
    )
