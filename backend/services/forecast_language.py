"""
Is this sentence a forecast?

The scenario card's entire claim is printed on it: "Bu bir tahmin DEĞİL" /
"This is NOT a forecast". It is the distribution of an asset's own history,
and the guard above it refuses to draw a band at all when the record holds
too few independent periods.

A news sentence sitting beside that card saying "analysts expect further
declines" contradicts the claim — not numerically, but IN KIND. The figures
stay a measurement while the prose beside them makes a prediction, and the
reader has no way to know the two halves are different sorts of statement.

Nothing checked for this. The digest prompt forbids ALARMIST words, which
is a different thing: "the Fed may cut rates" is perfectly calm and still a
forecast.

THE COST ASYMMETRY RUNS THE OTHER WAY HERE, which is why this is stricter
than explanation_check. `context_sentence` already returns None rather than
filler, and the card is designed to render without a sentence — so dropping
a borderline one costs almost nothing, while printing a forecast costs the
card the only promise it makes.

Still bounded, though: these are explicit forecast MARKERS, not any mention
of the future. "Markets can fall" is a fact about volatility and must pass;
"markets will fall" is a claim about what happens next and must not.
"""
import re

# Explicit forecast markers, per language. Deliberately verb forms and
# analyst vocabulary rather than anything future-tense: Turkish marks the
# future with -ecek/-acak, which appears in far too many ordinary words to
# match on, so the specific verbs are listed instead.
_MARKERS = {
    "tr": (
        # Both voices. Turkish analyst copy says "bekliyor" (active, "expects")
        # at least as often as "bekleniyor" (passive, "is expected"), and the
        # first draft of this list had only the passive form — so the single
        # most common forecast sentence in Turkish financial news walked
        # straight through. "bekliyor" also covers "bekliyorlar".
        r"bekliyor", r"bekleniyor", r"beklentisi", r"beklenmekte",
        r"tahmin edil", r"sürecek", r"devam edecek",
        r"öngör", r"hedef fiyat", r"projeksiyon",
        # Definite future claims about direction.
        r"yükselecek", r"düşecek", r"artacak", r"azalacak", r"gerileyecek",
        r"çıkacak", r"inecek",
    ),
    "en": (
        r"expected to", r"analysts expect", r"forecast", r"projected",
        r"is likely to", r"are likely to", r"price target", r"outlook for",
        r"will rise", r"will fall", r"will climb", r"will drop",
        r"set to rise", r"set to fall", r"poised to",
    ),
    "de": (
        r"erwartet", r"erwartung", r"prognose", r"voraussichtlich",
        r"dürfte", r"kursziel", r"aussichten für",
        r"wird steigen", r"wird fallen", r"wird sinken", r"wird klettern",
    ),
}

# One pattern over every language's markers. The sentence's language is
# known at the call site, but checking all three costs nothing and covers
# the case the app has hit repeatedly: text served under the wrong language.
_ALL = re.compile(
    "|".join(m for markers in _MARKERS.values() for m in markers),
    re.IGNORECASE,
)


def is_forecast(text: str) -> bool:
    """True when the sentence predicts rather than reports."""
    return bool(text) and bool(_ALL.search(text))


def markers_in(text: str) -> list[str]:
    """Which markers fired — for logging, so a drop can be explained."""
    if not text:
        return []
    return sorted({m.group(0).lower() for m in _ALL.finditer(text)})
