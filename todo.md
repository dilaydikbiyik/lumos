# Lumos - Smart Investment Assistant — TODO

> **~18 weeks · 8 phases · $0 starting cost**
> Started: 2026-05-09

## 🌟 Product Vision

**People who know nothing about investing should be able to invest WITHOUT FEAR, learning as they go.**

Every feature must pass this filter: *"Does this help a timid beginner understand and take action?"*

| Principle | Meaning |
|------|--------|
| Explain first, show second | No chart/term reaches the screen without an explanation |
| Jargon-free by default | Not "volatility" but "how bumpy the price ride is" — those who want the term click for detail |
| Small first step | Start the user with practice and small steps, not a big lump sum |
| Fear = data | A user's hesitation is a signal to address, not to suppress |
| Two worlds, one roof | Real estate + stocks in the same portfolio, same language |

---

## 📁 Project Folder Structure

```
lumos/                          ← project root
│
├── backend/                    ← FastAPI application (Python)
│   ├── __init__.py
│   ├── main.py                 ← FastAPI app, middleware registration, lifespan
│   ├── requirements.txt        ← Python dependencies ✅
│   ├── .env.example            ← environment variable template ✅
│   │
│   ├── routers/                ← [CONTROLLER] HTTP endpoint definitions
│   │   ├── __init__.py
│   │   ├── chat.py             ← POST /chat
│   │   ├── profile.py          ← POST /profile
│   │   ├── recommend.py        ← POST /recommend
│   │   ├── users.py            ← GET|PATCH /users
│   │   └── health.py           ← GET /health
│   │
│   ├── services/               ← [SERVICE] business logic layer
│   │   ├── __init__.py
│   │   ├── ai_service.py       ← Provider-agnostic AI client (Gemini/Claude)
│   │   ├── risk_engine.py      ← Risk score computation (1-10)
│   │   ├── market_data.py      ← yfinance data fetching
│   │   ├── tefas_service.py    ← TEFAS fund data
│   │   ├── portfolio_engine.py ← Volatility-weighted portfolio
│   │   ├── volatility.py       ← Standard deviation / numpy math
│   │   ├── hybrid_basket.py    ← REIT hybrid basket logic
│   │   ├── explainer.py        ← Portfolio explanation via LLM
│   │   └── cache.py            ← Daily diskcache layer
│   │
│   ├── models/                 ← [MODEL] SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   ├── user.py             ← User ORM model
│   │   ├── user_profile.py     ← Risk profile schema
│   │   ├── risk_score.py       ← Risk score schema
│   │   └── portfolio.py        ← Portfolio schema
│   │
│   ├── middleware/             ← Auth & global error handling
│   │   ├── __init__.py
│   │   ├── verify_clerk.py     ← Clerk JWT verification
│   │   └── error_handler.py    ← Global exception handler
│   │
│   ├── db/                     ← Database connection & session
│   │   ├── __init__.py
│   │   └── database.py         ← SQLAlchemy engine, AsyncSession
│   │
│   ├── prompts/                ← LLM system prompts (plain text)
│   │   ├── system_prompt.txt
│   │   └── reit_explain_prompt.txt
│   │
│   ├── data/                   ← Static JSON data files
│   │   ├── fund_list.json      ← TEFAS fund list
│   │   └── asset_universe.json ← All assets (stocks, ETFs, REITs)
│   │
│   └── tests/                  ← Backend unit tests
│       ├── __init__.py
│       ├── test_risk_engine.py
│       └── test_chat.py
│
├── frontend/                   ← React 18 + Vite application
│   ├── src/
│   │   ├── App.jsx             ← Root component, router definition
│   │   ├── main.jsx            ← ClerkProvider wrapper
│   │   │
│   │   ├── components/         ← Reusable UI components
│   │   │   ├── ChatWindow.jsx
│   │   │   ├── MessageBubble.jsx
│   │   │   ├── RiskGauge.jsx
│   │   │   ├── PortfolioChart.jsx
│   │   │   ├── AssetCard.jsx
│   │   │   ├── ReitCard.jsx
│   │   │   ├── AssetExplainer.jsx
│   │   │   └── DisclaimerModal.jsx
│   │   │
│   │   ├── pages/              ← Page-level components (1 per route)
│   │   │   ├── OnboardingPage.jsx
│   │   │   ├── ProfilePage.jsx
│   │   │   ├── RecommendPage.jsx
│   │   │   └── DashboardPage.jsx
│   │   │
│   │   ├── hooks/              ← Custom React hooks
│   │   │   ├── useChat.js
│   │   │   └── usePortfolio.js
│   │   │
│   │   └── utils/              ← Helpers & error boundary
│   │       └── errorBoundary.jsx
│   │
│   ├── .env                    ← (never commit!)
│   └── .env.production
│
├── tests/
│   └── e2e/                    ← End-to-end test scenarios
│       ├── test_full_flow.py
│       └── scenarios.json
│
├── docs/                       ← Architecture and API documentation
│   ├── architecture.md
│   ├── api_reference.md
│   └── case_study.md
│
├── demo/
│   └── demo_script.md
│
├── venv/                       ← Python virtual environment ✅ (not in git)
├── .gitignore                  ✅
├── .env.example                ✅
├── render.yaml                 ← Render.com deployment config
├── Dockerfile                  ← Backend Docker image
├── vercel.json                 ← Vercel deployment config
├── README.md
└── todo.md                     ← This file
```

---

## Phase 1 — Setup, Scaffolding & Auth

**Duration:** Weeks 1–2
**Stack:** Python 3.11+, FastAPI, React 18, Vite, Git, **Clerk Auth** 🆕

### Backend

- [x] Create Python virtual environment (venv)
- [x] Install FastAPI and core dependencies
- [x] Create the folder structure: `/backend`, `/frontend`, `/docs`
- [x] `backend/main.py` — FastAPI app bootstrap
- [x] `backend/requirements.txt` — list all dependencies
- [x] `backend/routers/` — empty router folder with `__init__.py`
- [x] `backend/.env` — environment variables file (never commit!)

### Frontend

- [x] Create React 18 project with Vite
- [x] Set up React Router and the base page structure
- [x] `frontend/src/App.jsx` — main app component + ErrorBoundary + bottom nav
- [x] `frontend/src/components/` — create the component folder
- [x] `frontend/.env.example` — frontend environment variable template

### Auth — Clerk Integration 🆕

- [x] Create a Clerk account, register the app (free tier — 10,000 MAU)
- [x] Install the Clerk SDK on the frontend (`@clerk/clerk-react`)
- [x] `frontend/src/main.jsx` → wrap the app with `<ClerkProvider>`
- [x] Protected-route middleware (App.jsx ProtectedRoute)
  - Unauthenticated users must not reach portfolio and chat pages
- [x] `backend/middleware/verify_clerk.py` → Clerk JWT verification middleware
- [x] Add Clerk publishable and secret keys to `.env`

### Auth — User Profile Persistence 🆕

- [x] `backend/models/user.py` — user data model
- [x] `backend/routers/users.py` — user endpoints
- [x] `backend/db/database.py` — DB connection (SQLite to start, Postgres for production)
- [x] Persist risk profile results keyed to the Clerk user ID
- [x] Returning users can view their own portfolio

### Config & DevOps

- [x] Obtain the Anthropic API key and add it to `.env`
- [x] Add Clerk publishable + secret keys to `.env`
- [x] `.env.example` → sample file listing every variable name
- [x] `.gitignore` → add `.env`, `__pycache__`, `node_modules`, `venv/`
- [x] Initialize the git repo: `main / dev / feature/*` branch model
- [x] Make the first commit
- [!] Protect the `main` branch on GitHub — branch protection is locked on private repo + free plan ("Upgrade to GitHub Pro or make public"); once the repo goes public or Pro, one command enables it: `gh api repos/.../branches/main/protection`
- [x] `README.md` — basic project description

> 💡 Clerk's free tier covers up to 10,000 monthly active users.

---

## Phase 2 — NLP Engine & Risk Profile Module

**Duration:** Weeks 3–5
**Stack:** Claude API, FastAPI, Pydantic, Python, SQLite / Postgres

### AI — Claude API Connection

- [x] Install the Anthropic Python SDK (`pip install anthropic`)
- [x] `backend/services/ai_service.py` → Claude API client and base chat function
- [x] `backend/prompts/system_prompt.txt` → write the financial-advisor system prompt
  - **MANDATORY:** include: *"This app does not provide investment advice. It is for educational purposes only. Consult a licensed financial advisor."*
- [x] `backend/routers/chat.py` → open the `/chat` endpoint

### AI — Risk Profile Extraction Flow

- [x] Design the 5-question conversation flow:
  1. Budget
  2. Time horizon
  3. Loss tolerance
  4. Investment goal
  5. Experience level
- [x] `backend/services/risk_engine.py` → produce a 1-10 risk score from answers
- [x] `backend/models/user_profile.py` → user profile data model (Pydantic)

### API — Profile Persistence

- [x] `backend/routers/profile.py` → `POST /profile` endpoint
  - Input: 5 answers → compute risk score → persist keyed to the Clerk user ID
- [x] `backend/models/risk_score.py` → risk score data model

### Testing

- [x] `backend/tests/test_risk_engine.py` → risk engine unit tests with pytest (10/10 ✅)
- [x] `backend/tests/test_chat.py` → chat endpoint tests
- [x] Prompt regression tests: marker/safety/zero-knowledge/fear/ethics rules + extraction JSON requirement (6 tests)

---

## Phase 3 — Market Data & Portfolio Engine 🔄 UPDATED

**Duration:** Weeks 5–8
**Stack:** yfinance, pandas, numpy, TEFAS API, ExchangeRate API

### Data — Yahoo Finance Integration

- [x] Install `yfinance`, `pandas`, `numpy`
- [x] `backend/services/market_data.py` → asset price fetching service
  - BIST stocks (XU100)
  - US ETFs (SPY, QQQ)
  - Gold (GLD)
- [x] `backend/services/cache.py` → daily caching layer (to avoid rate limits)

### Data — TEFAS Fund Data

- [x] TEFAS research: no official public API; current service kept (assessment note in Phase 6)
- [x] `backend/services/tefas_service.py` → fetch Turkish mutual funds
- [x] `backend/data/fund_list.json` → build the fund list:
  - Conservative funds
  - Balanced funds
  - Aggressive funds

### Algorithm — Volatility-Weighted Portfolio Formula 🆕

- [x] `backend/services/volatility.py` → volatility computation module
  - Fetch daily returns for the last 252 trading days (1 year)
  - Compute standard deviation with `numpy`
  - Compute once a day and write to cache
- [x] `backend/services/portfolio_engine.py` → main portfolio engine (fixed buckets removed)
  - v2 formula `(RiskScore × Vol) / Σ(...)` was replaced on 2026-07-10 by the
    **v3 risk-blended formula** — see the "Transparency & Realism round" below
    (v2 cancelled out in normalisation; allocation was risk-independent)
- [x] `backend/models/portfolio.py` → portfolio data model

### API — Recommendation Endpoint

- [x] `backend/routers/recommend.py` → `POST /recommend`
  - Input: risk score + budget
  - Output: portfolio weights + plain-language explanation
- [x] `backend/services/explainer.py` → generate the portfolio explanation via LLM

---

## Phase 3.5 — Real Estate Layer / REIT ETF 🆕 NEW

**Duration:** Weeks 8–10
**Stack:** yfinance, pandas, VNQ, SCHH

### Data — REIT ETF Data

- [x] `backend/data/asset_universe.json` → add VNQ and SCHH to the asset universe
- [x] `backend/services/market_data.py` → extend the existing yfinance pipeline (zero new APIs)

### Algorithm — Hybrid Basket Logic 🆕

- [x] `backend/services/hybrid_basket.py` → hybrid basket service
  - If the user's budget is below the real-estate threshold, auto-include REIT ETFs
  - Present it as "real estate exposure without buying property"
- [x] `backend/services/portfolio_engine.py` → integrate the hybrid basket logic

### UI — REIT Card 🆕

- [x] `frontend/src/components/ReitCard.jsx`
  - What a REIT is, why it was chosen, historical returns — Turkish, jargon-free
- [x] `frontend/src/components/AssetExplainer.jsx` — generic asset explainer (3 tabs: what/why/risk)

### Content — REIT Explainer Prompt 🆕

- [x] `backend/prompts/reit_explain_prompt.txt`
  - Prompt for a personalised 2-sentence dynamic explanation per user
  - Not a static template — personalised for each user

> 💡 Why REIT instead of Zillow? REITs trade like stocks, so yfinance covers them. Zillow would require a separate data model + a paid API.

---

## Phase 4 — Frontend: Chatbot UI & Visualization

**Duration:** Weeks 10–14
**Stack:** React 18, Recharts, Axios, React Router, Clerk

> 📱 **Strategy: Mobile-First Web → Capacitor**
> The whole UI is designed portrait/phone-friendly (100dvh, 48px touch targets, bottom nav, safe-area-inset).
> After Phase 5 it can be wrapped into a native iOS/Android app with Capacitor.

### UI — Chatbot Interface

- [x] `frontend/src/components/ChatWindow.jsx`
  - Message bubbles, typing animation, iOS momentum scroll
  - `enterKeyHint="send"` — mobile keyboard send button
- [x] `frontend/src/components/MessageBubble.jsx` — user/assistant message bubble
- [x] `frontend/src/hooks/useChat.js` — chat state + Clerk JWT attachment

### UI — Risk Profile Screen

- [x] `frontend/src/pages/ProfilePage.jsx` — chat → score reveal, single-column flow
- [x] `frontend/src/components/RiskGauge.jsx` — SVG half-circle gauge (green→amber→red)

### Charts — Portfolio Allocation Chart

- [x] `frontend/src/components/PortfolioChart.jsx`
  - Recharts donut chart: stocks / REIT / funds / gold / cash
  - Clickable slices → AssetCard opens
- [x] `frontend/src/components/AssetCard.jsx` — detail panel

### Charts — Historical Performance Chart

- [x] ~~`PerformanceChart.jsx` (12-month line chart)~~ — **REMOVED 2026-07-11**: it
  rendered `Math.random()` curves as "performance"; fabricated data violates the
  realism principle. The real backtest (Time Machine) covers this need.
- [x] `frontend/src/pages/RecommendPage.jsx` — single column: badge → pie → REIT → explanation

### UX — Legal Disclaimer & Onboarding

- [x] `frontend/src/components/DisclaimerModal.jsx`
  - Mandatory checkbox — no continue without acceptance
- [x] `frontend/src/pages/OnboardingPage.jsx` — hero + 3 feature cards + CTA

### UX — Saved Portfolio Dashboard

- [x] `frontend/src/pages/DashboardPage.jsx`
  - Profile card + re-run / re-profile buttons + portfolio snapshot
- [x] `frontend/src/hooks/usePortfolio.js` — portfolio + profile management

### Mobile-First Extras 📱

- [x] `frontend/src/components/AppNav.jsx` — responsive nav: fixed bottom bar on mobile, left sidebar on desktop (renamed from BottomNav on 2026-07-11)
- [x] `frontend/src/index.css` — mobile-first design system (100dvh, touch targets, safe-area)
- [x] `frontend/index.html` — PWA meta tags (theme-color, apple-mobile-web-app)
- [x] `frontend/src/utils/errorBoundary.jsx` — React Error Boundary
- [x] `frontend/src/utils/api.js` — Axios client + Clerk JWT binding

> 💡 This dashboard is only possible thanks to Phase 1's Clerk Auth. Auth comes first.

> 🚀 **Capacitor (optional — after Phase 5)**
> `npm install @capacitor/core @capacitor/cli @capacitor/ios @capacitor/android`
> `npx cap init && npx cap add ios && npx cap sync`
> A native app with one command.

---

## Phase 5 — Testing, Deployment & Portfolio Presentation

**Duration:** Weeks 14–18
**Stack:** pytest, Playwright, React Testing Library, Render.com, Vercel, GitHub Actions

### Testing — E2E Tests

- [x] `test_full_flow.py` → API-level full flow (TestClient; pragmatic choice over Playwright — real HTTP surface without Clerk)
- [x] `tests/e2e/scenarios.json` → 5 user-type scenarios:
  1. Conservative
  2. Moderate
  3. Aggressive
  4. Short-term
  5. Retirement
- [x] Each scenario: path selection → fear check-in → profile → recommendation → "I bought it" → wealth summary → readiness score (5 personas, parametrised)

### Testing — Error Handling & Edge Cases

- [x] `backend/middleware/error_handler.py` → global error-handling middleware
  - API crash, nonsense input, empty portfolio, expired session
- [x] `frontend/src/utils/errorBoundary.jsx` → React Error Boundary
- [x] Show a meaningful message for every error state (Turkish error copy)

### Deploy — Backend → Render.com

- [x] `Dockerfile` → Docker image for the FastAPI app
- [x] `render.yaml` → Render.com deployment configuration (free plan, Docker, health check)
- [x] `backend/routers/health.py` → `/health` endpoint (uptime monitoring)
- [x] All env vars set on Render (4 Gemini keys, Anthropic, Clerk, TCMB, Neon `DATABASE_URL`)
- [x] Deployment tested live: `/health` → `{db: ok, ai: ok}`, CORS verified for the Vercel origin, Render↔Neon connection observed in pg_stat_activity (2026-07-12)

### Deploy — Frontend → Vercel

- [x] `vercel.json` → Vercel deployment configuration (Vite framework, SPA rewrite, asset caching)
- [x] `frontend/.env.production` → `VITE_BACKEND_URL`, `VITE_CLERK_PUBLISHABLE_KEY`
- [/] Clerk runs on the development instance for now (works end to end; production instance requires a custom domain — deferred until one is purchased)
- [x] Deployed to Vercel: https://lumos-sooty.vercel.app (root=frontend, Vite preset) → backend https://lumos-backend-u6il.onrender.com → Neon Postgres (Frankfurt) (2026-07-12)

### Portfolio — README & Architecture Docs

- [x] `README.md` — what it does, how to run it, architecture decisions + rationale
- [x] `docs/architecture.md` — system architecture diagram and explanation (ASCII art + design-decision table)
- [x] `docs/api_reference.md` — all API endpoints and usage (10 routers, 26 endpoints)

### Portfolio — Demo Video & Case Study

- [x] `demo/demo_script.md` → 3-minute scene-by-scene demo script (with filming notes)
  - Full flow: sign-up → onboarding → chat → risk profile → portfolio → dashboard
- [ ] Record the screen capture (Loom / OBS / QuickTime)
- [x] `docs/case_study.md` → problem, product decisions, 4 technical challenges + solutions, learnings
- [ ] Upload the demo video to the GitHub repo
- [ ] Share on LinkedIn

> 💡 AWS migration becomes meaningful only after this phase ships the MVP. Not before.

---

## Phase 6 — Technical Debt & Production Hardening 🆕

**Duration:** after Phase 5
**Source:** project analysis report (2026-06-16)

### Test Coverage

- [x] `backend/tests/test_chat.py` → chat router integration test (AI mocked, 4 tests)
- [x] `backend/tests/test_recommend.py` → recommend endpoint test (engine + explainer mocked, 4 tests)
- [x] `backend/tests/test_profile.py` → profile router test (in-memory DB, 5 tests)
- [x] AI mock fixture for AI service tests (`conftest.py` — `_dispatch` patch + auth bypass)
- [x] `tests/e2e/` filled (scenarios.json + backend test_full_flow.py)

### CI/CD

- [x] `.github/workflows/ci.yml` → ruff + pytest on push/PR (backend)
- [x] Same workflow gained eslint + build (frontend, Node 22) — vitest frontend tests will be added when written
- [!] Branch protection: same GitHub Pro/public constraint as above

### Database

- [x] `alembic init` (async template) + baseline migration (`04f9da6e7e6d`: users table + indexes); dev DB stamped with `alembic stamp head`
- [/] `create_all` → migration transition plan: dev keeps create_all (harmless, checkfirst); for new schema changes the flow = edit model → `alembic revision --autogenerate` → `alembic upgrade head`; production deploy runs `alembic upgrade head` before startup, create_all removed in prod

### Deployment

- [x] `Dockerfile` (backend) — python slim, migration + uvicorn startup; build verified in CI (no local Docker)
- [/] docker-compose.yml ready (persistent volume + healthcheck) — needs Docker Desktop for local testing

### Data-Provider Risk

- [x] yfinance rate-limit/breakage fallbacks: 7-day stale copy + **never-expiring last-known-good tier (added 2026-07-10)** — download failure serves dated real data; only a totally cold install with the source down raises MarketDataError; volatility additionally falls back to historical baselines so /recommend never dies
- [x] TEFAS assessment: no official/free API (fintables etc. are paid); current tefas_service scraping + cache suffices — will be abstracted as a source adapter in the Market Pack
- [x] Cache TTL strategy reviewed: fresh 24h + stale 7d + LKG forever (three tiers)

### AI Service Observability

- [x] Structured logging for AI calls (`lumos.ai` logger: provider, prompt_version, latency_ms, message count, status, error type)
- [x] Prompt versioning: system prompt SHA1 hash (`PROMPT_VERSION`) on every log line — traceable which answer came from which prompt version
- [x] Anthropic SDK updated (0.39.0 → 0.112.0); prompt caching to be added if we switch to Anthropic

### Security & Compliance

- [x] Rate limiting on AI endpoints with `slowapi` (chat, recommend)
- [x] Prompt-injection protection: role/length validation (Literal role, 4000 chars, 80 messages) + SECURITY RULES block in the system prompt (marker forgery, prompt leaking, role switching refused)
- [/] Structured output: risk profile extraction structured (`/chat/extract-profile` + JSON extraction prompt) — portfolio output to move to tool-use

### AI Advisor Quality 🆕

> ✅ **Solved (2026-07-04):** the broken profile flow was repaired — the AI emits `[PROFILE_COMPLETE]` when done, the frontend pulls structured answers via `/chat/extract-profile` and moves to the score screen.

- [x] Deepen `system_prompt.txt`: explicit MPT/risk-return framing, counter-question behaviour, clear legal/ethical boundaries
- [x] Add few-shot example dialogues (1 embedded example) — teach the advisor tone by example
- [x] Deepen `reit_explain_prompt.txt`: 3-sentence structure, profile-specific tone, honest risk warning, MPT context
- [x] RAG: `chat_context.py` — daily market summary (BIST/SPY/GLD + monthly CPI) injected into the system prompt, 6-hour cache, fail-open (3 tests)
- [ ] Tool-use architecture: `get_market_data(ticker)`, `calculate_volatility(asset)`, `get_risk_score(profile)` tool definitions — the LLM pulls data from services instead of inventing it
- [/] Feedback loop v1: `recommendation_served` structured log + admin/stats holdings comparison; UI-based accept/reject events in a later version
- [ ] A/B test prompt versions; strengthen the current prompt with Anthropic Console's Prompt Improver

---

## Phase 7 — Product Deepening & Personal Investment Tracking 🆕

**Duration:** can run in parallel with Phase 6
**Source:** product vision discussion (2026-06-28)

### AI Provider Flexibility (cost solution)

- [x] Make `ai_service.py` provider-agnostic: single `chat()` / `generate_text()` interface with adapters behind it
- [x] Add the Gemini adapter (`google-generativeai`) — free tier, default for dev/demo
- [x] `google-generativeai` → `google-genai` (2.10.0) SDK migration — deprecation warning gone, verified live
- [x] `AI_PROVIDER=gemini|anthropic` selection in `.env`; the Claude adapter wraps the existing code
- [x] Provider-specific error handling (credits out / quota exceeded → meaningful user message)
- [x] Gemini free-tier fallback chain: 2.5-flash → 2.5-flash-lite → 2.0-flash — each model has its OWN free quota, so 429/5xx auto-switches; ~3x free capacity, users never see the error (5 tests)

### Risk Profile Deepening

- [x] Fold two dimensions into the questions: age/time to retirement + income stability
- [x] Dynamic follow-up: the LLM may ask extra questions when the profile is unclear (flexible 7–10 question flow)
- [x] Update `risk_engine.py` for the new dimensions (age and income stability affect the score)

### Personal Investment Tracking 💰

- [x] `backend/models/holding.py` — user holding model (10 types: stock/fund/etf/home/land/vehicle/gold/crypto/cash/other) + Alembic migration
- [x] Vehicle asset type — with honest framing: counts in the net-worth picture BUT shown with depreciation math (annual value loss + insurance/tax/maintenance); accompanied by the "is your car wealth or an expense?" education card — the AI NEVER recommends buying a car as an investment
- [x] `backend/routers/holdings.py` — CRUD + ticker required for exchange assets (7 tests)
- [x] Budget tracking: `/holdings/summary` — total invested, current value, remaining budget, per-type breakdown
- [/] Manual valuation field for off-exchange assets ✅; live yfinance valuation of exchange assets shipped later (see 2026-07-09 round)
- [x] `frontend/src/pages/HoldingsPage.jsx` — "My Assets": total value + remaining budget + Lantern score + list + add form (added to nav)
- [x] Dashboard summary card: total asset value + remaining budget + daily change
- [x] Actual vs recommended portfolio comparison ("drift from target allocation" indicator)

### Architecture & Code Quality 🏛️ (clean-architecture revision)

> Suggested order: repository/schema refactor → error handling → RBAC → Python 3.12

- [x] `backend/repositories/` layer: user_repository + holding_repository; no inline SQL left in routers
- [x] `backend/schemas/` folder: user_profile/portfolio/risk_score/holding schemas moved; `models/` is ORM only (user, holding)
- [/] Domain exception classes: `MarketDataError` + `AIServiceError` added (`backend/exceptions.py`), mapped to 503 in error_handler — `QuotaExceededError` comes with the quota feature
- [x] Standard error envelope: `{detail, error:{code,message,request_id}}` — detail kept for frontend compatibility
- [x] `X-Request-ID` middleware: contextvar-based correlation — returned in the header, visible in the error envelope and logs (3 tests)
- [ ] API versioning: move all routers under an `/api/v1` prefix (update frontend api.js baseURL)
- [x] Light RBAC: `role` column (migration 734ca3a1) + `require_role()` + admin-only /admin/stats (user/holding/message volume, path distribution) (2 tests)
- [x] Deepen the health check: `/health` genuinely probes DB connectivity and AI provider access (`{"db": "ok", "ai": "ok"}`)
- [x] Python 3.9 → 3.12 migration: venv rebuilt, Dockerfile+CI moved to 3.12, `datetime.utcnow` deprecations fixed (Optional→| None conversion is cosmetic, gradual)
- [x] pre-commit config: ruff + ruff-format + basic hygiene hooks (`pip install pre-commit && pre-commit install`)
- [ ] Rotate the leaked Anthropic API key (Console → API Keys)

### Mobile Strategy 📱 (decision: 3 tiers — 2026-06-28)

> Tier 1: mobile-first web ✅ (done in Phase 4) → Tier 2: full PWA (with MVP) → Tier 3: Capacitor native (post-MVP, when budget allows)
> NO switch to React Native/Flutter — the existing React codebase is preserved.

- [x] PWA complete: manifest.webmanifest + sw.js (network-first, API never cached) + prod-only registration
- [ ] Capacitor wrap (post-MVP): store legitimacy + **push notifications = the behavioural coach's carrier** ("market dropped, stay calm" only works in real time via push; iOS web push is weak) — requires Apple $99/yr + Google $25

### Usage Quota

- [x] Daily per-user message quota (users.quota_date/quota_used, DAILY_MESSAGE_QUOTA=50, 429 + polite TR/EN message)
- [x] Polite notification when the quota is exhausted (backend message shows in the chat error area)

### Education Layer 📚 (the heart of the vision — priority raised)

- [ ] Per-asset education: "what is it / why is it in your portfolio / what's the risk" LLM explanation for every portfolio item (generalised explain prompt)
- [x] Fill `AssetExplainer.jsx` with this content — 6 known tickers + 3 category fallbacks, 3-tab static card
- [x] Core-concepts glossary (`frontend/src/data/glossary.js`, 12 terms, jargon-free Turkish)
- [ ] Auto-show an education card on the first purchase of every asset type the user invests in
- [/] Jargon tooltip system: `IsikTut` component + 12-term glossary ready; roll-out to all pages continues
- [x] "Assume zero knowledge" rule in the system prompt: explain terms in everyday language in every answer, gradually technical as the user shows knowledge (+ fear-awareness rule: acknowledge the worry first, then answer)
- [ ] UI copy audit: revise all existing page copy against the jargon-free principle — RecommendPage + ReitCard done ✅, other pages to follow

---

## Phase 8 — Differentiating Features 🚀 (market analysis: 2026-06-28)

> Positioning: Midas/Getir Finans = execution, robo-advisors = black-box recommendations, Fintables = analysis.
> Lumos's gap: **"investing with understanding"** — an assistant that explains its advice, coaches behaviour, and speaks to Turkish realities.

### Time Machine & Asset Character 🕰️ (strongest demo feature)

- [x] "What if you'd built this portfolio 5 years ago?" — `backtest.py` service + POST /backtest (1y/3y/5y)
- [x] `backend/services/backtest.py` → cumulative series + max drawdown + recovery time + chart data (5 tests)
- [x] Stagnation-period detection: ±5% band algorithm → per-asset `longest_stagnation_months` (profile-match badge later)
- [ ] Asset character card: "longest stagnation", "deepest drawdown", "recovery time" summary per asset — profile-fit badge (does this asset match your patience?)
- [x] `TimeMachine` component on RecommendPage: 1/3/5-year simulation + honest "X TL at its worst moment" emphasis + line chart
- [x] Concretise the risk-tolerance question: instead of an abstract "if it drops 20%", show it with the user's own budget: "your 50.000 TL would become 40.000 TL"

### Real Estate + Stocks Hybrid 🏘️📈 (the main edge over Midas)

> Midas is an execution tool with zero real-estate depth. Lumos's identity: guiding **the entire purchase journey** —
> "I have 1M TL" → the AI suggests a split → shows appreciating regions → links to listings → records the purchase → plans the remainder in stocks.

#### ⚖️ Execution Model (final decision — 2026-06-28)

> **Lumos does NOT execute transactions — in both worlds the model is: guide → buy outside → track in the app.**
>
> | | Stocks | Real estate |
> |---|---|---|
> | Why no in-app buying | Requires an SPK brokerage licence (capital + audits + years) | Physical-world transaction (title deed) |
> | Guidance | Portfolio recommendation + "how to buy at your broker" guide | Region cards + listing bridge + evaluation assistant |
> | Purchase | The user's own broker (Midas, İş Yatırım...) | Via Sahibinden/estate agents |
> | Return | "I bought it" → record in holdings → portfolio updates | "I bought it" → record in holdings → portfolio updates |
>
> Advantages: zero regulatory risk, no custody of funds (lower trust threshold — a plus for the scared beginner), $0 cost preserved.
> Later phase (business development): brokerage API partnership for "one-tap order routing" — same status as a real-estate platform partnership, out of MVP.

- [x] Honest expectation line in onboarding: "Lumos shows you the way; you buy at your own broker, then we track it here"
- [x] Stock "I bought it" flow: `BoughtItBridge` — records the recommended allocation into holdings in one tap, remaining budget auto-updates
- [ ] "How to open a brokerage account" guide (same item as the guided journey in Fearless Start — a reference, not a duplicate)

#### Flow 0 — Path Selection 🧭 (structural principle: flows are chosen, never forced)

> ⚠️ Note (2026-07-04): onboarding path selection + backend `investment_path` field work live. Conditional module hiding partially applied (nav filtering ✅); real-estate-specific PAGES came with ExplorePage later.

> The user is NEVER forced to pick real estate. Three equal paths: stocks only (Midas style) / real-estate discovery only / mixed. Each flow works independently.

- [x] Path question in onboarding: `PathSelectionPage` (4 cards) → PATCH /users/me/investment-path → users.investment_path
- [x] Path-based module adaptation: nav filters by chosen path (stocks-only → Explore hidden; real-estate-only → Portfolio hidden)
- [ ] "Real estate only" path: the risk profile still runs (horizon + liquidity are critical) but the output is region cards + listing evaluation + education; no stock recommendation forced
- [ ] "Undecided" path: the AI suggests a path from profile + fear check-in ("regular savings + long horizon → start with stock funds, I'll tell you when you reach the real-estate threshold")
- [ ] The path can change at any time (settings + a soft "explore the real-estate world" invitation on the dashboard — never forced)
- [ ] The budget-split advisor is active only on mixed/undecided paths; single-path users get the whole budget planned in their chosen world

#### Flow 1 — Budget Split Advisor (entry point)

- [ ] Make real estate an allocatable asset class: portfolio_engine takes "1.000.000 TL + profile" → suggests "600K real estate / 300K stocks-funds / 100K cash reserve" (inputs: risk score + liquidity need + budget threshold)
- [ ] LLM narration of the split rationale: why these ratios, how they'd differ per profile (teaching tone)
- [ ] REIT vs physical real-estate decision point: below the budget threshold or with high liquidity needs, steer to "REIT instead of physical" (hybrid_basket both ways)

#### Flow 2 — Region Appreciation Intelligence (the AI's "where should I buy?" answer)

- [x] TCMB housing price index LIVE: 19 NUTS2 regions (TP.KFE.*), 1-3 year nominal + real appreciation ranking (`region_intelligence.py`)
- [ ] TÜİK population/migration data integration: districts with net inbound migration + young populations = demand signal
- [x] "Appreciation potential" region cards: GET /planning/region-intelligence + ExplorePage UI — verified live with TCMB data; TÜİK migration signal later
- [ ] Match against the user's goal: "I can wait 20 years" → long-horizon appreciation regions; "I'll sell in 5 years" → central, liquid regions

#### Flow 3 — Listing Bridge (routing to the purchase)

- [x] Filter-ready external links: service + endpoint + ExplorePage "Go to listings" card (province/district/type form → external links)
- [ ] **Listing evaluation assistant**: the user pastes a listing's details (location, m², price) → the AI compares against the region's average m² price: "20% above the region average" + negotiation/inspection checklist (zoning, deed type, road frontage...)
- [ ] Purchase checklist guide: step-by-step checks when buying land/a flat (static education content, Turkey-specific: deed, zoning, DASK...)
- [ ] (Later phase — business development) Real-estate platform API partnership: real listings + agent contact in-app

#### Flow 4 — Close the Loop (after the purchase)

- [ ] "I bought it" flow: one-tap record into holdings from the listing evaluation (Phase 7 form pre-filled)
- [ ] Auto-replan the remaining budget: "you locked 600K into land; your stock-fund plan for the remaining 400K is ready" → bridge into the recommend flow
- [ ] Periodically update the real-estate holding's value with the TCMB index (labelled "index-based estimate")
- [ ] Rent yield vs dividend yield comparison: "this flat yields 4% rent a year; this dividend portfolio pays 6%"
- [x] Liquidity score: the Lantern's 40%-weighted component — produces a warning note for illiquid-heavy portfolios
- [ ] "A 500.000 TL plot or a 500.000 TL portfolio?" comparison screen: same amount, past 5 years, housing index vs portfolio returns side by side (+ liquidity and cost differences table)

#### Flow 5 — Rent & Home Decisions 🏠 (gateway feature)

> In Turkey, the first financial question of a non-investor is "should I rent or buy?" — the tool that answers it becomes the door that brings users in.

- [x] "Rent or buy?" decision tool: service + endpoint + ExplorePage UI card (two scenarios side by side + emotional-value note) — verified live
- [ ] Add the emotion dimension to the tool: also narrate the non-monetary value of "the security of owning a home" (vision principle: fear/emotion = data)
- [ ] Make monthly rent a profile input: real investable amount = income − rent − essential expenses → the budget-split advisor speaks with this net amount
- [x] Scope limit (deliberate decision): rental-listing search / mortgage marketplace NOT added — listing_bridge.py only produces filter-ready external links, no listing data is ever stored

### Inflation Reality 🇹🇷 (local differentiator — nobody does this)

- [x] Dual nominal + real display for all returns: `real_return_pct` in Time Machine results, "after inflation (real)" line in the UI
- [x] CPI data: LIVE TCMB EVDS integration (`evds_service.py`, TP.FG.J0, daily cache) — static file kept as fallback
- [x] TL/FX split and currency-risk indicator in the portfolio — `CurrencyExposure.jsx` (integrated into HoldingsPage)
- [x] "Is my money melting?" card: monthly real erosion of idle budget + cash on the holdings page (5 tests)

### Behavioural Coach 🧠 (what robo-advisors don't do)

- [x] Market-move messages: `behavior_coach.py` + POST /coach/market-move — drop/rally messages by loss_tolerance (template-based, zero AI cost)
- [x] Behaviour mirror: GET /coach/behavior-mirror — emotion_tag distribution + a gentle note on profile/behaviour mismatch
- [x] Optional one-tap emotion tag on purchases (plan/fomo/tip/panic) — `holdings.emotion_tag`; monthly report UI later

### Goal-Based Investing 🎯

- [x] Goal definition: service + endpoint + Dashboard `GoalPlanner` card — verified live (800K/3yr → 17.993 TL/month)
- [x] Progress + drift: endpoint + UI progress bar — verified live ("21 months late" warning at a 10K pace)
- [x] Goal-drift warning: "⏳ at this pace your goal slips X months" card live

### Portfolio Health Score 💯

- [/] Lantern score v1: diversification (HHI) + liquidity components, 0-100 + jargon-free notes (goal fit + currency balance next version)
- [ ] "Why is it low, how does it rise" LLM explanation per component
- [/] Lantern card on the holdings page ✅; score-over-time chart later
- [x] Courage Score UI: `ReadinessScore.jsx` — 5 milestones + circular score on the Dashboard, "ready for real investing" message at the 60% threshold

### What-If Assistant 🔮

- [x] Scenario questions in chat: "what if I add 10.000 TL?", "what if I were more aggressive?" — `what_if.py` tool-use: the LLM only extracts intent to JSON, `portfolio_engine` computes the real before/after, the LLM only narrates (never invents math); `/chat/what-if` + `WhatIfAssistant` UI card, 6 tests, verified live on Gemini

### Future Scenarios 🔮 (user idea — 2026-07-05)

> The honest answer to "what happens if I put it in SPY for 5 years?": NOT a forecast — the distribution of every N-year window in the asset's own history (bad p10 / typical p50 / good p90).

- [x] `projection.py`: rolling-window distribution engine — asset (yfinance 10y, monthly sampling) + region (TCMB KFE) (7 tests)
- [x] POST /planning/projection/asset + /projection/region — honest refusal on insufficient history ("not enough windows")
- [x] `FutureScenarios` card on RecommendPage: pick asset + horizon → 3 scenario bars with your budget
- [x] Region cards on ExplorePage open a scenario band on click: "what would X TL become here in N years?" + real terms + the "60x" anecdote warning — verified live (Ankara 1M → typical +85.9% nominal / +15.15% real)
- [ ] LLM current-context sentence on the scenario card (fed by the calm news digest, never touching the numbers)
- [x] Combined scenario band for the whole portfolio (weighted window distribution)

### Panic Button 🫨 (original idea — 2026-07-08, no finance app has one)

> The crisis-moment form of "fear = data": a real button to press when the market gets scary.
> No dark patterns — selling is never blocked; the user is calmed according to their own profile.

- [x] POST /coach/panic: profile-based calming + 4 honest static facts (zero LLM cost) + press/resolution logging (behaviour-mirror data) (4 tests)
- [x] `PanicButton.jsx`: floating button → 3-stage full-screen flow: breathing ring (3 breaths, skippable) → coach message + facts → "I've calmed down / Still worried"
- [x] "Still worried" → 24-hour wait suggestion + licensed-advisor referral (honest escalation)
- [x] Verified live: press → coach → resolution message end to end

### Calm News Feed 📰 (news = education, not noise)

> A raw news feed is a fear machine for a beginner. Lumos filters the news, calms it, teaches with it.

- [x] RSS integration: AA Ekonomi + Bloomberg HT (httpx + stdlib XML, no new dependency) → `news_service.py`
- [x] LLM news filter: path-based selection, headline + why_it_matters + calmness_note JSON, daily cache (5 tests)
- [/] GET /news/digest ready (≤3 items, path-based); dashboard card UI shipped
- [/] News + coach infrastructure ready (`news_service.py` + `behavior_coach.py`) — the automatic trigger bridge (news → coach) is the next integration step
- [x] Headline-language training: "what actually happens when you see a MARKET CRASHES headline?" micro-education card — `HeadlineEducation.jsx` (4 scenarios, localStorage)

### Fearless Start 🐣 (the vision itself — highest priority)

> Someone who doesn't know investing must gain confidence before risking real money.

- [x] Practice portfolio: service + endpoint + `PracticeMode` card on RecommendPage ("Try with fake money first")
- [x] Weekly change computed (weekly_change_amount + biggest_mover); LLM narration layer later
- [x] Guided first-investment journey: step-by-step wizard — "what is a brokerage account → how to open one → how to place the first order" (Turkey-specific, static 5 steps) — `BeginnerGuide.jsx`
- [x] Fear check-in: `FearCheckInPage.jsx` + PATCH /users/me/fear-check-in — 4 fear tags + instant personalised reassurance (verified live)
- [x] "Today you learned" micro-cards: one small concept per session ("an ETF is actually a basket") — 15-second read, progress counter — `DailyTip.jsx` (12 cards, localStorage tracking)
- [x] Progressive UI: minimal view for new users (3 metrics), enriches via "show details" — `ProgressiveDetails` on the Dashboard, toggle button
- [x] Courage indicator: GET /users/me/readiness — 5 transparent milestones, 0-100 score, 60% threshold = "ready for real investing" (verified live: score 60, threshold crossed)

---

## Phase 8.5 — Globalization Architecture 🌍 the "Market Pack" System

> Decision (2026-06-28): the project is designed GLOBAL. Method: everything country-specific lives in one pack — code never knows the country, it asks the pack.
> Adding a country = new config + data adapter + content pack, not new code. TR is built out as the reference pack.

### User Feedback Round 🛠️ (2026-07-09)

- [x] **Listing-link realism audit**: the old Emlakjet pattern 301'd → real patterns verified with curl (/satilik-arsa/edirne-kesan → 200, including quarter depth); Sahibinden moved to canonical slugs (satilik-arsa/satilik-daire) + Turkish-character slugify (Keşan→kesan)
- [x] **Village/quarter depth**: district + village/quarter fields on the province card — "Keşan Çeribaşı köyü" goes to a real Emlakjet path when it resolves, and to Sahibinden's safe search route; with the honesty note "no official price data is published at district/village level"
- [x] Note: "link blocked" in the preview panel is not an app bug — the panel only opens localhost; links work in a real browser

- [x] **Explore went province-level**: TCMB unit-price series discovered (bie_birimfiyat — 81 provinces, TL/m², quarterly, 2010→today) → concrete per-province prices ("Muğla 79.110 TL/m²") instead of NUTS2 blur; province search + top-12 list; batched fetching (15 series/request, daily cache) (7 tests, verified live)
- [x] Horizon buttons 1/2/3 → **1/3/5 years** (16 years of quarterly history honestly supports it)
- [x] Click a province card → 5-year scenario band + that province's Sahibinden/Emlakjet listing links
- [x] **Math error fixed**: the scenario band's "real" value compared the median of ALL windows against a single period's inflation (Muğla showed a nonsensical −62%) → each window is now deflated by its OWN period inflation (Muğla typical real +137.6%)

- [x] **Permanent "Signature has expired" fix**: Clerk tokens die in ~1 minute and the page-load token went stale → the axios request interceptor now pulls a fresh token from Clerk's getToken() on every request (registered by AuthBridge; free because Clerk caches and auto-refreshes internally)

- [x] **Live holding valuation**: exchange assets auto-revalue with current yfinance prices (units, or units derived from the purchase-date price), real estate/land via the TCMB national housing index ratio — with source labels (📡 live / 📊 index estimate / ✍️ manual) and ▲▼ change badges in the list (7 tests; real estate verified live: Jan 2024 3M home → 5.42M +80.6%)
- [x] Priority chain: manual > live/index > purchase amount; fail-open to purchase basis if sources die
- [x] The "I bought it" bridge now writes the purchase date automatically → live tracking starts instantly
- [x] **Rebuild my portfolio**: "rebuild with remaining X TL" button on the holdings page → new recommendation flow with the current risk score + remaining budget
- [x] **Questions split to single-topic**: Q2 (horizon+age) and Q7 (obligations+income) were double-barreled → 9 single questions; "each message asks exactly one thing" rule added to the prompt; all "7 questions" copy updated
- [x] Invisible (black) text on path-selection cards fixed (color: var(--text) on the button) + "Recommended" badge removed

### End-to-End Test Round Findings 🔍 (2026-07-09)

- [x] Tab icon alignment: logo-icon.svg viewBox wasn't square (84×90) and clipped the tail → square (100×100), content-centred viewBox; verified with a fixture (middle of the L = middle of the firefly)
- [x] Navbar/hero and the tab icon now share the same brand mark (logo-icon.svg)
- [x] Critical UX gap: a signed-out user deep-linking to a protected route got a BLACK SCREEN → `AuthPending` fallback (firefly + "redirecting" message), including ClerkLoading — verified live
- [x] Deep health check verified live: /health now probes db+ai

### Quota Problem — Permanent Solution Pack ⚡ (2026-07-09)

- [x] Model-major key matrix: 4 models × 4 keys = 16 independent quota pools — when a key's quota fills, the key changes, not the quality
- [x] Thinking disabled (2.5 family, thinking_budget=0): invisible token burn gone, warm-path latency down to ~2s
- [x] 24h cache on deterministic generations (portfolio/REIT explanations) — the same input never burns quota twice
- [x] Short-TTL cache for empty RAG context: 10.1s → 1.9s while yfinance is down (measured live)
- [x] 3 new keys verified live; honest ToS note in .env.example (failover framing, the production answer is the paid tier)
- [x] 3 new tests (multi-key order, thinking-off config, generate_text cache)

### Transparency & Realism Round 🔍 (2026-07-10 → 2026-07-11)

> User request: "there must be an explanation for why the portfolio has those ratios; the risk
> score must explain why it is that number; no logical gaps anywhere."

- [x] **Portfolio engine v3 (real bug fix)**: the v2 formula `RiskScore × Vol` cancelled out in normalisation — the allocation was independent of the risk profile. v3: `α = score/10; raw = (1-α)·(1/vol) + α·vol` — cautious profiles overweight calm assets, aggressive ones overweight volatile (10 logic tests)
- [x] **Position-count logic**: dust pruning (<8%) + budget-based cap (75k→≤3, 200k→≤4, else ≤6); every dropped asset reported with its reason in metadata — no silent pruning
- [x] **AllocationRationale card**: formula + the user's α + per-asset role/weight rationale + the dropped list — "these ratios are the output of a deterministic formula, not the AI's whim"
- [x] **Risk score breakdown**: every scoring dimension returns a RiskFactor (weight, readable answer, contribution, explanation); ProfilePage renders "where did this score come from?" — contributions sum exactly to the score (verified live: 2.25+1.5+1.75+0.2+0.5 = 6.2)
- [x] **Score persistence**: age + income_stability now persisted (migration a1c9e4b2) — GET /profile recomputes the exact quiz-time score (closed the 6.2 vs 5.7 inconsistency); ProfilePage loads the stored profile, so a refresh no longer wipes 9 answers
- [x] **Market data resilience**: yfinance 0.2.51 → 1.5.1 (Yahoo blocked the old version's requests — seen live); third cache tier "last known good" (never expires); volatility falls back to historical baselines — /recommend can no longer die with an error page and never fabricates values
- [x] **Fake chart removed**: PerformanceChart rendered Math.random() curves as "12-Month Performance" — deleted; the real backtest (Time Machine) covers it

### Universal Compatibility Round 🌍 (2026-07-11)

> Plan decisions: desktop sidebar now · currency/locale layer now · full i18n after deploy ·
> OpenAI/Mistral adapters after billing lands (tier table is already billing-ready).

- [x] **Desktop sidebar**: BottomNav → AppNav — one component, two surfaces (mobile bottom bar / ≥768px left sidebar); investment_path filter in one place; content offset via body.has-sidebar; duplicate navbar logo hidden; verified live at 375px/1280px
- [x] **MarketContext + useMarket**: locale number formatting and currency flow from the user's Market Pack; 14 hardcoded 'tr-TR' formatters removed
- [x] **Currency truth**: `money(n, 'TRY')` pinning — TL-denominated data (TCMB m², TL practice basket, FX exposure) never masquerades as $/€ when the market changes
- [x] **MarketSwitcher** in the sidebar footer (TR/US/DE); packs without live data labelled "sınırlı veri"; Explore shows an honest "integration on the way" state for non-TR markets (verified live: TR→US switch $ formatting + gate, TR return, persistence across reload)
- [ ] i18n infrastructure: UI copy + LLM prompts in locale files (react-i18next + language parameter in prompt templates) — **after deploy, separate sprint**
- [ ] OpenAI/Mistral adapters (single OpenAI-compatible `base_url` adapter covers both + Ollama) — **when billing lands**; keyless tiers must degrade to the free chain instead of crashing

### Paid AI Tier Infrastructure 💳 (billing-ready — 2026-07-08)

> Payment integration deliberately NOT included; the integration point is one line: `user.plan = "plus"`.
> When the Stripe/Iyzico webhook arrives nothing else changes — models, quotas and fallbacks flow from the tier table.

- [x] `ai_tiers.py`: free (Firefly, Gemini flash chain, 50/day) · plus (Lantern, Gemini Pro, 500/day, ~$4.99) · pro (Dawn, Claude chain, 2000/day, ~$14.99)
- [x] Adapters take the model chain as a parameter — the Anthropic chain degrades symmetrically with Gemini on credit/rate-limit (the quota solution carried to premium)
- [x] `users.plan` column (migration 38f539c3) + plan-based chat quota + upgrade hint in the 429 message
- [x] GET /users/me/plans (pricing payload, internal model chains never leak) + PATCH /admin/users/{id}/plan (webhook integration point)
- [ ] Stripe/Iyzico webhook + payment page (real billing — requires accounts)

### Market Pack Core

- [x] `backend/markets/` structure: `base.py` (frozen dataclass) + `tr.py` (reference, fully wired) + `us.py`/`de.py` (researched skeletons) + registry (unknown code → safe TR fallback)
- [x] Pack contents: currency/locale, data-source declarations (TR live, US: FRED / DE: Destatis roadmap), listing bridges (Zillow/Realtor, ImmoScout24/Immowelt), regulator + local tax/brokerage education notes (US: 401k/IRA + capital-gains holding periods; DE: Abgeltungsteuer + Sparer-Pauschbetrag) — all with a "consult a local professional" disclaimer
- [x] `users.market` column + PATCH /users/me/market + GET /users/markets ✅; listing_bridge pack-aware ✅; frontend MarketContext/Switcher ✅ (2026-07-11) — full pack-routing of inflation/index services comes with the US/DE adapters
- [ ] i18n infrastructure (same item as above — after deploy)

### Content Localization (the LLM advantage)

- [ ] Legal/tax education content generated per pack by the LLM + "general information, consult a local professional" disclaimer (education, no legal claims)
- [x] Cultural fear map: every pack carries localized fear_options (TR/EN/DE)
- [ ] Concept glossary localization, not translation: examples with local currency and local products ("an ETF is a basket — with THY, Aselsan..." vs "...Apple, Microsoft...")

### Rollout Order

- [ ] Finish the TR pack completely as the reference implementation (MVP = TR)
- [ ] Choose the second pack by data (US general market vs DE expat segment) — POST-MVP
- [ ] Hardcode audit: verify every TL/CPI/Sahibinden reference in the codebase has moved to a pack reference (frontend format layer done 2026-07-11; backend service routing pending)

## Phase 9 — Brand & Original UI Identity ✨ the "Light" Design Language

> Brand story = product vision: **the unknown is darkness; knowledge holds up a light.** HP-inspired, copyright-safe original interpretation.

### Logo & Brand — DECISION: Firefly 🪰✨ (2026-06-28)

- [x] Logo decision: firefly (a tiny light guiding through the dark) — copyright-safe, warm, original
- [x] Logo design: minimalist SVG firefly (amber halo + purple/blue wings) — favicon + navbar LumosLogo component with a breathing-glow animation
- [x] Entry animation: 10 CSS-particle fireflies drift toward the title in the onboarding hero (2.6s, respects prefers-reduced-motion)
- [x] The firefly appears as the guide character in empty states/onboarding illustrations
- [x] Brand manifesto (first onboarding screen): "Investing looks like a dark forest. Lumos is the light in your hand." — live in the hero section
- [x] Copyright check: no lightning bolts, no wand drawings, no HP fonts — the firefly + abstract light motif is ours

### The "Illuminating UI" 🌗 (signature feature — no other finance app has it)

- [x] Illuminating UI v1: `useIllumination` hook — at courage-score thresholds 25/50/80 the background walks night→dusk→pre-dawn→dawn (1.2s soft transition)
- [x] "Your world brightens as you learn" — a one-time soft glow animation + congratulation micro-card at the moment the score crosses a threshold

### Signature Interactions

- [x] "Işık Tut" tooltip: tapping a jargon term fires a tiny light burst + a plain-language bubble — firefly-themed, amber, with a pointer
- [x] Number animation: values "warm up" onto the screen from cold grey to amber — `.number-warm` CSS class
- [x] Loading state: a growing light dot instead of a spinner — `.light-loader` CSS animation
- [x] Education micro-cards open with a card-flip animation
- [x] Portfolio health score = "Fener" (Lantern): the lantern icon burns brighter as health improves

### Design System

- [x] Palette tokens: `--firefly/--firefly-soft/--firefly-glow` + `--bg-night/dusk/predawn/dawn` steps in index.css
- [x] Typography: Outfit font added (`'Outfit', 'Inter', system-ui, sans-serif`), soft-cornered warm premium sans — NO gothic/fantasy fonts
- [x] Turkish feature naming: "Seni Tanıyalım" (profile), "Işık Tut" (explain), "Fener" (portfolio health), "Şafak Skoru" (readiness), "Zaman Makinesi" (backtest) — live on all pages
- [x] Empty states: firefly in the dark + radial glow animation + encouraging message (Dashboard + Holdings)

---

## 🔑 Critical Reminders

| # | Rule |
|---|-------|
| 1 | **Never** commit the `.env` file |
| 2 | Add the legal disclaimer to every system prompt |
| 3 | Put every API call behind the daily cache |
| 4 | Verify Clerk JWTs on the backend |
| 5 | Write fallback UI for every error state |
| 6 | Defer AWS and Ollama until after the MVP |
| 7 | Ground rule: update todo.md automatically after every piece of work |

---

## 📊 Progress Summary

| Phase | Title | Weeks | Status |
|-----|--------|-------|-------|
| 1 | Setup, Scaffolding & Auth | 1–2 | `[x]` Complete ✅ |
| 2 | NLP Engine & Risk Profile | 3–5 | `[x]` Complete ✅ |
| 3 | Market Data & Portfolio Engine | 5–8 | `[x]` Complete ✅ |
| 3.5 | Real Estate / REIT Layer | 8–10 | `[x]` Complete ✅ |
| 4 | Frontend — Mobile-First Chat UI | 10–14 | `[x]` Complete ✅ |
| 5 | Testing, Deploy & Portfolio | 14–18 | `[/]` Error handling ✅ · Deploy pending |
| 6 | Technical Debt & Production Hardening | 18+ | `[/]` Tests + CI ✅ · Structural improvements ongoing |
| 7 | Product Deepening & Investment Tracking | 18+ | `[/]` Holdings + coach + goal ✅ · Comparison pending |
| 8 | Differentiating Features | 20+ | `[/]` Backtest + TCMB + news ✅ · Asset card pending |
| 8.5 | Globalization (Market Packs) | 20+ | `[/]` Packs + tiers + market layer ✅ · i18n & adapters post-deploy |
| 9 | Brand & Original UI Identity | 20+ | `[/]` Logo + palette + font ✅ · Animations ongoing |
