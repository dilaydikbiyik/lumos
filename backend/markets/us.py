"""
United States — Market Pack.

Live inflation and rent come from the BLS public API with no key, so real
returns work out of the box.

House prices were the honest gap for a while: BLS publishes a rent index,
which measures what it costs to OCCUPY a home — not what homes sell for, and
substituting one for the other would quietly corrupt every buy-vs-rent
verdict. That gap is now closed by FRED's FHFA All-Transactions House Price
Index, a genuine price index published nationally AND for all 50 states plus
DC — so the US gets a real state-by-state breakdown, the equivalent of the
81-province table in Türkiye.

FRED needs a free key. Without it fred_service reports unavailable and these
features degrade to their stated assumptions rather than guessing.
"""
from backend.markets.base import ListingSite, MarketPack

US = MarketPack(
    code="US",
    name="United States",
    currency="USD",
    currency_symbol="$",
    locale="en-US",
    languages=["en"],

    inflation_source="bls",        # CPI-U, monthly, no key
    housing_index_source="fred",   # FHFA All-Transactions HPI, quarterly
    regional_housing_breakdown=True,  # 50 states + DC, same series family
    rent_index_source="bls",       # rent of primary residence
    default_index_ticker="^GSPC",

    listing_sites=[
        ListingSite("Zillow", "https://www.zillow.com/homes/{query}_rb/"),
        ListingSite("Realtor", "https://www.realtor.com/realestateandhomes-search/{query}"),
    ],

    # ── Planning inputs (US reality) ──
    mortgage_rate_pct=6.5,
    mortgage_term_years=30,
    # Closing costs rather than a single deed tax: transfer taxes vary by
    # state and county, and lender/title/escrow fees are the larger share.
    transfer_tax_pct=2.5,
    # Buyer-side agent commission is negotiable and, since the 2024 NAR
    # settlement, no longer assumed to be seller-paid.
    agency_commission_pct=2.5,
    vat_pct=0.0,                   # no VAT on residential purchases
    annual_upkeep_pct=1.5,         # taxes, insurance and maintenance run high
    gross_rental_yield=0.06,
    housing_real_spread_pct=1.0,
    rent_real_spread_pct=0.0,
    portfolio_real_spread_pct=4.5,
    inflation_fallback_pct=3.0,

    asset_universe=[
        {"ticker": "SPY", "name": "S&P 500 ETF", "category": "stocks"},
        {"ticker": "QQQ", "name": "Nasdaq 100 ETF", "category": "stocks"},
        {"ticker": "VXUS", "name": "Total International Stock ETF", "category": "stocks"},
        {"ticker": "GLD", "name": "Gold ETF", "category": "gold"},
    ],
    reit_assets=[
        {"ticker": "VNQ", "name": "Vanguard Real Estate ETF", "category": "reit"},
        {"ticker": "SCHH", "name": "Schwab US REIT ETF", "category": "reit"},
    ],

    regulator="SEC / FINRA",
    broker_note={
        "en": (
            "Buying stocks and ETFs requires a brokerage account (Fidelity, "
            "Schwab, Vanguard, or an app-based broker). Most accounts open "
            "online in minutes. Check for SIPC membership, which protects your "
            "assets if the broker itself fails — it does not protect you from "
            "investment losses."
        ),
        "tr": (
            "Hisse ve ETF almak için bir aracı kurum hesabı gerekir (Fidelity, "
            "Schwab, Vanguard ya da uygulama tabanlı aracılar). Çoğu hesap "
            "dakikalar içinde çevrimiçi açılır. Kurumun SIPC üyeliğine bak: bu, "
            "aracı kurumun batması hâlinde varlıklarını korur — yatırım "
            "zararlarına karşı bir koruma değildir."
        ),
        "de": (
            "Für Aktien und ETFs brauchst du ein Brokerkonto (Fidelity, Schwab, "
            "Vanguard oder App-Broker). Die meisten Konten sind in Minuten "
            "online eröffnet. Achte auf die SIPC-Mitgliedschaft: sie schützt "
            "dein Vermögen bei einer Broker-Insolvenz — nicht vor Kursverlusten."
        ),
    },
    tax_note={
        "en": (
            "General information: investment gains are taxed differently by how "
            "long you held the position, with lower rates applying past one "
            "year. Tax-advantaged accounts (401(k), IRA, Roth IRA) shelter "
            "growth and are usually the first stop before a taxable brokerage "
            "account. Rules change and vary by state — confirm your situation "
            "with a CPA or licensed tax professional."
        ),
        "tr": (
            "Genel bilgi: yatırım kazançları elde tutma süresine göre farklı "
            "vergilendirilir; bir yılı aşan pozisyonlarda oran düşer. Vergi "
            "avantajlı hesaplar (401(k), IRA, Roth IRA) getiriyi korur ve "
            "genellikle vergiye tabi bir aracı kurum hesabından önce gelir. "
            "Kurallar değişir ve eyaletten eyalete farklılık gösterir — kendi "
            "durumun için lisanslı bir mali müşavire danış."
        ),
        "de": (
            "Allgemeine Information: Kapitalgewinne werden nach Haltedauer "
            "unterschiedlich besteuert; ab einem Jahr gelten niedrigere Sätze. "
            "Steuerbegünstigte Konten (401(k), IRA, Roth IRA) schützen die "
            "Erträge und kommen meist vor einem steuerpflichtigen Depot. Regeln "
            "ändern sich und unterscheiden sich je Bundesstaat — kläre deine "
            "Situation mit einer Steuerfachperson."
        ),
    },
    fear_options={
        "losing_money": {
            "en": "I'm afraid of losing money",
            "tr": "Para kaybetmekten korkuyorum",
            "de": "Ich habe Angst, Geld zu verlieren",
        },
        "being_scammed": {
            "en": "I'm afraid of being scammed",
            "tr": "Kandırılmaktan korkuyorum",
            "de": "Ich habe Angst, betrogen zu werden",
        },
        "not_understanding": {
            "en": "I don't understand any of this",
            "tr": "Hiçbir şey anlamıyorum",
            "de": "Ich verstehe davon nichts",
        },
        "messing_up": {
            "en": "I'm afraid I'll mess it up",
            "tr": "Batırmaktan korkuyorum",
            "de": "Ich habe Angst, etwas falsch zu machen",
        },
    },
    disclaimer={
        "en": (
            "Educational content only — rules change and individual situations "
            "differ. Always confirm with a licensed local professional."
        ),
        "tr": (
            "Yalnızca eğitim amaçlıdır — kurallar değişir ve herkesin durumu "
            "farklıdır. Her zaman yerel lisanslı bir profesyonele doğrulat."
        ),
        "de": (
            "Nur zu Bildungszwecken — Regeln ändern sich und jede Situation ist "
            "anders. Bitte bestätige alles mit einer lizenzierten Fachperson."
        ),
    },
)
