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
from datetime import date, timedelta

import pandas as pd

from backend.services.holdings_valuation import (
    EXCHANGE_TYPES,
    _price_on_or_before,
    enrich_holdings,
    current_value,
)
from backend.services.market_data import fetch_price_history


def portfolio_value_history(holdings, days: int = 30) -> dict:
    """Return {series, change_amount, change_pct, live_count, flat_count}."""
    window_start = date.today() - timedelta(days=days)

    live = []
    for h in holdings:
        if h.asset_type in EXCHANGE_TYPES and h.ticker and (
            h.quantity is not None or h.purchase_date is not None
        ):
            live.append(h)

    history: dict = {}
    if live:
        try:
            history = fetch_price_history(sorted({h.ticker for h in live}), period="3mo")
        except Exception:
            history = {}

    # Trading-day index from whatever price data we have
    if history:
        idx = sorted({d.date() for s in history.values() for d in s.index if d.date() >= window_start})
    else:
        idx = [window_start + timedelta(days=i) for i in range(days + 1) if window_start + timedelta(days=i) <= date.today()]
    if not idx:
        idx = [date.today()]

    enrichment = enrich_holdings(holdings)
    live_ids = set()
    per_day = {d: 0.0 for d in idx}

    for h in holdings:
        series = history.get(h.ticker) if h.ticker else None
        units = None
        if h in live and series is not None and not series.empty:
            units = h.quantity
            if units is None:
                entry = _price_on_or_before(series, h.purchase_date)
                if entry and entry > 0:
                    units = h.purchase_amount / entry
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
                    per_day[d] += units * last_price
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
