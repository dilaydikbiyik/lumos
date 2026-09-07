"""
Germany — Market Pack.

Live data, no API key required: Eurostat carries both the harmonised CPI and
a genuine quarterly HOUSE PRICE index, so the real-return and buy-vs-rent
maths rest on measured German numbers rather than Turkish ones.

The universe is the part that matters most here. An EU retail investor
CANNOT buy US-domiciled ETFs — SPY, QQQ, VNQ and friends have no PRIIPs Key
Information Document, so European brokers refuse the order. Recommending
them to a German user would name something they are legally unable to
purchase, which is the German version of the "search SPY at a Turkish
broker" mistake. Everything below is a UCITS fund listed in Germany, the
defensive sleeve included.

Copy is written in three languages because language and market are separate
choices: an English reader may well be investing in Germany.
"""
from backend.markets.base import ListingSite, MarketPack

DE = MarketPack(
    code="DE",
    name="Deutschland",
    currency="EUR",
    currency_symbol="€",
    locale="de-DE",
    languages=["de", "en"],

    inflation_source="eurostat",       # HICP, monthly, no key
    housing_index_source="eurostat",   # prc_hpi_q — a real price index
    rent_index_source="eurostat",      # HICP CP041, actual rentals
    default_index_ticker="^GDAXI",     # DAX

    listing_sites=[
        ListingSite("ImmoScout24", "https://www.immobilienscout24.de/Suche/de/{query}"),
        ListingSite("Immowelt", "https://www.immowelt.de/suche/{query}/immobilien"),
    ],

    # ── Planning inputs (German reality, not Turkish) ──
    mortgage_rate_pct=3.8,
    mortgage_term_years=20,
    # Grunderwerbsteuer varies by Bundesland (3.5%–6.5%); notary and land
    # registry add roughly 1.5–2%. This is a mid-range national assumption
    # and the UI says so — a Berlin buyer pays more than a Bavarian one.
    transfer_tax_pct=8.0,
    # Maklerprovision has been split between buyer and seller since 2020.
    agency_commission_pct=3.57,
    vat_pct=19.0,
    annual_upkeep_pct=1.2,
    gross_rental_yield=0.035,
    housing_real_spread_pct=0.0,
    rent_real_spread_pct=0.0,
    portfolio_real_spread_pct=4.0,
    inflation_fallback_pct=2.5,

    # UCITS only — see the module docstring. Cash and bonds too: a German
    # investor cannot buy BIL or BND any more than they can buy SPY.
    asset_universe=[
        {"ticker": "EXS1.DE", "name": "iShares Core DAX UCITS ETF", "category": "stocks"},
        {"ticker": "IUSA.DE", "name": "iShares S&P 500 UCITS ETF", "category": "stocks"},
        {"ticker": "EUNL.DE", "name": "iShares Core MSCI World UCITS ETF", "category": "stocks"},
        {"ticker": "4GLD.DE", "name": "Xetra-Gold", "category": "gold"},
    ],
    reit_assets=[
        {"ticker": "IQQP.DE", "name": "iShares European Property Yield UCITS ETF", "category": "reit"},
    ],
    cash_asset={"ticker": "XEON.DE", "name": "Xtrackers EUR Overnight Rate UCITS ETF", "category": "cash"},
    bond_asset={"ticker": "EUNA.DE", "name": "iShares Core EUR Aggregate Bond UCITS ETF", "category": "bond"},

    regulator="BaFin",
    broker_note={
        "de": (
            "Aktien und ETFs kaufst du über einen Broker oder eine Depotbank. "
            "Die Eröffnung läuft meist vollständig online mit Video-Ident. "
            "Wichtig: Als Privatanleger in der EU kannst du keine US-domizilierten "
            "ETFs kaufen — es fehlt das gesetzlich vorgeschriebene "
            "Basisinformationsblatt (PRIIPs). Achte auf 'UCITS' im Namen."
        ),
        "en": (
            "You buy stocks and ETFs through a broker or a custodian bank; most "
            "accounts open fully online with video identification. Important: as "
            "an EU retail investor you cannot buy US-domiciled ETFs — they lack "
            "the legally required Key Information Document (PRIIPs). Look for "
            "'UCITS' in the fund's name."
        ),
        "tr": (
            "Hisse ve ETF'leri bir aracı kurum ya da saklama bankası üzerinden "
            "alırsın; hesap açılışı çoğunlukla video kimlik doğrulamasıyla "
            "tamamen çevrimiçi yapılır. Önemli: AB'de bireysel yatırımcı olarak "
            "ABD merkezli ETF'leri alamazsın — yasal olarak zorunlu olan temel "
            "bilgilendirme belgesi (PRIIPs) bulunmuyor. Fon adında 'UCITS' ara."
        ),
    },
    tax_note={
        "de": (
            "Allgemeine Information: Kapitalerträge unterliegen der "
            "Abgeltungsteuer zuzüglich Solidaritätszuschlag und ggf. Kirchensteuer. "
            "Ein Sparer-Pauschbetrag stellt einen Teil der Erträge frei, und für "
            "Fonds gilt eine Teilfreistellung. Beim Immobilienkauf fällt "
            "Grunderwerbsteuer an, deren Satz je Bundesland unterschiedlich ist. "
            "Regeln ändern sich — kläre deine Situation mit einer Steuerberaterin "
            "oder einem Steuerberater."
        ),
        "en": (
            "General information: investment income is subject to a flat capital "
            "gains tax plus a solidarity surcharge and, where applicable, church "
            "tax. An annual saver's allowance exempts part of the income, and "
            "funds receive a partial exemption. Buying property triggers a real "
            "estate transfer tax whose rate differs by federal state. Rules "
            "change — confirm your situation with a tax adviser."
        ),
        "tr": (
            "Genel bilgi: yatırım gelirleri sabit oranlı bir sermaye kazancı "
            "vergisine, dayanışma katkısına ve varsa kilise vergisine tabidir. "
            "Yıllık bir istisna tutarı gelirin bir kısmını vergi dışı bırakır; "
            "fonlarda kısmi istisna uygulanır. Gayrimenkul alımında eyaletten "
            "eyalete değişen bir devir vergisi doğar. Kurallar değişir — kendi "
            "durumun için bir mali müşavire danış."
        ),
    },
    fear_options={
        "losing_money": {
            "de": "Ich habe Angst, Geld zu verlieren",
            "en": "I'm afraid of losing money",
            "tr": "Para kaybetmekten korkuyorum",
        },
        "being_scammed": {
            "de": "Ich habe Angst, betrogen zu werden",
            "en": "I'm afraid of being scammed",
            "tr": "Kandırılmaktan korkuyorum",
        },
        "not_understanding": {
            "de": "Ich verstehe davon nichts",
            "en": "I don't understand any of this",
            "tr": "Hiçbir şey anlamıyorum",
        },
        "messing_up": {
            "de": "Ich habe Angst, etwas falsch zu machen",
            "en": "I'm afraid I'll mess it up",
            "tr": "Batırmaktan korkuyorum",
        },
    },
    disclaimer={
        "de": (
            "Nur zu Bildungszwecken — Regeln ändern sich und jede Situation ist "
            "anders. Bitte bestätige alles mit einer lizenzierten Fachperson vor Ort."
        ),
        "en": (
            "Educational content only — rules change and individual situations "
            "differ. Always confirm with a licensed local professional."
        ),
        "tr": (
            "Yalnızca eğitim amaçlıdır — kurallar değişir ve herkesin durumu "
            "farklıdır. Her zaman yerel lisanslı bir profesyonele doğrulat."
        ),
    },
)
