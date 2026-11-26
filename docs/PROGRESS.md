# Lumos — progress (handoff)

Updated: 2026-11-26. Overwritten each session; history is in `todo.md` → "Session log".

## Current state

- Phases 1–4 complete; 5–9 partly done (`todo.md` → "📊 Progress Summary").
- Code is store-ready. Paid plans: Lemon Squeezy (web), RevenueCat (App Store).
- Vercel and Render auto-deploy on push to `main`. The batch 1/6/2/3 fixes are pushed (live since
  2026-11-26 11:18) but not yet checked signed in. Batch 4 audit docs pushed. Per `git status -sb`
  at commit time: `main` is 1 ahead of `origin/main` (CLAUDE.md security-notes rule +
  `docs/private/` in `.gitignore`; to go out with the next fix).
- App-wide UI/UX audit (`docs/ui-audit.md`). Batches 1, 6, 2, 3 audited, all their highs fixed.
  **Batch 4 (Portfolio plan) audited 2026-11-26, nothing fixed**: 3 high (4.1 glossary shows raw
  `{{placeholders}}`; 4.2 ReitCard names US funds to DE readers + Turkish "Dahil"; 4.3 `/recommend`
  blank or dead-end error), 10 medium, 7 low. Remaining audit: batch 5 (Real estate). Skip /admin.
- REIT purple vs `--violet`: never on one screen (violet only on `/profile`). Recheck if 4.6
  colours the `/recommend` risk badge with `bandColor()`.
- Audit rules (`docs/ui-audit.md` Rules): no `opacity` on text; colour+alpha only via
  `withAlpha()`; band colours as fills/dots only, text in `--text`. Batch 4's opacity fixes are
  listed but held (see the rule below).
- Risk bands have one source: server `risk_band()`; `utils/riskBand.js` maps key → colour only.

## Rule until the owner reports back (owner, 2026-11-26)

**No code fixes in any batch until the owner reports the signed-in check.** Each fix adds one
more unchecked item. Audits (read code, write findings) are fine.

## Next step

1. **Owner: ~10 min signed-in check at 375px.** Plans buy buttons only after load, offline error
   + Try again (6.1); Holdings explainer above the list (6.2, 6.3); panic ✕/Escape (2.1); facts
   loader (2.2); `/profile` gauge and card same band name, violet for aggressive (3.3); dashboard
   "Build my portfolio" with the server down shows an error (3.2); DriftCard under "Show
   details"; headline card wording (3.12); holdings mini-bar colours (3.16).
2. After the report: fix what looked wrong, push.
3. Owner creates the throwaway Clerk test user (passwordless `+clerk_test` email, via Clerk API
   in a subshell; auto mode blocked Claude from doing it) → `DEMO_USER_ID` in `.env`. Then
   Claude builds `scripts/dev-signin.mjs` (ticket sign-in, scratch-SQLite guard like
   `demo/journeys.mjs`) so every fix is checked signed in at 375px before it is committed.
4. Batch 4 highs: 4.2 first (US funds shown to DE readers), then 4.1, 4.3 (all effort S).
5. Then audit batch 5 (Real estate, `/explore`).
6. Medium/low items (3.6–3.15, batch 4 mediums, etc.): prioritise together once all batches are
   audited, not batch by batch.

## Open in code

- Batch 3 medium/low 3.6–3.15; batch 4 4.4–4.20; batch 6 6.5, 6.6, 6.8, 6.10–6.12, 6.14–6.17;
  batch 1/2 medium/low per `ui-audit.md`.
- AssetCard #5 (focus return + live region), #8 (Işık Tut on category, plain "what is this").
- PortfolioChart legend % in slice colour (low contrast for REIT/cash).
- Web Plans page shows USD to TR/DE readers — confirm whether Lemon Squeezy charges local currency.
- RevenueCat `TRANSFER` (restore on another account) not handled.
- CSP still `Report-Only`. Accepted, no fix exists: diskcache advisory PYSEC-2026-2447.

## Later (separate tasks, not the audit)

- Animations: every existing animation honours reduced motion first (2.15, 3.15, 4.20).
- Rename "advisor/danışman/Berater" → assistant.

## Open decisions (owner)

- Waiting on legal review (`legal-review-brief.md` q11): `doesBody`, the crash nudge, unsourced
  "historically" claims. Copy 1.18/6.4/6.18/3.12 applied (`docs/copy-decisions.md`).
- Clerk sign-in methods (affects Sign in with Apple).
- Whether the first store release is free (proposed in `todo.md`).

## Owner-only steps

In order, from `todo.md` → "SENİN LİSTEN — mağazaya giden yol": Apple Developer enrolment,
Xcode, Play Console; Render env (VAPID keys, `CRON_SECRET`); cron-job.org market sweep;
`SENTRY_DSN`; enforce CSP.
