#!/usr/bin/env python
"""
Refresh the bundled US price-index snapshots from the BLS public API.

Why they exist: the BLS v1 endpoint allows 25 requests/day per IP, and our
datacenter shares that budget with every other tenant on it. When the live
call fails, US inflation used to fall back to a hardcoded 3.0% constant while
still presenting itself as measured. A slightly stale real index is honest;
an invented number is not.

Run occasionally (the series are monthly):

    venv/bin/python scripts/refresh_us_index.py

It refuses to overwrite with anything shorter or older than what is already
committed, so a rate-limited run cannot quietly degrade the fallback.
"""

import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from backend.services import bls_service  # noqa: E402

DATA_DIR = pathlib.Path(__file__).parent.parent / "backend" / "data"

TARGETS = [
    ("us_cpi_index.json", bls_service.get_cpi_index,
     "US CPI-U (CUUR0000SA0) monthly index, snapshotted from the BLS public "
     "API. Used only when the live call fails — see scripts/refresh_us_index.py."),
    ("us_rent_index.json", bls_service.get_rent_index,
     "US rent of primary residence (CUUR0000SEHA) monthly index, snapshotted "
     "from the BLS public API. Same fallback role as us_cpi_index.json."),
]


def main() -> int:
    failures = 0
    for filename, fetch, note in TARGETS:
        path = DATA_DIR / filename
        fresh = fetch()
        if not fresh:
            print(f"✗ {filename}: no live data (rate limited?) — kept existing file")
            failures += 1
            continue

        existing = {}
        if path.exists():
            existing = json.loads(path.read_text()).get("index", {})

        if existing and (len(fresh) < len(existing) or max(fresh) < max(existing)):
            print(f"✗ {filename}: live data is shorter/older than committed — refused")
            failures += 1
            continue

        months = sorted(fresh)
        path.write_text(json.dumps({
            "_note": note,
            "base_series": "BLS CPI-U (1982-84=100)",
            "generated_from": f"{months[0]}..{months[-1]}",
            "index": {m: fresh[m] for m in months},
        }, indent=2) + "\n")
        print(f"✓ {filename}: {len(fresh)} months through {months[-1]}")

    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
