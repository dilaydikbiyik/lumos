"""
Portfolio health score ("Fener") — one 0-100 glance at the user's wealth.

Components (each 0-100):
  - diversification: 1 - Herfindahl index over asset-type values
  - liquidity: share of wealth that can realistically become cash quickly
Overall = weighted mean. Every component ships with a plain-language note
so the beginner learns WHY, not just the number (vision: explain first).
"""

# vehicle/land/real_estate can take months to sell; cash is instant
_LIQUID_TYPES = {"stock", "fund", "etf", "gold", "crypto", "cash"}

_WEIGHTS = {"diversification": 0.6, "liquidity": 0.4}


def _diversification_score(by_type: dict[str, float]) -> int:
    total = sum(by_type.values())
    if total <= 0 or len(by_type) == 0:
        return 0
    hhi = sum((v / total) ** 2 for v in by_type.values())  # 1/n .. 1
    # hhi=1 (single asset type) -> 0 points; hhi=0.2 (5 balanced types) -> 100
    score = (1 - hhi) / (1 - 0.2)
    return round(min(max(score, 0.0), 1.0) * 100)


def _liquidity_score(by_type: dict[str, float]) -> int:
    total = sum(by_type.values())
    if total <= 0:
        return 0
    liquid = sum(v for t, v in by_type.items() if t in _LIQUID_TYPES)
    return round(liquid / total * 100)


def compute_health(by_type: dict[str, float]) -> dict:
    if not by_type:
        return {
            "overall": 0,
            "components": {},
            "notes": ["Henüz varlığın yok — ilk ışığı birlikte yakalım. / No holdings yet."],
        }

    diversification = _diversification_score(by_type)
    liquidity = _liquidity_score(by_type)
    overall = round(
        diversification * _WEIGHTS["diversification"] + liquidity * _WEIGHTS["liquidity"]
    )

    notes = []
    if diversification < 40:
        notes.append(
            "Servetin büyük ölçüde tek varlık tipinde toplanmış — çeşitlendirme, "
            "tek bir kötü gün senaryosunun etkisini azaltır."
        )
    if liquidity < 30:
        illiquid_pct = 100 - liquidity
        notes.append(
            f"Varlıklarının ~%{illiquid_pct}'i hızla nakde dönmez (arsa/ev/araç). "
            "Acil bir ihtiyaç planın var mı?"
        )
    if not notes:
        notes.append("Dengeli görünüyor — fenerin gür yanıyor. 🔦")

    return {
        "overall": overall,
        "components": {"diversification": diversification, "liquidity": liquidity},
        "notes": notes,
    }
