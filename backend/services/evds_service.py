"""
TCMB EVDS client — live Turkish central bank data (free API).

Series used:
  TP.FG.J0      -> TÜFE (CPI, 2003=100) — feeds the inflation reality layer
  TP.KFE.<NUTS> -> Konut Fiyat Endeksi by NUTS2 region — feeds region
                   intelligence ("nereden arsa/ev alayım?")

All responses are disk-cached for a day; EVDS updates monthly, so this
keeps us far under any rate limit while staying fresh enough.
"""
import logging
from typing import Optional

import httpx

from backend.config import settings
from backend.services import cache as cache_service

logger = logging.getLogger("lumos.evds")

BASE_URL = "https://evds3.tcmb.gov.tr/igmevdsms-dis"

CPI_SERIES = "TP.FG.J0"

# NUTS2 housing index series -> human-readable region (province list)
KFE_REGIONS = {
    "TP.KFE.TR10": "İstanbul",
    "TP.KFE.TR51": "Ankara",
    "TP.KFE.TR31": "İzmir",
    "TP.KFE.TR21": "Tekirdağ, Edirne, Kırklareli",
    "TP.KFE.TR22": "Balıkesir, Çanakkale",
    "TP.KFE.TR32": "Aydın, Denizli, Muğla",
    "TP.KFE.TR33": "Manisa, Afyonkarahisar, Kütahya, Uşak",
    "TP.KFE.TR41": "Bursa, Eskişehir, Bilecik",
    "TP.KFE.TR42": "Kocaeli, Sakarya, Düzce, Bolu, Yalova",
    "TP.KFE.TR52": "Konya, Karaman",
    "TP.KFE.TR61": "Antalya, Isparta, Burdur",
    "TP.KFE.TR62": "Adana, Mersin",
    "TP.KFE.TR63": "Hatay, Kahramanmaraş, Osmaniye",
    "TP.KFE.TR7": "İç Anadolu (Kayseri, Sivas, Konya çevresi)",
    "TP.KFE.TR8": "Batı Karadeniz",
    "TP.KFE.TR9": "Doğu Karadeniz (Trabzon çevresi)",
    "TP.KFE.TRA": "Kuzeydoğu Anadolu (Erzurum çevresi)",
    "TP.KFE.TRB": "Ortadoğu Anadolu (Malatya, Van çevresi)",
    "TP.KFE.TRC": "Güneydoğu Anadolu (Gaziantep, Diyarbakır çevresi)",
}

_CACHE_TTL = 60 * 60 * 24  # EVDS publishes monthly; daily refresh is plenty


def is_configured() -> bool:
    return bool(settings.TCMB_EVDS_API_KEY)


def fetch_series(series_code: str, start: str, end: str) -> dict[str, float]:
    """
    Fetch a monthly EVDS series. Dates are dd-mm-yyyy.
    Returns {"YYYY-MM": value} (months zero-padded), cached daily.
    """
    cache_key = f"evds:{series_code}:{start}:{end}"
    cached = cache_service.get(cache_key)
    if cached is not None:
        return cached

    url = f"{BASE_URL}/series={series_code}&startDate={start}&endDate={end}&type=json"
    resp = httpx.get(url, headers={"key": settings.TCMB_EVDS_API_KEY}, timeout=15)
    resp.raise_for_status()
    payload = resp.json()

    field = series_code.replace(".", "_")
    result: dict[str, float] = {}
    for item in payload.get("items", []):
        raw = item.get(field)
        tarih = item.get("Tarih", "")  # "2026-5"
        if raw is None or "-" not in tarih:
            continue
        year, month = tarih.split("-")
        result[f"{year}-{int(month):02d}"] = float(raw)

    if result:
        cache_service.set(cache_key, result, ttl=_CACHE_TTL)
    return result


def get_live_cpi_index(start: str = "01-01-2020") -> Optional[dict[str, float]]:
    """
    Live TÜFE index keyed by YYYY-MM, or None when the key is missing or
    the call fails — callers fall back to the bundled static index.
    """
    if not is_configured():
        return None
    try:
        from datetime import date
        end = date.today().strftime("%d-%m-%Y")
        index = fetch_series(CPI_SERIES, start, end)
        return index or None
    except Exception as exc:
        logger.warning("EVDS CPI fetch failed (%s) — falling back to static index", exc)
        return None


def get_regional_housing_indices(start: str = "01-01-2023") -> dict[str, dict]:
    """
    Housing price index history for every NUTS2 region.
    Returns {series_code: {"region": name, "index": {month: value}}}.
    Regions whose fetch fails are skipped (partial data beats no data).
    """
    from datetime import date
    end = date.today().strftime("%d-%m-%Y")

    out: dict[str, dict] = {}
    for code, region in KFE_REGIONS.items():
        try:
            index = fetch_series(code, start, end)
            if index:
                out[code] = {"region": region, "index": index}
        except Exception as exc:
            logger.warning("EVDS KFE fetch failed for %s: %s", code, exc)
    return out
