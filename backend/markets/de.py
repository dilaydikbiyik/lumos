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

    # Eurostat and the Bundesbank publish the same harmonised index; the
    # Bundesbank's is current while Eurostat's stopped nine months short —
    # for every euro-area country, not only Germany. Same concept, fresher copy.
    inflation_source="bundesbank",       # HICP, monthly, no key
    housing_index_source="eurostat",   # prc_hpi_q — a real price index
    # No Bundesland-level index is reachable WITHOUT AN ACCOUNT, re-checked
    # 2026-10-03 by querying each source rather than trusting the last note:
    #   - Eurostat `prc_hpi_q` is country-level; TR and DE both return a
    #     single series. (Its regional POPULATION data is a different
    #     dataset, and that one the app does use.)
    #   - The Bundesbank's BBDP1 carries exactly three region codes —
    #     DE0007, DE0127, DEK. Every Bundesland code tried (DE1, DEBY,
    #     DEBW, …) returns 404, so this is the shape of the data rather
    #     than a gap in the query.
    #   - Destatis documents GENESIS as free and registration-free, and its
    #     `helloworld/whoami` does answer — but every data method returns the
    #     web app rather than JSON, so anonymous access does not reach them
    #     in practice.
    #   - Destatis REGIONALSTATISTIK does carry Bundesland and Kreis figures
    #     and has required a free account since May 2025. That is the one
    #     real route to a province table here, and it needs a person to
    #     create the account — see todo.md.
    # The Bundesbank's city-size aggregates are what is reachable today: a
    # real breakdown of a different shape — nested segments, not alternative
    # places — and the UI says so in the reader's own language.
    regional_housing_source="bundesbank",
    population_source="eurostat",
    # NUTS-2 regions, with Eurostat's own labels so the names on screen
    # match the source a reader can go and check.
    population_regions={
        "DE11": "Stuttgart",
        "DE12": "Karlsruhe",
        "DE13": "Freiburg",
        "DE14": "Tübingen",
        "DE21": "Oberbayern",
        "DE22": "Niederbayern",
        "DE23": "Oberpfalz",
        "DE24": "Oberfranken",
        "DE25": "Mittelfranken",
        "DE26": "Unterfranken",
        "DE27": "Schwaben",
        "DE30": "Berlin",
        "DE40": "Brandenburg",
        "DE50": "Bremen",
        "DE60": "Hamburg",
        "DE71": "Darmstadt",
        "DE72": "Gießen",
        "DE73": "Kassel",
        "DE80": "Mecklenburg-Vorpommern",
        "DE91": "Braunschweig",
        "DE92": "Hannover",
        "DE93": "Lüneburg",
        "DE94": "Weser-Ems",
        "DEA1": "Düsseldorf",
        "DEA2": "Köln",
        "DEA3": "Münster",
        "DEA4": "Detmold",
        "DEA5": "Arnsberg",
        "DEB1": "Koblenz",
        "DEB2": "Trier",
        "DEB3": "Rheinhessen-Pfalz",
        "DEC0": "Saarland",
        "DED2": "Dresden",
        "DED4": "Chemnitz",
        "DED5": "Leipzig",
        "DEE0": "Sachsen-Anhalt",
        "DEF0": "Schleswig-Holstein",
        "DEG0": "Thüringen",
    },
    rent_index_source="bundesbank",    # HICP actual rentals, same lineage
    default_index_ticker="^GDAXI",     # DAX

    news_feeds=[
        # Public RSS, no key.
        "https://www.tagesschau.de/wirtschaft/index~rss2.xml",
        "https://www.handelsblatt.com/contentexport/feed/finanzen",
    ],

    example_ticker="SAP.DE",
    example_asset_name="Eigentumswohnung",
    area_kind="segment",
    example_district="Neukölln",
    example_locality="Rixdorf",

    listing_terms={"arsa": "Grundstück", "daire": "Wohnung", "konut": "Haus"},

    listing_sites=[
        ListingSite("ImmoScout24", "https://www.immobilienscout24.de/Suche/de/{query}"),
        ListingSite("Immowelt", "https://www.immowelt.de/suche/{query}/immobilien"),
    ],

    # ── Planning inputs (German reality, not Turkish) ──
    mortgage_rate_source="bundesbank",  # MFI effective rate, new housing loans
    mortgage_rate_pct=3.8,             # used only if the Bundesbank is unreachable
    mortgage_term_years=20,
    # Grunderwerbsteuer varies by Bundesland (3.5% in Bayern to 6.5% in NRW,
    # Brandenburg and others), so a national figure can only be a midpoint:
    # 5.0% for the tax, plus roughly 1.5% notary and 0.5% land registry, both
    # of which are fee-schedule driven rather than negotiable. A Bavarian
    # buyer pays visibly less than a Berlin one, and the UI says so.
    transfer_tax_pct=7.0,
    # Maklerprovision, NET of VAT — the engine adds vat_pct on top, and
    # 3.0% + 19% is the 3.57% a German buyer sees quoted. Storing the gross
    # figure here billed the VAT twice. Split between buyer and seller
    # since the 2020 Gesetz, so this is the buyer's half.
    agency_commission_pct=3.0,
    vat_pct=19.0,
    annual_upkeep_pct=1.2,
    gross_rental_yield=0.035,
    # Germany is the strictest of the three: lenders expect the buyer to
    # cover the ~7% Kaufnebenkosten from their OWN funds on top of the
    # down payment, so the entry bar is genuinely higher than elsewhere.
    property_entry_threshold=100_000.0,
    # German revolving card and Dispokredit rates sit around 11-12% a year,
    # far below the Turkish ceiling — quoting 4.25% a month to a German
    # cardholder overstates the cost of their debt by roughly six times.
    card_monthly_rate_pct=0.95,
    material_debt=500.0,
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

    transfer_cost_note={
        "tr": "Bu oran tek bir vergi değil: eyalete göre %3,5–6,5 arasında değişen devir vergisi (Grunderwerbsteuer) ile noter ve tapu sicili ücretlerinin toplamıdır. Devir vergisini uygulamada alıcı öder; Berlin'de alıcı, Bavyera'da olduğundan daha fazlasını öder.",
        "en": "This rate is not a single tax: it bundles the transfer tax (Grunderwerbsteuer), which ranges from 3.5% to 6.5% by federal state, with notary and land-registry fees. In practice the buyer pays the transfer tax; a Berlin buyer pays more than a Bavarian one.",
        "de": "Dieser Satz ist keine einzelne Steuer: er fasst die Grunderwerbsteuer, die je nach Bundesland zwischen 3,5% und 6,5% liegt, mit Notar- und Grundbuchgebühren zusammen. In der Praxis zahlt die kaufende Seite die Grunderwerbsteuer; in Berlin mehr als in Bayern.",
    },

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
)
