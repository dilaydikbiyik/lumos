"""
Nobody may take the silent Turkish default.

Forty-eight functions in this backend declare `market: str = "TR"`. The
default is reasonable on its own — TR is the reference market, and it keeps
old call sites working. That is exactly what makes it dangerous: a caller
that FORGETS to pass market does not fail, does not warn, and returns a
confident, wrong, Turkish answer.

Two live bugs were found this way, both user-visible numbers:

  routers/holdings.py  monthly_cash_erosion(idle_cash)
      Every US and German reader was shown Turkish inflation eating their
      idle cash. 100.000 came back as 2.025 lost per month against a real
      German figure of 548 — 3.7x too large, under a heading that asks
      whether their money is melting.

  services/what_if.py  build_portfolio(risk_score=..., budget=...)  (x2)
      Every what-if answer compared two TURKISH portfolios. A German user
      asking what changes if they add money was shown BIST instruments,
      narrated as real engine output, which it was — for the wrong country.

Neither was caught by any test, because every test passed the market
explicitly. The bug lives in the ABSENCE of an argument, which only a scan
of the source can see. So this walks the AST: any call to a
market-defaulting function that does not supply market, positionally or by
keyword, fails here.

This is the same technique as the content catalogues: assert a rule over
the source rather than an instance in a fixture.
"""
import ast
import pathlib

BACKEND = pathlib.Path(__file__).resolve().parent.parent

# Functions whose own body RESOLVES the market before dispatching, so an
# internal call that omits it is forwarding, not defaulting. Each of these
# dispatches on the market pack's declared source and calls a service that
# is specific to one country and takes no market argument at all.
FORWARDING_OK = {
    # inflation_service.get_rent_index -> bls_service / bundesbank_service
    ("inflation_service.py", "get_rent_index"),
}


def _market_defaulting_functions() -> dict[str, tuple[str, int]]:
    """name -> ("pos"|"kw", index of the market parameter)."""
    sigs: dict[str, tuple[str, int]] = {}
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
            pos = [a.arg for a in node.args.posonlyargs + node.args.args]
            kwo = [a.arg for a in node.args.kwonlyargs]
            if "market" in pos:
                i = pos.index("market")
                ndef = len(node.args.defaults)
                if i >= len(pos) - ndef:
                    default = node.args.defaults[i - (len(pos) - ndef)]
                    if isinstance(default, ast.Constant) and default.value == "TR":
                        sigs[node.name] = ("pos", i)
            elif "market" in kwo:
                i = kwo.index("market")
                default = node.args.kw_defaults[i]
                if isinstance(default, ast.Constant) and default.value == "TR":
                    sigs[node.name] = ("kw", i)
    return sigs


def test_the_backend_has_market_defaulting_functions_to_check():
    """Guards the guard: if the scan finds nothing, the test below is vacuous."""
    sigs = _market_defaulting_functions()
    assert len(sigs) > 20, (
        f"only {len(sigs)} market-defaulting functions found — the scan is "
        "probably broken, which would make the real test below pass for free"
    )


def test_no_call_site_takes_the_silent_turkish_default():
    sigs = _market_defaulting_functions()
    offenders: list[str] = []

    for path in BACKEND.rglob("*.py"):
        if "tests" in path.parts:
            continue
        try:
            tree = ast.parse(path.read_text())
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            name = (node.func.attr if isinstance(node.func, ast.Attribute)
                    else getattr(node.func, "id", None))
            if name not in sigs:
                continue
            if (path.name, name) in FORWARDING_OK:
                continue
            kind, index = sigs[name]
            if any(kw.arg == "market" for kw in node.keywords):
                continue
            if kind == "pos" and len(node.args) > index:
                continue
            offenders.append(
                f"{path.relative_to(BACKEND.parent)}:{node.lineno} "
                f"calls {name}() without a market"
            )

    assert not offenders, (
        "these call sites fall back to Turkish for every reader:\n  "
        + "\n  ".join(offenders)
    )
