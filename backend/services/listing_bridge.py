"""
Listing bridge — filter-ready deep links to real estate portals.

Lumos never scrapes or hosts listings (legal risk, brittle, against ToS).
Instead it hands the user a pre-filtered search URL on sites they already
trust. Zero API keys, zero maintenance burden.

REALISM NOTE (verified live 2026-07-10):
- Emlakjet province-district patterns verified via curl:
  /satilik-arsa/edirne-kesan → 200. Quarter/village paths resolve ONLY for
  slugs in the site's own database (cumhuriyet-mahallesi → 200 but
  ceribasi-koyu → 404) — so we never invent a path from free-text detail;
  we land on the district page instead.
- Sahibinden's bot protection blocks external verification (403 on every
  path); we use the canonical public patterns (satilik-arsa/satilik-daire)
  and fall back to the site's own search route (query_text) for
  micro-locations like villages — the most robust defence against broken
  deep links.

Market-aware: TR keeps hand-tuned deep URLs; other markets use their
pack's search templates.
"""
from typing import Optional
from urllib.parse import quote

from backend.markets import get_market_pack

_TR_CHAR_MAP = str.maketrans("çğıöşüÇĞİÖŞÜ", "cgiosucgiosu")

# category -> (sahibinden slug, emlakjet slug)
_CATEGORY_SLUGS = {
    "arsa": ("satilik-arsa", "satilik-arsa"),
    "daire": ("satilik-daire", "satilik-konut"),
    "konut": ("satilik-daire", "satilik-konut"),
}


def _slug(text: str) -> str:
    """Simplifies Turkish characters into a URL slug: 'Keşan' → 'kesan'."""
    return "-".join(text.strip().lower().translate(_TR_CHAR_MAP).split())


def _tr_links(il: str, ilce: str, asset_type: str, detail: Optional[str] = None) -> list[dict]:
    sahibinden_slug, emlakjet_slug = _CATEGORY_SLUGS.get(asset_type, _CATEGORY_SLUGS["konut"])

    il_s = _slug(il)
    ilce_s = _slug(ilce) if ilce else ""
    location = f"{il_s}-{ilce_s}" if ilce_s else il_s

    if detail and detail.strip():
        # Micro-location (village/quarter): no guaranteed deep path on
        # Sahibinden → falling back to the site's own full-text search is
        # the most realistic behaviour.
        text = " ".join(part for part in (il, ilce, detail, asset_type) if part).strip()
        return [
            {
                "site": "Sahibinden",
                "url": f"https://www.sahibinden.com/arama?query_text={quote(text)}",
            },
            {
                # We NEVER invent a village slug: Emlakjet paths resolve
                # only for locations in its own database (ceribasi-koyu → 404
                # seen live). Landing on the guaranteed province-district page
                # and leaving the micro filter to the site is the honest move.
                "site": "Emlakjet",
                "url": f"https://www.emlakjet.com/{emlakjet_slug}/{location}",
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
