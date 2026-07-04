"""
Listing bridge — filter-ready deep links to real estate portals.

Lumos never scrapes or hosts listings (legal risk, brittle, against ToS).
Instead it hands the user a pre-filtered search URL on sites they already
trust. Zero API keys, zero maintenance burden.
"""
from urllib.parse import quote

_ASSET_TYPE_MAP_SAHIBINDEN = {"arsa": "arsa", "daire": "konut", "konut": "konut"}


def build_listing_links(il: str, ilce: str, asset_type: str) -> list[dict]:
    il_q = quote(il.strip().lower())
    ilce_q = quote(ilce.strip().lower()) if ilce else ""
    sahibinden_type = _ASSET_TYPE_MAP_SAHIBINDEN.get(asset_type, "konut")

    location_path = f"{il_q}-{ilce_q}" if ilce_q else il_q

    return [
        {
            "site": "Sahibinden",
            "url": f"https://www.sahibinden.com/{sahibinden_type}/{location_path}",
        },
        {
            "site": "Emlakjet",
            "url": f"https://www.emlakjet.com/{sahibinden_type}-{location_path}/",
        },
    ]
