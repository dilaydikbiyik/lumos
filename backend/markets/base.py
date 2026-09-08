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
    inflation_source: str         # "tcmb_evds" | "bls" | "eurostat" | "none"
    housing_index_source: str     # "tcmb_evds" | "eurostat" | "none"
    default_index_ticker: str     # yfinance ticker for the local blue-chip index
    rent_index_source: str = "none"   # "bls" | "eurostat" | "none"
    # A NATIONAL house-price index and a province-by-province BREAKDOWN are
    # different data products. Eurostat gives Germany the first but not the
    # second, so gating the province table on housing_index_source showed a
    # German reader Turkish provinces priced in lira. This flag is what the
    # per-province table keys on.
    regional_housing_breakdown: bool = False

    # ── Real-estate listing bridge ──
    listing_sites: list[ListingSite] = field(default_factory=list)

    # ── Country-specific planning inputs ──
    # These were Turkish constants living in assumptions.py. A 39% mortgage
    # rate and a 4% deed fee are facts about Türkiye, not about the world;
    # applying them to a German buyer produced a confident, nonsensical
    # answer. Every rate below is a documented ASSUMPTION shown to the user.
    mortgage_rate_pct: float = 39.0
    mortgage_term_years: int = 10
    # Buyer-side transfer tax / duty on a property purchase.
    transfer_tax_pct: float = 4.0
    # Estate-agent commission charged to the buyer, before VAT.
    agency_commission_pct: float = 2.0
    vat_pct: float = 20.0
    # Yearly ownership cost as a share of home value (dues, insurance, upkeep).
    annual_upkeep_pct: float = 1.0
    # Gross rental yield, used to back out a home price from a rent figure.
    gross_rental_yield: float = 0.05
    # Real (above-inflation) spreads for the planning projections.
    housing_real_spread_pct: float = 0.0
    rent_real_spread_pct: float = 0.0
    portfolio_real_spread_pct: float = 3.0
    # Fallback used only when live inflation cannot be read at all.
    inflation_fallback_pct: float = 40.0

    # ── Investable universe ──
    # Which tickers this market's users can ACTUALLY buy. Empty = use the
    # shared default universe. Getting this wrong is not cosmetic: EU retail
    # investors are barred from US-domiciled ETFs, so recommending SPY to a
    # German user names something they cannot legally purchase.
    asset_universe: list[dict] = field(default_factory=list)
    reit_assets: list[dict] = field(default_factory=list)
    # The defensive sleeve is subject to the same legal reality as the growth
    # sleeve: BIL and BND are US-domiciled, so a German portfolio cannot hold
    # them either. Empty = use the shared defaults.
    cash_asset: dict = field(default_factory=dict)
    bond_asset: dict = field(default_factory=dict)

    # ── Educational, locale-specific content (NOT advice) ──
    #
    # Language and market are INDEPENDENT axes. Someone reading the English UI
    # may invest in the Turkish market, and someone reading Turkish may look at
    # Germany. Writing each pack's copy in a single national language quietly
    # welded the two together, so an English reader who picked DE got German
    # prose. Every field below is therefore {lang: text}, resolved with `.say()`.
    regulator: str = ""
    broker_note: dict[str, str] = field(default_factory=dict)
    tax_note: dict[str, str] = field(default_factory=dict)
    fear_options: dict[str, dict[str, str]] = field(default_factory=dict)
    disclaimer: dict[str, str] = field(default_factory=dict)

    def say(self, field_name: str, lang: str = "en") -> str:
        """
        A localized pack string. Falls back to English, then to whatever the
        pack has — a market must never render blank because one translation
        is missing.
        """
        value = getattr(self, field_name) or {}
        if not isinstance(value, dict):
            return value
        return value.get(lang) or value.get("en") or next(iter(value.values()), "")

    def fears(self, lang: str = "en") -> dict[str, str]:
        """Fear check-in options in the reader's language, keyed by stable id."""
        return {
            key: (labels.get(lang) or labels.get("en") or next(iter(labels.values()), ""))
            for key, labels in self.fear_options.items()
        }
