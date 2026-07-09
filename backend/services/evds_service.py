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


# ── İl bazında konut birim fiyatları (TL/m², çeyreklik, 2010→bugün) ──────────
# TCMB bie_birimfiyat veri grubu: ulusal + 81 il. NUTS2 bölge endeksinden çok
# daha somut: "Muğla'da m² 79.110 TL" — kullanıcının istediği spesifiklik.

UNIT_PRICE_PREFIX = "TP.BIRIMFIYAT."

PROVINCES: dict[str, str] = {
    "IST": "İstanbul", "ANK": "Ankara", "IZM": "İzmir",
    "ADANA": "Adana", "ADIYAMAN": "Adıyaman", "AFYON": "Afyonkarahisar",
    "AGRI": "Ağrı", "AMASYA": "Amasya", "ANTALYA": "Antalya",
    "ARTVIN": "Artvin", "AYDIN": "Aydın", "BALIKESIR": "Balıkesir",
    "BILECIK": "Bilecik", "BINGOL": "Bingöl", "BITLIS": "Bitlis",
    "BOLU": "Bolu", "BURDUR": "Burdur", "BURSA": "Bursa",
    "CANAKKALE": "Çanakkale", "CANKIRI": "Çankırı", "CORUM": "Çorum",
    "DENIZLI": "Denizli", "DIYARBAKIR": "Diyarbakır", "EDIRNE": "Edirne",
    "ELAZIG": "Elazığ", "ERZINCAN": "Erzincan", "ERZURUM": "Erzurum",
    "ESKISEHIR": "Eskişehir", "ANTEP": "Gaziantep", "GIRESUN": "Giresun",
    "GUMUSHANE": "Gümüşhane", "HAKKARI": "Hakkari", "HATAY": "Hatay",
    "ISPARTA": "Isparta", "MERSIN": "Mersin", "KARS": "Kars",
    "KASTAMONU": "Kastamonu", "KAYSERI": "Kayseri", "KIRKLARELI": "Kırklareli",
    "KIRSEHIR": "Kırşehir", "KOCAELI": "Kocaeli", "KONYA": "Konya",
    "KUTAHYA": "Kütahya", "MALATYA": "Malatya", "MANISA": "Manisa",
    "MARAS": "Kahramanmaraş", "MARDIN": "Mardin", "MUGLA": "Muğla",
    "MUS": "Muş", "NEVSEHIR": "Nevşehir", "NIGDE": "Niğde",
    "ORDU": "Ordu", "RIZE": "Rize", "SAKARYA": "Sakarya",
    "SAMSUN": "Samsun", "SIIRT": "Siirt", "SINOP": "Sinop",
    "SIVAS": "Sivas", "TEKIRDAG": "Tekirdağ", "TOKAT": "Tokat",
    "TRABZON": "Trabzon", "TUNCELI": "Tunceli", "URFA": "Şanlıurfa",
    "USAK": "Uşak", "VAN": "Van", "YOZGAT": "Yozgat",
    "ZONGULDAK": "Zonguldak", "AKSARAY": "Aksaray", "BAYBURT": "Bayburt",
    "KARAMAN": "Karaman", "KIRIKKALE": "Kırıkkale", "BATMAN": "Batman",
    "SIRNAK": "Şırnak", "BARTIN": "Bartın", "ARDAHAN": "Ardahan",
    "IGDIR": "Iğdır", "YALOVA": "Yalova", "KARABUK": "Karabük",
    "KILIS": "Kilis", "OSMANIYE": "Osmaniye", "DUZCE": "Düzce",
}


def _quarter_to_month(quarter_label: str) -> str:
    """'2026-Q1' → '2026-03' (çeyrek sonu ayı — enflasyon kıyası için)."""
    year, q = quarter_label.split("-Q")
    return f"{year}-{int(q) * 3:02d}"


def fetch_quarterly_series_batch(codes: list[str], start: str, end: str) -> dict[str, dict[str, float]]:
    """
    Çeyreklik serileri TOPLU çeker (tek istekte ~15 seri) — 82 il için
    6 istek, günlük cache. Dönüş: {code: {"YYYY-MM": değer}} (çeyrek→ay).
    """
    cache_key = f"evds_batch_q:{hashlib_key(codes)}:{start}:{end}"
    cached = cache_service.get(cache_key)
    if cached is not None:
        return cached

    out: dict[str, dict[str, float]] = {c: {} for c in codes}
    CHUNK = 15
    for i in range(0, len(codes), CHUNK):
        chunk = codes[i:i + CHUNK]
        url = f"{BASE_URL}/series={'-'.join(chunk)}&startDate={start}&endDate={end}&type=json"
        resp = httpx.get(url, headers={"key": settings.TCMB_EVDS_API_KEY}, timeout=20)
        resp.raise_for_status()
        for item in resp.json().get("items", []):
            tarih = item.get("Tarih", "")
            if "-Q" not in tarih:
                continue
            month = _quarter_to_month(tarih)
            for code in chunk:
                raw = item.get(code.replace(".", "_"))
                if raw is not None:
                    out[code][month] = float(raw)

    if any(out.values()):
        cache_service.set(cache_key, out, ttl=_CACHE_TTL)
    return out


def hashlib_key(codes: list[str]) -> str:
    import hashlib
    return hashlib.sha1(",".join(sorted(codes)).encode()).hexdigest()[:12]


def get_province_unit_prices() -> dict[str, dict]:
    """
    81 il + 3 büyükşehir için TL/m² birim fiyat geçmişi (2010→bugün, çeyreklik).
    Dönüş: {suffix: {"name": il_adı, "prices": {"YYYY-MM": tl_m2}}}
    """
    from datetime import date as _date

    if not is_configured():
        return {}
    codes = [UNIT_PRICE_PREFIX + suffix for suffix in PROVINCES]
    try:
        batch = fetch_quarterly_series_batch(
            codes, start="01-01-2010", end=_date.today().strftime("%d-%m-%Y")
        )
    except Exception as exc:
        logger.warning("province unit prices unavailable: %s", exc)
        return {}

    return {
        suffix: {"name": name, "prices": batch.get(UNIT_PRICE_PREFIX + suffix, {})}
        for suffix, name in PROVINCES.items()
        if batch.get(UNIT_PRICE_PREFIX + suffix)
    }
