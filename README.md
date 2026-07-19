# 🪰✨ Lumos — Smart Investment Assistant

[![CI](https://github.com/dilaydikbiyik/lumos/actions/workflows/ci.yml/badge.svg)](https://github.com/dilaydikbiyik/lumos/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-async-009688)
![React](https://img.shields.io/badge/react-19-61DAFB)
![Tests](https://img.shields.io/badge/tests-245%20backend%20%2B%2014%20frontend-3DD68C)
![Cost](https://img.shields.io/badge/running%20cost-%240%2Fmonth-F5A524)
🔗 **[Live demo →](https://lumos-sooty.vercel.app)**
> An AI-powered investment guide built for people who have never invested — and are scared to start.
> *"Investing looks like a dark forest. Lumos is the light in your hand."*

Lumos is **not a trading app**. It's the layer missing *before* trading apps: a guide that profiles
your risk tolerance through natural conversation, explains every recommendation in plain language,
shows you the honest downside before the upside, and treats your fear as **data — not weakness**.

**Table of contents:**
[Why Lumos](#why-lumos-exists) · [Feature tour](#feature-tour) · [Architecture](#architecture) ·
[AI layer](#the-ai-layer-quota-resilient-billing-ready) · [Going global](#going-global-market-packs) ·
[Data sources](#data-sources-all-free) · [Security](#security--honesty-by-design) ·
[Testing](#testing) · [Getting started](#getting-started) · [Engineering docs](#engineering-docs) ·
[Roadmap](#roadmap)

---

## Screenshots

<p align="center">
  <img src="demo/video/lumos-demo.gif" width="300" alt="Lumos demo — mobile tour" />
</p>

| Onboarding | Risk profile | Portfolio |
|---|---|---|
| ![Karşılama](demo/screens/01-karsilama.png) | ![Risk profili](demo/screens/02-risk-profili.png) | ![Portföy](demo/screens/03-portfoy.png) |

| Holdings + live chart | Dashboard | AI advisor |
|---|---|---|
| ![Varlıklarım](demo/screens/05-varliklarim.png) | ![Panel](demo/screens/06-panel.png) | ![Danışman](demo/screens/08-danisman.png) |

| Rent vs. buy | Province price explorer | Desktop layout |
|---|---|---|
| ![Kirada mı otur, ev mi al](demo/screens/04-kira-vs-ev.png) | ![Emlak Keşfet](demo/screens/07-emlak-kesfet.png) | ![Desktop](demo/screens/09-desktop-panel.png) |

**The screen no investing app wants to show you** — carrying card debt, the app
says clear it first and does the arithmetic, before it will show you a portfolio:

<p align="center">
  <img src="demo/screens/11-borc-once.png" width="300" alt="Borcu önce kapat" />
</p>

<details>
<summary>More: desktop portfolio view</summary>

![Desktop portföy](demo/screens/10-desktop-portfoy.png)

</details>

> Full demo video: [demo/video/lumos-demo.mp4](demo/video/lumos-demo.mp4)

---

## Why Lumos exists

Millions of people want to invest but never start. The blocker isn't access — commission-free
apps are everywhere — it's **fear**: *"my money will melt away", "I'll get scammed",
"I don't understand any of this"*. Existing apps solve execution; nobody solves the trust
layer that comes before execution.

Lumos fills that gap with three product pillars:

| Pillar | What it means in practice |
|---|---|
| 🧠 **Fear is data** | Onboarding asks what scares you; the AI adapts its language to *your* fear; a literal **Panic Button** exists for scary market days |
| 📉 **Inflation honesty** | Every return is shown *nominal AND real* (CPI-adjusted, live central-bank data). A region that "gained 40%" while inflation ran 60% actually lost value — Lumos is built to say so |
| 🏘️ **Real estate + stocks, one roof** | Land and apartments (Turkey's favorite asset class) and capital markets in a single guided journey: budget split → region intelligence → listing bridge → one portfolio |

**Execution model (deliberate):** Lumos never places trades and never holds money. It guides;
you buy at your own broker or from a listing site, then log it with one tap. Zero regulatory
surface, zero custody risk — and a lower trust barrier for scared beginners.

---

## Feature tour

### 🧭 Fearless onboarding
- **Path selection** — stocks-only, real-estate-only, hybrid, or "undecided, guide me"; navigation
  and modules adapt to the choice (no real-estate content forced on a stocks-only user)
- **Fear check-in** — "What scares you most?" with instant, specific reassurance; feeds the AI's tone
- **Readiness score** — five transparent milestones toward "ready for real money"; the UI background
  literally brightens from night toward dawn as the score grows

### 💬 Conversational risk profiling
- 9 single-topic questions grounded in Modern Portfolio Theory (budget, horizon, age, loss
  tolerance, goal, experience, current holdings, obligations, income stability) — each message
  asks exactly one thing, so a nervous beginner never has to answer two questions at once
- **Zero-knowledge language rules**: every finance term explained inline on first use; technicality
  escalates only when the user demonstrates knowledge
- **Fear-aware**: worry is acknowledged and normalized before any answer
- Structured extraction turns the conversation into a validated 1–10 risk score with a fully
  transparent breakdown — every factor's weight, your answer, its exact contribution, and why
  (contributions sum to the score; no black box)
- The score drives a **risk-blended allocation engine**: cautious profiles overweight calm assets,
  bold ones overweight growth engines — and the UI shows the formula, each asset's role, and every
  asset that was *dropped*, with its reason (no silent pruning, no pie-slice decoration)

### 🕰️ Time Machine (honest backtesting)
- "What if you'd built this portfolio 5 years ago?" — with **your own budget** as the start value
- Max drawdown, recovery time, and the worst moment framed as a question: *could you have held on?*
- **Stagnation detection** flags assets that went sideways for years — crucial for
  guaranteed-return seekers
- Real (inflation-adjusted) return next to nominal, always

### 🔮 Future Scenarios (projections without predictions)
- "What could my 100.000 TL become in SPY over 5 years?" — answered honestly: the distribution of
  **every rolling 5-year window in the asset's own history** (pessimistic p10 / typical p50 /
  optimistic p90), never a model's guess
- Works per-asset, for the **whole weighted portfolio** (diversification visibly narrows the band),
  and for **housing regions** (with the real-return companion that exposes nominal illusions)
- Thin histories are refused outright rather than dressed up as statistics

### 🏘️ Real-estate intelligence (live central-bank data)
- **Province intelligence**: concrete TL/m² prices for all **81 provinces** (central-bank unit-price
  series, quarterly since 2010) ranked by *real* appreciation over 1/3/5 years — plus the coarser
  19-region NUTS2 index; every scenario band deflates each window by its own period inflation
- **Rent vs. buy** decision tool — the same home under two strategies with an equal monthly
  housing budget, including an affordability check (the installment/income ratio is flagged past
  the ~45% banks lend against) and the honest note that homeownership has non-financial value too
- **What buying actually costs**: title deed fee, agency commission with VAT and annual upkeep are
  in the comparison rather than a footnote saying they were excluded — enough to flip the verdict
  in the default scenario. A checkbox says "this is all my cash" and takes the fees out of the down
  payment, which is the surprise that derails first-time buyers. Loan cost is shown in full: total
  interest against principal, with the user's own rate and term
- **Listing bridge**: filter-ready links out to listing portals (market-aware: Sahibinden/Emlakjet
  in TR, Zillow/Realtor in US, ImmoScout24/Immowelt in DE) — no scraping, no listing data stored

### 💰 Personal wealth tracker
- Every asset in one picture: stocks, funds, ETFs, gold, crypto, cash — **and land, apartments,
  vehicles** (cars are tracked with honest depreciation framing, never recommended)
- **Daily value chart** of what you actually own: ticker holdings follow real market closes,
  cash/manual assets are carried flat (no invented movement), and each holding enters the series
  on its own purchase date
- Remaining-budget math and an *"is my money melting?"* idle-cash erosion card (live monthly CPI)
  that itemises its own arithmetic — cash holdings + uninvested budget × monthly CPI
- **Drift advice** — the guidance a beginner needs *after* buying: prices move at different speeds,
  so the winner quietly grows into an outsized bet. Target weights are recomputed from the risk
  score and compared with reality; below a meaningful threshold it explicitly says *do nothing*,
  and the suggested remedy is steering new contributions rather than selling
- **Monthly-plan tracking** for people who invest regularly: planned vs. recorded this month
- **Fener (lantern) score**: 0–100 portfolio health from diversification + liquidity, with
  plain-language notes explaining *why* and *how to improve*
- One-tap **"I bought it" bridge** transfers a recommendation into holdings after an external
  purchase — and stops offering itself once the portfolio is already recorded

### 🧠 Behavioral coaching
- **Panic Button 🫨** — a real button for scary market days: guided breathing → a calming message
  keyed to *your* stated loss tolerance → four honest facts → your choice, never blocked
  (no dark patterns; "doing nothing is also a valid decision")
- Optional 1-tap **emotion tag** on every purchase (plan / FOMO / tip / panic) feeding a gentle
  behavior mirror that compares stated vs. actual behavior
- **Calm news digest**: at most 3 headlines a day, AI-rewritten in non-alarmist language with a
  "does this affect you?" note — plus micro-lessons on decoding scary headlines
- **Debt before investing**: card interest compounds far above any portfolio expectation, so a user
  carrying it is told to clear it first — one year of avoided interest against one year of expected
  return on the same amount, both shown, repayment labelled certain and returns labelled expected.
  Above the portfolio, not below it. Every app with something to sell has a reason not to say this
- **Feedback from inside the app**: beginners close the tab rather than report problems, so saying
  "I didn't understand this screen" costs one tap and captures the route automatically

### 🎯 Goal-based planning & 🐣 practice mode
- "800.000 TL for a down payment in 3 years" → required monthly contribution (annuity math) with
  drift detection: *"at your current pace you'll be 21 months late"*
- **Virtual portfolio**: a fake 100.000 TL on the recommended allocation with **real market data** —
  feel the swings before risking anything

### 💬 Always-on advisor chat
- A floating assistant on every page for whatever is on the user's mind — "what is an ETF?",
  "why is gold in my portfolio?", "what does my risk score mean?"
- Answers are personal: the backend injects the user's real profile (risk score, budget, path,
  stated fear) as context
- Guard-railed for honesty: no buy/sell calls, no market predictions, and it never invents
  numbers — engine outputs are the only source of figures. Output is script-checked: a reply
  containing foreign-script corruption (a failure mode of small fallback models) is rejected
  and re-served by the next provider

### 🤖 What-If assistant (tool-use, not hallucination)
- "What changes if I add 10.000 TL?" / "What if I were more aggressive?" — the LLM only *extracts
  the intent*; the real portfolio engine computes before/after; the LLM only *phrases* the result.
  **Every number the user sees comes from the engine, never from the model's imagination.**

---

## Architecture

```
┌─ frontend/  React 19 + Vite · Clerk auth · Recharts · PWA (service worker + manifest)
│             firefly design system: animated wordmark, "brightening UI" tied to readiness
│
├─ backend/   FastAPI (Python 3.12) · async SQLAlchemy 2 · Alembic migrations · SQLite (dev)
│   ├─ routers/       thin HTTP layer — validation, auth, rate limits only
│   ├─ services/      domain logic (risk, portfolio, backtest, projection, inflation,
│   │                 coach, news, what-if, evds, ai_service + ai_tiers)
│   ├─ repositories/  ALL database access (no inline SQL in routers)
│   ├─ markets/       Market Packs — every country-specific fact in one object (TR/US/DE)
│   ├─ schemas/       Pydantic request/response models
│   └─ models/        SQLAlchemy ORM (users, holdings)
│
└─ data       yfinance (markets) · TCMB EVDS (CPI + housing indices, live) · RSS (news)
```

**Engineering highlights**

- **Layered by rule, not by habit**: routers never touch SQL; services never parse HTTP;
  one repository layer owns every query
- **Three-tier market-data cache** (fresh 24h → stale 7-day → never-expiring last-known-good,
  plus historical volatility baselines as the final resort) — a Yahoo Finance outage degrades
  gracefully instead of breaking the app (observed and survived live, twice)
- **Structured observability**: every AI call logs tier, provider, prompt-version hash, latency,
  and outcome; every request carries an `X-Request-ID` echoed in the standard error envelope
  `{detail, error: {code, message, request_id}}`
- **Alembic is the only schema authority** — CI applies every migration to a fresh database on
  every push, plus a Docker build gate and full lint/test matrix
- **RAG chat context**: the advisor speaks from *today's* numbers (index levels + monthly CPI)
  injected into the system prompt with a 6-hour cache — and fails open if sources are down

---

## The AI layer: three free providers, one honest chain

The hardest constraint of a $0 project is AI quota. Lumos turns that constraint into
architecture — and everything below runs today on **free tiers only**. No paid model has ever
served a request in production.

**1. Cross-provider fallback.** Three independent free tiers rarely run dry at the same moment,
so a spent quota is never a dead end. Each step is itself a model chain, because every model
carries its own free allowance:

```
gemini      gemini-2.5-flash → 2.5-flash-lite → 2.0-flash → 2.0-flash-lite
   ↓ (quota spent / region-blocked / key rejected)
groq        openai/gpt-oss-120b → llama-3.3-70b → llama-3.1-8b
   ↓
openrouter  llama-3.3-70b:free → deepseek-chat-v3:free → gemma-4-31b:free → gemma-4-26b:free
```

Gemini is crossed with a **multi-key matrix** (up to 4 keys × 4 models = 16 independent quota
pools): when one key's allowance fills, the user loses a key — not an answer. A provider that
returns 429/5xx, is missing a key, or is blocked by region simply hands off to the next one.
This is not theory: Google blocks its free Gemini tier from EU datacenter IPs, which is why the
backend runs in Oregon — and why the chain exists at all.

**2. A quality gate, not just a quota gate.** The scripted 9-question risk quiz has to follow its
Turkish script exactly, and lighter models paraphrase questions or corrupt Turkish. So profiling
accepts only Gemini/Gemma/Claude-class models (`gemini`, `gemma`, `claude`, `gpt-oss`) wherever
they are hosted, while Llama and DeepSeek stay available to the free-form advisor, where a
slightly weaker answer beats an error. Replies containing foreign-script characters (a real
failure mode: *"rahat的话"*) are rejected and re-served by the next provider.

**3. Payments-ready, payments-excluded.** Providers, model chains and daily quotas all hang off a
single tier table, so introducing paid plans later is a configuration change rather than a
refactor: a Stripe/Iyzico webhook would flip `user.plan` and models, quotas and fallbacks follow.
The paid rows are **defined but never enabled** — no billing exists, so no user has been served by
them:

| Plan | Status | Provider & chain | Daily quota |
|---|---|---|---|
| **free** — "Ateş Böceği" (Firefly) | **live** | Gemini → Groq → OpenRouter (11 models) | 50 msg/day |
| **plus** — "Fener" (Lantern) | planned | Gemini 2.5 Pro → flash chain | 500 msg/day |
| **pro** — "Şafak" (Dawn) | planned | Claude Sonnet → Haiku | 2000 msg/day |

The Anthropic adapter is written and symmetrical with the others (it handles credit exhaustion
the way Gemini's handles quota), but Claude has no free tier — so it sits unused behind the
`pro` row, waiting for the day billing is turned on.

**4. AI never does math.** Risk scores, allocations, backtests, projections, drift, what-if
comparisons — all computed by deterministic engines. The LLM extracts intent (strict JSON with a
3-strategy parser) and phrases results. This is a product-safety decision, enforced by tests.

---

## Going global: Market Packs

Country-specific behavior lives in exactly one place — a **Market Pack**. Application code never
hardcodes a country; it asks the user's pack:

| | 🇹🇷 TR *(reference, fully wired)* | 🇺🇸 US *(skeleton)* | 🇩🇪 DE *(skeleton)* |
|---|---|---|---|
| Currency / locale | TRY · tr-TR | USD · en-US | EUR · de-DE |
| Inflation source | **TCMB EVDS (live)** | FRED *(roadmap)* | Destatis *(roadmap)* |
| Housing index | **TCMB EVDS, 19 regions (live)** | Case-Shiller *(roadmap)* | Häuserpreisindex *(roadmap)* |
| Listing bridge | Sahibinden, Emlakjet | Zillow, Realtor | ImmoScout24, Immowelt |
| Regulator (edu. content) | SPK | SEC / FINRA | BaFin |
| Local finance notes | withholding-tax basics, title-deed fees | long/short-term capital gains, 401(k)/IRA | Abgeltungsteuer 25%, Sparer-Pauschbetrag |
| Fear check-in | localized 🇹🇷 | localized 🇺🇸 | localized 🇩🇪 |

Adding a country = adding one pack module + data adapters. The TR pack is the complete reference
implementation; unknown market codes degrade safely to it. An in-app market switcher drives
currency and number formatting end to end — and TL-denominated data stays **pinned to TRY**
(never dressed up as dollars), while markets without live data show an honest
"integration on the way" state instead of masquerading foreign numbers. All tax/regulatory content is
**educational only** and every pack carries an explicit "confirm with a licensed local professional"
disclaimer — Lumos gives no tax or legal advice in any market.

---

## Data sources (all free)

| Source | Used for | Resilience |
|---|---|---|
| **TCMB EVDS** (Turkish central bank) | Live CPI, 19-region housing price indices | Daily cache; in-repo static CPI fallback; honest `available: false` when down |
| **yfinance** | Prices, volatility, backtests, projections | Fresh 24h + stale 7d + last-known-good cache tiers; baseline volatilities as final resort |
| **RSS** (AA, Bloomberg HT) | Calm news digest | Per-feed fail-open; digest hides when empty |
| **Google Gemini** (free tier) | Advisor chat, extraction, phrasing | 4-model chain × up to 4 keys, then hands off to Groq |
| **Groq** (free tier) | Fallback when Gemini is spent or region-blocked | gpt-oss-120b → Llama chain; quiz-eligible models only |
| **OpenRouter** (`:free` models) | Last-resort fallback | Llama / DeepSeek / Gemma chain; corrupted replies rejected |

---

## Security & honesty by design

- **Prompt-injection hardening**: user messages are data, never instructions; the profile-completion
  marker can't be forged from user text; strict role/length validation on every request
- **Per-user daily AI quotas** (DB-backed, plan-aware) + per-IP rate limiting on every AI endpoint
- **Auth**: Clerk JWT verified server-side on every request; lightweight RBAC (user/admin) gates
  operational stats and plan management
- **No execution, no custody**: architecturally incapable of moving user money
- **Honesty guarantees are tested**: prompt-rule regression tests, a no-dark-patterns assertion on
  the Panic Button, refusal paths for thin statistical histories
- Full failure-mode analysis: [docs/risk_register.md](docs/risk_register.md)

## Testing

```bash
python -m pytest backend/tests/ -q     # 245 tests, ~3s, zero network
cd frontend && npm test                # 14 vitest tests (retry safety, currency truth)
```

- External boundaries (AI providers, yfinance, EVDS, RSS) are fully mocked; business logic runs real
- **API-level E2E**: five personas (conservative → retirement) walk the entire HTTP surface:
  path selection → fear check-in → profiling → recommendation → "I bought it" → wealth summary →
  readiness score ([tests/e2e/scenarios.json](tests/e2e/scenarios.json))
- CI on every push: ruff + pytest + eslint + frontend build + Docker image build + fresh-database
  migration check

## Getting started

```bash
# 1. Backend
python3.12 -m venv venv && source venv/bin/activate
pip install -r backend/requirements.txt
cp .env.example .env        # fill in the keys below
alembic upgrade head
uvicorn backend.main:app --reload --port 8000

# 2. Frontend
cd frontend && npm install && npm run dev
```

**Required keys (all free, no credit card):**

| Key | Where |
|---|---|
| `GEMINI_API_KEY` | [aistudio.google.com/apikey](https://aistudio.google.com/apikey) |
| `VITE_CLERK_PUBLISHABLE_KEY`, `CLERK_SECRET_KEY`, `CLERK_JWT_ISSUER` | [clerk.com](https://clerk.com) — free to 10k MAU |
| `TCMB_EVDS_API_KEY` | [evds3.tcmb.gov.tr](https://evds3.tcmb.gov.tr) → Benim Sayfam → Profilim *(optional; static CPI fallback included)* |

Or with Docker: `docker compose up --build` (runs migrations, serves on :8000).

## Engineering docs

- [Architecture](docs/architecture.md) — system diagram and layer responsibilities
- [API reference](docs/api_reference.md) — every endpoint with request/response shapes
- [Case study](docs/case_study.md) — product decisions, four hard technical problems, lessons learned
- [Risk register](docs/risk_register.md) — 19 failure modes with mitigations and residual gaps
- [Demo script](demo/demo_script.md) — 3-minute scene-by-scene walkthrough

## Roadmap

**Live:** [lumos-sooty.vercel.app](https://lumos-sooty.vercel.app) · **Near-term:** Stripe/Iyzico
webhook onto the existing plan-tier switch (the paid rows above become real) · Sentry · uptime ping

**Growth:** wire US/DE data adapters (FRED, Destatis) onto the Market Pack skeletons ·
react-i18next localization · OpenAI/Mistral adapters once billing lands · Capacitor wrap for
stores (push notifications power the behavioral coach in real time)

See [todo.md](todo.md) for the full 9-phase build log — kept honest since day one.
Before real traffic: [docs/production-readiness.md](docs/production-readiness.md)
(Clerk production instance, always-on backend, persistent cache).
Brand assets and trademark notes: [brand/](brand/).

## License

**All rights reserved** — this repository is public for portfolio review only.
The code, the Lumos brand, and the product concept may not be copied, reused,
or deployed without written permission. See [LICENSE](LICENSE).

---

⚠️ **Educational purposes only. Not investment advice.** Past performance does not guarantee
future results. Lumos never executes trades or holds funds. Always consult a licensed financial
advisor before investing.
