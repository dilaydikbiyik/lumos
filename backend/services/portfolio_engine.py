"""
Risk-blended volatility portfolio engine — v3.

GERÇEKÇİLİK DÜZELTMESİ (2026-07-10): v2 formülü `RiskScore × Vol(asset)` idi;
risk skoru her varlığı aynı çarptığı için normalizasyonda SADELEŞİYORDU —
dağılım risk profilinden bağımsızdı ve yüksek oynaklık her profilde daha çok
ağırlık alıyordu (muhafazakâr için tam ters). v3 bunu düzeltir:

    α = risk_score / 10                       (risk iştahı, 0.1–1.0)
    raw(asset) = (1-α)·(1/vol) + α·vol        (defansif ↔ agresif harman)
    weight     = raw / Σ raw

  - Düşük skor → ters-oynaklık ağırlığı: sakin varlıklar (altın vb.) öne çıkar.
  - Yüksek skor → oynaklık ağırlığı: büyüme motorları öne çıkar.
  Her ağırlık tek cümleyle açıklanabilir — mantıksal boşluk yok.

POZİSYON SAYISI MANTIĞI: pasta dilimi süsü değil, gerekçeli sayı:
  - %{MIN_WEIGHT_PCT} altındaki "kırıntı" pozisyonlar elenir (takip yükü ve
    işlem maliyeti getirir, portföye ölçülebilir katkısı yoktur).
  - Küçük bütçe daha az parçaya bölünür (75k → ≤3, 200k → ≤4 pozisyon).
  Elenen her varlık ve nedeni metadata'da raporlanır — sessiz eleme yok.
"""

import json
from pathlib import Path

from backend.schemas.portfolio import AssetAllocation, PortfolioRecommendResponse
from backend.services.hybrid_basket import get_reit_assets, should_include_reits
from backend.services.volatility import compute_volatility

_ASSET_UNIVERSE_PATH = Path(__file__).parent.parent / "data" / "asset_universe.json"

MIN_WEIGHT_PCT = 8          # bunun altı "kırıntı" — elenir ve raporlanır
_BUDGET_POSITION_CAPS = [   # (bütçe üst sınırı, azami pozisyon)
    (75_000, 3),
    (200_000, 4),
    (float("inf"), 6),
]

# Kategori → portföydeki rolü (varlık-başına gerekçenin çekirdeği)
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

    # ── v3 harman: risk iştahı dağılımı GERÇEKTEN şekillendirir ──
    alpha = min(max(risk_score / 10.0, 0.1), 1.0)
    raw_weights: dict[str, float] = {}
    for asset in universe:
        t = asset["ticker"]
        vol = max(volatilities.get(t, 0.15), 0.01)
        raw_weights[t] = (1 - alpha) * (1.0 / vol) + alpha * vol

    # normalize (birinci tur)
    total = sum(raw_weights.values())
    weights = {t: w / total for t, w in raw_weights.items()}

    # ── pozisyon sayısı mantığı: kırıntı eleme + bütçe sınırı ──
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
        ranked = sorted(weights, key=weights.get)  # küçükten büyüğe
        for t in ranked[: len(weights) - cap]:
            dropped.append({
                "ticker": t,
                "weight_pct": round(weights[t] * 100, 1),
                "reason": f"{budget:,.0f} TL bütçe için azami {cap} pozisyon hedeflendi — küçük bütçeyi çok parçaya bölmek pratik değil",
            })
            weights.pop(t)

    # yeniden normalize (ikinci tur)
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

    # yuvarlama artığını en büyük pozisyona ekle → toplam tam 1.0
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
