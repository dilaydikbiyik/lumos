"""
No error a reader can see is a hard-coded sentence.

"Holding not found.", "Weights must sum to ~1" and "Extracted profile is
incomplete" reached Turkish and German readers in English. The smoke run's
language check skips short strings, which is how the first two slipped
through, so this reads the routers instead: an HTTPException's detail must
come from the translation table, not be written in place.
"""
import ast
from pathlib import Path

ROUTERS = Path(__file__).resolve().parents[1] / "routers"

# Not shown to readers: the admin console, and a market code the client
# only ever sends from the server's own list.
ALLOWED = {("admin.py", "Unknown plan"), ("users.py", "Unknown market")}


def _literal_details():
    for path in sorted(ROUTERS.glob("*.py")):
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            if not (isinstance(node, ast.Call) and getattr(node.func, "id", "") == "HTTPException"):
                continue
            for kw in node.keywords:
                if kw.arg != "detail":
                    continue
                if isinstance(kw.value, ast.Constant) and isinstance(kw.value.value, str):
                    yield path.name, kw.value.value, node.lineno
                elif isinstance(kw.value, ast.JoinedStr):
                    head = "".join(v.value for v in kw.value.values if isinstance(v, ast.Constant))
                    yield path.name, head, node.lineno


def test_reader_facing_errors_go_through_the_translation_table():
    offenders = [f"{name}:{line} {text!r}" for name, text, line in _literal_details()
                 if not any(name == f and text.startswith(p) for f, p in ALLOWED)]
    assert offenders == []


def test_the_scan_sees_a_literal_detail():
    """Proof the scan is not empty: the allowed ones are found."""
    found = {(name, text.split("'")[0].strip()) for name, text, _ in _literal_details()}
    assert any(name == "admin.py" for name, _ in found)


def test_a_validation_error_reaches_the_reader_in_their_language(client):
    """Pydantic's English ("Input should be greater than 0") was printed to
    Turkish and German readers."""
    bad = {"asset_type": "cash", "name": "x", "purchase_amount": -5}
    for lang, word in (("tr", "geçerli"), ("de", "ungültig"), ("en", "valid")):
        res = client.post("/holdings", json=bad, headers={"X-Lumos-Lang": lang})
        assert res.status_code == 422
        body = res.json()
        assert isinstance(body["detail"], str) and word in body["detail"], (lang, body)
        assert body["errors"] and body["errors"][0]["field"] == "purchase_amount"
