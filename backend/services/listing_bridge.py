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
  with the province-district slug.

  It used to fall back to the site's own `?query_text=` search for
  micro-locations. That turned out to be worse, not more robust: query_text
  searches listing TITLES rather than filtering by location, so a search for
  "Kırklareli Lüleburgaz Emirali" came back filtered to the PROVINCE only —
  the district the user picked was silently dropped. Reported from the app.
  A returned link now always keeps the district, and any finer location
  travels beside it as `manual_filter` for the UI to show.

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
        # A micro-location (village / neighbourhood) has no guaranteed deep
        # path on either site, so neither gets one invented for it. What both
        # DO have is a reliable province-district page, and that is where the
        # link lands.
        #
        # Sahibinden used to drop to `?query_text=` here. That is a full-text
        # search over listing TITLES, not a location filter: reported from the
        # app, "Kırklareli + Lüleburgaz + Emirali" came back filtered to
        # Kırklareli alone, because the district and village are not words in
        # the titles. Losing the district the user explicitly chose is worse
        # than not applying the village — so both sites now keep the district
        # and leave the last hop to the site's own filters.
        return [
            {
                "site": "Sahibinden",
                "url": f"https://www.sahibinden.com/{sahibinden_slug}/{location}",
                "manual_filter": detail.strip(),
            },
            {
                # Emlakjet paths resolve only for locations in its own
                # database (ceribasi-koyu → 404, seen live), so the same rule
                # applies: the guaranteed page, not a guessed slug.
                "site": "Emlakjet",
                "url": f"https://www.emlakjet.com/{emlakjet_slug}/{location}",
                "manual_filter": detail.strip(),
            },
        ]

    return [
        {"site": "Sahibinden", "url": f"https://www.sahibinden.com/{sahibinden_slug}/{location}"},
        {"site": "Emlakjet", "url": f"https://www.emlakjet.com/{emlakjet_slug}/{location}"},
    ]


# market code -> verified deep-link builder. Adding a market means adding
# search templates to its pack; adding an entry here is an optional upgrade
# once someone has checked the paths resolve.
_DEEP_LINK_BUILDERS = {"TR": _tr_links}


def build_listing_links(
    il: str, ilce: str, asset_type: str,
    market: str = "TR", detail: Optional[str] = None,
) -> list[dict]:
    # Hand-tuned deep URLs exist only where the paths were verified against
    # the live sites; every other market uses its pack's search templates.
    # Keyed by market because the URLs themselves are, but a pack without an
    # entry here simply gets the generic path — nothing to remember.
    builder = _DEEP_LINK_BUILDERS.get((market or "TR").upper())
    if builder:
        return builder(il, ilce, asset_type, detail)

    pack = get_market_pack(market)
    # The asset_type ids are Turkish ("arsa", "daire") because Türkiye was the
    # first market. Passing them straight into a foreign portal's search box
    # sent a German buyer looking for "daire" on ImmoScout24 — zero results,
    # and no way for them to tell why.
    term = pack.listing_terms.get(asset_type, asset_type)
    query = quote(" ".join(p for p in (il.strip(), ilce.strip(), detail or "", term) if p))
    return [
        {"site": site.name, "url": site.search_template.format(query=query)}
        for site in pack.listing_sites
    ]
