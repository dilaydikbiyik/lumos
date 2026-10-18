"""
Future scenarios — the honest answer to "what could my money become?".

We never predict. Instead we compute EVERY rolling N-year window in the
asset's own history and report the distribution: pessimistic (p10),
typical (median), optimistic (p90). The user sees a RANGE the asset has
actually produced, applied to their own amount — with the worst window
shown first (vision: honest downside before upside).
"""
import logging
from typing import Optional

import numpy as np

from backend.exceptions import MarketDataError
from backend.i18n import t
from backend.services.market_data import fetch_price_history
from backend.services.portfolio_series import build_normalized_series

logger = logging.getLogger("lumos.projection")

TRADING_DAYS_PER_YEAR = 252
MIN_WINDOWS = 6  # fewer rolling windows than this -> not enough to describe at all

# The guard that actually matters.
#
# MIN_WINDOWS counts OVERLAPPING windows, and its comment used to claim it
# stopped the app "pretending it's a distribution". It does not: six
# overlapping windows is six steps past the horizon, so a five-year band
# passed on five and a half years of history — one independent period,
# resampled sixty-six times, presented as a spread of outcomes.
#
# What carries information is how many times the horizon fits in the record
# WITHOUT reusing the same years. Three is still few, and the answer says so
# rather than hiding it; below three there is no spread to describe, only a
# single history wearing a percentile's clothes.
MIN_INDEPENDENT_PERIODS = 3


def _independent_periods(sample_count: int, window: int) -> int:
    """How many non-overlapping windows the record actually holds."""
    if window <= 0:
        return 0
    return sample_count // window


def _rolling_window_returns(values: np.ndarray, window: int, step: int) -> list[float]:
    """Total returns of every `window`-length slice, sampled every `step` points."""
    returns = []
    for start in range(0, len(values) - window, step):
        begin, end = values[start], values[start + window]
        if begin > 0:
            returns.append(end / begin - 1)
    return returns


def _windowed_real_band(
    values, months: list[str], window: int, amount: float, market: str = "TR",
) -> tuple[dict, Optional[dict]]:
    """
    NOMINAL band of rolling windows over a monthly/quarterly series, plus a
    REAL band where each window is deflated by its OWN period inflation.
    (Comparing the nominal median of all windows against a single period's
    inflation is an apples-to-oranges error.)
    """
    from backend.services import inflation_service

    nominals: list[float] = []
    reals: list[float] = []
    for start in range(0, len(values) - window):
        begin, end = values[start], values[start + window]
        if begin <= 0:
            continue
        nominal = end / begin - 1
        nominals.append(nominal)
        try:
            real_pct = inflation_service.real_return_pct(
                nominal * 100, months[start], months[start + window], market
            )
            reals.append(real_pct / 100)
        except Exception:
            # A window that cannot be deflated is dropped from the REAL band
            # only. That is correct, but it is not neutral: deflation fails
            # where inflation data is missing, which is systematically the
            # OLDEST periods. So the real band can silently describe a shorter
            # history than the nominal band printed beside it. The counts are
            # reported per band below so the two cannot be read as covering
            # the same span when they do not.
            logger.debug("window %s..%s not deflatable for %s",
                         months[start], months[start + window], market)

    if len(nominals) < MIN_WINDOWS:
        return {}, None

    band = _band(nominals, amount)
    real_band = None
    if len(reals) >= MIN_WINDOWS:
        import numpy as _np
        p10, p50, p90 = _np.percentile(_np.array(reals), [10, 50, 90])
        real_band = {
            "pessimistic_pct": round(p10 * 100, 1),
            "typical_pct": round(p50 * 100, 1),
            "optimistic_pct": round(p90 * 100, 1),
            # Its own count, because it is not always the nominal band's.
            "windows_analysed": len(reals),
        }
    return band, real_band


def _band(returns: list[float], amount: float) -> dict:
    arr = np.array(returns)
    p10, p50, p90 = np.percentile(arr, [10, 50, 90])
    return {
        "windows_analysed": len(returns),
        "pessimistic": {"return_pct": round(p10 * 100, 1), "value": round(amount * (1 + p10), 2)},
        "typical":     {"return_pct": round(p50 * 100, 1), "value": round(amount * (1 + p50), 2)},
        "optimistic":  {"return_pct": round(p90 * 100, 1), "value": round(amount * (1 + p90), 2)},
    }


def project_asset(ticker: str, amount: float, years: int, lang: str = "tr") -> dict:
    """
    Scenario band for an exchange-traded asset from its own daily history.

    Uses the WHOLE record the provider has. It used to ask for ten years,
    which quietly decided the quality of every band drawn from it.
    """
    # The whole record, not ten years. The cap was the real reason bands were
    # thin: ten years of history under a five-year window is two independent
    # periods however many overlapping ones are counted, and it refused
    # ten-year bands outright for assets that have thirty years of history.
    history = fetch_price_history([ticker], period="max")
    series = history.get(ticker)
    if series is None or series.empty:
        raise MarketDataError(f"No history for {ticker}")

    values = series.to_numpy()
    window = years * TRADING_DAYS_PER_YEAR
    # sample monthly so windows overlap without being near-duplicates
    returns = _rolling_window_returns(values, window, step=21)

    independent = _independent_periods(len(values), window)
    if len(returns) < MIN_WINDOWS or independent < MIN_INDEPENDENT_PERIODS:
        return {
            "available": False,
            "reason": (
                t("projection.no_history_asset", lang, ticker=ticker, years=years)
            ),
        }

    years_covered = round(len(values) / TRADING_DAYS_PER_YEAR, 1)
    return {
        "available": True,
        "ticker": ticker,
        "amount": amount,
        "years": years,
        "history_years": years_covered,
        # The number that says how much the band is worth. A reader shown
        # "sixty windows" hears sixty observations; what they have is this
        # many non-overlapping stretches of history, and three of them is a
        # thin basis stated honestly rather than a thick one implied.
        "independent_periods": independent,
        **_band(returns, amount),
        "honesty_note": (
            t("projection.note_asset", lang, ticker=ticker, years=years)
        ),
    }


def project_portfolio(weights: dict[str, float], amount: float, years: int,
                      lang: str = "tr") -> dict:
    """
    Scenario band for a whole weighted portfolio, not a single asset.

    We build the combined daily value series (same normalisation as
    backtest.py) and run the rolling-window distribution on THAT series —
    so diversification's smoothing effect shows up in the band width.
    """
    # Same reasoning as the single asset: the whole record. A portfolio band
    # is bounded by its SHORTEST member's history, so the cap bit hardest
    # exactly where a mix includes one young fund.
    history = fetch_price_history(list(weights), period="max")
    # Renormalized, coverage-guarded series (starts at 1.0) — partial
    # yfinance data can no longer shrink the portfolio into a fake tiny return.
    portfolio_series = build_normalized_series(history, weights)
    values = portfolio_series.to_numpy()

    window = years * TRADING_DAYS_PER_YEAR
    returns = _rolling_window_returns(values, window, step=21)

    independent = _independent_periods(len(values), window)
    if len(returns) < MIN_WINDOWS or independent < MIN_INDEPENDENT_PERIODS:
        return {
            "available": False,
            "reason": (
                t("projection.no_history_portfolio", lang, years=years)
            ),
        }

    years_covered = round(len(values) / TRADING_DAYS_PER_YEAR, 1)
    return {
        "available": True,
        "independent_periods": independent,
        "amount": amount,
        "years": years,
        "history_years": years_covered,
        "tickers": list(weights),
        **_band(returns, amount),
        "honesty_note": (
            t("projection.note_portfolio", lang, years=years)
        ),
    }
