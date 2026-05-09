"""
Hybrid basket service — Phase 3.5.

If the user's budget is below the REAL_ESTATE_THRESHOLD (in TRY),
automatically include REIT ETFs (VNQ, SCHH) in the portfolio mix.

This presents real estate exposure without the capital requirement of buying property.
"""

REAL_ESTATE_THRESHOLD_TRY = 5_000_000  # ~$150k at ~33 TRY/USD

REIT_TICKERS = ["VNQ", "SCHH"]


def should_include_reits(budget: float) -> bool:
    """Return True if the budget is below the real estate purchase threshold."""
    return budget < REAL_ESTATE_THRESHOLD_TRY


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
