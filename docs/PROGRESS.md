# Lumos — progress (handoff)

Updated: 2026-11-26. Overwritten each session; history is in `todo.md` → "Session log".

## Current state

- Phases 1–4 complete; 5–9 partly done (`todo.md` → "📊 Progress Summary").
- Code is store-ready. Paid plans: Lemon Squeezy (web), RevenueCat (App Store).
- Vercel and Render auto-deploy on push to `main`.
- App-wide UI/UX audit (`docs/ui-audit.md`). Done: batches 1, 6, 2, 3 audited; all their highs
  fixed. Remaining: batch 4 (Portfolio plan) → 5 (Real estate), one per session. Skip /admin.
- Audit rules (`docs/ui-audit.md` Rules): no `opacity` on text; colour+alpha only via
  `withAlpha()`; band colours as fills/dots only, text in `--text`.
- Risk bands now have one source: the server's `risk_band()` sends `band` with the profile and
  `allocation_logic.risk_band` with the portfolio; `utils/riskBand.js` maps key → colour only.
  Gauge and summary card show the server's label (fixes "Growth-Focused" vs "Aggressive").
- Dashboard's "Recommended vs actual" card (client-made target) replaced by DriftCard (3.1).
- Aggressive band = `--violet` (#9D4EDD, fills/dots only): four bands, four colours, no red.
- 3.12: headline card `action` lines now describe, not instruct (tr/en/de); crash line sent to
  legal review (brief, under q11) as a behavioural-nudge check.
- 3.16: dashboard mini-bar colours by holding type (`holdingTypeColors`), not position.

## Next step

1. **Owner: ~10 min signed-in check at 375px** (fixes so far verified by code/tests only) — Plans buy buttons only after load, offline
   error + Try again (6.1); Holdings explainer above the list (6.2, 6.3); panic ✕/Escape (2.1);
   facts loader (2.2); `/profile` gauge and card show the same band name (3.3); dashboard
   "Build my portfolio" with the server down shows an error (3.2); DriftCard in "Show details"; violet gauge for an aggressive profile; headline card wording; dashboard
   holdings mini-bar colours (3.16). Do this before batch 4.
2. **Batch 4 (Portfolio plan) audit**: `/recommend`, `/stocks`. Re-check that REIT purple
   (`#7A4A93`) and `--violet` never share a screen (today: violet only on `/profile`).

## Open in code

- Batch 3 medium/low: 3.6–3.15 (tip/headline cards as buttons, GoalPlanner labels + market
  notation, one category colour map — `palette.js` already has `CATEGORY_COLORS`, dashboard
  layout order, legend tap targets).
- AssetCard #5 (focus return + live region), #8 (Işık Tut on category, plain "what is this").
- PortfolioChart legend % in slice colour (low contrast for REIT/cash).
- Batch 6 medium/low: 6.5, 6.6, 6.8, 6.10–6.12, 6.14–6.17. Batch 1/2 medium/low per `ui-audit.md`.
- Web Plans page shows USD to TR/DE readers — confirm whether Lemon Squeezy charges local currency.
- RevenueCat `TRANSFER` (restore on another account) not handled.
- CSP still `Report-Only`.
- Accepted, no fix exists: diskcache advisory PYSEC-2026-2447.

## Later (separate tasks, not the audit)

- Animations, starting with 2.15/3.15: every existing animation honours reduced motion first.
- Rename "advisor/danışman/Berater" → assistant.

## Open decisions (owner)

- Copy 1.18/6.4/6.18/3.12 applied (`docs/copy-decisions.md`). Waiting on legal review
  (`legal-review-brief.md` q11): `doesBody`, the crash nudge, unsourced "historically" claims.
- Clerk sign-in methods (affects Sign in with Apple).
- Whether the first store release is free (proposed in `todo.md`).

## Owner-only steps

In order, from `todo.md` → "SENİN LİSTEN — mağazaya giden yol": Apple Developer enrolment,
Xcode, Play Console; Render env (VAPID keys, `CRON_SECRET`); cron-job.org market sweep;
`SENTRY_DSN`; enforce CSP.
