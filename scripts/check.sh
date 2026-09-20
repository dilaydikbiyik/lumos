#!/usr/bin/env bash
#
# Everything CI runs, locally, with exit codes that actually propagate.
#
# This exists because of a real miss: verifying with
#
#     npx vitest run 2>&1 | tail -3
#
# always reports success. The pipeline's exit status is `tail`'s, not
# vitest's, so a failing suite looked green and was committed — the
# neutrality test had correctly caught country-specific wording in shared
# copy, and the failure was invisible until CI said so.
#
# `set -euo pipefail` is the whole point of this file. Run it before pushing.

set -euo pipefail

cd "$(dirname "$0")/.."

PYTHON="./venv/bin/python"
[ -x "$PYTHON" ] || PYTHON="python3"

step() { printf '\n\033[1m── %s\033[0m\n' "$1"; }

step "ruff"
$PYTHON -m ruff check backend/

step "pytest"
$PYTHON -m pytest backend/tests -q

step "eslint"
(cd frontend && npx eslint src --max-warnings=0)

step "vitest"
(cd frontend && npx vitest run)

step "build"
(cd frontend && npm run build)

# Journeys need a running app and a Clerk secret, so they are opt-in rather
# than part of every run. They are the ones that catch state-transition bugs —
# the right screen for the wrong account state — which every bug reported from
# the app so far has been.
if [ -n "${RUN_JOURNEYS:-}" ]; then
  step "journeys"
  node demo/journeys.mjs
else
  printf '\n\033[2m(skipping journeys — set RUN_JOURNEYS=1 with a local app + backend)\033[0m\n'
fi

printf '\n\033[32mAll checks passed.\033[0m\n'
