"""
RAG context for the advisor chat — a compact, cached market snapshot
injected into the system prompt so the AI speaks from TODAY's numbers
instead of its training data.

Fail-open by design: if any source is down the chat continues without
context rather than breaking (the advisor can profile risk without
knowing today's SPY price).
"""
import logging
from datetime import date

from backend.services import cache as cache_service

logger = logging.getLogger("lumos.chat_context")

_CACHE_TTL = 60 * 60 * 6  # market snapshot refreshes 4x a day
_SNAPSHOT_TICKERS = ["XU100.IS", "SPY", "GLD"]
# Instrument names, not prose — they read the same in every language, so the
# context block itself stays English. Writing the block in Turkish was
# steering the model into Turkish replies whatever the system prompt said.
_TICKER_LABELS = {"XU100.IS": "BIST 100", "SPY": "S&P 500 (SPY)", "GLD": "Gold (GLD)"}


def _market_lines() -> list[str]:
    from backend.services.market_data import fetch_price_history

    history = fetch_price_history(_SNAPSHOT_TICKERS, period="5d")
    lines = []
    for ticker in _SNAPSHOT_TICKERS:
        series = history.get(ticker)
        if series is None or len(series) < 2:
            continue
        last, prev = float(series.iloc[-1]), float(series.iloc[-2])
        change = (last / prev - 1) * 100
        lines.append(f"- {_TICKER_LABELS[ticker]}: {last:,.0f} ({change:+.1f}% daily)")
    return lines


def _inflation_line(market: str = "TR") -> str:
    from backend.services.inflation_service import monthly_cash_erosion

    erosion = monthly_cash_erosion(100, market=market)  # only to read the rate
    pct = erosion.get("monthly_inflation_pct")
    return f"- Monthly inflation ({market}, latest reading): {pct}%" if pct else ""


def build_market_context(market: str = "TR") -> str:
    """
    Compact market snapshot block, cached. Empty string when nothing is
    available — callers append it to the system prompt only if non-empty.

    The block is written in English on purpose: it is instruction text for the
    model, not copy for the reader. The system prompt decides what language
    the ANSWER comes back in.
    """
    cache_key = f"chat_market_context:{date.today().isoformat()}:{market}"
    cached = cache_service.get(cache_key)
    if cached is not None:
        return cached

    lines: list[str] = []
    try:
        lines.extend(_market_lines())
    except Exception as exc:
        logger.warning("market snapshot for chat context failed: %s", exc)
    try:
        line = _inflation_line(market)
        if line:
            lines.append(line)
    except Exception as exc:
        logger.warning("inflation line for chat context failed: %s", exc)

    if not lines:
        # Cache even the empty result BRIEFLY — prevents every chat message
        # from waiting out the yfinance timeout while sources are down.
        cache_service.set(cache_key, "", ttl=600)
        return ""

    context = (
        "\n\n---\nCURRENT MARKET CONTEXT (today's data — use it where relevant, "
        "never turn it into a forecast):\n" + "\n".join(lines)
    )
    cache_service.set(cache_key, context, ttl=_CACHE_TTL)
    return context
