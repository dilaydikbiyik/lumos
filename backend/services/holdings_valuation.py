"""
Live holding valuation — answers "my SPY doubled, will I see it?".

Value-source priority (returned with an honesty label):
  1. manual   — a user-entered current value overrides everything
  2. live     — exchange assets: current yfinance price × units
                (units derived from the purchase-date price if not given)
  3. index    — real estate/land: estimate via the TCMB national housing
                index ratio ("index-based estimate" — not a parcel claim)
  4. purchase — with no source at all, the purchase amount (no change shown)

Fail-open: if data sources fail we quietly fall back to purchase basis —
the holdings list never breaks.
"""
import logging
from datetime import date
from typing import Optional

from backend.services import evds_service, fx_service
from backend.services.market_data import fetch_price_history

logger = logging.getLogger("lumos.valuation")

EXCHANGE_TYPES = {"stock", "fund", "etf", "gold", "crypto"}
REAL_ESTATE_TYPES = {"real_estate", "land"}

NATIONAL_KFE_SERIES = "TP.KFE.TR"

# Which currency a symbol is quoted in. Resolved from the exchange suffix
# because it is deterministic and free; an unsuffixed US listing is the
# default. A wrong guess here becomes a wrong portfolio value, so anything
# unrecognised falls through to the lookup service rather than being assumed.
_SUFFIX_CURRENCY = {
    ".IS": "TRY",   # Borsa İstanbul
    ".DE": "EUR",   # Xetra / German venues
    ".F": "EUR",    # Frankfurt
    ".PA": "EUR", ".AS": "EUR", ".MI": "EUR",
    ".L": "GBP",    # London
    ".SW": "CHF",
    ".TO": "CAD",
}


def ticker_currency(ticker: str) -> str:
    """ISO 4217 the symbol is quoted in."""
    symbol = (ticker or "").upper()
    for suffix, currency in _SUFFIX_CURRENCY.items():
        if symbol.endswith(suffix):
            return currency
    # Ask the quote service before falling back — it knows listings our
    # suffix table doesn't.
    try:
        from backend.services import ticker_lookup

        info = ticker_lookup.lookup(symbol)
        if info and info.get("currency"):
            return info["currency"].upper()
    except Exception:
        pass
    return "USD"


def _price_on_or_before(series, target: date) -> Optional[float]:
    """Closest closing price at or before the target date."""
    try:
        eligible = series[series.index.date <= target]
        if len(eligible) == 0:
            return None
        return float(eligible.iloc[-1])
    except Exception:
        return None


def _exchange_values(holdings, user_currency: str = "TRY") -> dict[int, dict]:
    """
    Live values for exchange assets — one batched yfinance call, then a
    currency step that used to be missing entirely.

    A price is quoted in the asset's own currency; the user typed what they
    paid in theirs. Multiplying units by a dollar price and comparing the
    result to a lira amount reported a break-even SPY position as a 97% loss.
    Everything below is converted into the user's currency before it is shown
    or compared.
    """
    tickers = sorted({
        h.ticker for h in holdings
        if h.asset_type in EXCHANGE_TYPES and h.ticker
    })
    if not tickers:
        return {}

    try:
        history = fetch_price_history(tickers, period="10y")
    except Exception as exc:
        logger.warning("live valuation skipped — market data unavailable: %s", exc)
        return {}

    out: dict[int, dict] = {}
    for h in holdings:
        if h.asset_type not in EXCHANGE_TYPES or not h.ticker:
            continue
        series = history.get(h.ticker)
        if series is None or series.empty:
            continue

        latest = float(series.iloc[-1])
        asset_ccy = ticker_currency(h.ticker)
        # A row written before the column existed has no currency; it always
        # implicitly meant the user's, so that is what it is read as.
        held_ccy = (getattr(h, "currency", None) or user_currency).upper()

        # Today's rate turns the quote into the currency the user thinks in.
        to_held_now = fx_service.rate(asset_ccy, held_ccy)
        if to_held_now is None:
            # Unknown rate must mean "can't value this", never an assumed 1.0.
            continue

        units = h.quantity
        if units is None and h.purchase_date is not None:
            entry_price = _price_on_or_before(series, h.purchase_date)
            # The purchase amount is in the user's currency, the entry price in
            # the asset's — convert at the rate that applied ON THAT DAY, not
            # today's, or the unit count absorbs every FX move since.
            to_held_then = fx_service.rate(asset_ccy, held_ccy, h.purchase_date)
            if entry_price and entry_price > 0 and to_held_then:
                units = h.purchase_amount / (entry_price * to_held_then)

        if units is None:
            # No units and no purchase date — not enough data for live tracking
            continue

        live_value = round(units * latest * to_held_now, 2)
        out[h.id] = {
            "value": live_value,
            "source": "live",
            "currency": held_ccy,
            "change_pct": round((live_value / h.purchase_amount - 1) * 100, 1)
            if h.purchase_amount else None,
        }
    return out


def _real_estate_values(holdings) -> dict[int, dict]:
    """Estimated current value for real estate/land via the national KFE index ratio."""
    re_holdings = [
        h for h in holdings
        if h.asset_type in REAL_ESTATE_TYPES and h.purchase_date is not None
    ]
    if not re_holdings:
        return {}

    try:
        earliest = min(h.purchase_date for h in re_holdings)
        index = evds_service.fetch_series(
            NATIONAL_KFE_SERIES,
            start=earliest.strftime("01-%m-%Y"),
            end=date.today().strftime("%d-%m-%Y"),
        )
    except Exception as exc:
        logger.warning("index valuation skipped — EVDS unavailable: %s", exc)
        return {}

    if not index:
        return {}

    months = sorted(index)
    latest_val = index[months[-1]]

    out: dict[int, dict] = {}
    for h in re_holdings:
        purchase_month = h.purchase_date.strftime("%Y-%m")
        # closest index point at or before the purchase month
        base_months = [m for m in months if m <= purchase_month]
        if not base_months:
            continue
        base_val = index[base_months[-1]]
        if base_val <= 0:
            continue
        ratio = latest_val / base_val
        est = round(h.purchase_amount * ratio, 2)
        out[h.id] = {
            "value": est,
            "source": "index",
            "change_pct": round((ratio - 1) * 100, 1),
        }
    return out


def enrich_holdings(holdings, user_currency: str = "TRY") -> dict[int, dict]:
    """
    Map of holding.id -> {"value", "source", "change_pct"}.
    Priority: manual > live/index > purchase (absent entries mean purchase).

    `user_currency` is the currency every returned value is expressed in, so
    a total can be summed without adding dollars to lira.
    """
    enrichment: dict[int, dict] = {}
    enrichment.update(_exchange_values(holdings, user_currency))
    enrichment.update(_real_estate_values(holdings))

    # manual overrides everything
    for h in holdings:
        if h.manual_current_value is not None:
            enrichment[h.id] = {
                "value": h.manual_current_value,
                "source": "manual",
                "change_pct": round((h.manual_current_value / h.purchase_amount - 1) * 100, 1)
                if h.purchase_amount else None,
            }
    return enrichment


def current_value(holding, enrichment: dict[int, dict]) -> float:
    """Best known value for a single holding."""
    info = enrichment.get(holding.id)
    if info:
        return info["value"]
    return holding.purchase_amount
