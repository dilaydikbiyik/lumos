"""
Does this asset match your patience?

The backtest already measures an asset's character — how far it fell, how
long it took to come back, how long it went nowhere. Those numbers were
computed and returned and never shown, which is the least useful place for
them: a beginner cannot read "-42% / 18 months" and know whether that is
survivable FOR THEM.

So this turns the metrics into a verdict against the reader's own answers.
The judgment is deliberately about BEHAVIOUR rather than returns, because
the way people lose money in a good asset is selling it during the part
they were not told about.

The stagnation number matters more than the drawdown here, and it is the one
nobody quotes. A crash is frightening and brief; three years of going
nowhere is what actually makes people give up, and it does not look like a
disaster on any chart.
"""

import logging
from typing import Optional

from backend.i18n import t

logger = logging.getLogger("lumos.asset_character")

# Below this, a fall is ordinary movement rather than something to warn about.
_NOTABLE_DRAWDOWN = -20.0
# A stretch this long with the price going nowhere outlasts most people's
# patience, whatever their stated risk tolerance.
_LONG_STAGNATION_MONTHS = 18.0

_TOLERANCE_LIMITS = {
    "low": -20.0,
    "medium": -35.0,
    "high": -60.0,
}

_HORIZON_YEARS = {"short": 2, "medium": 6, "long": 15}


def _recovery_months(trading_days: Optional[int]) -> Optional[float]:
    if trading_days is None:
        return None
    return round(trading_days / 21.0, 1)


def fit(metrics: dict, *, loss_tolerance: Optional[str] = None,
        time_horizon: Optional[str] = None, lang: str = "tr") -> dict:
    """
    {verdict, reason, recovery_months} for one asset's measured character.

    verdict: comfortable | demanding | mismatch | unknown
    """
    drawdown = metrics.get("max_drawdown_pct")
    stagnation = metrics.get("longest_stagnation_months")
    recovery = _recovery_months(metrics.get("recovery_trading_days"))

    if drawdown is None:
        return {"verdict": "unknown", "reason": t("character.unknown", lang),
                "recovery_months": None}

    limit = _TOLERANCE_LIMITS.get(loss_tolerance or "", -35.0)
    horizon_years = _HORIZON_YEARS.get(time_horizon or "", 6)

    # A fall deeper than the reader said they could sit through.
    if drawdown < limit:
        return {
            "verdict": "mismatch",
            "reason": t("character.too_deep", lang,
                        drawdown=abs(round(drawdown)), limit=abs(round(limit))),
            "recovery_months": recovery,
        }

    # Recovery that outlasts the horizon: the money would have been needed
    # before the price came back, which is the scenario that turns a paper
    # loss into a real one.
    if recovery is not None and recovery > horizon_years * 12:
        return {
            "verdict": "mismatch",
            "reason": t("character.slow_recovery", lang,
                        months=round(recovery), years=horizon_years),
            "recovery_months": recovery,
        }

    if stagnation is not None and stagnation >= _LONG_STAGNATION_MONTHS:
        return {
            "verdict": "demanding",
            "reason": t("character.long_flat", lang, months=round(stagnation)),
            "recovery_months": recovery,
        }

    if drawdown <= _NOTABLE_DRAWDOWN:
        return {
            "verdict": "demanding",
            "reason": t("character.notable_fall", lang,
                        drawdown=abs(round(drawdown)),
                        months=round(recovery) if recovery else None),
            "recovery_months": recovery,
        }

    return {
        "verdict": "comfortable",
        "reason": t("character.steady", lang, drawdown=abs(round(drawdown))),
        "recovery_months": recovery,
    }


def describe_all(per_asset: dict, *, loss_tolerance: Optional[str] = None,
                 time_horizon: Optional[str] = None, lang: str = "tr") -> dict:
    """Enrich each asset's metrics with its fit against this reader."""
    out = {}
    for ticker, metrics in (per_asset or {}).items():
        out[ticker] = {
            **metrics,
            "character": fit(metrics, loss_tolerance=loss_tolerance,
                             time_horizon=time_horizon, lang=lang),
        }
    return out
