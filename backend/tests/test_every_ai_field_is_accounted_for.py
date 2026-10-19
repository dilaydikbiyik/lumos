"""
No AI-written field may reach a reader unaccounted for.

Three guards exist, each for a different reason, and each was added only
after somebody asked whether the previous one covered the next field. That
is not a process that scales: the fourth AI field will be written by
somebody who does not remember this conversation.

So the question "is there another unguarded AI field?" is asked of the
SOURCE. Every call site that produces model text must appear in the
register below with what guards it, or this fails.

The register is deliberately not a list of guarded things — it is a list of
every call site and its verdict, including the ones whose verdict is "needs
no content rule, and here is why". A field that needs no rule is a
judgement worth writing down, because the alternative is each person
re-deciding it from scratch and one of them getting it wrong.

THE LESSON THIS FILE ENCODES: a consistency rule is only valid for text
whose prompt promises the same things. Applying the portfolio rule to the
REIT explanation silently deleted every correct one, because that prompt
instructs figures which are not portfolio weights. So "guarded" is never
enough — the register records WHICH rule, and the reason.
"""
import ast
import pathlib

BACKEND = pathlib.Path(__file__).resolve().parent.parent

# call site (file, enclosing function) -> the rule, and why that one.
REGISTER = {
    ("explainer.py", "explain_portfolio"):
        "explanation_check.verified_or_dropped — its prompt is handed the "
        "portfolio's own weights, so weights, category totals and the risk "
        "score are all checkable.",
    ("explainer.py", "explain_reit_inclusion"):
        "explanation_check.reit_verified_or_dropped — percentage rule OFF. "
        "reit_explain_prompt.txt instructs the 90% distribution requirement "
        "and ~8-10% historical returns, which are not portfolio weights; the "
        "portfolio rule deleted every correct REIT explanation.",
    ("news_service.py", "get_daily_digest"):
        "forecast_language, per item. No portfolio is in scope, so there is "
        "nothing to compare figures against; what it must not do is predict.",
    ("what_if.py", "answer_what_if"):
        "explanation_check.whatif_verified_or_dropped — a DIFFERENT allowed "
        "set from the portfolio rule, because a what-if answer legitimately "
        "states before-weights that are not in the current portfolio and the "
        "tickers are the union of two portfolios.",
    ("ai_service.py", "chat"):
        "The multi-turn producer. Like generate_text it has no content rule "
        "and should not: it cannot know what its caller asked for. Its own "
        "job is the provider chain, the quota and the injection hardening.",
    ("ai_service.py", "generate_text"):
        "The producer itself. No content rule belongs here — it has no idea "
        "what its caller asked for, which is exactly why each caller needs "
        "its own. Carries the daily cache and the provider fallback chain.",
    ("chat.py", "chat_endpoint"):
        "forecast_language, MEASURED not enforced (_note_if_predictive). "
        "No figure rule: there is no single set of numbers it narrates. "
        "The forecast rule is detectable and deliberately not enforced — a "
        "dropped reply leaves somebody who asked a question with nothing, "
        "and on long prose the rule's residual imprecision (3 of this "
        "app's 239 strings, in the word's non-market senses) grows with "
        "answer length. Structural guards carry it: injection hardening, "
        "quotas, no tool that can move money.",
    ("chat.py", "advisor_endpoint"):
        "Same as chat_endpoint, and the reason matters more here: this is "
        "the widest output in the app. advisor_prompt.txt forbids naming "
        "instruments as a buy call, predicting direction, tax or legal "
        "advice, and inventing numbers. Only the prediction clause is "
        "mechanically detectable, and it is logged rather than enforced "
        "for the reason above.",
}


# The functions that put model text into the world, by every name they are
# imported under.
_AI_PRODUCERS = {"generate_text", "chat", "ai_chat"}


def _ai_call_sites() -> set[tuple[str, str]]:
    """
    Every (file, function) in backend/ that puts model text into the world.

    REFERENCES, not only calls. The chat surface reaches the model through
    `asyncio.to_thread(ai_chat, ...)`, which passes the function rather than
    calling it — so a scan that only looked at call targets missed the
    single largest AI surface in the app while reporting four sites and
    looking thorough. Every explainer is invoked the same way from the
    routers.
    """
    sites: set[tuple[str, str]] = set()
    for path in BACKEND.rglob("*.py"):
        if "tests" in path.parts:
            continue
        try:
            tree = ast.parse(path.read_text())
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            # The producer's own definition is where its guard belongs, so a
            # function NAMED after a producer counts as that site.
            if node.name in _AI_PRODUCERS:
                sites.add((path.name, node.name))
                continue
            for inner in ast.walk(node):
                name = None
                if isinstance(inner, ast.Name):
                    name = inner.id
                elif isinstance(inner, ast.Attribute):
                    name = inner.attr
                if name in _AI_PRODUCERS:
                    sites.add((path.name, node.name))
                    break
    return sites


def test_the_scan_finds_the_call_sites_it_should():
    """Guards the guard: an empty scan would make the real test pass free."""
    sites = _ai_call_sites()
    assert len(sites) >= 4, f"only found {sites} — the scan is probably broken"


def test_no_ai_call_site_is_missing_from_the_register():
    sites = _ai_call_sites()
    unregistered = sorted(s for s in sites if s not in REGISTER)
    assert not unregistered, (
        "these produce model text and no one has said what guards it:\n  "
        + "\n  ".join(f"{f}::{fn}" for f, fn in unregistered)
        + "\n\nAdd each to REGISTER with the rule AND the reason that rule "
          "fits. Do not copy an existing rule: applying the portfolio check "
          "to the REIT explanation silently deleted every correct one."
    )


def test_the_register_has_no_entries_for_code_that_is_gone():
    """
    A register naming call sites that no longer exist rots into fiction, and
    a reader checking "is this guarded?" against it would be misled.
    """
    sites = _ai_call_sites()
    stale = sorted(k for k in REGISTER if k not in sites)
    assert not stale, (
        f"REGISTER names call sites that no longer exist: {stale}. "
        "Remove them, or the register stops describing the code."
    )
