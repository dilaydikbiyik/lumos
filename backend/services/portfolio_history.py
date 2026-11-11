"""
Daily value series for the user's ACTUAL holdings — "what happened to my
portfolio since I bought it?".

Honest by construction:
  • exchange assets with a resolvable unit count (quantity, or purchase_date
    to back units out of the entry price) follow real daily closes;
  • everything else (cash, manual values, real estate) is carried flat at its
    best-known value — no invented daily wiggle;
  • a holding only enters the series on its purchase date (money that wasn't
    in the market can't have moved).
"""
import logging
from datetime import date, timedelta

import pandas as pd

from backend.services.holdings_valuation import (
    EXCHANGE_TYPES,
    _price_on_or_before,
    enrich_holdings,
    current_value,
)
from backend.services import fx_service
from backend.services.holdings_valuation import LEGACY_CURRENCY, ticker_currency
from backend.services.market_data import fetch_price_history
from backend.exceptions import MarketDataError

logger = logging.getLogger("lumos.portfolio_history")

# (days covered, provider period) — the shortest that covers what is needed.
_PERIODS = ((85, "3mo"), (175, "6mo"), (360, "1y"), (725, "2y"), (1820, "5y"), (3640, "10y"))


def _daily_rates(base: str, quote: str, days, period: str = "3mo") -> dict:
    """{day: rate} carrying the last known rate forward; {} when unknown."""
    base, quote = (base or "").upper(), (quote or "").upper()
    if not base or not quote or base == quote:
        return {d: 1.0 for d in days}
    try:
        series = fetch_price_history([f"{base}{quote}=X"], period=period).get(f"{base}{quote}=X")
    except MarketDataError:
        series = None
    if series is None or series.empty:
        now = fx_service.rate(base, quote)
        return {d: now for d in days} if now else {}
    by_day = {i.date(): float(v) for i, v in series.dropna().items()}
    out, last = {}, None
    for d in sorted(days):
        last = by_day.get(d, last)
        if last is not None:
            out[d] = last
    return out


def portfolio_value_history(holdings, days: int = 30, user_currency: str = "TRY",
                            market: str = "TR") -> dict:
    """Return {series, change_amount, change_pct, live_count, flat_count}."""
    window_start = date.today() - timedelta(days=days)

    live = []
    for h in holdings:
        if h.asset_type in EXCHANGE_TYPES and h.ticker and (
            h.quantity is not None or h.purchase_date is not None
        ):
            live.append(h)

    # Enough history for the window asked for AND for the oldest purchase
    # whose units must be backed out of its entry price. It was a fixed three
    # months: a holding bought earlier found no entry price, was drawn flat
    # (the list said +8.9%, the chart 0.0%), and "1Y" showed three months.
    oldest = min((h.purchase_date for h in live if h.quantity is None and h.purchase_date),
                 default=None)
    need = max(days, (date.today() - oldest).days if oldest else 0) + 7
    period = next((p for limit, p in _PERIODS if need <= limit), "max")

    history: dict = {}
    if live:
        try:
            history = fetch_price_history(sorted({h.ticker for h in live}), period=period)
        except MarketDataError as exc:
            # MarketDataError only, for the same reason as in
            # property_vs_portfolio: this fallback carries every holding
            # FLAT, which draws a believable chart. A broken call here
            # would flatten everybody's history and look like a quiet
            # market. fetch_price_history raises MarketDataError for every
            # real failure, so narrowing costs nothing and stops a
            # programming error from being rendered as data.
            logger.warning("price history unavailable (%s) — carrying holdings flat", exc)
            history = {}

    # Trading-day index from whatever price data we have
    if history:
        idx = sorted({d.date() for s in history.values() for d in s.index if d.date() >= window_start})
    else:
        idx = [window_start + timedelta(days=i) for i in range(days + 1) if window_start + timedelta(days=i) <= date.today()]
    if not idx:
        idx = [date.today()]

    enrichment = enrich_holdings(holdings, user_currency, market)
    live_ids = set()
    per_day = {d: 0.0 for d in idx}

    for h in holdings:
        series = history.get(h.ticker) if h.ticker else None
        units = None
        # A price is quoted in the asset's currency; the amount the user typed
        # is in theirs. Summing units × dollar price into a lira total was the
        # same missing conversion that reported a break-even SPY position as a
        # 97% loss — this chart had it too.
        held_ccy = (getattr(h, "currency", None) or LEGACY_CURRENCY).upper()
        asset_ccy = ticker_currency(h.ticker) if h.ticker else held_ccy
        fx_now = fx_service.rate(asset_ccy, held_ccy)
        # Each day at THAT day's rate into the reader's currency. Today's rate
        # applied to every day erased the currency's own move: a TR reader's
        # SPY bought for 100,000 TL started the chart at 103,369 and showed
        # -2.1% while the list beside it said +1.2%.
        daily_rate = _daily_rates(asset_ccy, user_currency, idx, period) if h in live else {}
        to_user_now = fx_service.rate(asset_ccy, user_currency)

        if (h in live and series is not None and not series.empty
                and fx_now is not None and to_user_now is not None):
            units = h.quantity
            if units is None:
                entry = _price_on_or_before(series, h.purchase_date)
                fx_then = fx_service.rate(asset_ccy, held_ccy, h.purchase_date)
                if entry and entry > 0 and fx_then:
                    units = h.purchase_amount / (entry * fx_then)
        if units is not None and series is not None and not series.empty:
            live_ids.add(h.id)
            daily = series.copy()
            daily.index = [d.date() for d in daily.index]
            last_price = None
            for d in idx:
                if h.purchase_date is not None and d < h.purchase_date:
                    continue
                price = daily.get(d)
                if price is not None and not pd.isna(price):
                    last_price = float(price)
                if last_price is not None:
                    per_day[d] += units * last_price * daily_rate.get(d, to_user_now)
        else:
            # Flat carry at best-known value from its purchase date onward
            val = current_value(h, enrichment)
            for d in idx:
                if h.purchase_date is not None and d < h.purchase_date:
                    continue
                per_day[d] += val

    points = [
        {"date": d.isoformat(), "value": round(v, 2)}
        for d, v in per_day.items() if v > 0
    ]
    change_amount = round(points[-1]["value"] - points[0]["value"], 2) if len(points) >= 2 else 0.0
    change_pct = (
        round(change_amount / points[0]["value"] * 100, 2)
        if len(points) >= 2 and points[0]["value"] > 0 else 0.0
    )
    return {
        "series": points,
        "change_amount": change_amount,
        "change_pct": change_pct,
        "live_count": len(live_ids),
        "flat_count": len(holdings) - len(live_ids),
        "window_days": days,
    }
