"""
Every number a client can send has an upper bound.

Pydantic accepts `1e999` (infinity) and `NaN` for a plain float, and `gt=0`
does not stop either. Both reached Postgres: a budget of Infinity read back
as null, a holding of Infinity turned every total on the summary into null,
and a goal of Infinity was a 500. Absurd finite figures (1e300) passed too
and produced a monthly mortgage of 7.9e300.

An upper bound fixes all three at once — `inf <= bound` is false and every
comparison with NaN is false — so this test walks the OpenAPI document and
refuses any numeric request field, body or query, that lacks one.
"""
from backend.main import app


def _schema(ref_or_schema, components):
    if "$ref" in ref_or_schema:
        return components[ref_or_schema["$ref"].rsplit("/", 1)[-1]]
    return ref_or_schema


def _numbers(schema, components, where, seen):
    """(where, schema) for every numeric leaf under `schema`."""
    schema = _schema(schema, components)
    for alt in schema.get("anyOf", []) + schema.get("allOf", []):
        if alt.get("type") != "null":
            yield from _numbers(alt, components, where, seen)
    if schema.get("type") in ("number", "integer"):
        yield where, schema
    if schema.get("type") == "array" and "items" in schema:
        yield from _numbers(schema["items"], components, where + "[]", seen)
    if isinstance(schema.get("additionalProperties"), dict):
        yield from _numbers(schema["additionalProperties"], components, where + "{}", seen)
    for name, prop in (schema.get("properties") or {}).items():
        key = (id(schema), name)
        if key in seen:
            continue
        seen.add(key)
        yield from _numbers(prop, components, f"{where}.{name}", seen)


def _unbounded():
    doc = app.openapi()
    components = doc.get("components", {}).get("schemas", {})
    out = []
    for path, ops in doc["paths"].items():
        for method, op in ops.items():
            sources = []
            for p in op.get("parameters", []):
                sources.append((f"{method.upper()} {path} ?{p['name']}", p.get("schema", {})))
            body = (op.get("requestBody") or {}).get("content", {}).get("application/json")
            if body:
                sources.append((f"{method.upper()} {path} body", body["schema"]))
            for where, schema in sources:
                for leaf, num in _numbers(schema, components, where, set()):
                    if not ({"maximum", "exclusiveMaximum", "enum", "const"} & num.keys()):
                        out.append(leaf)
    return sorted(set(out))


def test_every_numeric_request_field_has_an_upper_bound():
    missing = _unbounded()
    assert not missing, "numeric request fields with no upper bound:\n  " + "\n  ".join(missing)


import pytest  # noqa: E402


@pytest.mark.parametrize("raw", ["1e999", "-1e999", "NaN", "1e300"])
def test_infinity_nan_and_absurd_amounts_are_refused(client, raw):
    # Raw JSON: a client library would never send these, a direct call can.
    for path, body in [
        ("/api/v1/users/me/income", '{"monthly_income": %s}'),
        ("/api/v1/planning/goal-plan", '{"target_amount": %s, "years": 5}'),
    ]:
        method = client.patch if path.endswith("income") else client.post
        res = method(path, content=body % raw, headers={"Content-Type": "application/json"})
        assert res.status_code == 422, (path, raw, res.status_code)


def test_a_holding_id_past_the_integer_range_is_a_422_not_a_500(client):
    assert client.delete(f"/api/v1/holdings/{2**40}").status_code == 422
