"""
API versioning.

Every router is served under `/api/v1` and, for now, at its bare legacy path
too. The prefix is what allows a future breaking change to ship as `/api/v2`
without stranding anyone. The legacy mount exists only because the frontend
and the backend deploy independently: for a window after either ships, an old
client is talking to a new server, and dropping the old paths in the same
release that adds the prefix would turn that window into an outage.
"""
from backend.main import API_V1, app


def _paths() -> set[str]:
    return {route.path for route in app.routes if hasattr(route, "path")}


def test_every_endpoint_is_reachable_under_the_version_prefix():
    paths = _paths()
    legacy = {p for p in paths
              if not p.startswith((API_V1, "/docs", "/redoc", "/openapi"))
              and not p.startswith("/static")}

    missing = [p for p in legacy if f"{API_V1}{p}" not in paths]
    assert not missing, f"served unversioned only: {sorted(missing)}"


def test_the_legacy_paths_still_answer():
    """
    The deprecated mount is load-bearing until the deployed frontend has been
    on /api/v1 long enough that no cached bundle calls the old paths.
    """
    paths = _paths()
    for legacy in ("/health", "/users/me", "/holdings", "/profile"):
        assert legacy in paths, legacy
        assert f"{API_V1}{legacy}" in paths, legacy


def test_the_docs_describe_one_api_not_two(client):
    """
    Both mounts in the schema would show every endpoint twice and leave a
    reader guessing which is canonical. Only the versioned one is documented.
    """
    schema = client.get("/openapi.json").json()
    documented = set(schema["paths"])

    unversioned = [p for p in documented if not p.startswith(API_V1)]
    assert not unversioned, f"legacy paths leaked into the schema: {unversioned}"
    assert any(p.startswith(f"{API_V1}/users") for p in documented)


def test_both_mounts_serve_the_same_handler(client):
    """A versioned call and a legacy call must not be able to drift apart."""
    versioned = client.get(f"{API_V1}/health")
    legacy = client.get("/health")

    assert versioned.status_code == legacy.status_code == 200
    # Compare the stable fields: `status` can depend on live probes, but the
    # shape and the version string come from the same handler.
    assert set(versioned.json()) == set(legacy.json())
    assert versioned.json()["version"] == legacy.json()["version"]


def test_a_versioned_call_carries_auth_the_same_way(client):
    """
    The prefix must not bypass or duplicate a dependency. Hitting a protected
    route through the new mount has to behave exactly as the old one does.
    """
    versioned = client.get(f"{API_V1}/users/me")
    legacy = client.get("/users/me")
    assert versioned.status_code == legacy.status_code
