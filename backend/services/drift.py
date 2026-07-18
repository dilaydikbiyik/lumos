"""
Portfolio drift — the advice a beginner actually needs AFTER buying.

You bought a mix (say 36% stocks / 33% REIT / 16% bonds / 15% cash). Prices
move at different speeds, so months later the real mix is no longer the one
your risk profile called for: the winner quietly grows into an outsized bet.

This computes the gap between the target weights (recomputed deterministically
from the same risk score, so nothing has to be stored) and the actual weights
of what the user owns — and says, in plain words, whether it is worth acting.

Deliberately conservative: rebalancing has costs and taxes, so we only raise a
flag past a meaningful threshold, and we never tell anyone to buy or sell a
specific security.
"""

# Below this, drift is noise — nudging someone to trade over 2 points of
# movement would cost them more in fees than it gains.
NOTABLE_DRIFT_PCT = 5.0
SERIOUS_DRIFT_PCT = 10.0

# Category names as the reader knows them — the message is user-facing copy
_CATEGORY_TR = {
    "stocks": "hisse/ETF", "reit": "gayrimenkul", "bond": "tahvil",
    "fund": "fon", "gold": "altın", "cash": "nakit", "other": "diğer",
}

# Portfolio categories mapped onto the holding types users record
_CATEGORY_BY_TYPE = {
    "stock": "stocks", "etf": "stocks", "fund": "fund",
    "gold": "gold", "crypto": "stocks",
    "cash": "cash", "real_estate": "reit", "land": "reit",
    "vehicle": "other", "other": "other",
}


def _actual_weights(holdings, values: dict[int, float],
                    category_by_ticker: dict[str, str]) -> dict[str, float]:
    """Weights per portfolio category.

    Ticker wins over asset_type: a REIT ETF is recorded as type 'etf', so
    type-only mapping would file VNQ under stocks and then claim the user
    owns no real estate — advice that is not just useless but wrong.
    """
    total = sum(values.values())
    if total <= 0:
        return {}
    out: dict[str, float] = {}
    for h in holdings:
        ticker = (getattr(h, "ticker", None) or "").upper()
        cat = category_by_ticker.get(ticker) or _CATEGORY_BY_TYPE.get(h.asset_type, "other")
        out[cat] = out.get(cat, 0.0) + values.get(h.id, 0.0) / total
    return out


def compute_drift(holdings, values: dict[int, float], target_allocations) -> dict:
    """
    Compare what the user owns against the mix their profile calls for.

    Args:
        holdings: the user's holdings
        values:   holding.id -> current value
        target_allocations: allocation objects with .category and .weight

    Returns a per-category comparison plus a plain-language verdict.
    """
    target: dict[str, float] = {}
    category_by_ticker: dict[str, str] = {}
    for a in target_allocations:
        cat = getattr(a, "category", None) or a["category"]
        w = getattr(a, "weight", None) if hasattr(a, "weight") else a["weight"]
        tkr = (getattr(a, "ticker", None) or (a.get("ticker") if isinstance(a, dict) else None) or "")
        target[cat] = target.get(cat, 0.0) + w
        if tkr:
            category_by_ticker[tkr.upper()] = cat

    actual = _actual_weights(holdings, values, category_by_ticker)
    if not actual:
        return {"available": False, "reason": "Henüz takip ettiğin bir varlık yok."}

    categories = sorted(set(actual) | set(target))
    rows = []
    worst = 0.0
    for cat in categories:
        a_pct = round(actual.get(cat, 0.0) * 100, 1)
        t_pct = round(target.get(cat, 0.0) * 100, 1)
        diff = round(a_pct - t_pct, 1)
        worst = max(worst, abs(diff))
        rows.append({
            "category": cat,
            "actual_pct": a_pct,
            "target_pct": t_pct,
            "diff_pct": diff,
        })

    if worst < NOTABLE_DRIFT_PCT:
        verdict, message = "balanced", (
            "Portföyün hedefine yakın duruyor. Şu an bir şey yapman gerekmiyor — "
            "dengeleme işlem masrafı ve vergi doğurur, gereksizken yapılmaz."
        )
    else:
        drifted = max(rows, key=lambda r: abs(r["diff_pct"]))
        direction = "büyüdü" if drifted["diff_pct"] > 0 else "küçüldü"
        level = "serious" if worst >= SERIOUS_DRIFT_PCT else "notable"
        label = _CATEGORY_TR.get(drifted["category"], drifted["category"])
        message = (
            f"En büyük sapma {label} tarafında: hedefin "
            f"%{drifted['target_pct']} iken şu an %{drifted['actual_pct']} — "
            f"yani {direction}. "
            + ("Bu, risk profilinin öngördüğünden belirgin bir sapma; "
               "yeni katkılarını geride kalan tarafa yönlendirmek, satmadan "
               "dengelemenin en ucuz yoludur."
               if level == "serious" else
               "Henüz küçük bir sapma; acele etmene gerek yok, bir sonraki "
               "katkında dengeleyebilirsin.")
        )
        verdict = level

    return {
        "available": True,
        "verdict": verdict,
        "max_drift_pct": round(worst, 1),
        "rows": rows,
        "message": message,
        "honesty_note": (
            "Dengeleme bir zorunluluk değil, bir tercihtir. Satış vergi ve masraf "
            "doğurabilir; çoğu durumda yeni alımları geride kalan tarafa yönlendirmek "
            "yeterlidir. Lumos senin adına işlem yapmaz."
        ),
    }
