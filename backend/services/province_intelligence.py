"""
İl bazında konut fiyat istihbaratı — "nereden ev alayım?"ın somut hali.

TCMB'nin il bazında birim fiyat serileri (TL/m², çeyreklik, 2010→bugün):
NUTS2 bölge bulanıklığı yerine "Muğla'da m² 79.110 TL, 5 yılda reel +X%"
diyebiliyoruz. Dürüstlük çerçevesi aynı: il ortalamasıdır, mahalle/parsel
değildir; geçmiş geleceğin garantisi değildir.
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
    81 ili seçilen ufukta (1/3/5 yıl) REEL değerlenmeye göre sırala.
    Her satır: il, güncel TL/m², nominal + reel değişim.
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
    'X TL bu ilde N yılda ne olurdu?' — ilin kendi 16 yıllık birim fiyat
    geçmişindeki tüm kaymalı N-yıl pencerelerinin dağılımı (tahmin değil).
    """
    from backend.services.projection import _windowed_real_band

    import numpy as np

    data = evds_service.get_province_unit_prices()
    entry = data.get(code)
    if not entry:
        return {"available": False, "reason": "İl verisi şu an alınamıyor."}

    months = sorted(entry["prices"])
    values = np.array([entry["prices"][m] for m in months])
    window = years * 4  # çeyreklik seri

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
        "real_band": real_band,  # her pencere KENDİ dönem enflasyonuyla düşürülmüş
        "honesty_note": (
            f"Bu bir tahmin DEĞİL: {entry['name']} il ortalamasının 2010'dan bugüne kendi "
            f"geçmişindeki tüm {years} yıllık dönemlerin dağılımı. Reel bant, her dönemin "
            "kendi enflasyonundan arındırılmıştır."
        ),
    }
