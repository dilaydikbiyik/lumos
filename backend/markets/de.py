"""
Germany — skeleton Market Pack (also a natural fit for the Turkish
diaspora segment noted in the product roadmap).
"""
from backend.markets.base import ListingSite, MarketPack

DE = MarketPack(
    code="DE",
    name="Deutschland",
    currency="EUR",
    currency_symbol="€",
    locale="de-DE",
    languages=["de", "en", "tr"],

    inflation_source="none",       # roadmap: Destatis GENESIS API (61111-0002)
    housing_index_source="none",   # roadmap: Destatis Häuserpreisindex
    default_index_ticker="EXS1.DE",  # iShares Core DAX UCITS ETF

    listing_sites=[
        ListingSite("ImmoScout24", "https://www.immobilienscout24.de/Suche/de/{query}"),
        ListingSite("Immowelt", "https://www.immowelt.de/liste/{query}"),
    ],

    regulator="BaFin (Bundesanstalt für Finanzdienstleistungsaufsicht)",
    broker_note=(
        "Stocks/ETFs are bought through a Depot (brokerage account) at a bank "
        "or neo-broker (e.g. Trade Republic, Scalable Capital). ETF savings "
        "plans (Sparpläne) from ~€1/month are a popular beginner entry point."
    ),
    tax_note=(
        "General info: investment income is subject to the flat Abgeltungsteuer "
        "(25% + solidarity surcharge); the annual Sparer-Pauschbetrag exempts "
        "the first ~€1,000 of gains — set up a Freistellungsauftrag with your "
        "broker to use it automatically."
    ),
    fear_options={
        "inflation": "Inflation frisst mein Geld",
        "betrug": "Angst vor Betrug",
        "verstehen": "Ich verstehe das alles nicht",
        "fehler": "Angst, Fehler zu machen",
    },
)
