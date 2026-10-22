"""
A field the handler returns and the model does not declare is invisible.

`response_model` FILTERS the response. `push` was returned by the health
handler for several commits and FastAPI dropped it silently, so it reached
no client at all — and its absence from production read as "production is
running an older build", which is the wrong thing to act on. A field added
to the handler and not to the model is invisible, not late.

So the rule is asserted over the SOURCE: every key the handler puts in its
return dict must be a declared field on HealthResponse. That cannot be
tested by calling the endpoint, because the endpoint is exactly where the
evidence is destroyed.
"""
import ast
import inspect

from backend.routers import health


def _returned_keys() -> set[str]:
    """The literal keys of the dict the health handler returns."""
    tree = ast.parse(inspect.getsource(health.health_check))
    keys: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Return) and isinstance(node.value, ast.Dict):
            for k in node.value.keys:
                if isinstance(k, ast.Constant) and isinstance(k.value, str):
                    keys.add(k.value)
    return keys


def test_the_scan_finds_the_keys_it_should():
    """Guards the guard: an empty scan would pass the real test for free."""
    keys = _returned_keys()
    assert len(keys) >= 6, f"only found {keys} — the scan is probably broken"
    assert "status" in keys


def test_every_key_the_handler_returns_is_declared_on_the_model():
    declared = set(health.HealthResponse.model_fields)
    undeclared = sorted(_returned_keys() - declared)
    assert not undeclared, (
        f"these keys are computed and then silently dropped by "
        f"response_model: {undeclared}. Declare them on HealthResponse, or "
        "stop computing them — a field the handler returns and the model "
        "does not declare reaches no client, and its absence looks like a "
        "stale deployment rather than a missing field."
    )


def test_the_model_declares_nothing_the_handler_never_sets():
    """
    The other direction. A declared field the handler never fills is served
    as its default forever, which is worse than absent: a reader sees a
    confident `false` for something that was never measured.
    """
    returned = _returned_keys()
    orphans = sorted(set(health.HealthResponse.model_fields) - returned)
    assert not orphans, (
        f"HealthResponse declares fields the handler never sets: {orphans}. "
        "Each is served as its default, which reads as a measurement."
    )


def test_the_endpoint_actually_serves_the_push_flag(client):
    """
    The instance, alongside the rule. Booleans only — the VAPID private key
    must never appear in a health response.
    """
    body = client.get("/health").json()
    assert "push" in body
    assert isinstance(body["push"], bool)
