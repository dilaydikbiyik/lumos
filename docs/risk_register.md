# Lumos — Risk Register

*End-to-end audit of failure-prone points, their blast radius, and current mitigations.*
*Last reviewed: 2026-07-08. Severity: 🔴 breaks core flow · 🟡 degrades experience · 🟢 cosmetic.*

## External data sources

| # | Risk | Severity | Mitigation in place | Residual gap |
|---|------|----------|--------------------|--------------|
| 1 | **yfinance rate-limits (429) or breaks** — Yahoo has no SLA; observed live during development | 🟡 | Two-tier cache (fresh 24h + stale 7-day); `MarketDataError` → friendly 503; chat RAG context fails open | A cold cache (fresh deploy) + 429 = no data until Yahoo recovers. Roadmap: seed cache in CI artifact or secondary provider (Stooq) |
| 2 | **TCMB EVDS API drift** — the evds2→evds3 migration happened mid-development and silently redirected | 🟡 | Live-verified against evds3 (`igmevdsms-dis`); daily cache; static TÜFE fallback file ships in-repo; region features return `available: false` honestly | Static fallback ages; refresh checkpoint values quarterly |
| 3 | **EVDS housing series re-based again** (KFE was re-based to 2023=100 in 2024, killing old series) | 🟡 | Series codes centralized in `evds_service.KFE_REGIONS`; short-history guard refuses to fake distributions | Detection is manual; add a data-freshness alert to `/health` |
| 4 | **RSS feeds change shape or die** | 🟢 | Per-feed try/except; digest degrades to empty list; UI hides the card | — |

## AI layer

| # | Risk | Severity | Mitigation in place | Residual gap |
|---|------|----------|--------------------|--------------|
| 5 | **Free-tier quota exhaustion (429)** | 🟡 | Model fallback chain per tier (each Gemini model has its own free quota → ~3× capacity); per-user daily quotas by plan; polite bilingual 429 | Heavy multi-user load still shares one API key; paid tiers (infrastructure ready) are the real fix |
| 6 | **Provider outage (503, observed live)** | 🟡 | Chain treats 5xx like 429 and falls through; Anthropic chain handles credit-exhaustion the same way | Cross-provider fallback (gemini→anthropic) not automatic — deliberate, to keep costs predictable |
| 7 | **LLM returns malformed JSON in extraction** (profile / what-if) | 🟡 | 3-strategy parser (fence strip → first-object regex → nested regex); 422 with "continue the conversation" guidance; thinking-token truncation fixed via 4096+ budgets | — |
| 8 | **`[PROFILE_COMPLETE]` marker forgery via prompt injection** | 🔴 | SECURITY RULES block in system prompt; marker never honored from user text (only assistant output is scanned); role/length validation (Literal roles, 4k chars, 80 msgs) | Prompt-level defenses are probabilistic by nature; server-side re-validation (Pydantic) is the hard gate |
| 9 | **Prompt regression by future edits** | 🟡 | `test_prompt_rules.py` asserts marker/security/fear/ethics rules exist; prompt SHA in every log line | — |
| 10 | **AI invents financial numbers** | 🔴 | What-If pattern: LLM only extracts intent + phrases results; all math from `portfolio_engine`; projections are historical-window math, never model output | Applies to built surfaces; any NEW AI surface must follow the same pattern (documented in case study) |

## Platform & infrastructure

| # | Risk | Severity | Mitigation in place | Residual gap |
|---|------|----------|--------------------|--------------|
| 11 | **SQLite under concurrency** — single writer; fine for dev/demo | 🟡 | Async SQLAlchemy + short transactions; Alembic owns schema so Postgres swap is `DATABASE_URL` change | Not load-tested; move to Postgres before real multi-user traffic |
| 12 | **Clerk outage / JWKS unreachable** | 🔴 | 5s timeout on JWKS fetch; clean 401/500 — no data leak | No JWKS cache → Clerk down = login down. Roadmap: cache JWKS keys with TTL |
| 13 | **Quota race condition** — two simultaneous messages could both pass the counter check | 🟢 | Single-writer SQLite serializes in practice | On Postgres, switch `consume_quota` to an atomic UPDATE...RETURNING |
| 14 | **create_all vs Alembic drift** (bit us once in dev) | 🟡 | `create_all` removed from lifespan; Alembic is the only schema authority; CI applies migrations to a fresh DB on every push | — |
| 15 | **Secrets leakage** — an Anthropic key was exposed during development | 🟡 | Key rotation flagged to owner; `.env` gitignored; `detect-private-key` pre-commit hook | Rotation is manual; no secret scanning in CI yet (add gitleaks) |

## Product / correctness

| # | Risk | Severity | Mitigation in place | Residual gap |
|---|------|----------|--------------------|--------------|
| 16 | **Nominal returns mislead users** (the core domain risk) | 🔴 | Real (CPI-adjusted) values shown next to nominal everywhere: backtest, projections, region ranking, cash-erosion card | Static-fallback CPI slightly understates when live EVDS is down |
| 17 | **Scenario bands read as promises** | 🔴 | Every band ships an "this is NOT a prediction" honesty note; thin histories refuse to render a distribution (`MIN_WINDOWS`) | — |
| 18 | **Manual real-estate valuations go stale** | 🟢 | "endekse göre tahmin" labeling; TCMB index drift shown at region level | Per-holding index-based revaluation is roadmap |
| 19 | **Market pack content ages** (tax rules change) | 🟡 | Packs carry an explicit "confirm with a licensed local professional" disclaimer; content is data, not code — one-file updates | No review cadence; add a quarterly checklist |

## Monitoring gaps (roadmap)

- No error aggregation (Sentry) — request-ID correlation exists, but log search is manual
- `/health` checks liveness only; should also probe DB, cache write, EVDS freshness
- No uptime monitoring until deployment (Render health checks planned)
