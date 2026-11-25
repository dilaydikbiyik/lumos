# Lumos

Investment assistant for complete beginners: "invest without fear, learning as you go."
FastAPI backend (`backend/`), React + Vite PWA (`frontend/`), Alembic migrations, Clerk auth.
API on Render, web on Vercel; iOS/Android store release in progress. Market Packs = the
per-market data and i18n layer (`docs/adding-a-market.md`).

Product filter for every change: *does this help a timid beginner understand and act?*
Explain before showing, no jargon by default, describe instruments but never recommend one.

## Sessions

- **Start by reading `docs/PROGRESS.md`.** Do not re-derive the project's history.
- `todo.md` is the full log (~258 KB, ~65K tokens). Never read it whole: `grep -n` the heading
  you need, then read that range.
- When the user wraps up, rewrite `docs/PROGRESS.md` (state, next step, decisions and why,
  open items). Keep it under ~60 lines; detail goes to `todo.md` and git, not there.
  Overwrite it from scratch every time — never append. Finished items and history move to a
  dated "Session log" section at the end of `todo.md`.

## Session habits (do these without being asked)

- **Session start:** read `docs/PROGRESS.md` before the first task and say in one line where we left off.
- **Before proposing or making a commit:** update `docs/PROGRESS.md` first and include it in the commit.
- **When a task is finished:** update `docs/PROGRESS.md`, then remind the user:
  "Done — PROGRESS.md updated. Run `/clear` before the next task."
- **When the session has grown long** (many files read, many turns, a long debugging loop),
  remind the user: "Check `/context`; past 100K, run `/compact`." You cannot see the context
  size yourself, so judge by how much has happened.

## Commands

```
./scripts/check.sh                          # everything CI runs; exit codes propagate
./venv/bin/python -m pytest backend/tests/ -q
alembic upgrade head && uvicorn backend.main:app --reload --port 8000
cd frontend && npm run dev | npm test | npm run lint
```

Never judge a test run through a pipe (`... | tail`): the pipe's exit code hides failures.
Use `scripts/check.sh`.

## Rules

- Plain English. The first time a technical or architectural term comes up (e.g. hook, middleware,
  migration, estimand), add a short plain-language gloss in parentheses.
- Reply in English, concisely; switch to Turkish when the user asks. Code, comments and commits in English.
- Commit or push only when the user explicitly asks. No `Co-Authored-By` or AI-attribution lines.
- Never commit `.env`. Every external API call goes behind the daily cache. Clerk JWTs are
  verified on the backend. Every error state has fallback UI. Money fields are bounded
  (`backend/schemas/limits.py`). Every system prompt carries the legal disclaimer.

## Docs

`docs/architecture.md` · `docs/api_reference.md` · `docs/production-readiness.md` ·
`docs/risk_register.md` · `docs/store-submission.md` · `docs/billing-setup.md`.
Graphify navigation notes: `CLAUDE.local.md`.
