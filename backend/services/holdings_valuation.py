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

from backend.services import evds_service
from backend.services.market_data import fetch_price_history

logger = logging.getLogger("lumos.valuation")

EXCHANGE_TYPES = {"stock", "fund", "etf", "gold", "crypto"}
REAL_ESTATE_TYPES = {"real_estate", "land"}

NATIONAL_KFE_SERIES = "TP.KFE.TR"


def _price_on_or_before(series, target: date) -> Optional[float]:
    """Closest closing price at or before the target date."""
    try:
        eligible = series[series.index.date <= target]
        if len(eligible) == 0:
            return None
        return float(eligible.iloc[-1])
    except Exception:
        return None


def _exchange_values(holdings) -> dict[int, dict]:
    """Live values for exchange assets — one batched yfinance call."""
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

        units = h.quantity
        if units is None and h.purchase_date is not None:
            entry_price = _price_on_or_before(series, h.purchase_date)
            if entry_price and entry_price > 0:
                units = h.purchase_amount / entry_price

        if units is None:
            # No units and no purchase date — not enough data for live tracking
            continue

        live_value = round(units * latest, 2)
        out[h.id] = {
            "value": live_value,
            "source": "live",
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


def enrich_holdings(holdings) -> dict[int, dict]:
    """
    Map of holding.id -> {"value", "source", "change_pct"}.
    Priority: manual > live/index > purchase (absent entries mean purchase).
    """
    enrichment: dict[int, dict] = {}
    enrichment.update(_exchange_values(holdings))
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
