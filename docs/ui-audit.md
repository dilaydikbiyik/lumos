# Lumos UI/UX audit

Audit only. Findings here, fixes later (high severity + effort S first, as with AssetCard).

**Scope per batch:** accessibility (contrast against the real `index.css` tokens, `:focus-visible`,
screen-reader labels, tap targets vs `--touch-target`) · mobile at 375px and the installed PWA ·
"explain before showing" (Işık Tut or a plain line for every term/number) · loading / empty /
error states · i18n tr/en/de (hardcoded strings, long German) · market-pack leaks · describe,
never recommend · reduced motion.

**Rules:** keep the "Light" design language (todo.md Phase 9: firefly motif, `index.css` tokens,
Outfit). No new style, palette or font. **Text is never faded with `opacity`** (owner, 2026-11-26,
from 6.7): use `--text-muted` or `--text-dim`, and `--t-micro` for the smallest text. In each later
batch, fix this on sight in that batch's components and do not report it as a finding. (Opacity on
graphics, e.g. chart bars, and on disabled controls is fine.) **No alpha appended to a colour
variable** (`` `${color}55` ``, `color + '44'`; owner, 2026-11-26, from 6.13): colours arrive as hex,
`hsl()` or `var(--token)`, so this is invalid CSS for most of them and the tint silently vanishes. Use
`withAlpha(color, percent)` from `utils/palette.js` (a `color-mix`). Fix on sight, do not report
it. Each finding is **verified** (code read or measured) or
**suspected**. AssetCard is out of scope (audited and fixed 2026-11-26; its open #5 and #8 stay
in `docs/PROGRESS.md`).

Source of the inventory: routes in `frontend/src/App.jsx`, nav in `components/AppNav.jsx` +
`navItems.js`, first-run order in `utils/homeRoute.js`. Note: `components/HomeRoutes.jsx` is
not the router; it is the "ways into a home" card on Explore.

## Batches (in the order a new user meets them)

Size = lines of JSX in the batch (a rough effort proxy).

| # | Batch | Screens / flows | Components in scope | ~Lines | Status |
|---|---|---|---|---|---|
| 1 | First contact (signed out) + install | `/` landing, disclaimer modal, sign-in (web redirect + in-app Clerk `SignIn`), `AuthPending` loading, crash screen, unknown URL → `/`, `/privacy`, `/terms`, PWA install + offline | OnboardingPage, DisclaimerModal, LanguageSwitcher, LumosLogo, FireflyMark, LegalPage, InstallHint, utils/errorBoundary, `public/manifest.webmanifest`, `public/sw.js` | 950 | done 2026-11-26 |
| 2 | Getting to know you + the app shell | `/path` (step 1), `/fear-check-in` (step 2), `/profile` risk quiz (step 3, chat + structured); shell first seen here: header, bottom nav / sidebar, market + language switchers, panic button, advisor chat, feedback | PathSelectionPage, FearCheckInPage, ProfilePage, ChatWindow, MessageBubble, StructuredQuiz, RiskGauge, DebtFirstCard · AppHeader, AppNav, MarketSwitcher, HeaderSelect, PanicButton, AdvisorChat, FeedbackButton, Section, Disclaimer | 1,890 | done 2026-11-26 |
| 3 | Home | `/dashboard` (first tab, where a finished profile lands) | DashboardPage, ReadinessScore, PathSuggestion, PathInvitation, DailyTip, HeadlineEducation, NewsDigest, BudgetSplit, GoalPlanner, BehaviorMirror, PortfolioChart (minus AssetCard), PortfolioComparison, StocksLink | 1,730 | done 2026-11-26 |
| 4 | Your portfolio plan | `/recommend` (allocation, why, what-if, practice), `/stocks` (asset classes) | RecommendPage, AllocationRationale, RoleAlternatives, AssetExplainer, ReitCard, ReferenceFacts, TimeMachine, AssetCharacter, IsikTut, FutureScenarios, WhatIfAssistant, PracticeMode, BoughtItBridge, BeginnerGuide, Glossary, RealEstatePathNotice · StocksPage, AssetClasses | 2,140 | audited 2026-11-26 (no fixes yet) |
| 5 | Real estate | `/explore` (property vs portfolio, purchase checks, listing evaluation, population trend, ways into a home) | ExplorePage, PropertyVsPortfolio, PurchaseChecks, ListingEval, PopulationTrend, HomeRoutes | 1,390 | audited 2026-11-28 (no fixes yet) |
| 6 | What you own, account and plans | `/holdings` (record purchases, value, drift, currency); path switch + delete account (on `/profile`); `/plans` billing (Lemon Squeezy web / RevenueCat app); `/admin` (admin only, low priority) | HoldingsPage, FirstPurchaseEducation, PortfolioValueChart, DriftCard, CurrencyExposure · PathSwitcher, DeleteAccount, PlansPage · AdminPage, UserAccessPanel | 1,820 | done 2026-11-26 (`/admin` skipped) |

Why this order: `homeRoute.js` sends a new reader `/` → `/path` → `/fear-check-in` → `/profile`
→ `/dashboard`. The nav then reads Dashboard → Portfolio → Holdings → Explore → Profile.
Explore comes before Holdings here because a new reader has nothing to record yet (Holdings
starts empty), and plans stay last as asked.

**Audit order (owner, 2026-11-26):** 1 → 6 (skip `/admin`) → 2 → 3 → 4 → 5.

Cross-batch items to check once, in batch 2: the illumination background (`useIllumination`,
night → dawn) for contrast and reduced motion, and the floating buttons overlapping content at 375px.

## Findings

Columns: issue · why it matters for a beginner · fix · effort (S/M/L) · severity (high/med/low) · evidence (verified/suspected).

<!-- One section per batch, added as each is audited. -->

### Batch 1 — first contact (signed out) + install (audited 2026-11-26)

Measured in the dev build at 375×667 and 375×560 (Chrome emulation); contrast computed from the
`index.css` tokens. Store-review items are marked **[store]**.

| # | Issue | Why it matters for a beginner | Fix | Effort | Sev | Evidence |
|---|---|---|---|---|---|---|
| 1.1 | **[store]** Disclaimer modal cannot scroll. At 375×560 the card is 596px tall, its top (the title) sits at −18px and nothing scrolls; in landscape (667×375) the "Got it" button is off-screen, so the app cannot be entered at all. Overlay is `position:fixed` with no `overflow`, card has no `max-height`. | A person on a small phone or holding it sideways is stuck at the very first screen; a reviewer on an iPhone SE in landscape sees a dead app. | Overlay `overflow-y:auto`; card `max-height: calc(100dvh - 32px)` + `overflow-y:auto`; empty emoji `<div>` dropped. Re-measured: 667×375 card 16→359px, scrolls, button reachable; 375×560 card 16→544px. | S | high | **fixed 2026-11-26** |
| 1.2 | **[store]** Privacy and Terms links on the landing page are `--text-dim` (#4E5070) on `--bg`: **2.53:1** (AA needs 4.5:1). Tap targets are fine (97×44, 93×44). | They are the two links a reviewer looks for first, and the ones a cautious person reads before signing up; at 12px and 2.5:1 they read as disabled. | ~~Use `--text-muted`~~ Superseded by 1.4: links keep `--text-dim`, whose value was raised. Re-measured after the change: **5.51:1** on `--bg` (`rgb(131,133,169)`, 44px tall). | S | high | **fixed 2026-11-26** |
| 1.3 | **[store]** The disclaimer modal covers the language picker and the Privacy/Terms links (hit-test on the picker lands on the modal card) and has no link of its own. A reader must agree to a legal text before they can switch its language or read the terms it refers to. | Agreeing to something you cannot read in your language, or before you may read the terms, is the opposite of "invest without fear"; a reviewer cannot reach the policy without agreeing first. | Compact `LanguageSwitcher` top-right of the card and Privacy/Terms links under the checkbox (44px targets). Re-tested: hit-test lands on the picker, switching to EN re-renders the title. The in-modal picker is still 46×27 (that is 1.13). | S | high | **fixed 2026-11-26** |
| 1.4 | Other `--text-dim` text on the landing page: the uppercase tagline (14px, OnboardingPage.jsx:167) and the "honest expectation" line (12px, :262) — both **2.53:1**. On the dawn background (`--bg-dawn`) it drops to 2.18:1. | The tagline and the honest-expectation line are the two sentences that set the tone; at this contrast many will not read them. | **Owner decision:** raise the token, not the call sites. `--text-dim` `#4E5070` → `#8385A9` (same hue, lighter): 5.51:1 on `--bg`, 5.13 on `--bg-card`, 4.62 on `--bg-input`, 4.75 on `--bg-dawn`. Hierarchy now rests on size/weight; if a screen looks flat, separate it with those, not a darker grey. | S | med | **fixed 2026-11-26** |
| 1.5 | `AuthPending` always says "Redirecting you to the sign-in page…" (`common.redirecting`), but it is also the fallback while Clerk loads and while a route chunk downloads for a **signed-in** reader (App.jsx:120, :123), and in the store build where nothing redirects. | A returning user who sees "sending you to sign-in" on every slow page load thinks they have been logged out — a small scare for someone already nervous. | A neutral "Loading…" for `ClerkLoading`/`Suspense`; keep "Redirecting…" only beside `RedirectToSignIn`. Add `role="status"` to the text. | S | med | verified (code) |
| 1.6 | **[store]** Clerk's sign-in UI is not localised: no `localization` prop on `ClerkProvider` (main.jsx:98) and no `@clerk/localizations` dependency. The web modal and the in-app `SignIn` (store build) are English for TR and DE readers. | Sign-in is the first form a beginner fills in; it switching to English right after a Turkish landing page feels like leaving the app. Apple reviews in the storefront's language. | Add `@clerk/localizations` and pass `trTR`/`deDE`/`enUS` from the current i18n language. | S | med | verified (code) |
| 1.7 | **[store]** In-app sign-in gate (`SignedOutGate`, store build) is a bare Clerk card: no Lumos heading or line saying why an account is needed, no way back to the landing page, no Privacy/Terms link. Clerk renders its default light card on the night page (`NATIVE_APPEARANCE` only hides social buttons). | A signed-out reader who opens a deep link lands on a foreign-looking form with no explanation and no exit. Reviewers check that sign-in explains itself and that the policy is reachable from it. | Wrap the `SignIn` with the logo, one plain sentence, and the two legal links; set Clerk `appearance.variables` from the existing tokens (no new palette). | S–M | med | verified (code); look in the simulator suspected |
| 1.8 | **[store]** Store build uses email-only sign-in. If the Clerk instance verifies email by **magic link** rather than a code, the link opens Safari/Chrome, not the app, and sign-up never completes. | The person is left in a browser tab, signed in on the website, with the app still asking them to sign in. | Owner: confirm Clerk uses email **code** (OTP) for verification before submission; note it in `docs/store-submission.md`. | S | med | suspected (depends on Clerk dashboard) |
| 1.9 | Disclaimer modal focus: on open, focus stays on `<body>`; there is no focus trap and the page behind is not `inert`, so Tab moves to the logo and language picker behind the overlay. On accept, focus is dropped to `<body>`. | A keyboard or screen-reader user does not hear the disclaimer first and can wander behind it; VoiceOver users are the ones who most need the plain framing. | Focus the title (or checkbox) on mount, set `inert` on the page behind, move focus to the "Get started" button on accept. **Same pattern as AssetCard #5.** | S–M | med | verified (measured `document.activeElement`) |
| 1.10 | The disclaimer is only shown on `/`. A reader who arrives on any protected link (`/dashboard` from a share, an email, a push) signs in and never sees or accepts it. | The one-time "what Lumos does and doesn't" framing is skipped for exactly the people who arrive mid-flow. | Check the flag in `ProtectedRoute` (or `AppShell`) and show the same modal there. | S | med | verified (code: flag read only in OnboardingPage) |
| 1.11 | Crash screen (`errorBoundary.jsx`) shows the raw `error.message` (e.g. "Failed to fetch dynamically imported module") under the title, offers only "Go home", and its button is ~40px tall (`padding:10px`) vs the 48px `--touch-target`. | A technical English sentence at the moment the app breaks reads as "something serious went wrong with my money". | One plain line per language ("Your data is safe. Try again or go back to the start."), a "Try again" (reload) button first, the raw message in a collapsed "details" for support, `min-height: 48px`. | S | med | verified (code) |
| 1.12 | Offline: the service worker caches `/` and only the asset chunks already fetched. Opening a route not visited before while offline fails the lazy `import()`, which lands on the crash screen (1.11) with an English network error. There is no "you're offline" state anywhere. | On a train or with bad signal the app looks broken, not offline. | In `errorBoundary`, detect `!navigator.onLine` / chunk-load errors and show "You're offline — Lumos needs a connection for live prices" with Retry. Optional: precache the route chunks at install. | S (message) / M (precache) | med | verified (code) |
| 1.13 | Compact language picker in the landing header is **46×27px** (HeaderSelect `padding: 4px 6px`). | Below the 48px `--touch-target`; it is the control a reader in the wrong language must hit first. | `min-height: var(--touch-target)` on the compact select (width can stay). Affects the shell header too (batch 2). | S | med | verified (measured) |
| 1.14 | `/privacy` and `/terms` use their own header without a safe-area inset; the installed PWA uses `black-translucent` status bar, so the logo row can sit under the clock/notch. The "updated" date is `--text-muted` at `opacity:0.7` = **3.6:1**. | The policy pages are what a reviewer and a cautious reader open; overlapping the status bar looks unfinished. | `padding-top: max(1.5rem, env(safe-area-inset-top))`; drop the opacity on the date. | S | low | contrast verified; notch overlap suspected (not run on a device) |
| 1.15 | Hero logo is a `<button>` with a hardcoded Turkish label "Lumos anasayfa" (LumosLogo.jsx:24) that navigates to `/` while already on `/` — two identical "Lumos anasayfa" buttons on the landing page (header + hero, 215×83). | English/German screen-reader users hear Turkish; a focusable button that does nothing is a dead stop. Also used by the `.navbar` CSS selector (index.css:196), so change both. | i18n the label; render the hero logo as non-interactive (`as="div"` prop or `hero` → no button). | S | low | verified (measured) |
| 1.16 | Landing "routing" state (signed-in reader, up to 8s) shows only a pulsing dot — no text, no `role="status"`/label. `.light-loader` and `.spinner` are not in the reduced-motion block. | 8 seconds of an unlabelled dot reads as frozen; screen readers announce nothing. | Reuse `AuthPending` (mark + one line) here; add both loaders to the `prefers-reduced-motion` rule (slow pulse or static). | S | low | verified (code) |
| 1.17 | InstallHint (shown on `/dashboard`, audited here): the ✕ dismiss button has `padding:0; line-height:1` (~16px target); titles use emoji (🔔, 📲) instead of the `Icon` set; text sizes are hardcoded 12.5px. Dismissing removes the card and drops focus to `<body>`. | A 16px target next to the main action invites a mis-tap that installs or asks for notifications by accident. | 48px hit area on ✕ (padding, keep the glyph); `Icon` for the title glyph; `--t-small`. Focus: same AssetCard #5 pattern. | S | low | verified (code) |
| 1.18 | **[store]** Wording leans toward recommending: the modal says Lumos "computes a portfolio allocation that fits [your profile]" and "the portfolio suggestions this app produces" (`disclaimerModal.doesBody`/`detail`, all 3 locales); the TR `<meta description>` says "şeffaf portföy önerisi". | "Describe, never recommend" is the product rule, and a finance reviewer reads "an allocation that fits you" as personalised advice — which the same modal says Lumos does not give. | Owner/copy decision: "shows an example allocation for a profile like yours and explains it" or similar; align the meta tags (index.html is TR-only while `<title>` is EN). | S | low | verified (copy) |
| 1.19 | `isInAppBrowser()` misses TikTok (`BytedanceWebview`/`musical_ly`), Snapchat and Pinterest web views, so the "open in your browser" hint does not show there; it also only shows on `/`, not in front of `RedirectToSignIn` on a deep link. | Google sign-in then fails with no explanation for people arriving from those apps. | Add the markers; show the same hint in `SignedOutGate` on the web. | S | low | suspected (UA strings not tested) |
| 1.20 | Smaller items: OnboardingPage.jsx:105/108 read/write `localStorage` without try/catch although `readFlag`/`writeFlag` exist in `utils/storage.js` (a storage-blocked web view throws → crash screen on first open); manifest `maskable` reuses the `any` 512 icon (likely no safe-zone padding, so Android may crop the firefly); hardcoded 12/12.5/13/14px sizes instead of `--t-*` tokens across the landing and modal. | First-open crash in strict privacy modes; a cropped home-screen icon. | Use `readFlag`/`writeFlag`; a padded maskable icon; `--t-small`/`--t-micro`. | S | low | code verified; icon crop suspected |

**Checked and fine:** no horizontal scroll at 375px (`scrollWidth` 375); landing fireflies and wordmark
stop under reduced motion; primary button text 9.6:1; `.disclaimer` box text 5.9:1 and the
"educational only, not investment advice" line is on the landing page in all three languages;
`/privacy` and `/terms` are public routes with 14 + 10 sections in tr/en/de; store build hides
Google sign-in (so no Sign in with Apple obligation, guideline 4.8); Privacy/Terms targets are 44px.

**What visibly changed with the `--text-dim` raise (1.4).** Every use in 40 files gets lighter. Worth
an eye: landing tagline / expectation line / legal links (checked, still distinct by uppercase and
spacing); `.num-label` above every number on the dashboard and holdings; inactive bottom-nav and
sidebar items (bottom-nav hover is `--text-muted`, now only 1.14:1 away, so that hover cue is gone;
touch devices never see it); input placeholders (4.6:1 vs entered text 14.8:1, still clearly
placeholders); inactive tabs/range buttons (AssetExplainer, PortfolioValueChart, FeedbackButton,
BeginnerGuide); the grey start frame of the number warm-up animation. Non-text uses also lighten:
`cash` slice colour in PortfolioComparison, `flat` in PopulationTrend, DriftCard's dashed target
marker, `other` in AdminPage. Suggested look: dashboard, disclaimer modal, a chart with a cash slice.

**Deferred AssetCard patterns — where they recur in batch 1 (not fixed):**
- **#5 focus return / live region:** DisclaimerModal (no initial focus, no trap, focus lost on
  accept — 1.9); InstallHint ✕ (focus lost on dismiss — 1.17); the "Continue" button's checking
  spinner and `AuthPending` text have no `role="status"` (1.5, 1.16).
- **#8 jargon without explanation:** disclaimer modal "risk profile", "portfolio allocation",
  "deflates every number", "regulated financial service"; landing feature cards "real returns",
  "real appreciation", "price per m²"; trust chips "official housing price index", "the formula is
  visible" (which formula?). The landing page has no Işık Tut, so the fix there is a plain
  half-line, not a tooltip.

### Batch 2 — getting to know you + the app shell (audited 2026-11-26)

Read from code; the panic overlay, floating buttons, header and nav were also checked live on the
local build with a test account, at 375/390px (mobile, bottom bar) and 1280px (web, sidebar).
Contrast is computed from the tokens.

| # | Issue | Why it matters for a beginner | Fix | Effort | Sev | Evidence |
|---|---|---|---|---|---|---|
| 2.1 | **Panic overlay can't be left and sits under the nav.** Its `z-index: 50` is below the bottom nav (100) and the header, so both show and stay tappable on top of a "stop and breathe" screen. There is no close button and no Escape in the pause and facts stages: the only way out is to pick an answer. Focus stays on `<body>`. | Someone who taps the lifebuoy by accident, or out of fear, is held in a full-screen dialog that only lets them out by answering. | `z-index` above the nav (as `.advisor-overlay`, 200); a labelled close button and Escape in every stage; focus into the dialog and back to the button on close. | S | high | verified live, 375px — **fixed 2026-11-26**: z-index 200, ✕ button (48px) + Escape in every stage, focus to ✕ on open and back to the lifebuoy on close (not re-checked live: sign-in needed) |
| 2.2 | **Panic facts stage can be blank.** "Show now", or the end of the 10s count, switches to `coach` before `/coach/panic` has answered; `stage === 'coach' && coach` then renders nothing. On a cold server (30–60s) that is an empty dark screen with no buttons (and, with 2.1, no exit). | The moment of panic is the worst time for a blank screen. | While `coach` is null, show the loader and one line ("getting your numbers…"); keep the close button. | S | high | verified (code) — **fixed 2026-11-26**: loader + "Getting your numbers…" (`panic.loading`) while `coach` is null; ✕ stays |
| 2.3 | **Hardcoded Turkish/English in onboarding.** Fear check-in continue button `"Harika, devam edelim →"`; RiskGauge `"Risk skorun"` and default label `'Dengeli'`; quiz chat send button `aria-label="Send"`. | EN and DE readers meet Turkish on step 2 and on their result. | i18n keys in tr/en/de. | S | high | verified (code) — **fixed 2026-11-26**: `fear.continue`, `profile.riskScoreCaption`, gauge label falls back to the band name, chat send uses `common.send` (tr/en/de) |
| 2.4 | **Quiz questions fail to load → dead end.** If `/profile/questions` fails, StructuredQuiz shows only the red error: no Try again, and the "I'd rather talk" link (the other way in) is not rendered. | Step 3 of 3 of onboarding, on the cold start a new user is most likely to meet. | Try again button + keep the "talk instead" link in the error state. | S | high | verified (code) — **fixed 2026-11-26**: friendly error (`quiz.loadError`), Try again, and "I'd rather just talk" in the error state |
| 2.16 | **Risk gauge and summary card disagreed on the band.** Gauge rounded the score (`Math.round`: 3.4 → 3 → green) and used green/amber/red; Profile summary card used `≤3 / ≤6` with green/firefly/accent; AllocationRationale used a third set (`≤3.5 / ≥7`). A 3.4 read "low" on the gauge and rationale but "Balanced" on the card. | The same number, two verdicts, on one screen. | One source: `utils/riskBand.js` (cut-offs mirror the server's `_label`: ≤3, ≤6; colours = the card's tokens). | S | high (owner) | **fixed 2026-11-26** — all three read `riskBand()`; `utils/riskBand.test.jsx` renders the gauge at 3.4, 3, 6, 6.6 and checks it matches the card's band |
| 2.5 | Quiz number input (age, budget, income…) has no `className="input"`: browser-default light field on the dark card, under 16px, so iOS Safari zooms on focus (as 6.10). | The first thing a new user types into. | `className="input"`. | S | medium | verified (code) |
| 2.6 | Quiz "Back" and "I'd rather talk" are 12px text buttons with `padding: 0` (~16px tall). | Back is the only way to fix a wrong answer; too small to hit. | `min-height: var(--touch-target)`, `--t-small`. | S | medium | verified (code) |
| 2.7 | **Gauge and summary disagree on the band.** RiskGauge bands by `Math.round` and paints 7–10 **red**; the summary card bands by `≤3 / ≤6` and paints "high" purple (`--accent`). Score 3.4: green gauge, amber "medium" label; 6.6: red gauge, purple "high". The SVG has no `role="img"`/label and uses hex, not tokens. | Red tells a reader their answer is wrong or dangerous; a risk tolerance is neither. Two colours for one score reads as two verdicts. | One band function in both; no red (use the summary's colours); `role="img"` + `aria-label`; tokens. | S | medium | verified (code) |
| 2.8 | "Redo" has no way back: the result hides until the quiz is finished again (only a reload restores it), and the saved draft is deleted first. | A curious tap costs the reader their result screen. | A "Back to my result" link while `retaking` and a result exists. | S | medium | verified (code) |
| 2.9 | Chat (quiz chat and advisor): message list has no `aria-live`, so replies are not announced; both inputs are placeholder-only (no label); advisor × has no size (~30px); advisor Escape works only once focus is inside the panel, and opening does not move focus there. | Screen-reader users get no answer read out; the close is hard to hit. | `aria-live="polite"` on the list; `aria-label` on inputs; 48px close; focus the input on open. | S | medium | verified (code) |
| 2.10 | **Dawn background lowers contrast** (cross-batch). At illumination stage 3 (`--bg-dawn` + the amber `body::after` glow) near the bottom of the screen: `--text-dim` ≈ **3.8:1**, `--text-muted` ≈ **4.3:1**, `--accent` ≈ **3.5:1**. Cards are opaque, so only page-level text there is hit: the "Say something about this" feedback link (`--text-dim`, 11px), page subtitles and footers. Night, dusk and pre-dawn stay ≥ 4.6:1. | The reward for learning makes the smallest text harder to read. | Cap the glow (e.g. 0.12 at stage 3) or give bottom-of-page text `--text-muted` on a surface. | S | medium | computed; glow strength at viewport bottom estimated (~13%) |
| 2.11 | Path and fear choices save in the background (5 tries, then `.catch(() => {})`); PathSelectionPage's `error` state is never set. If every try fails, the next app open asks again with no word why. | Silent loss of what the reader just told us. | After the last failed try, a small non-blocking note on the next screen. | S | low | suspected (needs a 15s outage to see) |
| 2.12 | Panic and advisor buttons show on `/path` and `/fear-check-in` (only `/profile` hides them): a lifebuoy "panic" button before the reader owns anything. FABs are 46px (< 48). | Two unexplained floating buttons on the first screens after sign-in. | Hide on the intro routes too; 48px. | S | low | verified live |
| 2.13 | Feedback sheet: no `role="dialog"`, no Escape; category chips have no `aria-pressed`; textarea is placeholder-only. | Screen readers don't know a sheet opened or which category is chosen. | Add them. | S | low | verified (code) |
| 2.14 | Small text and targets: `common.eduFooter` at 10px in both chats (below `--t-micro`); Plans button on Profile `min-height: 44`. | Legal line too small to read. | `--t-micro`; 48px. | S | low | verified (code) |
| 2.15 | Motion outside `prefers-reduced-motion`: path/fear cards slide/scale on hover, FABs slide on scroll, reassurance ring `light-pulse` loops, chats scroll smoothly. | Motion-sensitive readers get it anyway. | Wrap in the existing reduced-motion block. | S | low | verified (code) |

**Fixed on sight in this batch** (Rules): text faded with `opacity` → `--text-muted`/`--text-dim` in
ProfilePage (score breakdown), StructuredQuiz (help lines, Skip), DebtFirstCard (captions),
PanicButton (pause body, facts), FeedbackButton (subtitle), AdvisorChat (typing bubble), Section
(count, subtitle). ProfilePage summary border `color + '44'` → `withAlpha`.

**Checked and fine:** header pickers fit at 375px with no sideways scroll; bottom bar (mobile) and
sidebar (web) switch at 768px and never show together; nav buttons have `aria-label`s; the advisor
panel sits above the nav (z 200) and is full-screen on phones; the quiz counts "3 of 9" instead of a
bar, checks each answer's range on that question, allows skipping optional ones and has `role="alert"`
errors; RiskGauge prints the score in the reader's number format; `Section` uses `aria-expanded`;
`--text-dim`/`--text-muted` ≥ 4.6:1 on night, dusk and pre-dawn; the debt card shows its arithmetic
and its assumption.

**Deferred AssetCard patterns in batch 2:** #5 focus / live region: quiz step change (new question not
announced), fear choice → reassurance swap, panic stages, "Redo". #8 jargon: "risk score", the
factor "+2 / −1" contributions, "profile", the panic "10" with no word on what the count is.

### Batch 3 — Home (audited 2026-11-26)

Read from code; `/dashboard` needs a signed-in account, so nothing here was measured in the browser.
Contrast is computed from the tokens.

| # | Issue | Why it matters for a beginner | Fix | Effort | Sev | Evidence |
|---|---|---|---|---|---|---|
| 3.1 | **Two different "targets" for one reader.** PortfolioComparison ("Recommended vs actual split for your risk 6.6/10 profile") builds its target in the browser from a fixed table with its own cut-offs (≤3 / ≤5 / ≤7) and weights (e.g. 45% stock at 8+). It is not the plan on `/recommend`, and not the target DriftCard shows on Holdings, which the server builds from the reader's real plan (`/holdings/drift`). | The same portfolio is "balanced" on one screen and "off target" on another, against a "recommended" split the app never recommended. | Show DriftCard here instead and delete the client-side table. | S | high | **fixed 2026-11-26** — DriftCard (server, real plan) replaces it; PortfolioComparison and its table deleted |
| 3.2 | **"Build my portfolio" fails silently.** The tap replaces the whole dashboard with a spinner (`isLoading` with no cache); on failure `usePortfolio` sets `error`, but DashboardPage never reads it. After a cold start (30–60s) the reader lands back on the same card with no word. | The page's one primary action does nothing and says nothing, on the server state a new user meets most. | Show the error and Try again in the card. | S | high | **fixed 2026-11-26** — `role="alert"` error in the build card; the build button is the retry |
| 3.3 | **Risk band name differs on one screen** (cross-batch, see 2.16). The server has four bands (`≤3` conservative, `≤6` balanced, `≤8` growth, else aggressive); `utils/riskBand.js` copies only three, with "Aggressive" above 6. On `/profile` a 7 reads "Growth-Focused" on the gauge and "AGGRESSIVE PROFILE" on the card under it. | Two names for one number, and the harsher one is wrong. | Server returns the band key with the score; the frontend maps key → colour only and shows the server's label. | S | high | **fixed 2026-11-26** — server sends `band` (profile) and `allocation_logic.risk_band` (portfolio) from one `risk_band()`; `utils/riskBand.js` is key → colour only; gauge and card show the server label; "aggressive" colour still the owner's call |
| 3.4 | **Hardcoded Turkish on Home.** NewsDigest count `"{n} haber"`; HeadlineEducation ✕ `aria-label="Kapat"`. | EN and DE readers meet Turkish on their first tab. | `news.count` (plural) and `common.close`. | S | high | **fixed 2026-11-26** — `news.count` (plural, tr/en/de), `common.close` |
| 3.5 | Readiness card stays a grey skeleton forever when `/users/me/readiness` fails (the error is swallowed and `data` stays null). | A permanent ghost card at the top of the first tab reads as broken. | On failure render nothing. | S | medium | **fixed 2026-11-26** — renders nothing on failure |
| 3.6 | Daily tip and headline cards are `role="button"` divs with a button inside: no `tabIndex` or key handler (keyboard can't advance), and any tap while reading marks the tip "learned" and swaps it. The daily tip ✕ is 16px with `padding: 0`, so a near miss advances instead of closing. | The reader loses the text they were reading; keyboard users are stuck on card 1. | A real "Next" button (48px); card not clickable; ✕ 48px. | S | medium | verified (code) |
| 3.7 | GoalPlanner: three amount fields are placeholder-only (the hint vanishes on typing); `type="number"` + `Number()` cannot take market notation (DE "80.000"), while BudgetSplit uses `parseAmount`; error has no `role="alert"`; "delayed" in red; progress gradient in hex. | The reader forgets which box is which and German amounts go wrong. | Labels, text inputs with `parseAmount`, `role="alert"`, tokens. | S | medium | verified (code) |
| 3.8 | One asset type, three colours: the dashboard mini bar colours by position from a hex list (gold changes colour when the order changes), PortfolioComparison has its own `CATEGORY_COLORS` (hex `#FFD700`, `#9B59B6`, `#666`), Holdings another. | Colour stops meaning anything across screens. | One category → colour map in `utils/palette.js`. | S | medium | verified (code) |
| 3.9 | "↓ {amount}/month eroding" in red under remaining budget, with no word on what erodes it (inflation on uninvested cash) or how it is computed. | Red loss language with no explanation; explain before showing. | A plain line or Işık Tut with the inflation figure used. | S | medium | verified (code) |
| 3.10 | The risk-profile card and the portfolio snapshot sit at the very bottom, under the Disclaimer, after news, tips, budget split and the details drawer. The card shows "6.6/10" in an amber badge with no word on what the score is. GoalPlanner sits inside the details drawer, which is hidden until the reader owns something (the comment above the sections says planning cards were moved out of it so new users see them). | A reader with a portfolio scrolls the whole page to see it; a new reader never meets the goal planner. | Snapshot above "What's happening"; one plain line under the score; GoalPlanner into "Your next move". | M | medium | verified (code order) |
| 3.11 | PortfolioChart legend rows are ~28px tall (`padding: 4px`); pie has no accessible name; tooltip in hex. | Small targets for the main way into each asset. | 48px rows, `role="img"` + label, tokens. | S | medium | verified (code) |
| 3.12 | Headline card "action" copy tells the reader what to do ("Stay calm. Selling today turns the drop into a real loss."). | Close to "don't sell" advice. | Owner copy decision (`docs/copy-decisions.md`): all four headline `action` lines rewritten as descriptions (what happens, not what to do), tr/en/de. | S | low (owner) | **fixed 2026-11-26** |
| 3.13 | NewsDigest items: no `aria-expanded`; button contains `<p>`/`<div>`; chevron unlabeled. | Screen readers don't hear that an item opened. | `aria-expanded`, spans. | S | low | verified (code) |
| 3.14 | Small text and targets: tip/headline counters at 10px (below `--t-micro`) plus a progress bar (the app's own rule is "a count, not a bar"); StocksLink `minHeight: 44`; details toggle 12–13px; BudgetSplit input has `className` twice. | Hard to read and hit. | `--t-micro`, 48px, drop the bars. | S | low | verified (code) |
| 3.15 | Motion outside reduced motion: journey-card glow `pulse` loops, bar width transitions, news fade-in. | As 2.15. | Do with the animations task. | S | low | verified (code) |
| 3.16 | Dashboard holdings mini-bar coloured by position (`colors[i]`): the second type was always REIT purple, so gold or a fund could read as "REIT", and a type's colour changed with the rest of the holdings. | Breaks the `palette.js` rule that one asset has one colour everywhere. | `holdingTypeColors()` in `palette.js`: holding type → allocation category colour, fixed colours for crypto/vehicle/other, ranked in a fixed order. Test: same type, same colour, any order. | S | medium | **fixed 2026-11-26** |

**Fixed on sight in this batch** (Rules): text faded with `opacity` → `--text-muted`/`--text-dim` in
ReadinessScore, PathSuggestion, PathInvitation, StocksLink, BudgetSplit, GoalPlanner, BehaviorMirror,
PortfolioComparison (legend) and PortfolioChart (dimmed legend rows keep the dot faded, not the text).

**Checked and fine:** the primary "build" card sits at the top when there is no portfolio; the install
hint shows once; PathSuggestion shows its reasons and needs an explicit tap; PathInvitation's "not now"
is remembered per user; BehaviorMirror waits for three tagged purchases and puts no number in the
headline; BudgetSplit explains each part, uses `<dl>`, `parseAmount` and an `aria-label`; GoalPlanner
shows its formula; NewsDigest hides itself on failure; StocksLink is a real button.

**Deferred AssetCard patterns in batch 3:** #5 focus / live region — tip and headline swaps, news item
expand, goal result appearing. #8 jargon — "risk score", "remaining budget", "eroding", "deviation",
"Courage Score"; none has Işık Tut.

### Batch 4 — your portfolio plan (audited 2026-11-26)

Read from code; `/recommend` and `/stocks` need a signed-in account, so nothing here was measured in
the browser. 4.1 was checked by rendering the glossary with i18next. **No fixes in this batch yet**
(owner, 2026-11-26): none until the signed-in check of the earlier fixes is reported.

| # | Issue | Why it matters for a beginner | Fix | Effort | Sev | Evidence |
|---|---|---|---|---|---|---|
| 4.1 | **Glossary shows raw placeholders** for "inflation" and "real return": `Glossary.jsx` reads the entries with `returnObjects` and no values, so the text reads "At {{rate}}% inflation, 100 {{unit}} under the mattress…" and "You made {{nominal}}% but inflation was {{inflation}}%" (tr/en/de). `IsikTut` passes the values, the glossary list does not. | The two words the app most wants a beginner to understand show up broken, in the place they go to look words up. | Render each entry with `t('glossary.<id>.text', { unit, ...inflationExample(pack), ...realReturnExample(pack) })`, as `IsikTut` does. Test: no `{{` in the rendered list. | S | high | verified (rendered with i18next) |
| 4.2 | **ReitCard leaks the US market and Turkish.** It always names "VNQ (Vanguard REIT) · SCHH (Schwab US REIT)", but a German portfolio's REIT is `IQQP.DE` and `markets/de.py` says EU retail investors cannot buy VNQ. Its badge is hardcoded Turkish "Dahil". | A German reader is pointed at funds they cannot legally buy; EN/DE readers see Turkish. | Name the REITs from `portfolio.allocations` (category `reit`); badge → `t('reit.included')`. | S | high | verified (code) |
| 4.3 | **`/recommend` can be blank or a dead end.** `if (!portfolio) return null`: when the saved profile fails to load (cold start, offline) and nothing is cached, the page is empty with no header. The error state has no header, shows the raw error, and its button reads "Back Try again" (two strings glued together) and goes to the `/profile` quiz instead of retrying. | The Portfolio tab, on the server state a new user meets most, is an empty screen or sends them back to the quiz. | Header plus one error card; "Try again" re-runs the load; a blank state only while loading. | S | high | verified (code) |
| 4.4 | REIT in two colours on one screen: purple pie slice (`#7A4A93`), blue `ReitCard` (`rgba(91,142,240,…)`). `AssetExplainer`'s own `CATEGORY_META` / `ASSET_META` colours (REIT green, QQQ `#9B59B6`) are dead today because the page always passes the slice colour. | Breaks "one asset, one colour". | `ReitCard` uses `CATEGORY_COLORS.reit` via `withAlpha`; drop the unused colour fields. | S | medium | verified (code) |
| 4.5 | Işık Tut bubble is 260px, centred on the term with `position: absolute`. At 375px a term near either edge pushes it off-screen. No Escape or outside tap to close; `role="tooltip"` with no `aria-describedby`. Shared: also used in batches 2, 3 and 5. | The app's main "explain this word" tool can open half off-screen and stays open. | Clamp to the viewport (or open as an inline block under the line); Escape and outside tap close; `aria-describedby`. | M | medium | suspected (layout) / verified (keys) |
| 4.6 | The risk badge is always amber, "Risk 6.6/10", with no band name or plain line, though the server sends `allocation_logic.risk_band`. | The score that shaped the whole plan is unexplained, and its colour disagrees with `/profile`. | Show the server band label; colour from `bandColor()`; one plain line. | S | medium | verified (code) |
| 4.7 | Tickers alone where a beginner needs names: AssetCharacter rows ("XEON.DE"), what-if allocation changes, Practice's "biggest mover". Practice's mover % is the raw number (no `percent()`, so no locale decimal or rounding). | "IUSA.DE moved +1.2345" means nothing to a beginner, and the DE decimal mark is wrong. | Name (ticker) from the allocation; `signedPercent()`. | S | medium | verified (code) |
| 4.8 | WhatIfAssistant: the question box has only a placeholder (no label); "Risk" is hardcoded English. Errors in TimeMachine, FutureScenarios, WhatIf, Practice and BoughtItBridge have no `role="alert"`; results appear with no live region. | Screen-reader users don't hear failures or answers; DE shows English. | Label, `t()`, `role="alert"`, `aria-live` on the result. | S | medium | verified (code) |
| 4.9 | "I bought it" records the whole recommended amount, at today's date, in one tap, with no step for what was actually bought. | A reader who bought less, or yesterday, gets wrong holdings and wrong drift, then has to fix them on another screen. | Confirm step with the amount and date shown, or let the reader change them (the server already de-duplicates). | M | medium | verified (code) |
| 4.10 | "What you hold" section header says "· 3", but each `ReferenceFacts` card hides itself on failure, so the count can be wrong and the section can open empty. | An empty drawer after a tap reads as broken. | Count what loaded, or hide the section when none loaded. | S | medium | verified (code) |
| 4.11 | `/stocks` and asset-class load errors show text only, no "Try again". | Every error state needs a way forward (project rule). | Retry button that re-fetches. | S | medium | verified (code) |
| 4.12 | `/stocks` column labels "real", "worst drop", "volatility" and the "swing vs index" line have no Işık Tut or plain line (the glossary has these terms). | The page's whole lesson depends on words it doesn't explain. | Işık Tut on each label, once per page. | S | medium | verified (code) |
| 4.13 | FutureScenarios puts two selects and a button in one row; at 375px that is about 311px, and the asset names are long ("Vanguard Real Estate ETF (VNQ)"). | The asset picker is clipped on a phone. | Wrap the row: the select on its own line. | S | medium | suspected (layout) |
| 4.14 | Small targets: AssetExplainer ✕ (~34px) and tabs (12px text, ~33px); BeginnerGuide step chips (~28px, 11px text, active chip `#000`) and header button without `aria-expanded`; RoleAlternatives summary `minHeight: 24`; Glossary ✕; `/stocks` tabs and rows `minHeight: 44`. | Hard to hit on a phone. | `--touch-target`, `--t-micro` minimum, tokens, `aria-expanded`. | S | low | verified (code) |
| 4.15 | A real-estate-only reader: `getMe()` and `recommend()` start together, so a stock portfolio is built (server work) and can flash before the notice. | Briefly shows the thing the path choice said not to. | Wait for `getMe()` before building. | S | low | suspected (race) |
| 4.16 | AssetExplainer tabs and `/stocks` tabs: no full tab semantics (no `tablist`/`aria-selected` in the explainer; no `tabpanel` or arrow keys on `/stocks`). | Screen readers hear plain buttons. | ARIA tabs pattern. | S | low | verified (code) |
| 4.17 | Hex outside tokens: TimeMachine line `#8b8bf5` and tooltip label `#333`; PracticeMode border fallback; `rgba(...)` in ReitCard and IsikTut. | Drifts from the palette. | Tokens / `withAlpha`. | S | low | verified (code) |
| 4.18 | `stocks.asOf` gets the date as the server sends it, not formatted for the reader's locale. | "2026-11-20" in a German sentence. | Format with the market's date format. | S | low | suspected |
| 4.19 | AssetClasses: `available` with an empty `classes` list throws on `sharpest.key` (crash screen). | Edge case, but a crash on a teaching page. | Guard the empty list. | S | low | suspected (edge) |
| 4.20 | Motion outside reduced motion: AssetExplainer fade-in, Işık Tut pulse, chevron and chip transitions. | As 2.15. | Do with the animations task. | S | low | verified (code) |

**REIT purple vs `--violet` (asked in PROGRESS.md):** they never share a screen. `--violet` is used only by
`RiskGauge` and `ProfilePage` (`/profile`). `/recommend` gets REIT purple through `CATEGORY_COLORS`, and
every category the server sends (`stocks`, `bond`, `cash`, `gold`, `reit`) has a colour there, so the
position-based fallback list (which holds a light violet, `#A78BFA`) is never reached on this page. If
4.6 colours the risk badge with `bandColor()`, an aggressive reader *will* see violet next to the REIT
slice: give the badge a dot, not a fill, or recheck the pair then.

**Fix on sight, not done this time** (Rules; held because no code changes until the check): text faded
with `opacity` in AllocationRationale, RoleAlternatives, ReferenceFacts, TimeMachine, AssetCharacter,
FutureScenarios, WhatIfAssistant, PracticeMode, BoughtItBridge ("checking" card), RealEstatePathNotice
and Glossary. No colour-plus-alpha strings (`${color}55`) found in this batch.

**Checked and fine:** the page opens on the chart, with the reasoning and tools folded away; the rationale
lists every dropped asset with its reason; the currency-risk note sits on the Risk tab only; RoleAlternatives
ranks nothing; FutureScenarios measures past windows, gives no forecast and shows its honesty note; TimeMachine
shows the worst moment next to the result; BeginnerGuide gets regulator facts from the market pack; the
stock list is sorted by name in the reader's alphabet and is the same for every reader; AssetClasses keeps
the server's calm-to-volatile order; the glossary search has a label; "I bought it" never shows the button
while it doesn't know, and a retry skips what was already saved.

**Deferred AssetCard patterns in batch 4:** #5 focus / live region — tapping a slice opens AssetExplainer
below without moving focus; tool results (time machine, scenarios, practice, what-if) appear silently.
#8 jargon — "Risk 6.6/10", "defensive / growth target", "position cap", "stagnation".

### Batch 5 — real estate (audited 2026-11-28)

Read from code; `/explore` needs a signed-in account, so nothing was measured in the browser. Locale
strings and backend rounding were read to confirm the number and wording findings. **No fixes yet**
(same hold as batch 4).

| # | Issue | Why it matters for a beginner | Fix | Effort | Sev | Evidence |
|---|---|---|---|---|---|---|
| 5.1 | **Area pickers only offer the table's visible rows.** `ListingEval` and `PropertyVsPortfolio` get `visible`: by default the top 5 areas ranked by real change, or whatever the search box matches. A reader whose city is not in the top 5 cannot evaluate their listing or compare their area unless they find "Show all". A search with no hits hides both cards entirely. | The listing check is the tool a reader uses with a real flat in hand, and it hides their city. The list it does show is a leaderboard, which nudges toward "the winners". | Pass every area (`all`), sorted by name in the reader's locale, not `visible`. | S | high | verified (code) |
| 5.2 | **Rent-or-buy fields have no labels.** Down payment, rent, home price, income, loan rate and term are placeholder-only (no `<label>`, no `aria-label`). The placeholder disappears as soon as the reader types. | Six money fields that look the same once filled: a beginner can't tell rent from home price on a second look, and a screen reader announces "edit text". | Visible label above each field (keep the placeholder as an example). | S | high | verified (code) |
| 5.3 | **Province scenario goes stale and fails together.** After the first result the "What if I had bought…" button is gone, so changing the amount at the top leaves the old band on screen with no way to recompute. The band and the listing links load in one `Promise.all`, so if only the links fail, the whole scenario shows "couldn't be calculated". | The reader sees money values for an amount that is no longer on screen, and an unrelated failure hides the answer. | Recompute when the amount changes (or keep a "Recalculate" button); load the links separately and let them fail quietly. | S | high | verified (code) |
| 5.4 | The area table's error is text only ("try again shortly"), with no button. The EN text says "Province data" to US readers (their areas are states); `areaWord` variants exist for other strings but not this one. | A dead end on the page's first block, and a Turkish concept shown to US readers. | "Try again" that re-runs `load`; `explore.dataError_${areaWord}`. | S | medium | verified (code + strings) |
| 5.5 | Typing income in rent-or-buy silently saves it to the profile (`PATCH /users/me/income`). The placeholder says only "optional — checks affordability". | Saving a money figure the reader did not knowingly hand over breaks trust, and the field never shows again afterwards. | Say so in the label ("we'll remember this for next time"), or ask before saving. | S | medium | verified (code + strings) |
| 5.6 | Raw numbers: `vsCompare.realReturn` prints the server's 2-decimal value with a dot and no sign ("12.34% after inflation" in TR/DE); `population.workingAge` and the rent-or-buy assumptions/loan rate are raw too. | Wrong decimal mark in TR/DE, false precision, and a loss doesn't read as a loss. | `signedPercent()` / `percent()` with one decimal. | S | medium | verified (code + backend rounding) |
| 5.7 | Unexplained terms: "10th percentile" in the worst-band label, "gross / net rental yield", "dividend yield", "nominal". The yield strip shows before the reader does anything. | The card meant to stop "rent is free money" uses the words a beginner doesn't know. | Işık Tut on each (once per page); "one of the worst windows" alone is enough without the percentile. | S | medium | verified (strings) |
| 5.8 | The rent-or-buy assumptions are one ~110-word paragraph at 12px faded text, and it holds the numbers the verdict depends on (growth rates, fees, upkeep). | The verdict is read, the reasons behind it are not. | Short list under a "What we assumed" fold; the inflation/stale note stays visible. | S | medium | verified (code + strings) |
| 5.9 | "Background" section is always rendered, but `PopulationTrend` returns nothing for the US (`population_source="none"`), so US readers open an empty section. | An empty drawer reads as broken (as 4.10). | Hide the section when the market has no population source. | S | medium | verified (code) |
| 5.10 | No `role="alert"` on the scenario, rent-or-buy and listing-links errors (ListingEval and PropertyVsPortfolio have it); results appear with no live region. | Screen-reader users don't hear failures or answers. | `role="alert"`; `aria-live` on result blocks. | S | medium | verified (code) |
| 5.11 | Listing links: the standalone form defaults to "land" (`arsa`) while the scenario defaults to "flat"; no loading state, button not disabled while fetching; the link buttons sit in one row without wrap, and German labels ("Inserate auf ImmobilienScout24 →") are long. | A home-seeker gets land-plot links by default; at 375px the buttons can clip. | Default to flat; disable while loading; `flexWrap: 'wrap'`. | S | medium | verified (defaults) / suspected (layout) |
| 5.12 | Horizon buttons (1/3/5 years) have no `aria-pressed` (PropertyVsPortfolio's period buttons do); an opened ProvinceCard keeps `aria-expanded` with no role. | Screen readers can't tell which window is selected. | `aria-pressed`; drop `aria-expanded` once open, or move it to a real button. | S | low | verified (code) |
| 5.13 | Dates shown as the server sends them: `typical.as_of`, `data_through`, `inflation_as_of` (also in the stale-inflation warning). | As 4.18. | Market date format. | S | low | suspected |
| 5.14 | Rent-or-buy result is two columns at every width: at 375px each is ~135px with 17px bold totals. | Large lira totals may wrap mid-number. | One column below ~400px. | S | low | suspected (layout) |
| 5.15 | Colours outside tokens: rank badge `rgba(74,222,128,…)` / `rgba(248,113,113,…)`; green fallbacks disagree (`#4ade80` vs `#3DD68C`). | Drifts from the palette. | `withAlpha(var(--green|--red))`; drop fallbacks. | S | low | verified (code) |

**Fix on sight, not done this time** (held): text faded with `opacity` in all six components (ExplorePage
most of all, also PropertyVsPortfolio, PurchaseChecks, ListingEval, PopulationTrend, HomeRoutes). No
colour-plus-alpha strings found.

**Checked and fine:** amounts use the market's formatter (no TL for Texas); area search folds case in the
market's locale; ranks are only shown where areas are real alternatives (not Germany); the example amount
starts at a typical home for the market; purchase checks, home routes and population data are fetched per
market and hidden when absent; the scenario band is past windows with its honesty note; property vs
portfolio is backward-looking and itemises the costs only property pays, with net (not gross) rent; the
listing check refuses on index-only markets and keeps the caveat beside the verdict; rent-or-buy verdicts
are worded "on these assumptions … looks about X better" and keep the emotional card; "I bought this" only
prefills Holdings, it saves nothing.

**Deferred AssetCard patterns in batch 5:** #5 — results (scenario band, rent-or-buy, comparison,
listing check) appear below the form without moving focus. #8 — "real", "10th percentile", "yield".

### Batch 6 — what you own, account and plans (audited 2026-11-26, `/admin` skipped)

Read from code; these screens need a signed-in account, so nothing here was measured in the
browser. Contrast is computed from the tokens (with the new `--text-dim`, so it is not re-reported).

| # | Issue | Why it matters for a beginner | Fix | Effort | Sev | Evidence |
|---|---|---|---|---|---|---|
| 6.1 | **Possible double subscription.** PlansPage decides "already paying" from `/billing/me`, whose failure is swallowed (`.catch(() => {})`). If it fails, `current` falls back to `free`, `blocked` is false, and a paying web subscriber sees "Choose" on Plus/Pro, which opens a second Lemon Squeezy checkout. | Being charged twice for the same thing is the fastest way to lose a nervous person's trust, and refunds land on the owner. | Show no buy button until `mine` has loaded; on failure show `plans.loadError` with a retry instead of the buttons. | S | high | **fixed 2026-11-26** — server 409 already blocked a second *web* checkout; the App Store path had no server check, so the page now offers no purchase (and marks no plan current) until `/billing/me` has loaded; failure shows `plans.mineError` + Try again |
| 6.2 | **First-purchase explainer never appears.** `FirstPurchaseEducation` is rendered inside the "How it is doing" `Section`, which is `collapsible defaultOpen={false}`, so after the first holding of a type is added the card mounts into a closed section below the list. The code comment says "right after the add, above the list". | The "what have I just done" moment the feature exists for passes with nothing shown. | Render it directly above the holdings list (outside the collapsible) and move focus to its title when it appears. | S | high | **fixed 2026-11-26** — moved above the holdings list, focus moves to its title |
| 6.3 | **Holdings form fields have no labels**, only placeholders (type, symbol, quantity, name, purchase amount, current value). Once filled, "purchase amount" and "current value" — two number fields one under the other — cannot be told apart; a listing hand-off (`prefillHolding`) opens the form already filled, i.e. numbers with no labels at all. | This is where a beginner types real money amounts; mixing up "what I paid" and "what it is worth" silently corrupts every gain/loss figure after it. | A visible `<label>` above each field (placeholder text moves into the label); `inputMode="decimal"` on the money fields. | S | high | **fixed 2026-11-26** — visible `<label>` on type, symbol, quantity, name, purchase amount, current value; `inputMode="decimal"` on number fields |
| 6.4 | **Currency card recommends.** At ≥80% home currency it shows a red "Risk: High" badge and says "Consider adding foreign-currency assets" (`fx.highMsg`, all 3 locales) — the same rule for a German reader holding euros. | "Describe, never recommend": a direct portfolio instruction, in red, triggered by an ordinary position. | Owner/copy decision (as 1.18): describe the exposure and what would move it; drop "Consider…". "Concentrated" should not be `--red`. | S | high | verified (copy + code) |
| 6.5 | Holdings load failure with no cache: `loaded` never becomes true on error, so the loading spinner stays forever and the error line appears further down, under the add button. With a cache, stale numbers show with that error far below and nothing says they are old. | An endless spinner reads as "my money is gone"; stale values read as current. | `setLoaded(true)` in the catch; error + Retry in place of the spinner; with cached data, "showing your last saved values". | S | med | verified (code: HoldingsPage.jsx:84–97, 352) |
| 6.6 | Deleting a holding: `remove()` has no try/catch — a failed delete is an unhandled rejection, no message, the row just stays. Tapping ✕ swaps in a new "confirm" button, so focus drops to `<body>`; the 4s revert is silent for screen readers. | A tap that seems to do nothing makes people tap again or assume the app is broken. | try/catch → error line (new `holdings.deleteError`); `autoFocus` on the confirm button; `aria-live="polite"`. **Same pattern as AssetCard #5.** | S | med | verified (code) |
| 6.7 | Text dimmed with `opacity` instead of a token: holding row meta (12px, 0.7) **3.5:1**; "live / index estimate" tag (10px, 0.6×0.7) **2.0:1**; `liveHint` (10px, 0.55×0.7) **1.9:1**; PathSwitcher description 3.8:1, note 3.2:1; FirstPurchaseEducation subtitle 4.2:1. 10px is also below `--t-micro`. **Cross-batch:** the token raise does not reach these. | Whether a value is a live price or your own estimate is what tells a beginner how far to trust it — and it is the least readable text on the row. | No `opacity` on text; `--text-muted` or `--text-dim` and `--t-micro`. Grep `opacity: 0.[4-8]` on text in each batch. | S | med | **fixed 2026-11-26** — HoldingsPage, FirstPurchaseEducation, PathSwitcher, DeleteAccount; tags at `--t-micro` |
| 6.8 | `holdings.liveHint` says "(add quantity or purchase date for live tracking)", but the form has no purchase-date field and a saved holding cannot be edited (rows only have delete). | The app asks for something the reader cannot do. | Drop "or purchase date" and say "delete and re-add with a quantity" — or add an edit action (M). | S / M | med | verified (code + copy) |
| 6.9 | Form numbers are unformatted: `computedNote` shows raw `{{quantity}} × {{price}} = {{total}}` (e.g. `12345.68`); `lookupPrice`/`lookupConverted` show a raw price and ISO code (`1234.5 TRY`). Everywhere else uses `money()`. | A TR/DE reader expects a decimal comma; "1.250" vs "1,250" is a thousand-fold misread on the field that sets the purchase amount. | Format with `money()` / `Intl.NumberFormat` before `t()`. | S | med | **fixed 2026-11-26** — 2-decimal market-locale formatter (`money()` rounds to whole units, wrong for a unit price) |
| 6.10 | Delete-account confirm input has no `className="input"` (and no global `input` rule), so it renders as the browser's default light ~13px field on the dark card; iOS Safari zooms when a field under 16px gets focus. | The last screen before an irreversible step looks broken and jumps. | `className="input"`. | S | med | verified (code); iOS zoom suspected |
| 6.11 | Account deletion reports a partial delete and a still-active App Store subscription with two consecutive `window.alert`s: browser chrome ("… says"), untranslated OK, the second easy to dismiss unread. | The subscription warning is the one that costs money if missed. | One in-app message listing both, shown before `signOut`, with one "OK, sign me out". | S | med | verified (code) |
| 6.12 | After web checkout (`?paid=1`) the plan is re-read 6× over 18s, then polling stops silently; a slower webhook leaves "Thanks, switches on within a few seconds" above "Free — current". | Paid, and the screen says free. | After the last try, a "still confirming — refresh in a minute" line and a Refresh button. | S | low | verified (code) |
| 6.13 | Currency badge background is `` `${riskColor}18` `` with `var(--red)` → `var(--red)18`, invalid CSS, no tint (AssetCard #1 bug class). A holding without `current_value` falls back to `purchase_amount`, which may be in `h.currency`, and is summed as home currency. | The percentages are the card's whole point. | `color-mix(in srgb, … 10%, transparent)`; convert or skip the fallback. | S | low | **fixed 2026-11-26** — badge uses `withAlpha` (all 8 colour+hex-alpha sites app-wide replaced). Mixing: **not a bug** — `holdings_valuation.py` converts every foreign holding, fallback included, to the reader's currency (0 if the rate is unknown); checked live with USD cash. That live check found a real one, fixed: `getCurrency` counted cash/property/vehicles as home currency whatever `h.currency` said, so dollar cash read as lira (test in `utils/holdingCurrency.test.js`) |
| 6.14 | PortfolioValueChart: first load without cache shows only the title and range buttons (no spinner/text); error line has no retry; range buttons lack `aria-pressed`; hex colours instead of `--green`/`--red`. | A card with buttons and nothing else looks broken. | `role="status"` loading line, Retry, `aria-pressed`, tokens. | S | low | verified (code) |
| 6.15 | FirstPurchaseEducation ✕ is ~26px and its title starts with 🎉; PathSwitcher uses emoji (🏦 🏘️ ⚖️ 🤷) instead of the `Icon` set and shows nothing as current, with no message, if `getMe` fails; CurrencyExposure title uses 💱. | 🤷 beside "undecided" reads as flippant to someone anxious about the choice; small target. | 48px hit area; `Icon` glyphs; one-line load error. | S | low | verified (code) |
| 6.16 | Compact "Delete account" link (onboarding variant) is 12px with `padding:0` (~16px tall). | Hard to hit; reachability is a store requirement. | `padding: 14px 12px; min-height: 44px`, as the landing legal links. | S | low | verified (code) |
| 6.17 | Idle-cash card uses a red border and droplet for "your money is melting", shown to anyone holding cash. Empty-holdings glow uses an inline `pulse` animation outside `prefers-reduced-motion` (as 1.16). | Red framing for an ordinary cash buffer is the fear the product promises to remove. | Neutral border, keep the arithmetic; add the glow to the reduced-motion block. | S | low | verified (code); tone is a judgement |
| 6.18 | Copy, owner's call (with 1.18): `plans.sameAdvice` says "Recommendations, calculations and every figure are the same for everyone"; `rebuildCta` "Update my portfolio with the remaining …" leads to `/recommend`. | "Recommendations" restates the word the app avoids. | e.g. "Examples, calculations and every figure…". | S | low | verified (copy) |

**Checked and fine:** holdings delete asks once (4s confirm); every `.btn` is 48px (`min-height:
var(--touch-target)`), so ✕, range and lookup buttons meet the target; gain/loss shows ▲/▼ as well as
colour; the drift card says "no need to rush" and never says buy or sell (backend `drift.*`); account
deletion needs a typed word, links to Privacy, warns about App Store billing and clears local caches;
Plans says before any price that a paid plan changes only the AI advisor and uses
`role="status"`/`role="alert"`; PathSwitcher uses `aria-pressed` and rolls back on failure.

**Deferred AssetCard patterns in batch 6:** #5 focus / live region — holding ✕ ↔ confirm swap (6.6),
FirstPurchaseEducation appearing/closing (6.2, 6.15), delete-account panel opening without moving
focus, Plans buy-button spinner with no label. #8 jargon — "drift", "index estimate", "remaining
budget", "home vs foreign currency", the health notes; none has Işık Tut. The drift card's plain
line ("prices move at different speeds") is the model to copy.
