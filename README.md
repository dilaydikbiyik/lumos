# 🪰✨ Lumos — Smart Investment Assistant

[![CI](https://github.com/dilaydikbiyik/lumos/actions/workflows/ci.yml/badge.svg)](https://github.com/dilaydikbiyik/lumos/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-async-009688)
![React](https://img.shields.io/badge/react-19-61DAFB)
![Tests](https://img.shields.io/badge/tests-781%20backend%20%2B%2046%20frontend-3DD68C)
![Cost](https://img.shields.io/badge/running%20cost-%240%2Fmonth-F5A524)
![Markets](https://img.shields.io/badge/markets-TR%20%C2%B7%20US%20%C2%B7%20DE-7C5CFF)
![Languages](https://img.shields.io/badge/languages-tr%20%C2%B7%20en%20%C2%B7%20de-5B8EF0)
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
  <img src="demo/video/en/lumos-demo.gif" width="300" alt="Lumos demo — mobile tour" />
</p>

The English UI below. The same build also ships Turkish and German, and the
gallery is captured separately in each — see [all three](#the-same-app-in-three-languages).

| Onboarding | The risk quiz | Portfolio |
|---|---|---|
| ![Onboarding](demo/screens/en/01-welcome.png) | ![Risk quiz](demo/screens/en/22-risk-quiz.png) | ![Portfolio](demo/screens/en/03-portfolio.png) |

The quiz above calls **no model at all**. Its nine questions used to live in the
system prompt, read out one chat call at a time; they are served as data now and the
answers arrive already shaped like the schema. Talking is still one tap away.

| Holdings + live chart | Dashboard | AI advisor |
|---|---|---|
| ![Holdings](demo/screens/en/05-my-assets.png) | ![Dashboard](demo/screens/en/06-dashboard.png) | ![AI advisor](demo/screens/en/08-advisor.png) |

| Rent vs. buy | Region price explorer | Currency split |
|---|---|---|
| ![Rent vs. buy](demo/screens/en/04-rent-vs-buy.png) | ![Explore real estate](demo/screens/en/07-explore-property.png) | ![Currency split](demo/screens/en/19-currency-split.png) |

**Before you buy anything.** A listing's price against what the area actually trades
at — which *refuses* to answer in the US and Germany, because their area data is an
index and dividing an asking price by an index number means nothing. Then the same
amount, the same window, both worlds. Then the checks that stop a bad purchase.

| Check a listing | Plot or portfolio? | Before you buy |
|---|---|---|
| ![Listing check](demo/screens/en/25-listing-check.png) | ![Plot or portfolio](demo/screens/en/26-plot-or-portfolio.png) | ![Purchase checks](demo/screens/en/27-purchase-checks.png) |

**Where the money goes, and which half of the app you see.** The reserve comes off
the top — it is not an allocation competing with the others, it is what stops a bad
month becoming a forced sale.

| Budget split | Your path | Risk profile |
|---|---|---|
| ![Budget split](demo/screens/en/23-budget-split.png) | ![Your path](demo/screens/en/24-your-path.png) | ![Risk profile](demo/screens/en/02-risk-profile.png) |

**Three markets, one UI language.** Market and language are independent axes:
this is the *same English build*, pricing the US in dollars off FHFA state data
and Germany in euros off the Bundesbank.

| 🇺🇸 United States | 🇩🇪 Deutschland |
|---|---|
| ![US market](demo/screens/en/12-market-us.png) | ![German market](demo/screens/en/12-market-germany.png) |

**Rehearse before you risk anything.** Play money, the worst stretch of an
asset's own history, and a scenario the app refuses to call a forecast:

| Play money | Time machine | Future scenarios |
|---|---|---|
| ![Practice mode](demo/screens/en/14-play-money.png) | ![Time machine](demo/screens/en/15-time-machine.png) | ![Scenarios](demo/screens/en/16-scenarios.png) |

| Why this split? | What would happen? | Goal planner |
|---|---|---|
| ![Why this split](demo/screens/en/13-why-this-split.png) | ![What if](demo/screens/en/17-what-if.png) | ![Goal](demo/screens/en/18-goal.png) |

**The screen no investing app wants to show you** — carrying card debt, the app
says clear it first and does the arithmetic, before it will show you a portfolio:

<p align="center">
  <img src="demo/screens/en/11-clear-debt-first.png" width="300" alt="Clear the debt first" />
</p>

<details>
<summary>Desktop layouts</summary>

| Dashboard | Portfolio |
|---|---|
| ![Desktop dashboard](demo/screens/en/09-desktop-dashboard.png) | ![Desktop portfolio](demo/screens/en/10-desktop-portfolio.png) |

| Real-estate explorer | Rent vs. buy |
|---|---|
| ![Desktop explore](demo/screens/en/20-desktop-explore.png) | ![Desktop rent vs buy](demo/screens/en/21-desktop-rent-vs-buy.png) |

</details>

### The same app in three languages

Captured from the same production build, one run per language — not mockups.

| 🇹🇷 Türkçe | 🇬🇧 English | 🇩🇪 Deutsch |
|---|---|---|
| ![TR](demo/screens/tr/03-portfolio.png) | ![EN](demo/screens/en/03-portfolio.png) | ![DE](demo/screens/de/03-portfolio.png) |
| ![TR](demo/screens/tr/04-rent-vs-buy.png) | ![EN](demo/screens/en/04-rent-vs-buy.png) | ![DE](demo/screens/de/04-rent-vs-buy.png) |

> Full demo video: [en](demo/video/en/lumos-demo.mp4) · [tr](demo/video/tr/lumos-demo.mp4) · [de](demo/video/de/lumos-demo.mp4)
> Regenerate the whole gallery with `node demo/capture.mjs` (see [demo/](demo/)).

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
- **Readiness milestones** — five transparent steps toward "ready for real money", each one
  something the user actually did. It shows how many are done and **the single next step**, not a
  percentage: a ring reading 40% tells a beginner they are failing, while "two of five done, next:
  record one holding" tells them what to do. The UI background still brightens from night toward
  dawn as they progress

### 💬 Risk profiling — nine questions, one at a time
- 9 single-topic questions grounded in Modern Portfolio Theory (budget, horizon, age, loss
  tolerance, goal, experience, obligations, income stability, monthly contribution) — each screen
  asks exactly one thing, so a nervous beginner never has to answer two questions at once
- **It calls no model.** The questions used to live in the system prompt and a frontier model was
  paid to read them out, one chat call per answer, on the most restricted tier. They are served
  as data now; the answers arrive already shaped like the schema, with nothing to extract and
  nothing to parse. Tests assert the quiz and the schema cannot drift apart
- **Talking is still offered** — as a preference rather than a fallback, one tap either way. Some
  people genuinely prefer a conversation, and the conversational path is untouched
- **Zero-knowledge language rules**: every finance term explained inline on first use; technicality
  escalates only when the user demonstrates knowledge
- **Fear-aware**: worry is acknowledged and normalized before any answer
- A question the schema lets you skip is skippable on screen too, and bounds are checked at the
  step rather than at the end — an out-of-range answer on question seven used to surface as a
  failure after all nine were done, with nothing pointing at which one was wrong
- The answers become a validated 1–10 risk score with a fully transparent breakdown — every factor's weight, your answer, its exact contribution, and why
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
- **Thin histories are refused, counted honestly.** The guard counts how many times the horizon
  fits in the record *without reusing the same years* — three minimum — and reports that number
  beside the band. It used to count overlapping windows, which is six steps past the horizon: a
  five-year band passed on five and a half years of history, one stretch resampled sixty-six times
  and drawn as a spread of outcomes. Both paths now also read the **whole** price record instead of
  ten years, which was the real reason bands were thin. The effect is visible: SPY's 5-year band
  went from two independent periods to six, and 10-year bands for gold and the Nasdaq ETF are now
  refused rather than drawn

### 🏘️ Real-estate intelligence (live official data, per market)
- **Sub-national housing**, from each country's own source and honest about what it is:
  - **Türkiye** — TL/m² unit prices for all **81 provinces** (central bank, quarterly since 2010),
    ranked by *real* appreciation, plus the coarser 19-region NUTS2 index
  - **United States** — the FHFA house price index for **50 states and DC** (via FRED). An index,
    not a price level, so no per-m² figure is shown: it measures appreciation and cannot answer
    what a square metre costs
  - **Germany** — the Bundesbank's residential index for **three city-size segments** (seven
    largest cities / 127 cities / all districts). No Bundesland-level index exists in any free
    source, and these segments are *nested*, so they are compared rather than ranked — a rank
    badge would invite "pick number one" for a segment of a market you are already in
- Frequency and shape are declared by each source rather than assumed: the Turkish and US series
  are quarterly, the Bundesbank's annual, and reading a 3-year horizon as "12 observations back"
  silently turned it into a 12-year one
- Every scenario band deflates each window by **its own period's inflation**, from that market's
  own CPI — the app's core claim was only ever true for Türkiye until inflation was routed
  through the pack
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
- **Portfolio health, as two separate numbers** — diversification and liquidity, each with a
  plain-language note saying what it measures, why it sits where it does *for this portfolio*,
  and the one thing that moves it. There is deliberately **no single 0–100 grade**: averaging two
  unrelated facts into one invented number hid both of them, and "liquidity: 30" teaches nothing
  on its own either, so the explanation is the feature rather than the score
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

### 📚 What you're actually holding — structural reference, per market

Four catalogues, each written for all three markets **and** all three languages independently
(nine combinations, enforced by tests), because the structure genuinely differs by country while
the thing people misread differs too:

- **Funds** — written after 131 Turkish funds were closed to trading at once in September 2026.
  The app had always recommended funds (SPY, QQQ and GLD all are; the German universe is entirely
  UCITS) but taught only one kind of liquidity: how fast an asset sells. What actually happened to
  people was the other kind — the asset inside was fine, the wrapper froze. Separation is real,
  separation is **not** a guarantee of value, and the common misreading is different in each market
  ("the regulator approved it" / "it's SIPC insured" / "Sondervermögen, also geschützt")
- **Gold** — metal in a drawer, a claim on a bank, and a fund share are all called gold and fail in
  different ways. The point the fund lesson cannot teach: in Europe the common gold product is an
  **ETC, a debt security of its issuer, not a segregated fund** — so a reader who learned "funds are
  segregated" and applies it here has it exactly backwards
- **Crypto** — the one asset the app refuses to recommend, which makes it the one it owes the
  clearest explanation. A holding has been recordable since the first migration, and silence beside
  a recorded asset reads as endorsement. The card leads with *why* it is in no recommended
  portfolio, and the reason given is the real one: the projection guard refuses bands resting on too
  few independent periods, and crypto's record cannot supply them. Then — your keys or someone
  else's, a licence is supervision and not deposit insurance, and transfers are irreversible
- **Routes into a home** — savings-pool home financing alongside cash and a mortgage. In Türkiye the
  pool is legally segregated and that is *not* deposit insurance; in Germany the equivalent is a
  **bank** with a statutory deposit guarantee, but the allocation **date** is never promised

No product, fund, dealer or platform is named in any of them, and a test enforces it: a beginner
needs the *structure* explained, and naming one issuer would turn reference material into a
recommendation this app is not licensed to make. Volatile figures (spreads, tax rates, custody
percentages) are kept out by another test — the copy says what to **ask**, not what the answer is.

### 📲 Installable, because push is the coach's only carrier

"The market dropped, here is what you said you would do" is worthless an hour later, so the
behavioural coach needs push — and push needs the app on the home screen.

- Complete PWA: manifest, maskable icons, service worker with a **push handler**
- **Android** gets the real OS install dialog via `beforeinstallprompt`, held and offered in the
  page where the reason for it is, instead of Chrome's own mini-infobar
- **iOS** gets instructions instead, because there is no API — web push has worked since iOS 16.4
  but **only for home-screen web apps, and iOS never offers to install one.** Shown only in Safari:
  Chrome and Firefox on iOS are WebKit underneath and cannot add to the home screen at all, so
  telling their readers to tap Share would send them hunting for a menu item that is not there
- Renders nothing once installed or dismissed. The detection is a pure, unit-tested module —
  iPadOS 13+ reports itself as "Macintosh", so a user-agent test for "iPad" matches **no iPad made
  since 2019**, and touch points are the only thing separating one from a real Mac
- Once installed the card **changes its ask** rather than disappearing: being on the home screen is
  what makes push *possible* on iOS, not what grants it, and the reader who just installed is
  exactly the reader who will say yes. The prompt fires from a click, never an effect — Safari
  refuses otherwise, and a prompt on load is the fastest route to a permanent denial

### 🔔 Push, end to end — VAPID, and no store account

- `POST /push/subscribe` upserts on the **endpoint**, not the user: browsers reissue endpoints, so a
  reader who reinstalls would otherwise accumulate dead rows retried on every market move — which on
  a free tier is what gets a service suspended for outbound traffic
- A `404`/`410` from the push service **retires** that subscription instead of retrying it forever.
  Retired, not deleted: the row still records that this reader once granted permission, which is the
  difference between "never asked" and "asked and it lapsed"
- Unsubscribing **deletes**. `failed_at` means the push service says the browser is gone; a reader
  switching notifications off is a different fact, and conflating them would let a later
  re-subscribe silently revive something they turned off on purpose
- **No keys means no push, not a crash.** A deployment without VAPID keys serves a completely working
  app that never offers notifications, and `/push/public-key` says `available: false` so the frontend
  does not spend a permission grant on a subscription nothing can use
- **`POST /push/market-sweep`** is the sender, triggered by an **external cron** because a free
  Render instance has no scheduler — and the same request keeps the instance awake, which it needs
  anyway, so one free uptime pinger does both jobs. Authenticated by a shared secret; an empty
  `CRON_SECRET` disables the endpoint outright and the refusal is a `404` so a scanner cannot tell
  it exists
- Per-reader, never a broadcast: "the market dropped" is not a fact about somebody who holds nothing.
  Below a 5% move nothing is sent at all, and a 20-hour cooldown means a cron set to five minutes
  cannot send the same drop twelve times an hour
- The notification **body is the coach's sentence**, keyed to the loss tolerance the reader stated —
  never "you are down 12%". A test asserts no figure and no percent sign reaches it: that number is
  the alarm the message exists to answer, not to amplify
- Keys are generated **once** by `scripts/generate_vapid_keys.py` and live only in `.env` and the
  Render dashboard (`sync: false` for all four, the public key included, so the pair cannot drift —
  a mismatched pair encrypts for a key no browser holds and fails *silently*)

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
│   │         every route served under /api/v1 (and, deprecated, at its bare path)
│   ├─ routers/       thin HTTP layer — validation, auth, rate limits only
│   ├─ services/      domain logic (risk, portfolio, backtest, projection, inflation,
│   │                 coach, news, what-if, evds, ai_service + ai_tiers,
│   │                 path_advisor, budget_split, listing_eval, asset_character,
│   │                 property_vs_portfolio, quiz_questions, prompt_experiments)
│   ├─ repositories/  ALL database access (no inline SQL in routers)
│   ├─ markets/       Market Packs — every country-specific fact in one object (TR/US/DE)
│   ├─ content/       market-keyed educational copy (purchase checklists)
│   ├─ schemas/       Pydantic request/response models
│   └─ models/        SQLAlchemy ORM (users, holdings, feedback)
│
└─ data       yfinance (markets) · TCMB EVDS · BLS · FRED · Eurostat · Bundesbank · RSS
```

**Engineering highlights**

- **Layered by rule, not by habit**: routers never touch SQL; services never parse HTTP;
  one repository layer owns every query
- **Three-tier market-data cache** (fresh 24h → stale 7-day → never-expiring last-known-good,
  plus historical volatility baselines as the final resort) — a Yahoo Finance outage degrades
  gracefully instead of breaking the app (observed and survived live, twice)
- **The last-known-good tier survives a deploy.** It never expires *because* it exists for
  provider outages, yet it lived on Render's ephemeral disk and was discarded on every deploy —
  usually right when it was most needed, since a deploy is often the response to something
  already being wrong. Values now mirror into a small Postgres table through a synchronous
  driver (the data adapters are sync and run in thread pools); reads fall back to it and warm
  the local tier on the way past. Entirely optional, and hard-disabled under pytest
- **A dead upstream is attempted once, not on every request.** Each statistics adapter enters a
  short cooldown after a failure, raised *inside* its own `try` so the existing fallback chain
  still runs. Without it, an outage meant every request waiting out a 25s timeout on a single
  worker — which reads as a hung app rather than as stale data
- **Structured observability**: every AI call logs tier, provider, prompt-version hash, latency,
  and outcome; every request carries an `X-Request-ID` echoed in the standard error envelope
  `{detail, error: {code, message, request_id}}`
- **Alembic is the only schema authority** — CI applies every migration to a fresh database on
  every push, plus a Docker build gate and full lint/test matrix
- **RAG chat context**: the advisor speaks from *today's* numbers (index levels + monthly CPI)
  injected into the system prompt with a 6-hour cache — and fails open if sources are down
- **The risk quiz calls no model at all.** Its nine questions were written down in the system
  prompt and a frontier model was paid to read them out — one chat call per answer, on the most
  restricted tier, roughly ten calls from a 50/day quota before a new user saw anything. They
  are served as data (`/api/v1/profile/questions`) and the answers arrive already shaped like
  `RiskProfileAnswers`: nothing to extract, nothing to parse. Conversation is still offered as a
  preference. Tests assert the quiz and the schema cannot drift
- **Model output is parsed by the parser, not by regexes.** `json_extract` scans for the first
  complete JSON value with `raw_decode`, which understands nesting, strings and escapes. The
  ladder it replaced matched the *inner* object of a nested reply and returned it as the user's
  whole risk profile — a confident wrong answer rather than a failure
- **Journey tests.** Every bug reported from the live app has been a state-transition bug — the
  right screen for the wrong account state — and unit tests pass straight through those.
  `demo/journeys.mjs` drives the real app through the states an account actually passes through
  and checks for the error boundary *first*, because a crashed page still renders content

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

**2. A quality gate, not just a quota gate.** Profiling accepts only Gemini/Gemma/Claude-class
models (`gemini`, `gemma`, `claude`, `gpt-oss`) wherever they are hosted, while Llama and
DeepSeek stay available to the free-form advisor, where a slightly weaker answer beats an error.
Replies containing foreign-script characters (a real failure mode: *"rahat的话"*) are rejected
and re-served by the next provider.

The restriction existed because the 9-question quiz had to follow its script exactly and lighter
models paraphrase it. **That quiz no longer calls a model at all** — see below — so the gate now
protects only the paths where a model is genuinely doing the work.

**2b. The cheapest job does not get the most expensive model.** Summarising three headlines and
pulling a number out of one sentence are not the same task as explaining a portfolio to a
frightened beginner. The news digest and the what-if extraction run on small fast models;
everything with a person on the other end keeps the full chain. Every call also carries a
60-second wall-clock limit — without one a hung request held a thread-pool worker open
indefinitely *and* the failover chain never ran, because nothing ever failed.

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
comparisons — all computed by deterministic engines. The LLM phrases results; it never produces
a number. This is a product-safety decision, enforced by tests.

**5. And increasingly it does not do the talking either.** The risk quiz was nine chat calls to
read out nine questions that were already written down — the most expensive, most fragile path
in the app, and the one every reported bug lived in: a Turkish sentence in an English session,
a nested-JSON reply parsed into the wrong object, cold reads, burnt quota. The questions are
served as data now and the answers arrive already shaped like the schema. A journey test asserts
zero chat calls across a full run.

Three things were considered and rejected on the way: fine-tuning a model on investing,
self-hosting open weights from HuggingFace, and Kaggle. The reasoning is in `todo.md`, and it
comes down to one fact — *the model is not the source of a single number this app shows*, so
moving knowledge into one would undo the thing the architecture is built on, and it would fail
worst exactly where the legal exposure is.

**6. Prompt A/B, off by default.** Assignment is a stable hash of the reader, so nobody has the
prompt change between question three and four, and it is hashed with the experiment key so two
experiments never assign in lockstep. Variants can only *append* to the control — none can drop
the disclaimers or the language rule by omission. There is deliberately no automatic promotion
of a winner: changing what a financial-education app says to people is a person's decision.

---

## Going global: Market Packs

Country-specific behavior lives in exactly one place — a **Market Pack**. Application code never
hardcodes a country; it asks the user's pack:

| | 🇹🇷 Türkiye | 🇺🇸 United States | 🇩🇪 Deutschland |
|---|---|---|---|
| Currency / locale | TRY · tr-TR | USD · en-US | EUR · de-DE |
| Inflation | **TCMB EVDS** | **BLS CPI-U** | **Bundesbank HICP** |
| Rent index | — *(spread off CPI)* | **BLS, primary residence** | **Bundesbank, actual rentals** |
| National house prices | **TCMB** | **FHFA via FRED** | **Eurostat `prc_hpi_q`** |
| Sub-national | **81 provinces**, TL/m² | **50 states + DC**, index | **3 city-size segments**, index |
| Mortgage rate | 39% *(assumed)* / 10y | **live** Freddie Mac 30-yr fixed / 30y | **live** Bundesbank effective rate / 20y |
| Purchase costs | deed fee 4% + 2% agency +VAT | closing costs 2.5% + 2.5% agency | transfer tax + notary + registry 7% + 3% agency +VAT |
| Investable universe | BIST + global ETFs | SPY/QQQ/VXUS/GLD, VNQ/SCHH | **UCITS only** — EU retail cannot hold US-domiciled ETFs |
| Listing bridge | Sahibinden, Emlakjet | Zillow, Realtor | ImmoScout24, Immowelt |
| Regulator (edu. content) | SPK | SEC / FINRA | BaFin |

Every source above is live and keyless except FRED, which needs a free key.

**Which numbers are measured, and which are assumed.** Inflation, house-price growth and rent
growth are read live from the sources above for all three markets. The mortgage rate — the single
input that decides a rent-vs-buy verdict — is read live wherever a free source publishes it
(Freddie Mac for the US, the Bundesbank for Germany); Türkiye has no keyless series, so it keeps a
documented constant. A source that goes quiet falls back to *its own market's* constant, never to
another country's rate, and the footnote under every result says which of the two you are looking
at rather than letting an assumption pass for a measurement.

Transfer taxes, agency commission, VAT and upkeep are set by regulation or custom rather than by a
market, so they are constants held in the pack, shown to the user as assumptions, and covered by a
conformance test — one of which exists because Germany's commission was stored VAT-inclusive while
the engine added VAT on top, inventing about €2,700 of cost on a €400k home.

**Language and market are independent axes.** An expat in Istanbul reads English while investing in
Türkiye; a Turk in Berlin may want the opposite. Neither setting implies the other — a new account
starts in the market its language suggests and nothing moves it again, and the separation is
enforced at the source level so a well-meaning `setLanguage(pack.languages[0])` cannot creep back in.

**Adding a market is a contract, not a memory test.**
[`test_market_conformance.py`](backend/tests/test_market_conformance.py) is parametrised over every
market *and* every language, so adding either runs the whole suite against it. It checks that a pack
declares everything the app asks for, speaks every UI language rather than its own country's, copies
no other pack's country facts, prints no foreign currency, cannot claim a data table nothing can
read, and sends listing searches in its own market's words. It has teeth, and that is tested too: a
deliberately sloppy fourth market is registered in-test and the suite must refuse it.

Recipes: [docs/adding-a-market.md](docs/adding-a-market.md) ·
[docs/adding-a-language.md](docs/adding-a-language.md)

**Absent beats near-enough.** The US pack declared *no* house price index for months rather than
borrow the BLS rent series — rent measures what it costs to occupy a home, not what homes sell for,
and substituting one for the other corrupts every buy-vs-rent verdict. Germany still has no
Bundesland-level index because none exists freely, and the page says so instead of inventing one.
All tax and regulatory content is **educational only**, and every pack carries an explicit
"confirm with a licensed local professional" disclaimer — Lumos gives no tax or legal advice in any
market.

---

## Data sources (all free)

| Source | Used for | Resilience |
|---|---|---|
| **TCMB EVDS** (Turkish central bank) | TR: CPI, 81-province unit prices (TL/m²), 19-region NUTS2 index | Daily cache; in-repo static CPI fallback; freshest-wins against the bundled copy; honest `available: false` when down |
| **BLS** (US Bureau of Labor Statistics) | US: CPI-U, rent of primary residence | No key; bundled static fallback + refresh script |
| **FRED** (St. Louis Fed) | US: FHFA house price index, nationally and for 50 states + DC; Freddie Mac 30-year fixed mortgage average | Free key; 51 series fetched in parallel; a mostly-failed map is refused rather than cached |
| **Eurostat** | DE: house price index (`prc_hpi_q`) | No key; last-known-good tier |
| **Deutsche Bundesbank** | DE: harmonised CPI, actual rentals, residential prices for three city-size segments, and the MFI effective rate on new housing loans | No key. Chosen over Eurostat for prices because Eurostat's HICP stopped nine months short — for every euro-area country, not only Germany |
| **yfinance** | Prices, volatility, backtests, projections | Fresh 24h + stale 7d + last-known-good cache tiers; baseline volatilities as final resort |
| **RSS**, per market | Calm news digest — AA/Bloomberg HT (TR), CNBC/Yahoo (US), Tagesschau/Handelsblatt (DE) | Per-feed fail-open; digest hides when empty |
| **Google Gemini** (free tier) | Advisor chat, extraction, phrasing | 4-model chain × up to 4 keys, then hands off to Groq |
| **Groq** (free tier) | Fallback when Gemini is spent or region-blocked | gpt-oss-120b → Llama chain; quiz-eligible models only |
| **OpenRouter** (`:free` models) | Last-resort fallback | Llama / DeepSeek / Gemma chain; corrupted replies rejected |

---

## Security & honesty by design

- **Prompt-injection hardening**: user messages are data, never instructions; the profile-completion
  marker can't be forged from user text; strict role/length validation on every request
- **Per-user daily AI quotas** (DB-backed, plan-aware) + per-IP rate limiting on every AI endpoint
- **Auth**: Clerk JWT verified server-side on every request. **RBAC** grants named permissions
  rather than comparing a role string, so reading the feedback queue does not also confer the
  ability to change other people's plans (`user` / `support` / `admin`). Roles are managed from
  inside the app, with two lockout guards — an admin cannot demote themselves, and the last admin
  cannot be demoted by anyone — and every change is logged with actor and target
- **No execution, no custody**: architecturally incapable of moving user money
- **Delete your account, from inside the app.** It removes the profile, every holding and every
  piece of feedback, then deletes the login itself — and if that last step fails it says so
  rather than reporting a clean deletion you would discover was incomplete at your next sign-in.
  Holdings are deleted explicitly rather than trusting `ON DELETE CASCADE`, which SQLite does not
  enforce, so the guarantee and the test of it cannot disagree
- **Public [privacy policy](frontend/src/pages/LegalPage.jsx) and terms**, in all three languages,
  written against the actual database schema: what is stored, that the database is in Frankfurt
  while the application server is in Oregon, and exactly what reaches an AI provider
- **Secrets cannot reach a response or a log.** A test proves it by failing a provider with its
  own key in the error text. The `ValueError` handler used to return `str(exc)` verbatim to the
  client — and the only `ValueError`s the app ever sees come from drivers and SDKs, whose
  messages carry connection strings and keyed URLs
- **Browser security headers**, set in [frontend/vercel.json](frontend/vercel.json):
  `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, HSTS for two years,
  a referrer policy and a permissions policy denying camera, microphone and location.
  A **Content-Security-Policy ships in `Report-Only` mode** — its origin list was
  measured from the running app rather than guessed, and the journey harness injects
  the same policy locally and fails a run on any violation, so a directive too tight
  to allow sign-in is caught before a deploy rather than in a reader's console.
  It stays report-only until it has run against real traffic; to enforce it, rename the
  header key to `Content-Security-Policy` once the Vercel logs show no reports
- **Honesty guarantees are tested**: prompt-rule regression tests, a no-dark-patterns assertion on
  the Panic Button, refusal paths for thin statistical histories
- Full failure-mode analysis: [docs/risk_register.md](docs/risk_register.md)

## Testing

```bash
./scripts/check.sh                     # everything CI runs, with exit codes that propagate
python -m pytest backend/tests/ -q     # 1007 tests
cd frontend && npm test                # 191 vitest tests
```

### Running the journey tests

They drive a real browser against a real backend, and they **write** profiles,
paths and holdings — so they need a throwaway database, not the one in `.env`.
The harness refuses to start against anything but SQLite (it reads `db_engine`
from `/health`), but the setup is three steps:

```bash
# 1. scratch database + schema
DATABASE_URL="sqlite+aiosqlite:///./journeys-scratch.db" ./venv/bin/python -m alembic upgrade head

# 2. backend on that database, and the frontend, each in its own terminal
DATABASE_URL="sqlite+aiosqlite:///./journeys-scratch.db" ./venv/bin/python -m uvicorn backend.main:app --port 8000
cd frontend && npm run dev

# 3. the journeys — DEMO_USER_ID is a Clerk user id for a THROWAWAY account
set -a && source .env && set +a
DEMO_USER_ID=user_xxxxx RUN_JOURNEYS=1 ./scripts/check.sh
```

`source .env` keeps the Clerk secret out of shell history. The Clerk identity
is real even though the database is scratch, so point `DEMO_USER_ID` at an
account you do not mind filling with test data. Clean up with
`rm journeys-scratch.db`.

- External boundaries (AI providers, yfinance, EVDS, RSS) are fully mocked; business logic runs real
- **API-level E2E**: five personas (conservative → retirement) walk the entire HTTP surface:
  path selection → fear check-in → profiling → recommendation → "I bought it" → wealth summary →
  readiness score ([tests/e2e/scenarios.json](tests/e2e/scenarios.json))
- **Journey tests** ([demo/journeys.mjs](demo/journeys.mjs)) drive the real app in a browser
  through the states an account actually passes through — brand new, returning, mid-retake,
  each path, each market. Every bug reported from the live app has been a state-transition bug,
  and unit tests pass straight through all of them because each piece works in isolation.
  They check for the **error boundary first**: a crashed page still renders *content*, which is
  how a total crash was once reported as "the page loads slowly"
- **A conformance contract, not a memory test**: adding a market or a language is checked by
  tests parametrised over market × language — every pack asset must be explainable, every market
  must have a purchase checklist **in every language**, shared copy may not name one country's
  institutions, and the quiz may not drift from the schema it fills
- **Language and market are independent axes, and it is enforced rather than remembered.** The
  market decides what content is *about*; the language decides what it is *written in*. A reported
  bug — German prose in a Turkish session — traced to content that was market-keyed but carried
  one language each, behind a test that asked for English and accepted the fallback. Coverage is
  now asserted per exact language, the blocks must differ and must *read* as their language by
  script and function words, and the market-pack sweep is by reflection so a field added tomorrow
  is covered today
- `scripts/check.sh` exists because a verification once reported success while the suite failed:
  the exit status of `npx vitest run | tail -3` is `tail`'s. It runs with `set -euo pipefail`
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
