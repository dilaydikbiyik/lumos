# Adding a market

A market is a country: its currency, its rates, what its residents can legally
buy, where its price data comes from, and which portals list its property.

Everything country-specific lives in one frozen dataclass — `backend/markets/`.
Application code never asks "is this Türkiye?"; it asks the pack. The one
enforcement you get for free is `backend/tests/test_market_conformance.py`,
which is parametrised over every market and every language: **add a pack and
the whole suite runs against it.** An incomplete pack fails there rather than
in front of a reader.

## The steps

### 1. Write the pack

Copy the shape of `backend/markets/de.py` and register it in
`backend/markets/__init__.py`. Everything below is checked.

```python
MY_MARKET = MarketPack(
    code="XX",                  # ISO 3166-1 alpha-2, and the dict key
    name="Country name",
    currency="XXX",             # ISO 4217
    currency_symbol="¤",
    locale="xx-XX",             # BCP-47 — drives number formatting on the client
    languages=["xx"],           # informational; does NOT restrict the UI language

    inflation_source="eurostat",       # tcmb_evds | bls | eurostat | none
    housing_index_source="eurostat",   # tcmb_evds | fred | eurostat | none
    rent_index_source="eurostat",      # bls | eurostat | none
    regional_housing_breakdown=False,  # see step 3
    default_index_ticker="^XXXX",      # yfinance ticker for the local index

    news_feeds=[...],           # public RSS; empty means no digest for this market
    listing_sites=[...],        # at least one, with a {query} template
    example_district="...",     # a REAL place in this country
    example_locality="...",

    # Planning inputs. Every one is a documented assumption shown to the
    # reader — write the comment explaining where the number comes from.
    mortgage_rate_pct=..., mortgage_term_years=...,
    transfer_tax_pct=..., agency_commission_pct=..., vat_pct=...,
    annual_upkeep_pct=..., gross_rental_yield=...,

    asset_universe=[...],       # what residents can ACTUALLY buy — see step 4
    reit_assets=[...], cash_asset={...}, bond_asset={...},

    regulator="...",
    broker_note={...}, tax_note={...}, transfer_cost_note={...},
)
```

`disclaimer` is deliberately absent: the educational notice is the same promise
everywhere and lives in `backend/i18n.py` under `market.disclaimer`. Override it
in the pack only if a regulator demands specific wording.

### 2. Write the localized copy in **every** UI language

`broker_note`, `tax_note` and `transfer_cost_note` are `{lang: text}` dicts and
must carry every language the app supports — not just the country's own.
Language and market are independent axes: an English reader may pick the German
market, and a Turkish reader may look at the US.

`transfer_cost_note` explains **who bears the purchase taxes and on what basis**.
This exists because one shared sentence used to assert that "by law half the
transfer tax belongs to the seller" — true of Türkiye's tapu harcı, false of
German Grunderwerbsteuer and US transfer taxes alike. A legal claim cannot be
shared across jurisdictions.

The conformance suite rejects copy that reads as the wrong language, and rejects
a pack that copies another pack's country facts verbatim.

### 3. Data sources: declare only what you can actually read

Sources are dispatched on what the pack **declares**, never on its country code
(`inflation_service._get_index`, `province_intelligence._SOURCES`). Declaring an
existing source wires it up with no code change.

Two flags are separate on purpose:

- `housing_index_source` — a **national** house price index. Powers rent-vs-buy.
- `regional_housing_breakdown` — a **sub-national table** (provinces, states).

Germany has the first and not the second; gating the table on the national index
once showed a German reader Turkish provinces priced in lira. A pack that claims
a breakdown must name a source `province_intelligence._SOURCES` can read, or the
conformance test fails.

If your market needs a genuinely new source, add an adapter under
`backend/services/` following `fred_service.py`: cache tiers (fresh → stale →
last-known-good), partial results refused rather than cached, a missing key
reported as unavailable rather than guessed. Then add one reader to `_SOURCES`
and one `source.<name>` entry to the catalogue so the honesty note can name it.

**Never substitute a near-enough series.** A rent index measures what it costs
to occupy a home, not what homes sell for; the US pack declared no housing index
for months rather than borrow one. Absent and honest beats present and wrong.

### 4. The investable universe is a legal fact, not a preference

EU retail investors cannot buy US-domiciled ETFs — there is no PRIIPs Key
Information Document — so recommending SPY to a German user names something they
cannot legally purchase. The defensive sleeve is subject to the same rule: BIL
and BND are US-domiciled too.

Leave `asset_universe` empty only if the shared default is genuinely legal and
sensible for this country.

### 5. Run the suite

```bash
./venv/bin/pytest backend/tests/test_market_conformance.py -q
```

Then the whole thing:

```bash
./venv/bin/pytest -q && cd backend && ruff check .
```

## What you do NOT need to touch

Nothing outside `backend/markets/` in the ordinary case. The market flows
through `_market_of()` in the routers and reaches the engines as a parameter.
If you find yourself writing `if market == "XX"` anywhere else, that is the
signal that a fact belongs in the pack.
