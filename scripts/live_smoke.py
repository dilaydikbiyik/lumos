#!/usr/bin/env python
"""
Live smoke: the whole backend, as a user would walk it, against REAL data.

The test suite fakes every network source on purpose — that is what makes it
deterministic. It is also exactly why it cannot see the class of bug that
only exists against the real world: a ticker the provider renamed, a
statistics office that changed a series code, an AI provider returning a
shape nobody expected. This script is the other half. It runs once per
market x language, in the order a real reader goes:

    market -> path -> fear -> income -> profile -> recommendation
    -> holdings -> backtest -> projections -> planning -> news -> coach
    -> chat -> feedback -> push -> admin -> account deletion

against live price data, live official statistics and the live AI chain.

WHAT IT REFUSES TO TOUCH
  * Production. It points DATABASE_URL at a throwaway SQLite file BEFORE the
    app is imported, because .env holds the production Postgres URL and a
    smoke run that writes there is a smoke run that corrupts real accounts.
  * Clerk. Account deletion and the admin profile lookup call api.clerk.com
    with the real secret; both are stubbed. Every other call is real.

WHAT COUNTS AS A FAILURE
  * Any 5xx, EXCEPT a 503 carrying the app's own "upstream unavailable"
    code: that is the designed response to a provider outage, reported as
    a warning so an outage is visible without being mistaken for a bug.
  * A raw translation key in a response — i18next-style "a.b.c" strings
    are what the reader sees when copy is missing.
  * Prose that does not read as the language the device asked for.
  * Lira in prose served to a US or German reader.

    ./venv/bin/python scripts/live_smoke.py            # all 9 combinations
    ./venv/bin/python scripts/live_smoke.py --ai full  # chat on every combo

Exit code 0 means no failures. Warnings never change the exit code.
"""
import argparse
import asyncio
import json
import logging
import os
import pathlib
import re
import sys
import tempfile
import time

# ── isolation, BEFORE anything from the app is imported ─────────────────────
_SCRATCH = pathlib.Path(tempfile.mkdtemp(prefix="lumos-smoke-"))
os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{_SCRATCH / 'smoke.db'}"

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

logging.basicConfig(level=logging.ERROR)
for noisy in ("sqlalchemy", "httpx", "yfinance", "urllib3"):
    logging.getLogger(noisy).setLevel(logging.ERROR)

from unittest.mock import patch  # noqa: E402

from fastapi.testclient import TestClient  # noqa: E402

from backend.config import settings  # noqa: E402
from backend.db.database import Base, engine  # noqa: E402
from backend.limiter import limiter  # noqa: E402
from backend.main import app  # noqa: E402
from backend.middleware.verify_clerk import get_current_user  # noqa: E402

engine.echo = False   # development echoes every statement; that buries the report

MARKETS = ("TR", "US", "DE")
LANGS = ("tr", "en", "de")

# The same short-string language check production uses on the news digest,
# so the smoke run and the app cannot disagree about what "reads as German"
# means. Its docstring records how it was tuned on this script's output.
from backend.services.language_check import wrong_language as _wrong_language  # noqa: E402

# Keys whose string values are prose a reader sees. Everything else (tickers,
# codes, dates, enum values) is data and is not language-checked.
_PROSE_KEYS = {
    "detail", "message", "plain_explanation", "reit_explanation", "body",
    "answer", "reply", "reason", "honesty_note", "why_it_matters",
    "calmness_note", "headline", "note", "explanation", "summary", "context",
}

# An i18n key leaking into the UI: lower-case dotted segments, whole value.
_RAW_KEY = re.compile(r"^[a-z][a-z0-9_]*(\.[a-z0-9_]+){1,4}$")

# Region- and area-code inputs per market. A 4xx here is acceptable — the
# point is that it is a translated 4xx, never a 5xx.
_REGION = {"TR": "mugla", "US": "CA", "DE": "DE30"}
_AREA = {"TR": "MUGLA", "US": "CA", "DE": "BE"}
_CITY = {"TR": "Ankara", "US": "California", "DE": "Berlin"}

_CHAT_Q = {
    "tr": "ETF nedir, kısaca anlatır mısın?",
    "en": "What is an ETF, briefly?",
    "de": "Was ist ein ETF, kurz erklärt?",
}
_WHATIF_Q = {
    "tr": "Bütçemi 50.000 artırırsam ne değişir?",
    "en": "What changes if I add 50,000 to my budget?",
    "de": "Was ändert sich, wenn ich 50.000 zu meinem Budget hinzufüge?",
}


class Run:
    def __init__(self) -> None:
        self.failures: list[dict] = []
        self.warnings: list[dict] = []
        self.calls = 0
        self.slowest: list[tuple[float, str]] = []

    def fail(self, combo, step, why, snippet=""):
        self.failures.append({"combo": combo, "step": step, "why": why,
                              "snippet": str(snippet)[:240]})

    def warn(self, combo, step, why, snippet=""):
        self.warnings.append({"combo": combo, "step": step, "why": why,
                              "snippet": str(snippet)[:240]})


def _upstream_messages() -> set[str]:
    from backend.i18n import t
    return {t(k, lang) for k in ("error.ai_down", "error.ai_unavailable",
                                 "error.market_data") for lang in LANGS}


_UPSTREAM_MESSAGES = _upstream_messages()


def _strings(obj, key=None):
    """Every (key, string) pair in a JSON value, recursively."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from _strings(v, k)
    elif isinstance(obj, list):
        for v in obj:
            yield from _strings(v, key)
    elif isinstance(obj, str):
        yield key, obj


def _check_content(run: Run, combo: str, step: str, body, market: str, lang: str):
    for key, text in _strings(body):
        if _RAW_KEY.match(text):
            run.fail(combo, step, f"raw translation key in field {key!r}", text)
        if key not in _PROSE_KEYS or len(text) < 45:
            continue
        wrong = _wrong_language(text, lang)
        if wrong:
            run.fail(combo, step, f"{key!r} reads as {wrong}, reader asked for {lang}", text)
        if market != "TR" and re.search(r"(\bTL\b|₺)", text):
            run.fail(combo, step, f"lira in {key!r} for a {market} reader", text)


def call(run: Run, client: TestClient, combo, step, method, path, *,
         lang, market, expect="ok", **kw):
    """One request, checked. Returns the parsed body (or None)."""
    headers = {"X-Lumos-Lang": lang, **kw.pop("headers", {})}
    t0 = time.perf_counter()
    try:
        res = client.request(method, "/api/v1" + path, headers=headers, **kw)
    except Exception as exc:  # an exception escaping the app IS a 500
        run.fail(combo, step, f"raised {type(exc).__name__}", exc)
        return None
    dt = time.perf_counter() - t0
    run.calls += 1
    run.slowest.append((dt, f"{combo} {step}"))

    try:
        body = res.json()
    except ValueError:
        body = res.text

    code = res.status_code
    if code >= 500:
        err = body.get("error", {}) if isinstance(body, dict) else {}
        detail = body.get("detail") if isinstance(body, dict) else None
        upstream = code == 503 and (
            str(err.get("code", "")).endswith("_unavailable")
            # The AI chain raises a bare 503 without the error envelope; its
            # message is one of these two, in whichever language was asked.
            or detail in _UPSTREAM_MESSAGES
        )
        if upstream:
            run.warn(combo, step, f"upstream unavailable ({err.get('code') or 'ai'})", body)
            # An outage is not a bug — but its message in the wrong language
            # IS. The first run of this script returned before this check
            # and missed a German reader being told about the outage in
            # Turkish.
            _check_content(run, combo, step, body, market, lang)
            return None
        run.fail(combo, step, f"HTTP {code}", body)
        return None

    if expect == "ok" and code >= 400:
        run.fail(combo, step, f"HTTP {code} where success was expected", body)
    elif isinstance(expect, set) and code not in expect:
        run.fail(combo, step, f"HTTP {code}, expected one of {sorted(expect)}", body)
    elif expect == "any" and code >= 400:
        # Acceptable failure (bad region, admin-only, …) — but it must be
        # a translated message, never a key or an English stack for a
        # German reader.
        run.warn(combo, step, f"HTTP {code} (accepted)", body)

    _check_content(run, combo, step, body, market, lang)
    return body if code < 400 else None


async def _create_schema():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def _make_admin(clerk_id: str):
    from sqlalchemy import update

    from backend.models.user import User
    async with engine.begin() as conn:
        await conn.execute(update(User).where(User.clerk_user_id == clerk_id)
                           .values(role="admin"))


def journey(run: Run, client: TestClient, market: str, lang: str, ai_chat: bool):
    combo = f"{market}/{lang}"
    uid = f"smoke_{market}_{lang}"
    app.dependency_overrides[get_current_user] = lambda: uid
    kw = {"lang": lang, "market": market}

    def c(step, method, path, expect="ok", **extra):
        return call(run, client, combo, step, method, path, expect=expect, **kw, **extra)

    # ── account and onboarding ──────────────────────────────────────────────
    c("health", "GET", "/health")
    c("me", "GET", "/users/me")
    c("markets", "GET", "/users/markets")
    c("set market", "PATCH", "/users/me/market", json={"market": market})
    c("market pack", "GET", "/users/markets/pack")
    c("path", "PATCH", "/users/me/investment-path", json={"investment_path": "hybrid"})
    c("fear", "PATCH", "/users/me/fear-check-in", json={"primary_fear": "param_eriyor"})
    c("income", "PATCH", "/users/me/income", json={"monthly_income": 40000})
    c("outgoings", "PATCH", "/users/me/outgoings", json={"monthly_outgoings": 25000})
    c("quiz questions", "GET", "/profile/questions")

    budget = 250_000
    c("profile save", "POST", "/profile", json={
        "budget": budget, "monthly_contribution": 5000, "time_horizon": "long",
        "loss_tolerance": "medium", "goal": "growth", "experience": "beginner", "age": 30,
    })
    profile = c("profile read", "GET", "/profile") or {}
    risk = float(profile.get("risk_score") or 6.0)

    rec = c("recommend", "POST", "/recommend", json={"risk_score": risk, "budget": budget}) or {}
    allocs = rec.get("allocations") or []
    weights = {a["ticker"]: a["weight"] for a in allocs} or {"SPY": 1.0}
    if allocs and abs(sum(weights.values()) - 1) > 0.02:
        run.fail(combo, "recommend", f"weights sum to {sum(weights.values()):.3f}")

    c("readiness", "GET", "/users/me/readiness")
    c("path suggestion", "GET", "/users/me/path-suggestion")
    c("plans", "GET", "/users/me/plans")

    # ── holdings ────────────────────────────────────────────────────────────
    first = next(iter(weights))
    h1 = c("add etf", "POST", "/holdings", json={
        "asset_type": "etf", "name": first, "ticker": first, "purchase_date": "2025-01-15",
        "purchase_amount": 50_000, "quantity": 10, "emotion_tag": "plan"})
    # Both ways gold is held: metal in a drawer (a stated value, no symbol)
    # and a listed product. The drawer case was refused outright until this
    # script's first run caught it on every market at once.
    c("add drawer gold", "POST", "/holdings", json={
        "asset_type": "gold", "name": "Gold", "purchase_amount": 20_000,
        "manual_current_value": 23_000})
    c("add gold no value", "POST", "/holdings", expect={422}, json={
        "asset_type": "gold", "name": "Gold", "purchase_amount": 20_000})
    c("add cash", "POST", "/holdings", json={
        "asset_type": "cash", "name": "Cash", "purchase_amount": 15_000})
    h4 = c("add crypto", "POST", "/holdings", json={
        "asset_type": "crypto", "name": "BTC", "purchase_amount": 5_000,
        "manual_current_value": 4_200})
    c("list holdings", "GET", "/holdings")
    c("summary", "GET", "/holdings/summary")
    c("holdings health", "GET", "/holdings/health")
    c("drift", "GET", "/holdings/drift")
    c("history 30d", "GET", "/holdings/history", params={"days": 30})
    c("history 365d", "GET", "/holdings/history", params={"days": 365})
    c("lookup", "GET", "/holdings/lookup", expect="any", params={"ticker": first})
    if isinstance(h1, dict) and h1.get("id"):
        c("edit holding", "PATCH", f"/holdings/{h1['id']}", json={"note": "smoke"})
    if isinstance(h4, dict) and h4.get("id"):
        c("delete holding", "DELETE", f"/holdings/{h4['id']}")
    c("delete missing", "DELETE", "/holdings/99999999", expect={404})

    # ── analysis ────────────────────────────────────────────────────────────
    for period in ("1y", "5y"):
        c(f"backtest {period}", "POST", "/backtest",
          json={"weights": weights, "budget": budget, "period": period})
    c("projection asset", "POST", "/planning/projection/asset", expect="any",
      json={"ticker": first, "amount": 100_000, "years": 5})
    c("projection portfolio", "POST", "/planning/projection/portfolio", expect="any",
      json={"weights": weights, "amount": 100_000, "years": 5})
    c("projection province", "POST", "/planning/projection/province", expect="any",
      json={"region_code": _REGION[market], "amount": 100_000, "years": 3})

    # ── planning ────────────────────────────────────────────────────────────
    for ep in ("fund-facts", "gold-facts", "crypto-facts", "home-routes",
               "purchase-checks", "budget-split", "yield-comparison"):
        c(ep, "GET", f"/planning/{ep}")
    c("province intelligence", "GET", "/planning/province-intelligence",
      expect="any", params={"horizon_years": 5})
    c("population trend", "GET", "/planning/population-trend", expect="any")
    c("property vs portfolio", "GET", "/planning/property-vs-portfolio", expect="any",
      params={"region": _REGION[market], "amount": 500_000, "period": "5y"})
    c("goal plan", "POST", "/planning/goal-plan",
      json={"target_amount": 800_000, "years": 3, "current_savings": 100_000})
    c("goal progress", "POST", "/planning/goal-progress",
      json={"target_amount": 800_000, "years_remaining": 2,
            "current_savings": 300_000, "actual_monthly_contribution": 10_000})
    c("rent vs buy", "POST", "/planning/rent-vs-buy",
      json={"down_payment": 500_000, "monthly_rent": 15_000, "years": 10})
    c("listing eval", "POST", "/planning/listing-eval", expect="any",
      json={"area_code": _AREA[market], "size_m2": 100, "asking_price": 5_000_000})
    c("listing links", "POST", "/planning/listing-links", expect="any",
      json={"il": _CITY[market]})
    c("practice", "POST", "/practice/snapshot", json={"weights": weights})
    c("stock explorer", "GET", "/stocks/explore")
    c("asset classes", "GET", "/stocks/asset-classes")
    c("role alternatives", "GET", "/planning/alternatives")

    # ── news and coach ──────────────────────────────────────────────────────
    c("news digest", "GET", "/news/digest")
    c("behavior mirror", "GET", "/coach/behavior-mirror")
    c("market drop", "POST", "/coach/market-move",
      json={"direction": "drop", "drawdown_pct": -12.0})
    c("market rise", "POST", "/coach/market-move",
      json={"direction": "rise", "drawdown_pct": 9.0})
    c("panic", "POST", "/coach/panic", json={})
    c("panic held", "POST", "/coach/panic", json={"resolution": "held"})

    # ── AI conversation ─────────────────────────────────────────────────────
    if ai_chat:
        msgs = [{"role": "user", "content": _CHAT_Q[lang]}]
        c("advisor chat", "POST", "/chat/advisor", json={"messages": msgs})
        c("quiz chat", "POST", "/chat", json={"messages": msgs})
        c("extract profile", "POST", "/chat/extract-profile", expect="any",
          json={"messages": msgs})
        c("what-if", "POST", "/chat/what-if",
          json={"question": _WHATIF_Q[lang], "risk_score": risk, "budget": budget})

    # ── feedback, errors, push ──────────────────────────────────────────────
    c("feedback", "POST", "/feedback", json={"message": "smoke", "page": "/smoke"})
    c("feedback list (user)", "GET", "/feedback", expect={403})
    c("client error", "POST", "/client-errors", json={"message": "smoke"})
    c("push key", "GET", "/push/public-key")
    endpoint = f"https://push.example.com/smoke/{uid}"
    c("push subscribe", "POST", "/push/subscribe",
      json={"endpoint": endpoint, "keys": {"p256dh": "BSmoke", "auth": "smoke"}})
    c("push sweep (no secret)", "POST", "/push/market-sweep", expect={404})
    if settings.CRON_SECRET:
        c("push sweep", "POST", "/push/market-sweep",
          headers={"X-Lumos-Cron": settings.CRON_SECRET})
    c("push unsubscribe", "DELETE", "/push/subscribe", params={"endpoint": endpoint})

    # ── admin: refused, then granted ────────────────────────────────────────
    c("admin stats (user)", "GET", "/admin/stats", expect={403})
    asyncio.run(_make_admin(uid))
    c("admin stats", "GET", "/admin/stats")
    c("admin users", "GET", "/admin/users", params={"limit": 5})
    c("admin roles", "GET", "/admin/roles")
    c("feedback list (admin)", "GET", "/feedback")
    # On their own account: the plan change is allowed, and demoting the
    # last admin (themself) is refused by the lockout guard — either way a
    # translated answer, never a 5xx.
    c("admin set plan", "PATCH", f"/admin/users/{uid}/plan", expect="any",
      json={"plan": "free"})
    c("admin self-demote", "PATCH", f"/admin/users/{uid}/role", expect={409},
      json={"role": "user"})

    # ── leaving ─────────────────────────────────────────────────────────────
    c("delete account (wrong id)", "DELETE", "/users/me", expect={400, 403, 422},
      json={"confirm_user_id": "somebody_else"})
    c("delete account", "DELETE", "/users/me", json={"confirm_user_id": uid})


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ai", choices=("light", "full", "off"), default="light",
                    help="light: chat on the three native combos only (saves "
                         "free-tier quota); full: every combo")
    ap.add_argument("--report", default=str(_SCRATCH / "report.json"))
    args = ap.parse_args()

    if "postgres" in str(engine.url):
        print("REFUSING: engine points at Postgres, not the scratch database.")
        return 2

    asyncio.run(_create_schema())
    limiter.enabled = False
    run = Run()
    started = time.perf_counter()

    with patch("backend.services.clerk_service.delete_user", return_value=True), \
         patch("backend.services.clerk_service.fetch_profiles", return_value={}), \
         TestClient(app) as client:
        for market in MARKETS:
            for lang in LANGS:
                native = (market, lang) in {("TR", "tr"), ("US", "en"), ("DE", "de")}
                ai_chat = args.ai == "full" or (args.ai == "light" and native)
                t0 = time.perf_counter()
                journey(run, client, market, lang, ai_chat)
                print(f"  {market}/{lang}  {time.perf_counter() - t0:5.1f}s  "
                      f"fail={sum(f['combo'] == f'{market}/{lang}' for f in run.failures)}  "
                      f"warn={sum(w['combo'] == f'{market}/{lang}' for w in run.warnings)}",
                      flush=True)

    total = time.perf_counter() - started
    run.slowest.sort(reverse=True)
    report = {
        "calls": run.calls, "seconds": round(total, 1),
        "failures": run.failures, "warnings": run.warnings,
        "slowest": [{"s": round(s, 2), "step": n} for s, n in run.slowest[:10]],
    }
    pathlib.Path(args.report).write_text(json.dumps(report, ensure_ascii=False, indent=2))

    print(f"\n{run.calls} calls in {total:.0f}s — "
          f"{len(run.failures)} failures, {len(run.warnings)} warnings")
    for f in run.failures:
        print(f"  FAIL {f['combo']:6} {f['step']:26} {f['why']}\n       {f['snippet'][:160]}")
    print(f"report: {args.report}")
    return 1 if run.failures else 0


if __name__ == "__main__":
    sys.exit(main())
