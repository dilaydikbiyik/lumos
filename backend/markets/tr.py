"""
Türkiye — the reference Market Pack (fully wired: live TCMB data,
listing bridge, localized fear check-in).
"""
from backend.markets.base import ListingSite, MarketPack

TR = MarketPack(
    code="TR",
    name="Türkiye",
    currency="TRY",
    currency_symbol="₺",
    locale="tr-TR",
    languages=["tr", "en"],

    inflation_source="tcmb_evds",      # live CPI (backend/services/evds_service.py)
    housing_index_source="tcmb_evds",  # housing price index for 19 NUTS2 regions
    rent_index_source="none",          # no separate rent index — spread off CPI
    default_index_ticker="XU100.IS",

    # ── Planning inputs ──
    # These were global constants in assumptions.py until US and DE arrived
    # and made it obvious they were Turkish facts all along.
    mortgage_rate_pct=39.0,
    mortgage_term_years=10,
    transfer_tax_pct=4.0,       # tapu harcı — legally 2/2, buyer often absorbs all
    agency_commission_pct=2.0,  # capped per side by regulation, VAT on top
    vat_pct=20.0,
    annual_upkeep_pct=1.0,
    gross_rental_yield=0.05,
    housing_real_spread_pct=0.0,
    rent_real_spread_pct=0.0,
    portfolio_real_spread_pct=3.0,
    inflation_fallback_pct=40.0,

    # Stated explicitly rather than inherited from the shared file, so all
    # three markets describe themselves. These are the assets Türkiye has
    # always been offered: local equities first, then foreign ETFs, which a
    # Turkish broker can reach only with overseas-market access — a caveat the
    # first-investment guide spells out.
    asset_universe=[
        {"ticker": "XU100.IS", "name": "BIST 100 (Türkiye Hisseleri)", "category": "stocks"},
        {"ticker": "SPY", "name": "S&P 500 ETF", "category": "stocks"},
        {"ticker": "QQQ", "name": "Nasdaq 100 ETF", "category": "stocks"},
        {"ticker": "GLD", "name": "Gold ETF", "category": "gold"},
    ],
    reit_assets=[
        {"ticker": "VNQ", "name": "Vanguard Real Estate ETF", "category": "reit"},
        {"ticker": "SCHH", "name": "Schwab US REIT ETF", "category": "reit"},
    ],

    listing_sites=[
        ListingSite("Sahibinden", "https://www.sahibinden.com/arama?query_text={query}"),
        ListingSite("Emlakjet", "https://www.emlakjet.com/arama/?q={query}"),
    ],

    regulator="SPK (Sermaye Piyasası Kurulu)",
    broker_note={
        "tr": (
            "Hisse/fon almak için SPK lisanslı bir aracı kurumda hesap gerekir "
            "(ör. banka aracı kurumları veya dijital aracılar). Hesap açılışı "
            "çoğunlukla uzaktan kimlik doğrulama ile aynı gün tamamlanır. "
            "Yurtdışı borsalarda işlem gören ETF'ler için kurumun yurtdışı "
            "piyasa hizmeti vermesi gerekir; bu ayrı bir başvuru ve döviz "
            "dönüşümü ister."
        ),
        "en": (
            "Buying stocks or funds requires an account at a brokerage licensed "
            "by the Turkish regulator; most open the same day with remote "
            "identity verification. ETFs listed on foreign exchanges need a "
            "broker offering overseas market access, which is a separate "
            "application and involves currency conversion."
        ),
        "de": (
            "Für Aktien und Fonds brauchst du ein Konto bei einem in der Türkei "
            "lizenzierten Broker; die Eröffnung erfolgt meist am selben Tag per "
            "Fern-Identifikation. Für ETFs an ausländischen Börsen muss der "
            "Broker Auslandsmärkte anbieten — ein separater Antrag mit "
            "Währungsumtausch."
        ),
    },
    tax_note={
        "tr": (
            "Vergilendirme, varlık türüne ve edinim tarihine göre değişir; "
            "kurallar zaman içinde güncellenir. Gayrimenkulde tapu harcı alım "
            "anında doğar, satış hâlinde ise değer artış kazancı vergisi "
            "gündeme gelebilir. Hesaplamalarımız evde oturmaya/varlığı elde "
            "tutmaya devam ettiğin varsayımına dayanır ve satış vergilerini "
            "içermez. Kendi durumun için güncel mevzuata veya bir mali "
            "müşavire başvur."
        ),
        "en": (
            "Taxation depends on the asset type and the acquisition date, and "
            "the rules are periodically updated. Property purchases trigger a "
            "title deed fee, and a sale may trigger capital gains tax. Our "
            "calculations assume you keep living in the home or holding the "
            "asset, so they exclude sale taxes. Confirm your own situation "
            "against current rules or with a tax professional."
        ),
        "de": (
            "Die Besteuerung hängt von der Anlageart und vom Erwerbsdatum ab, "
            "und die Regeln werden regelmäßig angepasst. Beim Immobilienkauf "
            "fällt eine Grundbuchgebühr an, beim Verkauf kann eine "
            "Wertzuwachssteuer entstehen. Unsere Berechnungen gehen davon aus, "
            "dass du wohnen bleibst bzw. hältst, und enthalten keine "
            "Verkaufssteuern. Kläre deine Situation fachlich ab."
        ),
    },
    fear_options={
        "param_eriyor": {
            "tr": "Enflasyon param eritiyor",
            "en": "Inflation is melting my money",
            "de": "Die Inflation frisst mein Geld auf",
        },
        "kandirilirim": {
            "tr": "Kandırılmaktan korkuyorum",
            "en": "I'm afraid of being scammed",
            "de": "Ich habe Angst, betrogen zu werden",
        },
        "anlamiyorum": {
            "tr": "Hiçbir şey anlamıyorum",
            "en": "I don't understand any of this",
            "de": "Ich verstehe davon nichts",
        },
        "batiririm": {
            "tr": "Batırmaktan korkuyorum",
            "en": "I'm afraid I'll mess it up",
            "de": "Ich habe Angst, etwas falsch zu machen",
        },
    },
    disclaimer={
        "tr": (
            "Yalnızca eğitim amaçlıdır — kurallar değişir ve herkesin durumu "
            "farklıdır. Her zaman yerel lisanslı bir profesyonele doğrulat."
        ),
        "en": (
            "Educational content only — rules change and individual situations "
            "differ. Always confirm with a licensed local professional."
        ),
        "de": (
            "Nur zu Bildungszwecken — Regeln ändern sich und jede Situation ist "
            "anders. Bitte bestätige alles mit einer lizenzierten Fachperson."
        ),
    },
)
