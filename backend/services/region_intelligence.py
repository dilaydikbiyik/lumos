"""
Region intelligence — the honest answer to "where should I buy a home/land?".

Ranks NUTS2 regions by housing-index appreciation (nominal AND real).
Deliberate honesty constraints (vision principle):
  - region level only, never street/parcel claims
  - real (inflation-adjusted) change shown next to nominal — a region
    that "gained 40%" while inflation ran 60% actually LOST value
"""
import logging
from typing import Optional

from backend.services import evds_service, inflation_service

logger = logging.getLogger("lumos.region")


def _pct_change_over_months(index: dict[str, float], months: int) -> Optional[float]:
    """% change between the latest month and ~`months` earlier."""
    if len(index) < 2:
        return None
    keys = sorted(index)
    latest = keys[-1]
    target_pos = max(len(keys) - 1 - months, 0)
    base = keys[target_pos]
    if index[base] == 0:
        return None
    return round((index[latest] / index[base] - 1) * 100, 1)


def rank_regions(horizon_years: int = 1) -> dict:
    """
    Rank all regions by housing-index appreciation over the horizon.

    Returns ranked list with nominal + real change and a plain-language
    note, plus metadata about the data window.
    """
    months = horizon_years * 12
    data = evds_service.get_regional_housing_indices()
    if not data:
        return {"available": False, "regions": [], "note": "Bölge verisi şu an alınamıyor."}

    rows = []
    latest_month = None
    for code, entry in data.items():
        index = entry["index"]
        change = _pct_change_over_months(index, months)
        if change is None:
            continue

        keys = sorted(index)
        latest_month = keys[-1]
        base_month = keys[max(len(keys) - 1 - months, 0)]
        real_change = inflation_service.real_return_pct(change, base_month, latest_month)

        rows.append({
            "code": code,
            "region": entry["region"],
            "nominal_change_pct": change,
            "real_change_pct": real_change,
        })

    rows.sort(key=lambda r: r["real_change_pct"], reverse=True)

    for i, row in enumerate(rows):
        if row["real_change_pct"] > 0:
            row["note"] = "Enflasyonun ÜZERİNDE değerlendi — reel kazanç."
        elif row["real_change_pct"] > -10:
            row["note"] = "Nominal artışa rağmen enflasyona yakın seyretti."
        else:
            row["note"] = "Nominal artış yanıltıcı: enflasyon karşısında reel kayıp."
        row["rank"] = i + 1

    return {
        "available": True,
        "horizon_years": horizon_years,
        "data_through": latest_month,
        "honesty_note": (
            "Bu sıralama bölge (NUTS2) seviyesindedir — mahalle/parsel analizi değildir. "
            "Geçmiş değerlenme geleceğin garantisi değildir."
        ),
        "regions": rows,
    }
