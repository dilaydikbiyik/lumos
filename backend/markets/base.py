"""
Market Pack — everything country-specific lives in one object.

The core rule of Lumos's globalization architecture: application code
never hardcodes a country. It asks the user's pack. Adding a country =
adding a pack module + data adapters, not rewriting features.

Content fields (regulator, tax_note, broker_note) are EDUCATIONAL
summaries with an explicit local-professional disclaimer — Lumos never
gives tax or legal advice in any market.
"""
from dataclasses import dataclass, field


@dataclass(frozen=True)
class ListingSite:
    name: str
    # {query} is replaced with an URL-encoded "il ilçe arsa"-style search
    search_template: str


@dataclass(frozen=True)
class MarketPack:
    code: str                     # "TR", "US", "DE"
    name: str
    currency: str                 # ISO 4217
    currency_symbol: str
    locale: str                   # BCP-47, drives number formatting on the client
    languages: list[str]

    # ── Data source availability (adapters check these before wiring) ──
    inflation_source: str         # "tcmb_evds" | "none" (roadmap: "fred", "destatis")
    housing_index_source: str     # "tcmb_evds" | "none"
    default_index_ticker: str     # yfinance ticker for the local blue-chip index

    # ── Real-estate listing bridge ──
    listing_sites: list[ListingSite] = field(default_factory=list)

    # ── Educational, locale-specific content (NOT advice) ──
    regulator: str = ""
    broker_note: str = ""
    tax_note: str = ""
    fear_options: dict[str, str] = field(default_factory=dict)

    disclaimer: str = (
        "Educational content only — rules change and individual situations differ. "
        "Always confirm with a licensed local professional."
    )
