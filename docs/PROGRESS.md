# Lumos — progress (handoff)

Updated: 2026-11-26

## Where it stands

- Phases 1–4 complete; 5–9 partly done (`todo.md` → "📊 Progress Summary").
- Code is store-ready. Paid plans built: Lemon Squeezy on the web, RevenueCat in the App Store.
- Last work (2026-11-25): security audit and bug-hunt round 11 — billing stale and double
  events, Sentry startup crash, bounded money fields, readable 500s across origins.
- 2026-11-26: AssetCard UI/UX audit (11 findings). Fixed #1–4, 6, 7, 9, 10: hsl-safe border
  (color-mix), slice colour on border/dot only (text in tokens for contrast), 48px close
  button, i18n close label, global firefly `:focus-visible` ring, typography tokens, "—"
  fallbacks. Still open: #5 (focus return + live region), #8 (Işık Tut on category, plain
  "what is this" line). Same issues elsewhere: hardcoded "Kapat" in HeadlineEducation.jsx;
  PortfolioChart legend % in slice colour (low contrast for REIT/cash).
- 2026-11-26: App-wide UI/UX audit started (audit only, no code changes). Inventory and 6
  batches are in `docs/ui-audit.md`. Batch 1 (first contact, signed out) done: 20 findings,
  4 high — disclaimer modal can't scroll on small/landscape phones, Privacy/Terms links 2.5:1
  contrast, modal hides language picker + legal links, `--text-dim` fails AA as text app-wide.
  Order for the rest: 6 (skip /admin) → 2 → 3 → 4 → 5, one per session.
- 2026-11-26: Fixed batch 1 items 1.1–1.4. Disclaimer modal scrolls (fits 375×560 and landscape)
  and carries the language picker + Privacy/Terms links. Owner decision on 1.4: raise the
  `--text-dim` token (#4E5070 → #8385A9; 5.5:1 on --bg, 4.6:1 on --bg-input) instead of
  editing call sites, so 1.2 is fixed by it too; if a screen looks flat, use size/weight.
  1.18 (recommending copy) left for the owner.
- 2026-11-26: Batch 6 audited (18 findings, 4 high): Plans can offer a second subscription
  when /billing/me fails; first-purchase explainer renders inside a collapsed section; holdings
  form has placeholder-only labels; currency card says "Consider adding foreign-currency
  assets" (copy, owner's call with 1.18). Cross-batch: text dimmed with `opacity` (6.7).
- 2026-11-26: Fixed batch 6 items 6.1, 6.2, 6.3, 6.7, 6.9. 6.1: the server's 409 already blocked a
  second web checkout, but an App Store purchase never reaches the server, so Plans now offers no
  purchase until `/billing/me` loads and shows an error + Try again if it fails. Rule (owner):
  no `opacity` on text — use `--text-muted`/`--text-dim`; later batches fix it on sight (in
  `docs/ui-audit.md` Rules). Copy options for 1.18, 6.4, 6.18 drafted in `docs/copy-decisions.md`
  (not applied). Signed-in screens not checked in the browser (sign-in needed); check.sh green.

- 2026-11-26: Colour+hex-alpha concatenation (`${c}55`, `c + '44'`) replaced app-wide (8 sites)
  by `withAlpha()` in `utils/palette.js` (color-mix); rule added to `docs/ui-audit.md`. 6.13 fixed.
  Live check (test account, local) found dollar cash counted as lira on the currency card — fixed
  (`utils/holdingCurrency.js` + test); the suspected purchase-amount mixing was not a bug (server
  converts). Vercel and Render both auto-deploy on push to `main`. Local backend DB moved to
  `./e2e.db` (launch.json; old path was a cleared scratch folder).
- 2026-11-26: Batch 2 audited (15 findings, 4 high): panic overlay under the nav with no way out,
  blank panic facts on a cold server, hardcoded TR/EN strings in onboarding, quiz load failure is a
  dead end. Text-opacity fixed on sight in batch 2 components.
## Next step

UI audit: fix batch 2 highs (2.1–2.4, all effort S), then audit batch 3 (Home). `doesBody` copy
waits for legal review. Separate task: rename "advisor/danışman/Berater" → assistant. Batch 6
medium/low items 6.5, 6.6, 6.8, 6.10–6.12, 6.14–6.17 still open.

Owner-only steps, in order: `todo.md` → "SENİN LİSTEN — mağazaya giden yol". Apple Developer
enrolment, Xcode, Play Console; Clerk sign-in methods decision (affects Sign in with Apple);
Render env (VAPID keys, `CRON_SECRET`); cron-job.org market sweep; `SENTRY_DSN`; enforce CSP.

## Open in code

- Web plans page shows USD to TR/DE readers — confirm whether Lemon Squeezy charges local currency.
- RevenueCat `TRANSFER` (restore on another account) not handled.
- CSP still `Report-Only`.
- Accepted, no fix exists: diskcache advisory PYSEC-2026-2447.

## Undecided

- Whether the first store release is free (proposed in `todo.md`, not decided).
