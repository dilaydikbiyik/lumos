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
    inflation_source: str         # "tcmb_evds" | "bls" | "eurostat" | "bundesbank" | "none"
    housing_index_source: str     # "tcmb_evds" | "eurostat" | "none"
    default_index_ticker: str     # yfinance ticker for the local blue-chip index
    rent_index_source: str = "none"   # "bls" | "eurostat" | "bundesbank" | "none"
    # A NATIONAL house-price index and a SUB-NATIONAL breakdown are different
    # data products, and they need not come from the same provider: Germany's
    # national index is Eurostat's while its only free regional figures are
    # the Bundesbank's. A boolean could not say that, so this names the
    # regional source the same way housing_index_source names the national one.
    regional_housing_source: str = "none"   # tcmb_evds | fred | bundesbank | none

    @property
    def regional_housing_breakdown(self) -> bool:
        """Whether this market has a sub-national table at all."""
        return self.regional_housing_source != "none"

    # ── Beginner news digest ──
    # Headlines are a market fact, not a language one: a user investing in the
    # US does not need Turkish economy headlines, whatever language they read
    # in. Empty means the digest simply doesn't run for that market.
    news_feeds: list[str] = field(default_factory=list)

    # ── Real-estate listing bridge ──
    listing_sites: list[ListingSite] = field(default_factory=list)
    # Example place names for the micro-location inputs. A country fact like
    # any other: the Texas card was offering "e.g. Keşan" as a district, which
    # is the same category of mistake as pricing Texas in lira.
    example_district: str = ""
    example_locality: str = ""
    # A ticker and an asset a reader of THIS market would recognise, for the
    # "add a holding" placeholders. These were written per LANGUAGE, which is
    # the wrong axis: a Turkish reader in the US market was shown THYAO.IS.
    example_ticker: str = ""
    example_asset_name: str = ""
    # What this country calls its first-level subdivision. The client holds
    # the translations, keyed by this value, so a new market picks an existing
    # kind rather than shipping three more words.
    area_kind: str = "region"          # province | state | region
    # asset_type id -> the word that market's portals actually search for.
    # The ids are Turkish because Türkiye was the first market; feeding them
    # to ImmoScout24 sent a German buyer looking for "daire".
    listing_terms: dict[str, str] = field(default_factory=dict)

    # ── Country-specific planning inputs ──
    # These were Turkish constants living in assumptions.py. A 39% mortgage
    # rate and a 4% deed fee are facts about Türkiye, not about the world;
    # applying them to a German buyer produced a confident, nonsensical
    # answer. Every rate below is a documented ASSUMPTION shown to the user.
    # Where the mortgage rate comes from, and the value to use when that
    # source is silent. A rate constant goes stale in the direction that
    # flips a rent-vs-buy verdict, so it is read live where a free source
    # exists and falls back to the documented assumption where none does.
    mortgage_rate_source: str = "none"   # fred | bundesbank | none
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
    # The savings at which buying physical property becomes realistic here:
    # a customary down payment PLUS the purchase costs, which in most markets
    # cannot be borrowed. Below it the honest answer is "not yet, and here is
    # the instrument that gives you property exposure meanwhile" rather than
    # a smaller flat. A documented assumption, shown to the user, and a fact
    # about a country like every other number in this file.
    property_entry_threshold: float = 1_000_000.0
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
    # Who bears the purchase taxes, and on what basis. This was one sentence
    # inside the shared rent-vs-buy footnote asserting that "by law half
    # belongs to the seller" — true of Türkiye's tapu harcı and false of both
    # German Grunderwerbsteuer and US transfer taxes. A legal claim cannot be
    # shared across jurisdictions.
    transfer_cost_note: dict[str, str] = field(default_factory=dict)
    fear_options: dict[str, dict[str, str]] = field(default_factory=dict)
    disclaimer: dict[str, str] = field(default_factory=dict)

    def say(self, field_name: str, lang: str = "en") -> str:
        """
        A localized pack string.

        Resolution order: this pack's own wording, then the shared default
        for fields that have one, then English, then whatever the pack has.
        A market must never render blank because one translation is missing,
        and a new pack must not have to restate boilerplate to exist.
        """
        value = getattr(self, field_name) or {}
        if not isinstance(value, dict):
            return value
        own = value.get(lang) or value.get("en")
        if own:
            return own

        from backend.i18n import t

        key = f"market.{field_name}"
        shared = t(key, lang)
        if shared != key:
            return shared
        return next(iter(value.values()), "")

    def fears(self, lang: str = "en") -> dict[str, str]:
        """Fear check-in options in the reader's language, keyed by stable id."""
        return {
            key: (labels.get(lang) or labels.get("en") or next(iter(labels.values()), ""))
            for key, labels in self.fear_options.items()
        }
