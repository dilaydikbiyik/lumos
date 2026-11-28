# Lumos — progress (handoff)

Updated: 2026-11-28. Overwritten each session; history is in `todo.md` → "Session log".

## Current state

- Phases 1–4 complete; 5–9 partly done (`todo.md` → "📊 Progress Summary").
- Code is store-ready. Paid plans: Lemon Squeezy (web), RevenueCat (App Store).
- Vercel and Render auto-deploy on push to `main`. The batch 1/6/2/3 fixes are pushed (live since
  2026-11-26 11:18) but not yet checked signed in. Batch 4 audit docs pushed. Per `git status -sb`
  2026-11-28: `main` level with `origin/main`; batch 5 audit doc uncommitted.
- App-wide UI/UX audit (`docs/ui-audit.md`). Batches 1, 6, 2, 3 audited, all their highs fixed.
  **Batch 4 (Portfolio plan) audited 2026-11-26, nothing fixed**: 3 high (4.1 glossary shows raw
  `{{placeholders}}`; 4.2 ReitCard names US funds to DE readers + Turkish "Dahil"; 4.3 `/recommend`
  blank or dead-end error), 10 medium, 7 low.
  **Batch 5 (Real estate, `/explore`) audited 2026-11-28, nothing fixed**: 3 high (5.1 listing check
  and comparison only offer the 5 visible areas; 5.2 rent-or-buy fields unlabelled; 5.3 province
  scenario stale after amount change, fails if links fail), 8 medium, 4 low. **All batches audited.**
- REIT purple vs `--violet`: never on one screen; recheck if 4.6 uses `bandColor()`.
- Audit rules (`docs/ui-audit.md`): no `opacity` on text; alpha only via `withAlpha()`; band
  colours as fills/dots only. Batch 4/5 opacity fixes are listed but held.
- Risk bands have one source: server `risk_band()`; `utils/riskBand.js` maps key → colour only.

## Rule until the owner reports back (owner, 2026-11-26)

**No code fixes until the owner reports the signed-in check.** Audits are fine.

## Next step

1. **Owner: ~10 min signed-in check at 375px.** Plans buy buttons only after load, offline error
   + Try again (6.1); Holdings explainer above the list (6.2, 6.3); panic ✕/Escape (2.1); facts
   loader (2.2); `/profile` gauge and card same band name, violet for aggressive (3.3); dashboard
   "Build my portfolio" with the server down shows an error (3.2); DriftCard under "Show
   details"; headline card wording (3.12); holdings mini-bar colours (3.16).
2. After the report: fix what looked wrong, push.
3. Owner creates a throwaway Clerk test user (`+clerk_test` email) → `DEMO_USER_ID` in `.env`;
   Claude then builds `scripts/dev-signin.mjs` so every fix is checked signed in at 375px.
4. Highs, all effort S: 4.2 (US funds to DE readers), 4.1, 4.3, then 5.1, 5.3, 5.2.
5. Then all medium/low items together (list below), prioritised across batches.

## Open in code

- Medium/low: 3.6–3.15, 4.4–4.20, 5.4–5.15, 6.5, 6.6, 6.8, 6.10–6.12, 6.14–6.17, batch 1/2 per `ui-audit.md`.
- AssetCard #5 (focus return + live region), #8 (Işık Tut on category, plain "what is this").
- PortfolioChart legend % in slice colour (low contrast for REIT/cash).
- Web Plans page shows USD to TR/DE readers — confirm whether Lemon Squeezy charges local currency.
- RevenueCat `TRANSFER` (restore on another account) not handled.
- CSP still `Report-Only`. Accepted, no fix exists: diskcache advisory PYSEC-2026-2447.

- Later, separate tasks: reduced motion for animations (2.15, 3.15, 4.20); "advisor" → assistant.

## Open decisions (owner)

- Legal review (`legal-review-brief.md` q11): `doesBody`, crash nudge, unsourced "historically".
- Clerk sign-in methods (affects Sign in with Apple).
- Whether the first store release is free (proposed in `todo.md`).

## Owner-only steps

`todo.md` → "SENİN LİSTEN": Apple Developer, Xcode, Play Console; Render env (VAPID, `CRON_SECRET`);
cron-job.org sweep; `SENTRY_DSN`; enforce CSP.
