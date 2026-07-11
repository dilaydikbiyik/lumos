"""
Per-province housing price intelligence — the concrete answer to
"where should I buy a home?".

TCMB per-province unit-price series (TL/m², quarterly, 2010→today): instead
of blurry NUTS2 regions we can say "79.110 TL per m² in Muğla, +X% real
over 5 years". Same honesty frame: it is a province average, not a
quarter/parcel; the past is no guarantee of the future.
"""
import logging
from typing import Optional

from backend.services import evds_service, inflation_service

logger = logging.getLogger("lumos.province")

VALID_HORIZONS = (1, 3, 5)


def _change_over_quarters(prices: dict[str, float], quarters_back: int) -> Optional[float]:
    if len(prices) < 2:
        return None
    months = sorted(prices)
    latest = months[-1]
    base_pos = max(len(months) - 1 - quarters_back, 0)
    base = months[base_pos]
    if prices[base] <= 0 or base == latest:
        return None
    return round((prices[latest] / prices[base] - 1) * 100, 1)


def rank_provinces(horizon_years: int = 3) -> dict:
    """
    Rank all 81 provinces by REAL appreciation over the chosen horizon
    (1/3/5 years). Each row: province, current TL/m², nominal + real change.
    """
    horizon_years = horizon_years if horizon_years in VALID_HORIZONS else 3
    quarters = horizon_years * 4

    data = evds_service.get_province_unit_prices()
    if not data:
        return {"available": False, "provinces": [], "note": "İl verisi şu an alınamıyor."}

    rows = []
    latest_month = None
    for suffix, entry in data.items():
        prices = entry["prices"]
        change = _change_over_quarters(prices, quarters)
        if change is None:
            continue

        months = sorted(prices)
        latest_month = months[-1]
        base_month = months[max(len(months) - 1 - quarters, 0)]
        try:
            real_change = inflation_service.real_return_pct(change, base_month, latest_month)
        except Exception:
            real_change = None

        rows.append({
            "code": suffix,
            "province": entry["name"],
            "price_per_m2": round(prices[latest_month]),
            "nominal_change_pct": change,
            "real_change_pct": real_change,
        })

    rows.sort(key=lambda r: (r["real_change_pct"] is None, -(r["real_change_pct"] or 0)))
    for i, row in enumerate(rows):
        row["rank"] = i + 1

    return {
        "available": True,
        "horizon_years": horizon_years,
        "data_through": latest_month,
        "honesty_note": (
            "İl ortalaması birim fiyatlardır (TCMB) — mahalle/parsel analizi değildir. "
            "Geçmiş değerlenme geleceğin garantisi değildir."
        ),
        "provinces": rows,
    }


def project_province(code: str, amount: float, years: int) -> dict:
    """
    "What would X TL become in this province over N years?" — the
    distribution of every rolling N-year window in the province's own
    16-year unit-price history (not a forecast).
    """
    from backend.services.projection import _windowed_real_band

    import numpy as np

    data = evds_service.get_province_unit_prices()
    entry = data.get(code)
    if not entry:
        return {"available": False, "reason": "İl verisi şu an alınamıyor."}

    months = sorted(entry["prices"])
    values = np.array([entry["prices"][m] for m in months])
    window = years * 4  # quarterly series

    band, real_band = _windowed_real_band(values, months, window, amount)
    if not band:
        return {
            "available": False,
            "reason": f"{entry['name']} için {years} yıllık pencere dağılımına yetecek geçmiş yok.",
        }

    return {
        "available": True,
        "province": entry["name"],
        "amount": amount,
        "years": years,
        **band,
        "real_band": real_band,  # each window deflated by its OWN period inflation
        "honesty_note": (
            f"Bu bir tahmin DEĞİL: {entry['name']} il ortalamasının 2010'dan bugüne kendi "
            f"geçmişindeki tüm {years} yıllık dönemlerin dağılımı. Reel bant, her dönemin "
            "kendi enflasyonundan arındırılmıştır."
        ),
    }
