"""
Sub-national housing intelligence — the concrete answer to "where should I
buy a home?".

Two markets, two data products, one shape:

  TR   TCMB per-province unit prices (TL/m², quarterly, 2010→today). A price
       LEVEL, so we can say "79,110 TL per m² in Muğla, +X% real over 5 years".
  US   FHFA All-Transactions House Price Index per state via FRED (quarterly,
       1980:Q1 = 100). An INDEX, not a level: it measures appreciation
       faithfully but cannot answer "what does a square metre cost". Rows from
       this market carry no price, and `measure` says which is which so the
       client never prints an empty figure or implies the two are comparable.

Germany is deliberately absent: Eurostat publishes a national house price
index but no regional breakdown, and inventing one from the national series
would be a fabrication.

Same honesty frame throughout: these are area averages, not a specific
neighbourhood or parcel, and the past guarantees nothing.
"""
import logging
from typing import Optional

from backend.i18n import t
from backend.services import evds_service, fred_service, inflation_service

logger = logging.getLogger("lumos.province")

VALID_HORIZONS = (1, 3, 5)

# Both supported series are quarterly, so a horizon is that many quarters.
_QUARTERS_PER_YEAR = 4


def _change_over_quarters(prices: dict[str, float], quarters_back: int) -> Optional[float]:
    if len(prices) < 2:
        return None
    months = sorted(prices)
    latest = months[-1]
    base_pos = max(len(months) - 1 - quarters_back, 0)
    base = months[base_pos]
    if prices[base] <= 0 or base == latest:
        return None
    return round((prices[latest] / prices[base] - 1) * 100, 1)


def _row(code: str, name: str, series: dict[str, float], quarters: int,
         market: str, price_level: bool) -> Optional[dict]:
    """One area's nominal and real change, or None when its history is short."""
    change = _change_over_quarters(series, quarters)
    if change is None:
        return None

    months = sorted(series)
    latest_month = months[-1]
    base_month = months[max(len(months) - 1 - quarters, 0)]
    try:
        real_change = inflation_service.real_return_pct(
            change, base_month, latest_month, market
        )
    except Exception as exc:
        logger.warning("real-return conversion failed for %s (%s)", code, type(exc).__name__)
        real_change = None

    return {
        "code": code,
        "province": name,
        # An index has no unit price. Reporting one would be an invention.
        "price_per_m2": round(series[latest_month]) if price_level else None,
        "nominal_change_pct": change,
        "real_change_pct": real_change,
        "_latest_month": latest_month,
    }


def _tr_areas() -> tuple[dict[str, dict], bool]:
    data = evds_service.get_province_unit_prices() or {}
    return ({code: {"name": e["name"], "series": e["prices"]}
             for code, e in data.items()}, True)


def _us_areas() -> tuple[dict[str, dict], bool]:
    data = fred_service.get_all_state_hpi()
    return ({code: {"name": e["name"], "series": e["index"]}
             for code, e in data.items()}, False)


_SOURCES = {"TR": _tr_areas, "US": _us_areas}


def rank_provinces(horizon_years: int = 3, market: str = "TR",
                   lang: str = "tr") -> dict:
    """
    Rank every area in the market by REAL appreciation over the chosen
    horizon (1/3/5 years) — 81 provinces in Türkiye, 50 states plus DC in
    the United States.
    """
    horizon_years = horizon_years if horizon_years in VALID_HORIZONS else 3
    quarters = horizon_years * _QUARTERS_PER_YEAR
    market = (market or "TR").upper()

    source = _SOURCES.get(market)
    if source is None:
        return {"available": False, "provinces": [],
                "note": t("province.no_breakdown", lang, market=market)}

    areas, price_level = source()
    if not areas:
        return {"available": False, "provinces": [],
                "note": t("province.unavailable", lang)}

    rows = []
    latest_month = None
    for code, area in areas.items():
        row = _row(code, area["name"], area["series"], quarters, market, price_level)
        if row is None:
            continue
        latest_month = row.pop("_latest_month")
        rows.append(row)

    if not rows:
        return {"available": False, "provinces": [],
                "note": t("province.unavailable", lang)}

    rows.sort(key=lambda r: (r["real_change_pct"] is None, -(r["real_change_pct"] or 0)))
    for i, row in enumerate(rows):
        row["rank"] = i + 1

    return {
        "available": True,
        "horizon_years": horizon_years,
        "market": market,
        # The client needs to know WHICH kind of number it received: a price
        # level can be printed as "X per m²", an index cannot.
        "measure": "unit_price_per_m2" if price_level else "price_index",
        "data_through": latest_month,
        "honesty_note": t(
            "province.note_tr" if price_level else "province.note_us", lang
        ),
        "provinces": rows,
    }


def project_province(code: str, amount: float, years: int,
                     market: str = "TR", lang: str = "tr") -> dict:
    """
    "What would X become in this area over N years?" — the distribution of
    every rolling N-year window in the area's own history (not a forecast).
    """
    from backend.services.projection import _windowed_real_band

    import numpy as np

    market = (market or "TR").upper()
    source = _SOURCES.get(market)
    if source is None:
        return {"available": False, "reason": t("province.no_breakdown", lang, market=market)}

    areas, _ = source()
    entry = areas.get(code.upper()) or areas.get(code)
    if not entry:
        return {"available": False, "reason": t("province.unavailable", lang)}

    months = sorted(entry["series"])
    values = np.array([entry["series"][m] for m in months])
    window = years * _QUARTERS_PER_YEAR

    band, real_band = _windowed_real_band(values, months, window, amount, market)
    if not band:
        return {
            "available": False,
            "reason": t("province.no_window", lang, name=entry["name"], years=years),
        }

    return {
        "available": True,
        "province": entry["name"],
        "amount": amount,
        "years": years,
        **band,
        "real_band": real_band,  # each window deflated by its OWN period inflation
        "honesty_note": t("province.projection_note", lang,
                          name=entry["name"], years=years),
    }
