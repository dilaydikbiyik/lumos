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
set -E   # ERR trap fires inside functions too, so the FAIL line is never skipped

# Registered HERE, not at the end: a trap only exists from the line that
# declares it onward, so one written beside the success message can never
# fire — the script is already dead by the time that line would run. The
# first version of this did exactly that and printed nothing on failure.
trap 'printf "\n\033[31m== GATE FAILED (see the step above) ==\033[0m\n"' ERR

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

# A single unmissable last line.
#
# This script already exits non-zero on the first failure, which is the
# contract that matters. But a reader (me included) pipes it through
# `grep | head` to skim it, and a filter that keeps the first few matching
# lines will happily show ruff and pytest passing and never reach the
# eslint error underneath. CI then fails on something the local gate had
# already caught and the summary had hidden.
#
# So the verdict is the LAST line and it carries the word FAIL when the
# script dies early: a tail always tells the truth even when a grep does
# not, and an aborted run no longer ends on a cheerful line from an
# earlier step.
printf '\n\033[32m══ GATE PASSED — all steps green ══\033[0m\n'
