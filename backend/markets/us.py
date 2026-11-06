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
    regional_housing_source="fred",   # 50 states + DC, same series family
    rent_index_source="bls",       # rent of primary residence
    default_index_ticker="^GSPC",
    default_index_name="S&P 500",

    news_feeds=[
        # Public RSS, no key. CNBC's own finance feed and Yahoo Finance.
        "https://www.cnbc.com/id/10000664/device/rss/rss.html",
        "https://finance.yahoo.com/news/rssindex",
    ],

    example_ticker="AAPL",
    example_asset_name="Austin condo",
    area_kind="state",
    example_district="Travis County",
    example_locality="Round Rock",

    listing_terms={"arsa": "land", "daire": "apartment", "konut": "home"},

    listing_sites=[
        ListingSite("Zillow", "https://www.zillow.com/homes/{query}_rb/"),
        ListingSite("Realtor", "https://www.realtor.com/realestateandhomes-search/{query}"),
    ],

    # ── Planning inputs (US reality) ──
    mortgage_rate_source="fred",       # Freddie Mac 30-yr fixed, weekly
    mortgage_rate_pct=6.5,            # used only if FRED is unreachable
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
    # ~20% down on an entry-level home plus ~2.5% closing costs. Lower
    # down payments exist (FHA), but they carry mortgage insurance, so
    # this stays the conservative figure.
    property_entry_threshold=80_000.0,
    # Median sales price of houses sold (Census/HUD via FRED), $393,300 in
    # 2026-Q3.
    typical_home={"source": "fred", "source_name": "FRED", "series": "MSPUS",
                  "fallback": 393_300.0, "as_of": "2026-07"},
    # ~21% APR on US revolving card balances (Federal Reserve G.19 has run in
    # the low twenties), expressed as the monthly periodic rate the issuer
    # actually applies.
    card_monthly_rate_pct=1.75,
    material_debt=500.0,
    position_bands=((1_500.0, 3), (4_000.0, 4)),
    housing_real_spread_pct=1.0,
    rent_real_spread_pct=0.0,
    portfolio_real_spread_pct=4.5,
    inflation_fallback_pct=3.0,

    asset_universe=[
        {"ticker": "SPY", "name": "S&P 500 ETF", "category": "stocks", "overlap": "equity_us"},
        {"ticker": "QQQ", "name": "Nasdaq 100 ETF", "category": "stocks", "overlap": "equity_us"},
        {"ticker": "VXUS", "name": "Total International Stock ETF", "category": "stocks", "overlap": "equity_intl"},
        {"ticker": "GLD", "name": "Gold ETF", "category": "gold"},
    ],
    explorer_stocks=[
        {"ticker": "AAPL", "name": "Apple", "sector": "technology"},
        {"ticker": "AMD", "name": "Advanced Micro Devices", "sector": "technology"},
        {"ticker": "AMZN", "name": "Amazon", "sector": "consumer_discretionary"},
        {"ticker": "AVGO", "name": "Broadcom", "sector": "technology"},
        {"ticker": "BAC", "name": "Bank of America", "sector": "financials"},
        {"ticker": "BRK-B", "name": "Berkshire Hathaway", "sector": "financials"},
        {"ticker": "COST", "name": "Costco", "sector": "consumer_staples"},
        {"ticker": "CVX", "name": "Chevron", "sector": "energy"},
        {"ticker": "DIS", "name": "Walt Disney", "sector": "communication"},
        {"ticker": "GOOGL", "name": "Alphabet", "sector": "communication"},
        {"ticker": "HD", "name": "Home Depot", "sector": "consumer_discretionary"},
        {"ticker": "JNJ", "name": "Johnson & Johnson", "sector": "health_care"},
        {"ticker": "JPM", "name": "JPMorgan Chase", "sector": "financials"},
        {"ticker": "KO", "name": "Coca-Cola", "sector": "consumer_staples"},
        {"ticker": "LLY", "name": "Eli Lilly", "sector": "health_care"},
        {"ticker": "MA", "name": "Mastercard", "sector": "financials"},
        {"ticker": "MCD", "name": "McDonald's", "sector": "consumer_discretionary"},
        {"ticker": "META", "name": "Meta Platforms", "sector": "communication"},
        {"ticker": "MRK", "name": "Merck & Co.", "sector": "health_care"},
        {"ticker": "MSFT", "name": "Microsoft", "sector": "technology"},
        {"ticker": "NFLX", "name": "Netflix", "sector": "communication"},
        {"ticker": "NVDA", "name": "Nvidia", "sector": "technology"},
        {"ticker": "ORCL", "name": "Oracle", "sector": "technology"},
        {"ticker": "PEP", "name": "PepsiCo", "sector": "consumer_staples"},
        {"ticker": "PG", "name": "Procter & Gamble", "sector": "consumer_staples"},
        {"ticker": "TSLA", "name": "Tesla", "sector": "consumer_discretionary"},
        {"ticker": "UNH", "name": "UnitedHealth Group", "sector": "health_care"},
        {"ticker": "V", "name": "Visa", "sector": "financials"},
        {"ticker": "WMT", "name": "Walmart", "sector": "consumer_staples"},
        {"ticker": "XOM", "name": "Exxon Mobil", "sector": "energy"},
    ],
    explorer_as_of="2026-11",
    # ^GSPC is a price index. SPY tracks the S&P 500 with dividends
    # reinvested, which is how the companies are measured.
    explorer_benchmark={"ticker": "SPY", "total_return": True},
    role_alternatives={
        "GLD": [{"ticker": "IAU", "name": "iShares Gold Trust"}],
        "BND": [{"ticker": "AGG", "name": "iShares Core U.S. Aggregate Bond ETF"},
                {"ticker": "IEF", "name": "iShares 7-10 Year Treasury Bond ETF"}],
        "BIL": [{"ticker": "SHV", "name": "iShares 0-1 Year Treasury Bond ETF"}],
    },
    asset_classes=[
        {"key": "cash", "ticker": None, "currency": "USD", "total_return": True},
        {"key": "tbill", "ticker": "BIL", "currency": "USD", "total_return": True, "yield_ticker": "^IRX"},
        {"key": "short_bond", "ticker": "SHY", "currency": "USD", "total_return": True},
        {"key": "bonds", "ticker": "BND", "currency": "USD", "total_return": True},
        {"key": "long_bond", "ticker": "TLT", "currency": "USD", "total_return": True, "yield_ticker": "^TNX"},
        {"key": "gold", "ticker": "GLD", "currency": "USD", "total_return": True},
        {"key": "real_estate", "ticker": "VNQ", "currency": "USD", "total_return": True},
        {"key": "equity_home", "ticker": "SPY", "currency": "USD", "total_return": True},
        {"key": "equity_world", "ticker": "VXUS", "currency": "USD", "total_return": True},
        {"key": "crypto", "ticker": "BTC-USD", "currency": "USD", "total_return": True},
    ],
    reit_assets=[
        {"ticker": "VNQ", "name": "Vanguard Real Estate ETF", "category": "reit"},
        {"ticker": "SCHH", "name": "Schwab US REIT ETF", "category": "reit"},
    ],

    transfer_cost_note={
        "tr": "Bu oran tek bir vergi değil, kapanış masraflarının toplamıdır: devir vergileri eyalete ve ilçeye göre değişir, kredi/tapu sigortası ve emanet ücretleri ise çoğu zaman daha büyük kalemdir. Bazı eyaletlerde devir vergisini geleneksel olarak satıcı öder.",
        "en": "This rate is not a single tax but total closing costs: transfer taxes vary by state and county, and lender, title-insurance and escrow fees are usually the larger share. In some states the transfer tax is customarily paid by the seller.",
        "de": "Dieser Satz ist keine einzelne Steuer, sondern die gesamten Abschlusskosten: Übertragungssteuern variieren je Bundesstaat und County, und Kredit-, Titelversicherungs- und Treuhandgebühren machen meist den größeren Teil aus. In manchen Bundesstaaten zahlt üblicherweise die verkaufende Seite die Übertragungssteuer.",
    },

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
)
