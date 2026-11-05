"""
Does this text positively read as some OTHER language than the one asked for?

Built for short strings — API messages, one-line news summaries — where the
paragraph check the content tests use ("contains one of these function
words") fails on perfectly good prose: "Für diesen Markt gibt es keine
regionalen Bevölkerungsdaten" has none of der/die/das/und. Run against the
first live smoke report, that paragraph check produced 76 failures and 2 real
ones.

So the rule here is the one that identifies the actual bug: the text carries
POSITIVE evidence of another language and none of the requested one. Absence
of evidence is not a failure; English prose served to a German reader is.

Tuned on real output, both ways. It catches "Exchange-traded assets
(stock/fund/etf/gold/crypto) require a ticker." for a Turkish reader — one
signal, so the threshold is one — and stays silent on all 48 short-but-
correct strings from that first report.
"""
from typing import Optional

# Characters worth two points (they belong to one language here), and short
# function words worth one. Words are matched padded with spaces.
_SIGNALS: dict[str, tuple[set[str], tuple[str, ...]]] = {
    "tr": (set("şŞğĞıİ"), (" ve ", " bir ", " için ", " bu ", " ile ", " değil",
                          " gibi ", " olarak ", " daha ", " senin ", " sana ")),
    "en": (set(), (" the ", " and ", " you ", " is ", " of ", " that ", " your ",
                   " to ", " for ", " with ", " this ", " are ", " can ", " a ")),
    "de": (set("ß"), (" der ", " die ", " das ", " und ", " nicht ", " dir ", " ist ",
                      " ein", " für ", " mit ", " sich ", " dein", " kein", " auf ",
                      " es ", " wird ", " zu ", " du ", " bei ", " ihnen ")),
}


def score(text: str, lang: str) -> int:
    chars, words = _SIGNALS[lang]
    low = f" {text.lower()} "
    return len(set(text) & chars) * 2 + sum(w in low for w in words)


def wrong_language(text: str, lang: str) -> Optional[str]:
    """The language `text` positively reads as, when that is not `lang`."""
    if not text or lang not in _SIGNALS:
        return None
    if score(text, lang) > 0:
        return None
    others = {o: score(text, o) for o in _SIGNALS if o != lang}
    best = max(others, key=others.get)
    return best if others[best] >= 1 else None
