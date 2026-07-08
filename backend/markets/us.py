"""
United States — skeleton Market Pack.

Content researched for educational framing; data adapters (FRED CPI,
Case-Shiller housing) are declared but not wired yet — services check
`inflation_source`/`housing_index_source` and degrade gracefully.
"""
from backend.markets.base import ListingSite, MarketPack

US = MarketPack(
    code="US",
    name="United States",
    currency="USD",
    currency_symbol="$",
    locale="en-US",
    languages=["en"],

    inflation_source="none",       # roadmap: FRED API (CPIAUCSL) — free key
    housing_index_source="none",   # roadmap: FRED Case-Shiller (CSUSHPINSA)
    default_index_ticker="SPY",

    listing_sites=[
        ListingSite("Zillow", "https://www.zillow.com/homes/{query}_rb/"),
        ListingSite("Realtor", "https://www.realtor.com/realestateandhomes-search/{query}"),
    ],

    regulator="SEC / FINRA",
    broker_note=(
        "Buying stocks/ETFs requires a brokerage account (e.g. Fidelity, Schwab, "
        "Vanguard, or app-based brokers). Most accounts open online in minutes; "
        "look for SIPC membership."
    ),
    tax_note=(
        "General info: capital gains are taxed differently by holding period — "
        "positions held over one year qualify for lower long-term rates. "
        "Tax-advantaged accounts (401(k), IRA, Roth IRA) shelter investment "
        "growth and are usually the first stop for beginners."
    ),
    fear_options={
        "losing_money": "I'm afraid of losing money",
        "being_scammed": "I'm afraid of being scammed",
        "not_understanding": "I don't understand any of this",
        "messing_up": "I'm afraid I'll mess it up",
    },
)
