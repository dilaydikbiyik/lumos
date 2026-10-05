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

# The npm SCRIPTS, not hand-written equivalents of them. This file used to
# run `eslint src` while CI runs `npm run lint`, which is `eslint .` — so
# `public/` was never linted locally, a service-worker error went out twice,
# and CI failed on something this script had reported green. A gate that
# runs almost what CI runs is not a gate.
step "eslint"
(cd frontend && npm run lint)

step "vitest"
(cd frontend && npm test -- --passWithNoTests)

step "build"
(cd frontend && npm run build)

# CI applies every migration to an EMPTY database. A migration that only
# works against a database which already has the previous state passes
# locally and fails on a fresh deploy, which is the one time it matters.
step "alembic (fresh database)"
_tmpdb="$(mktemp -t lumos-migrations-XXXXXX.db)"
trap 'rm -f "$_tmpdb"' EXIT
DATABASE_URL="sqlite+aiosqlite:///$_tmpdb" $PYTHON -m alembic upgrade head >/dev/null
echo "   every migration applies to an empty database"

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
