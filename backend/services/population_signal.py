"""
Population trend as a DEMAND signal — and the limits of calling it that.

Why this exists. Where people are moving is the one thing a beginner can
check about a region that is not a price. Prices tell you what has already
happened; a region gaining working-age residents for six straight years is a
statement about the demand that has to live somewhere.

Why it took a second source. The obvious one is TÜİK's address-based
registration system, which is the authority for Turkish migration. It is
served from MEDAS, a ZK-framework UI whose every response is a session-bound
component update rather than data — reading it means scraping a government
site, and this app scrapes nothing anywhere (the listing bridge builds search
links precisely so it never has to). Eurostat publishes the same figures for
Türkiye as a candidate country, through an API this app already speaks for
Germany. Same numbers, a documented interface, no scraping.

THREE HONESTY CONSTRAINTS, because this is the kind of number people
over-read:

  IT IS NOT A PRICE FORECAST, and the copy never implies one. A region can
  gain people and lose value in real terms — that is most of Türkiye in the
  last decade. Population is shown NEXT TO the real price change, never
  instead of it.

  THE GRANULARITY IS STATED. This is NUTS-2: 26 regions in Türkiye, not 81
  provinces and certainly not districts. "Tekirdağ, Edirne, Kırklareli" is one
  row. Attaching a three-province trend to one district's listing would be
  exactly the false precision the rest of the app refuses.

  A SHORT SERIES SAYS SO. Two points is not a trend, and the caller is told
  how many years actually backed the number rather than being handed a
  percentage that looks equally solid either way.
"""

import logging
from typing import Optional

from backend.i18n import t
from backend.markets import get_market_pack

logger = logging.getLogger("lumos.population")

# Below this many yearly observations the change is reported but not ranked:
# a single year-on-year move is as likely to be a boundary revision or a
# census correction as a trend.
MIN_YEARS_FOR_TREND = 4

# A region has to move more than this for the direction to mean anything.
# Registration systems get revised, and calling a 0.2% drift "shrinking"
# would put a scary word next to statistical noise.
FLAT_BAND_PCT = 1.0

def _eurostat(geos: list[str], age: str) -> Optional[dict[str, dict[str, float]]]:
    from backend.services import eurostat_service
    return eurostat_service.get_regional_populations(geos, age=age)


_SOURCES = {
    "eurostat": _eurostat,
    "none": lambda geos, age: None,
}


def _table_for(market: str, age: str = "TOTAL"):
    """
    The WHOLE table in one read, dispatched on the DECLARED source rather
    than the country code.

    Plural because the first version asked per region: 26 serial requests for
    a Turkish reader, 38 for a German one, doubled again by the working-age
    band. The endpoint took two minutes on a cold cache, which on a screen
    somebody opens while deciding where to buy is the same as broken.
    """
    pack = get_market_pack(market)
    reader = _SOURCES.get(pack.population_source)
    if not reader:
        return None
    return reader(list(pack.population_regions), age)


def _pct_change(series: dict[str, float]) -> Optional[tuple[float, int, str, str]]:
    """(% change, years covered, first year, last year) over the whole series."""
    years = sorted(series)
    if len(years) < 2:
        return None
    first, last = years[0], years[-1]
    if not series[first]:
        return None
    change = (series[last] / series[first] - 1) * 100
    return round(change, 1), len(years), first, last


def _direction(change_pct: float) -> str:
    if change_pct > FLAT_BAND_PCT:
        return "growing"
    if change_pct < -FLAT_BAND_PCT:
        return "shrinking"
    return "flat"


def available(market: str) -> bool:
    return get_market_pack(market).population_source != "none"


def region_trend(market: str, geo: str, lang: str = "tr") -> dict:
    """Population trend for one region, with its working-age share."""
    pack = get_market_pack(market)
    if not available(market):
        return {"available": False, "reason": t("population.no_source", lang)}

    name = pack.population_regions.get(geo)
    if name is None:
        return {"available": False, "reason": t("population.no_region", lang)}

    table = _table_for(market)
    total = (table or {}).get(geo)
    if not total:
        return {"available": False, "reason": t("population.no_data", lang)}

    measured = _pct_change(total)
    if measured is None:
        return {"available": False, "reason": t("population.no_data", lang)}

    change_pct, years, first, last = measured

    # The working-age share matters more than the headline for housing demand:
    # a region growing only in over-65s is not gaining households the way a
    # region growing in 15-64s is. Optional — a missing band degrades to the
    # headline rather than failing the whole answer.
    working_share = None
    working_table = _table_for(market, "Y15-64")
    working = (working_table or {}).get(geo)
    if working and last in working and last in total and total[last]:
        working_share = round(working[last] / total[last] * 100, 1)

    return {
        "available": True,
        "region": name,
        "code": geo,
        "change_pct": change_pct,
        "direction": _direction(change_pct),
        "years": years,
        "from_year": first,
        "to_year": last,
        "latest_population": int(total[last]),
        "working_age_share_pct": working_share,
        "trustworthy": years >= MIN_YEARS_FOR_TREND,
        # Carried WITH the number, not under it. A reader who sees "+8%" and
        # not this sentence has been told something the data does not say.
        "caveat": t("population.caveat", lang),
    }


def rank_regions(market: str, lang: str = "tr", limit: int = 10) -> dict:
    """Regions ordered by population change, fastest-growing first."""
    pack = get_market_pack(market)
    if not available(market):
        return {"available": False, "regions": [], "reason": t("population.no_source", lang)}

    # Both tables read ONCE for the whole market, then every region computed
    # in memory. Calling region_trend() per region re-read them each time.
    totals = _table_for(market) or {}
    working = _table_for(market, "Y15-64") or {}

    rows = []
    for geo, name in pack.population_regions.items():
        series = totals.get(geo)
        if not series:
            continue
        measured = _pct_change(series)
        if measured is None:
            continue
        change_pct, years, _first, last = measured
        if years < MIN_YEARS_FOR_TREND:
            continue

        share = None
        band = working.get(geo)
        if band and last in band and series.get(last):
            share = round(band[last] / series[last] * 100, 1)

        rows.append({
            "code": geo,
            "region": name,
            "change_pct": change_pct,
            "direction": _direction(change_pct),
            "latest_population": int(series[last]),
            "working_age_share_pct": share,
        })

    if not rows:
        return {"available": False, "regions": [], "reason": t("population.no_data", lang)}

    rows.sort(key=lambda r: r["change_pct"], reverse=True)
    return {
        "available": True,
        "regions": rows[:limit],
        "area_kind": "nuts2",
        "caveat": t("population.caveat", lang),
        "source_note": t("population.source_note", lang),
    }
