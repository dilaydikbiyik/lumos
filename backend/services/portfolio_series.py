"""
Shared helper: build a normalized weighted-portfolio value series from
per-ticker price history.

REALISM GUARD (2026-07-13): backtest and projection both did
`sum(normalised[t] * w for t, w in weights.items() if t in normalised)`.
When some tickers returned no history (common when yfinance rate-limits a
cloud host), the surviving weights no longer summed to 1.0 — the series
started BELOW the budget while returns were still measured against the
full budget. A portfolio where only gold survived and gold doubled could
render as a 66% LOSS ("100.000 TL → 40 TL" class of nonsense).

The honest fix: renormalize the surviving weights to sum to 1.0, and
REFUSE outright when too much of the portfolio is missing — better an
explicit "not enough data" than a fabricated number.
"""
import pandas as pd

from backend.exceptions import MarketDataError

# If less than this fraction of the intended allocation has price data,
# we refuse rather than extrapolate from a sliver of the portfolio.
MIN_WEIGHT_COVERAGE = 0.8


def build_normalized_series(history: dict, weights: dict[str, float]) -> pd.Series:
    """
    Combine per-ticker price series into one portfolio series that starts
    at exactly 1.0, using ONLY tickers that have data, with their weights
    renormalized to sum to 1.0.

    Raises MarketDataError if no overlapping history exists or if the
    covered weight is below MIN_WEIGHT_COVERAGE.
    """
    frame = pd.DataFrame({t: s for t, s in history.items() if s is not None and not s.empty}).dropna()
    if frame.empty:
        raise MarketDataError(f"No overlapping history for {list(weights)}")

    covered = {t: w for t, w in weights.items() if t in frame.columns}
    covered_weight = sum(covered.values())
    total_weight = sum(weights.values()) or 1.0

    if covered_weight / total_weight < MIN_WEIGHT_COVERAGE:
        missing = [t for t in weights if t not in covered]
        raise MarketDataError(
            f"Portfolio price coverage too low ({covered_weight / total_weight:.0%}); "
            f"missing data for {missing}"
        )

    # Renormalize the surviving weights so the series is a faithful 1.0-based
    # representation of the ACTUAL held mix, not a shrunken fraction of it.
    scale = 1.0 / covered_weight
    normalised = frame / frame.iloc[0]  # each asset starts at 1.0
    series = sum(normalised[t] * (w * scale) for t, w in covered.items())
    return series
