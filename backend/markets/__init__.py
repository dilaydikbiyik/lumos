"""
Market Pack registry — country-specific behavior behind one lookup.

    from backend.markets import get_market_pack
    pack = get_market_pack(user.market)   # unknown codes fall back to TR
"""
from backend.markets.base import MarketPack
from backend.markets.de import DE
from backend.markets.tr import TR
from backend.markets.us import US

MARKET_PACKS: dict[str, MarketPack] = {p.code: p for p in (TR, US, DE)}

DEFAULT_MARKET = "TR"


def get_market_pack(code: str) -> MarketPack:
    """Pack for a market code; unknown codes degrade safely to the TR reference pack."""
    return MARKET_PACKS.get((code or DEFAULT_MARKET).upper(), MARKET_PACKS[DEFAULT_MARKET])


# Where a brand-new account starts, guessed from the language it arrived in.
#
# This is a DEFAULT, not a coupling. Someone reading English is more likely to
# be investing in the US than in Türkiye, and starting them there beats
# starting everyone in a market most of them cannot use. The moment they pick
# either setting it stands on its own: changing language never moves the
# market again, and changing market never moves the language. A language with
# no obvious home market falls to the reference market.
DEFAULT_MARKET_BY_LANGUAGE = {"tr": "TR", "en": "US", "de": "DE"}
REFERENCE_MARKET = "TR"


def default_market_for_language(language: str | None) -> str:
    code = DEFAULT_MARKET_BY_LANGUAGE.get((language or "").lower(), REFERENCE_MARKET)
    return code if code in MARKET_PACKS else REFERENCE_MARKET


def public_markets() -> list[dict]:
    """Market picker payload for the client."""
    return [
        {
            "code": p.code,
            "name": p.name,
            "currency": p.currency,
            "currency_symbol": p.currency_symbol,
            "locale": p.locale,
            "live_inflation": p.inflation_source != "none",
            "live_housing_index": p.housing_index_source != "none",
            "regional_housing_breakdown": p.regional_housing_breakdown,
            "example_district": p.example_district,
            "example_locality": p.example_locality,
            "example_ticker": p.example_ticker,
            "example_asset_name": p.example_asset_name,
            "area_kind": p.area_kind,
        }
        for p in MARKET_PACKS.values()
    ]
