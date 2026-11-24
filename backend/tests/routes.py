"""
Every path the app serves, for tests that check the route table.

FastAPI 0.162 keeps an included router as one entry (with its prefix in an
include context) instead of copying each route into app.routes, so reading
`route.path` off app.routes lost every included endpoint.
"""


def routes(app) -> list[tuple[str, frozenset]]:
    """(full path, methods) for every route, included routers expanded."""
    out: list[tuple[str, frozenset]] = []

    def walk(items, prefix: str = "") -> None:
        for route in items:
            if hasattr(route, "path"):
                out.append((prefix + route.path, frozenset(getattr(route, "methods", None) or ())))
            elif hasattr(route, "original_router"):
                walk(route.original_router.routes, prefix + route.include_context.prefix)

    walk(app.routes)
    return out


def route_paths(app) -> set[str]:
    return {path for path, _ in routes(app)}
