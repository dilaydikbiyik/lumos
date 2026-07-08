# 🪰✨ Lumos — Smart Investment Assistant

[![CI](https://github.com/dilaydikbiyik/lumos/actions/workflows/ci.yml/badge.svg)](https://github.com/dilaydikbiyik/lumos/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.12-blue)
![React](https://img.shields.io/badge/react-19-61DAFB)
![Tests](https://img.shields.io/badge/tests-133%20passed-3DD68C)
![License: Educational](https://img.shields.io/badge/license-educational%20use-lightgrey)

> **Yatırım hakkında hiçbir fikri olmayan insanların korkmadan, öğrenerek yatırım yapabilmesi için.**
> An AI-powered investment guide built for people who have never invested — and are scared to start.

Lumos is not a trading app. It's the layer that's missing *before* trading apps: a guide that
profiles your risk tolerance through a natural conversation, explains every recommendation in
plain language, shows you the honest downside before the upside, and treats your fear as data —
not as weakness.

**The two pillars that make Lumos different:**

🇹🇷 **Inflation honesty** — every return is shown *nominal AND real* (CPI-adjusted, live TCMB data).
A region that "gained 40%" while inflation ran 60% actually lost value. Lumos is built to say so.

🏘️ **Real estate + stocks under one roof** — Turkey's favorite asset class (land, apartments) and
capital markets in a single guided journey: budget split → region intelligence → listing bridge →
track it all in one portfolio.

---

## Features

### 🧭 Fearless onboarding
- **Path selection** — stocks-only, real-estate-only, hybrid, or "undecided, guide me"; the app
  adapts its modules to your choice (no real-estate content forced on a stocks-only user)
- **Fear check-in** — "What scares you most?" (losing money / being scammed / not understanding /
  messing up) with instant, specific reassurance; the AI advisor adapts its language to your fear
- **Readiness score** — five transparent milestones toward "ready for real money", shown as a
  live dashboard card *and* used to shift the whole UI's background from night toward dawn
  ("Aydınlanan Arayüz" — the interface literally brightens as you learn)

### 💬 Conversational risk profiling
- 7-question chat (budget, horizon + life stage, loss tolerance, goal, experience, current
  holdings, obligations + income stability) grounded in Modern Portfolio Theory
- Zero-knowledge language rules: every finance term explained inline on first use
- Fear-aware: worry is acknowledged and normalized before any answer
- Structured extraction: the conversation becomes a validated risk profile (1–10 score) that
  drives a volatility-weighted portfolio recommendation

### 🕰️ Time Machine (honest backtesting)
- "What if you'd built this portfolio 5 years ago?" with **your own budget** as the starting point
- Shows the worst moment, max drawdown, recovery time — and asks "could you have held on?"
- **Stagnation detection**: flags assets that went sideways for years (crucial for
  guaranteed-return seekers)
- Real (inflation-adjusted) return displayed next to nominal

### 🏘️ Real estate intelligence (live TCMB EVDS data)
- **Region ranking**: 19 NUTS2 regions ranked by *real* housing-index appreciation
- **Rent vs. buy** decision tool — two scenarios side by side, including the honest note that
  homeownership has non-financial value too
- **Listing bridge**: filter-ready links out to listing portals (no scraping, no execution —
  Lumos guides, you buy externally, then log it here)

### 💰 Personal wealth tracker
- All assets in one picture: stocks, funds, ETFs, gold, crypto, cash — **and land, apartments,
  vehicles** (with honest depreciation framing: a car is tracked, never recommended)
- Remaining-budget math, "is my money melting?" idle-cash erosion card (live monthly CPI)
- **Fener (lantern) score**: 0–100 portfolio health from diversification + liquidity, with
  plain-language notes
- One-tap **"Aldım" bridge**: transfer a recommendation into your holdings after you buy

### 🧠 Behavioral coaching
- Profile-keyed calm-down messages on market drops (a panic-seller gets recovery history; a
  dip-buyer gets "stick to the plan")
- Optional 1-tap emotion tag on every purchase (plan / FOMO / tip / panic) feeding a gentle
  behavior mirror
- **Calm news digest**: at most 3 headlines a day, rewritten by AI in non-alarmist language with
  a "does this affect you?" note

### 🎯 Goal-based planning
- "800.000 TL for a down payment in 3 years" → required monthly contribution (annuity math)
- Drift detection: "at your current pace, you'll be 21 months late"

### 🐣 Practice mode
- Virtual 100.000 TL on the recommended portfolio with **real market data** — feel the swings
  before risking anything

### 🔮 Future Scenarios & "What if?" (tool-use, not guesswork)
- **Scenario bands**: "What could SPY become in 5 years?" answered honestly — not a prediction,
  but the pessimistic/typical/optimistic distribution of *every* rolling 5-year window the asset
  has actually lived through, applied to your own amount
- Same treatment for real estate regions, paired with the *real* (inflation-adjusted) return
- **"Ne olurdu?" assistant**: ask "what if I add 10,000 TL?" or "what if I were more aggressive?"
  in plain language — the LLM never does the math itself. It extracts your intent, the real
  portfolio engine computes before/after twice, and the model only narrates the actual numbers

---

## Architecture

```
frontend/  React 19 + Vite · Clerk auth · Recharts · PWA (service worker + manifest)
backend/   FastAPI (Python 3.12) · async SQLAlchemy 2 + Alembic · SQLite (dev)
           ├── routers/       thin HTTP layer (validation + auth only)
           ├── services/      domain logic (risk, portfolio, backtest, inflation, coach…)
           ├── repositories/  all DB access (no inline SQL in routers)
           ├── schemas/       Pydantic request/response models
           └── models/        SQLAlchemy ORM
data       yfinance (markets) · TCMB EVDS (CPI + housing indices, live) · RSS (news)
AI         provider-agnostic adapter: Gemini (google-genai) or Claude (anthropic) via AI_PROVIDER
```

**Engineering highlights**
- Provider-agnostic AI layer with structured logging on every call
  (provider, prompt version hash, latency, outcome) and friendly quota/credit error mapping
- Two-tier market-data cache (fresh 24h + stale 7-day fallback) — a yfinance outage degrades
  gracefully instead of breaking the app
- Prompt-injection hardening: user messages are data, never instructions; completion marker
  can't be forged; role/length validation on every request
- Per-user daily AI quota (DB-backed) + per-IP rate limiting (slowapi)
- 133 backend tests (AI and market data fully mocked), ruff + eslint in CI, Docker build gate,
  fresh-database migration check on every push

---

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

**Required keys (all free):**

| Key | Where to get it |
|---|---|
| `GEMINI_API_KEY` | [aistudio.google.com/apikey](https://aistudio.google.com/apikey) — free tier, no card |
| `VITE_CLERK_PUBLISHABLE_KEY` + `CLERK_SECRET_KEY` + `CLERK_JWT_ISSUER` | [clerk.com](https://clerk.com) — free to 10k MAU |
| `TCMB_EVDS_API_KEY` | [evds3.tcmb.gov.tr](https://evds3.tcmb.gov.tr) → Benim Sayfam → Profilim (optional; static CPI fallback ships in-repo) |

Or with Docker:

```bash
docker compose up --build    # runs migrations, then serves on :8000
```

```bash
python -m pytest backend/tests/ -q     # 133 tests, no network needed
```

---

## Honesty principles (product, not legal boilerplate)

- Lumos **never executes trades** and never holds money — it guides; you buy at your own broker
  or from a listing site, then track it here
- Region intelligence is NUTS2-level; **no street or parcel claims, ever**
- Past performance framing is always paired with the worst historical moment, not just the gain
- Cars are trackable wealth, **never** recommended as investments
- Every AI answer ends with an educational-purpose disclaimer; Lumos is not licensed investment
  advice

## Roadmap

See [todo.md](todo.md) — active phases: Market Pack architecture for going global (TR is the
reference market) and deployment (Render + Vercel). Everything else in the original 9-phase plan
— including the firefly brand identity, the brightening UI, and the API-level 5-persona E2E
suite — is done.

---

⚠️ *Educational purposes only. Not investment advice. Consult a licensed financial advisor.*
