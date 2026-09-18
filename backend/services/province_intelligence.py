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
from backend.services import (
    bundesbank_service, evds_service, fred_service, inflation_service,
)

logger = logging.getLogger("lumos.province")

VALID_HORIZONS = (1, 3, 5)

# Readers declare their own frequency. The Turkish and US series are
# quarterly; the Bundesbank's are annual, and reading a 3-year horizon as 12
# observations back turned it into a 12-year one.
_PERIODS_PER_YEAR = {"quarterly": 4, "annual": 1}

# Nested segments (the seven largest cities sit inside the 127) are not
# alternative places to buy, so they are compared rather than ranked.
_COMPARISON = "comparison"
_RANKING = "ranking"


def _change_over_periods(prices: dict[str, float], periods_back: int) -> Optional[float]:
    if len(prices) < 2:
        return None
    months = sorted(prices)
    latest = months[-1]
    base_pos = max(len(months) - 1 - periods_back, 0)
    base = months[base_pos]
    if prices[base] <= 0 or base == latest:
        return None
    return round((prices[latest] / prices[base] - 1) * 100, 1)


def _row(code: str, name: str, series: dict[str, float], periods: int,
         market: str, price_level: bool) -> Optional[dict]:
    """One area's nominal and real change, or None when its history is short."""
    change = _change_over_periods(series, periods)
    if change is None:
        return None

    months = sorted(series)
    latest_month = months[-1]
    base_month = months[max(len(months) - 1 - periods, 0)]
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


def _tcmb_areas(lang: str = "tr") -> dict:
    """TCMB publishes a price LEVEL: TL per m², per province, quarterly."""
    data = evds_service.get_province_unit_prices() or {}
    return {
        "areas": {code: {"name": e["name"], "series": e["prices"]}
                  for code, e in data.items()},
        "price_level": True, "frequency": "quarterly", "shape": _RANKING,
    }


def _fred_areas(lang: str = "tr") -> dict:
    """FHFA via FRED publishes an INDEX per state, quarterly — no price level."""
    data = fred_service.get_all_state_hpi()
    return {
        "areas": {code: {"name": e["name"], "series": e["index"]}
                  for code, e in data.items()},
        "price_level": False, "frequency": "quarterly", "shape": _RANKING,
    }


# Keyed by the source a pack DECLARES, not by its country code — the same
# pattern inflation_service uses. A new market that declares an existing
# source works without touching this file; one that brings a new source adds
# a reader here and nowhere else.
def _bundesbank_areas(lang: str = "tr") -> dict:
    """
    The Bundesbank publishes an ANNUAL index for nested city-size aggregates.
    No price level, and the segments overlap rather than partition the
    country — so they are compared, never ranked against each other.
    """
    data = bundesbank_service.get_segments(lang)
    return {
        "areas": {code: {"name": e["name"], "series": e["index"]}
                  for code, e in data.items()},
        "price_level": False, "frequency": "annual", "shape": _COMPARISON,
    }


_SOURCES = {
    "tcmb_evds": _tcmb_areas,
    "fred": _fred_areas,
    "bundesbank": _bundesbank_areas,
}


def _pack(market: str):
    from backend.markets import get_market_pack

    return get_market_pack(market)


def _area_source(market: str):
    """
    The reader for this market's sub-national data, or None.

    A pack must both declare a breakdown AND name a source we can read;
    claiming one without the other would render an empty table rather than
    the honest "not published here" card.
    """
    return _SOURCES.get(_pack(market).regional_housing_source)


def rank_provinces(horizon_years: int = 3, market: str = "TR",
                   lang: str = "tr") -> dict:
    """
    Rank every area in the market by REAL appreciation over the chosen
    horizon (1/3/5 years) — 81 provinces in Türkiye, 50 states plus DC in
    the United States.
    """
    horizon_years = horizon_years if horizon_years in VALID_HORIZONS else 3
    market = (market or "TR").upper()

    source = _area_source(market)
    if source is None:
        return {"available": False, "provinces": [],
                "note": t("province.no_breakdown", lang, market=market)}

    read = source(lang)
    areas, price_level = read["areas"], read["price_level"]
    periods = horizon_years * _PERIODS_PER_YEAR[read["frequency"]]
    if not areas:
        return {"available": False, "provinces": [],
                "note": t("province.unavailable", lang)}

    rows = []
    latest_month = None
    for code, area in areas.items():
        row = _row(code, area["name"], area["series"], periods, market, price_level)
        if row is None:
            continue
        latest_month = row.pop("_latest_month")
        rows.append(row)

    if not rows:
        return {"available": False, "provinces": [],
                "note": t("province.unavailable", lang)}

    rows.sort(key=lambda r: (r["real_change_pct"] is None, -(r["real_change_pct"] or 0)))
    # A rank number invites "pick number one". That reads as advice when the
    # areas are alternatives, and as nonsense when they are nested segments of
    # one market, so it is only attached to the former.
    if read["shape"] == _RANKING:
        for i, row in enumerate(rows):
            row["rank"] = i + 1

    return {
        "available": True,
        "horizon_years": horizon_years,
        "market": market,
        # The client needs to know WHICH kind of number it received: a price
        # level can be printed as "X per m²", an index cannot.
        "measure": "unit_price_per_m2" if price_level else "price_index",
        # Whether these areas are alternatives to choose between, or nested
        # segments of one market that can only be compared.
        "shape": read["shape"],
        "frequency": read["frequency"],
        "data_through": latest_month,
        # Named for the kind of number, not the country: a new market reading
        # an index would otherwise be handed "the US note".
        "honesty_note": (
            t("province.note_price_level", lang) if price_level
            else t("province.note_index", lang,
                   source=t(f"source.{_pack(market).regional_housing_source}", lang))
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
    source = _area_source(market)
    if source is None:
        return {"available": False, "reason": t("province.no_breakdown", lang, market=market)}

    read = source(lang)
    areas = read["areas"]
    entry = areas.get(code.upper()) or areas.get(code)
    if not entry:
        return {"available": False, "reason": t("province.unavailable", lang)}

    months = sorted(entry["series"])
    values = np.array([entry["series"][m] for m in months])
    window = years * _PERIODS_PER_YEAR[read["frequency"]]

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
