"""
Every API route is walked by scripts/live_smoke.py, or this fails.

The smoke script is the only thing that exercises the backend against REAL
data — live prices, live statistics offices, the live AI chain — and it is
where three bugs no unit test could see were found: physical gold refused on
every market, a Turkish reader on the German market served German news, and
the recommendation lost whenever the AI quota ran out. Its value is its
coverage. A route added later and never put in the script is a route that
will only meet the real world in production.

So coverage is asserted over the SOURCE: every (method, path) the app serves
must match a request the script makes.
"""
import ast
import pathlib
import re

from backend.main import app

SMOKE = pathlib.Path(__file__).resolve().parents[2] / "scripts" / "live_smoke.py"


def _app_routes() -> set[tuple[str, str]]:
    out = set()
    for r in app.routes:
        path = getattr(r, "path", "")
        if not path.startswith("/api/v1"):
            continue
        for m in getattr(r, "methods", None) or ():
            if m not in ("HEAD", "OPTIONS"):
                out.add((m, path[len("/api/v1"):]))
    return out


def _render(node, bindings) -> list[str]:
    """Every concrete path a Constant or f-string can produce."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return [node.value]
    if not isinstance(node, ast.JoinedStr):
        return []
    variants = [""]
    for part in node.values:
        if isinstance(part, ast.Constant):
            variants = [v + part.value for v in variants]
        elif isinstance(part.value, ast.Name) and part.value.id in bindings:
            variants = [v + b for v in variants for b in bindings[part.value.id]]
        else:
            variants = [v + "{x}" for v in variants]   # an id, a user, …
    return variants


def _smoke_requests() -> set[tuple[str, str]]:
    tree = ast.parse(SMOKE.read_text())
    # `for ep in ("fund-facts", ...)` — the loop variable's possible values.
    bindings: dict[str, list[str]] = {}
    for node in ast.walk(tree):
        if (isinstance(node, ast.For) and isinstance(node.target, ast.Name)
                and isinstance(node.iter, (ast.Tuple, ast.List))):
            vals = [e.value for e in node.iter.elts
                    if isinstance(e, ast.Constant) and isinstance(e.value, str)]
            if vals:
                bindings[node.target.id] = vals

    reqs = set()
    for node in ast.walk(tree):
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                and node.func.id == "c" and len(node.args) >= 3
                and isinstance(node.args[1], ast.Constant)):
            method = node.args[1].value
            for path in _render(node.args[2], bindings):
                reqs.add((method, path))
    return reqs


def _covered(route, requests) -> bool:
    method, template = route
    pattern = re.compile("^" + re.sub(r"\\{[^/]+\\}", "[^/]+", re.escape(template)
                                      .replace(r"\\{", "{").replace(r"\\}", "}")) + "$")
    return any(m == method and pattern.match(p) for m, p in requests)


def test_the_scan_finds_the_requests_it_should():
    """Guards the guard: an empty parse would pass the real test for free."""
    assert len(_smoke_requests()) > 50


def test_every_route_is_walked_by_the_live_smoke():
    requests = _smoke_requests()
    missing = sorted(r for r in _app_routes() if not _covered(r, requests))
    assert not missing, (
        "routes the live smoke never calls — add them to scripts/live_smoke.py "
        "so they meet real data before production does:\n  "
        + "\n  ".join(f"{m} {p}" for m, p in missing)
    )
