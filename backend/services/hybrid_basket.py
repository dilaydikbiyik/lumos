"""
Hybrid basket service.

Below the amount at which buying physical property is realistic, the mix
includes REIT ETFs instead: property exposure without the capital, which is
the honest answer to "I want a flat but I have a tenth of one".

THE THRESHOLD IS A FACT ABOUT A COUNTRY. It used to be a module constant of
5,000,000 TRY compared against every budget in every currency, so an $80,000
American — who can genuinely put a deposit on a house — was told they could
not afford property and handed REITs instead, and the same for a German with
EUR 200,000. The market pack already carries this number as
`property_entry_threshold`, documented and reviewed per market; having a
second, stale answer to the same question was the whole defect.
"""

from backend.markets import get_market_pack

REIT_TICKERS = ["VNQ", "SCHH"]


def should_include_reits(budget: float, market: str = "TR") -> bool:
    """True when the budget is below this market's property entry point."""
    return budget < get_market_pack(market).property_entry_threshold


def get_reit_assets() -> list[dict]:
    """Return the REIT ETF definitions for the portfolio engine."""
    return [
        {
            "ticker": "VNQ",
            "name": "Vanguard Real Estate ETF",
            "category": "reit",
        },
        {
            "ticker": "SCHH",
            "name": "Schwab US REIT ETF",
            "category": "reit",
        },
    ]
