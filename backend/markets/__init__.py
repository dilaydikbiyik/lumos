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
        }
        for p in MARKET_PACKS.values()
    ]
