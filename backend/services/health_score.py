"""
Portfolio health score ("Fener") — one 0-100 glance at the user's wealth.

Components (each 0-100):
  - diversification: 1 - Herfindahl index over asset-type values
  - liquidity: share of wealth that can realistically become cash quickly
Overall = weighted mean. Every component ships with a plain-language note
so the beginner learns WHY, not just the number (vision: explain first).
"""

from backend.i18n import t as _t

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


def compute_health(by_type: dict[str, float], lang: str = "tr") -> dict:
    if not by_type:
        return {
            "overall": 0,
            "components": {},
            "notes": [_t("health.none", lang)],
        }

    diversification = _diversification_score(by_type)
    liquidity = _liquidity_score(by_type)
    overall = round(
        diversification * _WEIGHTS["diversification"] + liquidity * _WEIGHTS["liquidity"]
    )

    notes = []
    if diversification < 40:
        notes.append(_t("health.concentrated", lang))
    if liquidity < 30:
        illiquid_pct = 100 - liquidity
        notes.append(_t("health.illiquid", lang, pct=illiquid_pct))
    if not notes:
        notes.append(_t("health.balanced", lang))

    return {
        "overall": overall,
        "components": {"diversification": diversification, "liquidity": liquidity},
        "notes": notes,
        # A number with no account of itself teaches nothing. Each component
        # says what it measures, why it sits where it does FOR THIS portfolio,
        # and the one thing that moves it — otherwise "liquidity: 30" is just
        # a grade, and a beginner cannot act on a grade.
        "explanations": _explain(by_type, diversification, liquidity, lang),
    }


def _dominant_share(by_type: dict[str, float], lang: str) -> tuple[str, int]:
    """
    The largest asset type and its share, which is what drags HHI down.

    The name is translated: the raw key is "land", and dropping that into a
    Turkish sentence gives "servetinin %80'i land" — an English word in the
    middle of Turkish prose, which is the same defect the neutrality tests
    exist to catch, just generated at runtime instead of written down.
    """
    total = sum(by_type.values()) or 1.0
    key, value = max(by_type.items(), key=lambda kv: kv[1])
    return _t(f"asset_type.{key}", lang), round(value / total * 100)


def _explain(by_type: dict[str, float], diversification: int,
             liquidity: int, lang: str) -> list[dict]:
    """Per component: what it is, why this number, what raises it."""
    total = sum(by_type.values()) or 1.0
    top_type, top_share = _dominant_share(by_type, lang)
    illiquid_share = round(
        sum(v for t, v in by_type.items() if t not in _LIQUID_TYPES) / total * 100
    )

    if diversification >= 70:
        why_div = _t("health.why.div_high", lang, type=top_type, pct=top_share)
    elif diversification >= 40:
        why_div = _t("health.why.div_mid", lang, type=top_type, pct=top_share)
    else:
        why_div = _t("health.why.div_low", lang, type=top_type, pct=top_share)

    if liquidity >= 70:
        why_liq = _t("health.why.liq_high", lang, pct=illiquid_share)
    elif liquidity >= 30:
        why_liq = _t("health.why.liq_mid", lang, pct=illiquid_share)
    else:
        why_liq = _t("health.why.liq_low", lang, pct=illiquid_share)

    return [
        {
            "key": "diversification",
            "score": diversification,
            "what": _t("health.what.diversification", lang),
            "why": why_div,
            "how": _t("health.how.diversification", lang),
        },
        {
            "key": "liquidity",
            "score": liquidity,
            "what": _t("health.what.liquidity", lang),
            "why": why_liq,
            "how": _t("health.how.liquidity", lang),
        },
    ]
