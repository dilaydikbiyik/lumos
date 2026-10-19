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


# Negators that turn a forecast marker into its opposite.
#
# This is not a refinement, it is a correctness fix for a shipped bug. The
# first version flagged any marker anywhere, so it dropped exactly the
# sentences this app exists to produce:
#
#   "Kimse borsanın ne yapacağını öngöremez."   -> matched "öngör"
#   "Nobody can forecast the market."           -> matched "forecast"
#   "This is NOT a forecast."                   -> matched "forecast"
#
# That last one is the app's OWN honesty note, printed on every projection
# card. Measured against the app's 239 translated strings, 12 tripped the
# rule and 7 of those were the disclaimers asserting that a figure is not a
# forecast. A rule that deletes the sentence "this is not a forecast" for
# containing the word "forecast" is worse than no rule.
_NEGATORS_BEFORE = (
    r"kimse", r"hiç kimse", r"değil", r"yok",
    r"not", r"no one", r"nobody", r"cannot", r"can't", r"never", r"n't",
    r"kein", r"keine", r"nicht", r"niemand",
)
_NEG_BEFORE_RE = re.compile("|".join(_NEGATORS_BEFORE), re.IGNORECASE)

# Turkish negates with a SUFFIX, so the negator sits after the stem rather
# than before it: öngör|eme|z, bekle|me|yor. Nothing in a word-list
# approach catches that, which is why it is matched separately.
_TR_NEG_SUFFIX_RE = re.compile(r"^(?:[eaıi]?m[ae]|[eaıi]?maz|[eaıi]?mez)", re.IGNORECASE)

# How far back a negator still governs the marker. One clause, roughly —
# long enough for "kimse ... öngöremez", short enough that a negation two
# sentences earlier does not excuse a forecast.
_NEGATION_WINDOW = 45


def _is_negated(text: str, match: "re.Match[str]") -> bool:
    """Whether this particular marker is governed by a negation."""
    before = text[max(0, match.start() - _NEGATION_WINDOW):match.start()]
    if _NEG_BEFORE_RE.search(before):
        return True
    # Turkish suffixal negation, immediately after the stem.
    return bool(_TR_NEG_SUFFIX_RE.match(text[match.end():]))


def is_forecast(text: str) -> bool:
    """
    True when the sentence predicts rather than reports.

    A negated marker does not count: discussing forecasts, or saying that
    nobody can make one, is the opposite of making one — and is a thing
    this app says constantly.
    """
    if not text:
        return False
    return any(not _is_negated(text, m) for m in _ALL.finditer(text))


def markers_in(text: str) -> list[str]:
    """
    Which markers fired, negated ones excluded — for logging, so a drop can
    be explained and so a drop with no marker is impossible.
    """
    if not text:
        return []
    return sorted({
        m.group(0).lower() for m in _ALL.finditer(text) if not _is_negated(text, m)
    })
