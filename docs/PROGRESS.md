# Lumos — progress (handoff)

Updated: 2026-11-26. Overwritten each session; history is in `todo.md` → "Session log".

## Current state

- Phases 1–4 complete; 5–9 partly done (`todo.md` → "📊 Progress Summary").
- Code is store-ready. Paid plans: Lemon Squeezy (web), RevenueCat (App Store).
- Vercel and Render auto-deploy on push to `main`.
- App-wide UI/UX audit in progress (`docs/ui-audit.md`). Done: batch 1, 6, 2 audited; all
  their highs fixed. Remaining batches: 3 (Home) → 4 → 5, one per session. Skip /admin.
- Audit rules (`docs/ui-audit.md` Rules): no `opacity` on text; colour+alpha only via
  `withAlpha()`; band colours as fills/dots only, text in `--text`.
- Signed-in fixes are verified by code and tests only, not yet in the browser.

## Next step

1. **Owner: ~10 min signed-in check at 375px** — Plans buy buttons only after load, offline
   error + Try again (6.1); Holdings six labelled fields, explainer above the list (6.2, 6.3);
   panic ✕/Escape/above nav/focus back to lifebuoy (2.1); facts loader (2.2); same band on
   gauge and card (2.16).
2. **Batch 3 (Home) audit**, plus: server returns the risk **band key** with the score
   (`low/medium/growth/aggressive`); frontend maps key → colour/label only, no thresholds in
   `utils/riskBand.js` (today it copies the server's cut-offs — the drift behind 2.16).
   Colours: low green, medium `--firefly`, growth purple, aggressive = owner's choice.

## Open in code

- AssetCard #5 (focus return + live region), #8 (Işık Tut on category, plain "what is this").
- Hardcoded "Kapat" in `HeadlineEducation.jsx`; PortfolioChart legend % in slice colour
  (low contrast for REIT/cash).
- Batch 6 medium/low: 6.5, 6.6, 6.8, 6.10–6.12, 6.14–6.17. Batch 1/2 medium/low per `ui-audit.md`.
- Web Plans page shows USD to TR/DE readers — confirm whether Lemon Squeezy charges local currency.
- RevenueCat `TRANSFER` (restore on another account) not handled.
- CSP still `Report-Only`.
- Accepted, no fix exists: diskcache advisory PYSEC-2026-2447.

## Later (separate tasks, not the audit)

- Animations, starting with 2.15: every existing animation honours reduced motion first.
- Rename "advisor/danışman/Berater" → assistant.

## Open decisions (owner)

- Risk band colour for "aggressive" (suggested: deeper purple + lantern icon, not red).
- Copy: 1.18 (recommending copy), 6.4 (currency card "consider adding…"), 6.18 — options
  drafted in `docs/copy-decisions.md`, not applied. `doesBody` copy waits for legal review.
- Clerk sign-in methods (affects Sign in with Apple).
- Whether the first store release is free (proposed in `todo.md`).

## Owner-only steps

In order, from `todo.md` → "SENİN LİSTEN — mağazaya giden yol": Apple Developer enrolment,
Xcode, Play Console; Render env (VAPID keys, `CRON_SECRET`); cron-job.org market sweep;
`SENTRY_DSN`; enforce CSP.
