"""
Does the prose agree with the numbers?

The portfolio is a deterministic formula and the figures on screen are its
output. The sentence beside them is written by a model, from a prompt that
is handed those same figures — so the model has every number it needs and
no reason to invent one. "No reason to" is not a guarantee, and nothing
checked it: every test touching `plain_explanation` either passes an empty
string or asserts that a mocked value came back unchanged.

That is the app's one real consistency risk. Not the allocation — the same
input produces the same allocation every time — but the possibility of
prose that says "weighted toward gold" beside a chart that is weighted
toward equities. A reader cannot tell which half to believe, and the half
they are most likely to believe is the sentence, because it is in their
language.

A test alone cannot close this, because the thing being checked is
non-deterministic: the model writes something new whenever the cache
misses. So the rule lives in production and the tests pin the rule.

CONSERVATIVE BY DESIGN. Dropping a correct explanation has a real cost —
the reader loses the one part of the page written for them — so this
flags only what is definitely wrong, and deliberately lets through
anything it cannot judge. Each check below says what it refuses to guess
about.
"""
import logging
import re
from collections import defaultdict
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from backend.schemas.portfolio import PortfolioRecommendResponse

logger = logging.getLogger("lumos.explanation_check")

# Prose rounds. "30.3%" is reasonably written as "30%", and a model saying
# "about a third" is not making a claim this can check at all.
TOLERANCE_PP = 1.0

# A ticker-shaped token: two to six capitals, optionally dotted for a
# non-US listing (XU100.IS, 4GLD.DE). Matched on word boundaries so it does
# not fire inside an ordinary capitalised word.
_TICKER_RE = re.compile(r"\b[A-Z]{2,6}(?:\.[A-Z]{2})?\b")

# Percentages, in BOTH orders and both decimal conventions: "30.3%",
# "30,3 %", and Turkish "%30,3" — which puts the sign FIRST.
#
# The prefix form is not a nicety. Turkish is this app's primary language
# and writes every percentage that way, so a pattern matching only the
# suffix form detects nothing at all in Turkish prose. Worse, it fails
# SILENTLY: the check returns "consistent" because it found no figures to
# compare, and the test asserting that real figures pass goes green for the
# wrong reason. That is exactly how a vacuous test looks from the outside.
_PERCENT_RE = re.compile(r"%\s*(\d{1,3}(?:[.,]\d{1,2})?)|(\d{1,3}(?:[.,]\d{1,2})?)\s*%")

# "6/10", the risk score as the prompt states it.
_SCORE_RE = re.compile(r"\b(\d{1,2}(?:[.,]\d)?)\s*/\s*10\b")

# Capitalised words that are not tickers. Without this the check would flag
# ordinary prose: a German sentence capitalises every noun, and an English
# one starts with a capital. Only words that look like tickers AND are not
# ordinary vocabulary reach the assertion.
_NOT_TICKERS = {
    # Sentence-initial and common capitalised prose across the three languages.
    "ETF", "ETFS", "REIT", "REITS", "BIST", "TRY", "USD", "EUR", "TL",
    "AB", "EU", "US", "USA", "UK", "SPK", "SEC", "BAFIN", "UCITS", "ETC",
    "DAX", "MSCI", "VAT", "KDV", "AI", "APP", "PWA",
    # German nouns in caps that fit the ticker shape.
    "DEIN", "DEINE", "DAS", "DER", "DIE", "UND", "IST", "EIN", "EINE",
    # Turkish and English short words that fit it.
    "BU", "VE", "BIR", "ILE", "THE", "AND", "YOU", "FOR", "ARE",
}


def _allowed_percentages(portfolio: "PortfolioRecommendResponse") -> set[float]:
    """
    Every percentage the prose may legitimately state.

    Individual weights, because the prompt lists them. Category totals,
    because aggregating is the natural way to describe a mix in words
    ("about 30% in equities"). And 100, because "the whole portfolio" is a
    sentence somebody writes.

    NOT subset sums of arbitrary holdings: allowing those would permit
    almost any number in a five-asset portfolio and the check would stop
    meaning anything.
    """
    allowed = {100.0}
    by_category: dict[str, float] = defaultdict(float)
    for a in portfolio.allocations:
        pct = a.weight * 100
        allowed.add(round(pct, 1))
        by_category[a.category] += pct
    for total in by_category.values():
        allowed.add(round(total, 1))
    return allowed


def contradictions(text: str, portfolio: "PortfolioRecommendResponse") -> list[str]:
    """
    Where the prose disagrees with the figures. Empty means it is consistent
    as far as this can tell — which is not the same as "it is good prose".
    """
    if not text:
        return []

    problems: list[str] = []
    real_tickers = {a.ticker.upper() for a in portfolio.allocations}

    # 1. A ticker that is not in this portfolio. Unambiguous: the prompt was
    #    given these holdings and no others, so naming a different one is
    #    the model supplying an instrument from nowhere — which is also the
    #    single worst thing this app could print, because a reader may act
    #    on a symbol.
    for token in set(_TICKER_RE.findall(text)):
        if token in _NOT_TICKERS or token in real_tickers:
            continue
        # A token that is also a holding's NAME word is prose, not a symbol.
        if any(token.lower() in a.name.lower() for a in portfolio.allocations):
            continue
        problems.append(f"names {token!r}, which is not in this portfolio")

    # 2. A percentage matching no weight, no category total, and not 100.
    allowed = _allowed_percentages(portfolio)
    for prefix, suffix in set(_PERCENT_RE.findall(text)):
        value = float((prefix or suffix).replace(",", "."))
        if any(abs(value - ok) <= TOLERANCE_PP for ok in allowed):
            continue
        problems.append(
            f"states {value}%, which is no holding's weight and no category total"
        )

    # 3. A risk score that is not the reader's. Stated as x/10, which is how
    #    the prompt gives it, so a different value is the model altering a
    #    fact about the person it is writing to.
    for raw in set(_SCORE_RE.findall(text)):
        value = float(raw.replace(",", "."))
        if abs(value - portfolio.risk_score) > 0.05:
            problems.append(
                f"states a risk score of {value}/10; the reader's is "
                f"{portfolio.risk_score}/10"
            )

    return problems


def verified_or_dropped(text: str, portfolio: "PortfolioRecommendResponse") -> str:
    """
    The explanation, or an empty string when it contradicts the figures.

    DROPPED rather than corrected. Editing a model's sentence to match the
    numbers would produce prose nobody wrote and nobody checked, and the
    page is complete without it: the allocation, the chart and the formula
    are all still there. A missing paragraph is a smaller failure than a
    confident wrong one.
    """
    problems = contradictions(text, portfolio)
    if not problems:
        return text
    # WARNING, not debug: this firing means the model contradicted its own
    # prompt, and if it starts firing often that is worth knowing about
    # rather than discovering in a screenshot.
    logger.warning("explanation dropped — contradicts the portfolio: %s", problems)
    return ""
