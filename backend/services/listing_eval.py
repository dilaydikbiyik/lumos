"""
"Is this listing a fair price?"

The user pastes what a listing says — area, size, asking price — and gets the
asking price per m² set against what that area actually trades at.

WHAT MAKES THIS HONEST, and the reason it refuses more often than it answers:

A price INDEX and a price LEVEL are different data products, and only a level
can answer "is this expensive". Türkiye's TCMB publishes TL/m² per province,
so the comparison is real there. The FHFA index and the Bundesbank's segments
are indices — they say how prices MOVED, not what they ARE. Dividing an
asking price by an index number produces a number, and that number means
nothing.

So in a market without a price level this returns "cannot say" rather than a
comparison. A wrong verdict here is worse than no verdict: somebody walks
away from a fair price, or pays over the odds, on the strength of a number
the app made up.

Even where it works, the average is a PROVINCE average against one specific
property. A flat by the shore and a flat by the ring road are both in
İstanbul. The verdict says so rather than pretending precision it cannot
have.
"""

import logging
from typing import Optional

from backend.i18n import t

logger = logging.getLogger("lumos.listing_eval")

# Bands around the area average. Deliberately wide: within a fifth of the
# average is not "a good deal", it is noise between one street and the next.
_BARGAIN = -20.0
_FAIR_LOW = -20.0
_FAIR_HIGH = 20.0
_EXPENSIVE = 35.0


def _area_average_per_m2(area_code: str, market: str, lang: str) -> Optional[tuple[str, float]]:
    """(area name, latest TL/m²) where the market publishes a price LEVEL."""
    from backend.services.province_intelligence import _area_source

    source = _area_source(market)
    if source is None:
        return None
    read = source(lang)
    if not read.get("price_level"):
        return None            # an index cannot answer "is this expensive"

    entry = read["areas"].get(area_code.upper()) or read["areas"].get(area_code)
    if not entry or not entry.get("series"):
        return None

    periods = sorted(entry["series"])
    latest = entry["series"][periods[-1]]
    if not latest or latest <= 0:
        return None
    return entry["name"], float(latest)


def evaluate(*, area_code: str, size_m2: float, asking_price: float,
             market: str = "TR", lang: str = "tr") -> dict:
    """The listing's price per m² against its area's, with a verdict."""
    if not size_m2 or size_m2 <= 0 or not asking_price or asking_price <= 0:
        return {"available": False, "reason": t("listing.need_numbers", lang)}

    reference = _area_average_per_m2(area_code, market, lang)
    if reference is None:
        # Say WHY, because "no data" and "the data we have cannot answer
        # this" are different, and only one of them is fixable by waiting.
        return {"available": False, "reason": t("listing.index_only", lang)}

    area_name, area_per_m2 = reference
    listing_per_m2 = asking_price / size_m2
    delta_pct = round((listing_per_m2 / area_per_m2 - 1) * 100, 1)

    if delta_pct <= _BARGAIN:
        verdict = "below"
    elif delta_pct <= _FAIR_HIGH and delta_pct >= _FAIR_LOW:
        verdict = "fair"
    elif delta_pct >= _EXPENSIVE:
        verdict = "well_above"
    else:
        verdict = "above"

    return {
        "available": True,
        "area": area_name,
        "listing_per_m2": round(listing_per_m2, 2),
        "area_per_m2": round(area_per_m2, 2),
        "delta_pct": delta_pct,
        "verdict": verdict,
        "verdict_text": t(f"listing.verdict.{verdict}", lang,
                          pct=abs(delta_pct), area=area_name),
        # The caveat travels WITH the verdict rather than in a footnote,
        # because a province average against one property is the weakness of
        # this whole comparison and the reader has to hold both at once.
        "caveat": t("listing.caveat", lang, area=area_name),
        "questions": [
            t(f"listing.question.{key}", lang)
            for key in ("deed", "zoning", "access", "debts", "survey", "why_selling")
        ],
    }
