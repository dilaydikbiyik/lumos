"""
Listing bridge — filter-ready deep links to real estate portals.

Lumos never scrapes or hosts listings (legal risk, brittle, against ToS).
Instead it hands the user a pre-filtered search URL on sites they already
trust. Zero API keys, zero maintenance burden.

GERÇEKÇİLİK NOTU (2026-07-10 doğrulaması):
- Emlakjet kalıpları curl ile doğrulandı: /satilik-arsa/edirne-kesan → 200,
  /satilik-konut/edirne-kesan-cumhuriyet-mahallesi (MAHALLE seviyesi!) → 200.
- Sahibinden bot koruması dış doğrulamayı engelliyor (her yola 403);
  kanonik public kalıpları (satilik-arsa/satilik-daire) kullanıyoruz ve
  köy/mahalle gibi mikro konumlar için sitenin kendi arama rotasına
  (query_text) düşüyoruz — kırık derin link riskine karşı en sağlam yol.

Market-aware: TR keeps hand-tuned deep URLs; other markets use their
pack's search templates.
"""
from typing import Optional
from urllib.parse import quote

from backend.markets import get_market_pack

_TR_CHAR_MAP = str.maketrans("çğıöşüÇĞİÖŞÜ", "cgiosucgiosu")

# kategori -> (sahibinden slug, emlakjet slug)
_CATEGORY_SLUGS = {
    "arsa": ("satilik-arsa", "satilik-arsa"),
    "daire": ("satilik-daire", "satilik-konut"),
    "konut": ("satilik-daire", "satilik-konut"),
}


def _slug(text: str) -> str:
    """Türkçe karakterleri sadeleştirip URL parçasına çevirir: 'Keşan' → 'kesan'."""
    return "-".join(text.strip().lower().translate(_TR_CHAR_MAP).split())


def _tr_links(il: str, ilce: str, asset_type: str, detail: Optional[str] = None) -> list[dict]:
    sahibinden_slug, emlakjet_slug = _CATEGORY_SLUGS.get(asset_type, _CATEGORY_SLUGS["konut"])

    il_s = _slug(il)
    ilce_s = _slug(ilce) if ilce else ""
    location = f"{il_s}-{ilce_s}" if ilce_s else il_s

    if detail and detail.strip():
        # Köy/mahalle gibi mikro konum: Sahibinden'de derin yol garantisi yok →
        # sitenin kendi aramasına tam metinle düşmek en gerçekçi davranış.
        text = " ".join(part for part in (il, ilce, detail, asset_type) if part).strip()
        return [
            {
                "site": "Sahibinden",
                "url": f"https://www.sahibinden.com/arama?query_text={quote(text)}",
            },
            {
                # Emlakjet mahalle-seviyesi yolu destekliyor (canlı doğrulandı)
                "site": "Emlakjet",
                "url": f"https://www.emlakjet.com/{emlakjet_slug}/{location}-{_slug(detail)}",
            },
        ]

    return [
        {"site": "Sahibinden", "url": f"https://www.sahibinden.com/{sahibinden_slug}/{location}"},
        {"site": "Emlakjet", "url": f"https://www.emlakjet.com/{emlakjet_slug}/{location}"},
    ]


def build_listing_links(
    il: str, ilce: str, asset_type: str,
    market: str = "TR", detail: Optional[str] = None,
) -> list[dict]:
    if (market or "TR").upper() == "TR":
        return _tr_links(il, ilce, asset_type, detail)

    pack = get_market_pack(market)
    query = quote(" ".join(p for p in (il.strip(), ilce.strip(), detail or "", asset_type) if p))
    return [
        {"site": site.name, "url": site.search_template.format(query=query)}
        for site in pack.listing_sites
    ]
