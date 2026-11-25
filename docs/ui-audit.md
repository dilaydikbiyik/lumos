# Lumos UI/UX audit

Audit only. Findings here, fixes later (high severity + effort S first, as with AssetCard).

**Scope per batch:** accessibility (contrast against the real `index.css` tokens, `:focus-visible`,
screen-reader labels, tap targets vs `--touch-target`) · mobile at 375px and the installed PWA ·
"explain before showing" (Işık Tut or a plain line for every term/number) · loading / empty /
error states · i18n tr/en/de (hardcoded strings, long German) · market-pack leaks · describe,
never recommend · reduced motion.

**Rules:** keep the "Light" design language (todo.md Phase 9: firefly motif, `index.css` tokens,
Outfit). No new style, palette or font. Each finding is **verified** (code read or measured) or
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
| 2 | Getting to know you + the app shell | `/path` (step 1), `/fear-check-in` (step 2), `/profile` risk quiz (step 3, chat + structured); shell first seen here: header, bottom nav / sidebar, market + language switchers, panic button, advisor chat, feedback | PathSelectionPage, FearCheckInPage, ProfilePage, ChatWindow, MessageBubble, StructuredQuiz, RiskGauge, DebtFirstCard · AppHeader, AppNav, MarketSwitcher, HeaderSelect, PanicButton, AdvisorChat, FeedbackButton, Section, Disclaimer | 1,890 | todo |
| 3 | Home | `/dashboard` (first tab, where a finished profile lands) | DashboardPage, ReadinessScore, PathSuggestion, PathInvitation, DailyTip, HeadlineEducation, NewsDigest, BudgetSplit, GoalPlanner, BehaviorMirror, PortfolioChart (minus AssetCard), PortfolioComparison, StocksLink | 1,730 | todo |
| 4 | Your portfolio plan | `/recommend` (allocation, why, what-if, practice), `/stocks` (asset classes) | RecommendPage, AllocationRationale, RoleAlternatives, AssetExplainer, ReitCard, ReferenceFacts, TimeMachine, AssetCharacter, IsikTut, FutureScenarios, WhatIfAssistant, PracticeMode, BoughtItBridge, BeginnerGuide, Glossary, RealEstatePathNotice · StocksPage, AssetClasses | 2,140 | todo |
| 5 | Real estate | `/explore` (property vs portfolio, purchase checks, listing evaluation, population trend, ways into a home) | ExplorePage, PropertyVsPortfolio, PurchaseChecks, ListingEval, PopulationTrend, HomeRoutes | 1,390 | todo |
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

### Batch 6 — what you own, account and plans (audited 2026-11-26, `/admin` skipped)

Read from code; these screens need a signed-in account, so nothing here was measured in the
browser. Contrast is computed from the tokens (with the new `--text-dim`, so it is not re-reported).

| # | Issue | Why it matters for a beginner | Fix | Effort | Sev | Evidence |
|---|---|---|---|---|---|---|
| 6.1 | **Possible double subscription.** PlansPage decides "already paying" from `/billing/me`, whose failure is swallowed (`.catch(() => {})`). If it fails, `current` falls back to `free`, `blocked` is false, and a paying web subscriber sees "Choose" on Plus/Pro, which opens a second Lemon Squeezy checkout. | Being charged twice for the same thing is the fastest way to lose a nervous person's trust, and refunds land on the owner. | Show no buy button until `mine` has loaded; on failure show `plans.loadError` with a retry instead of the buttons. | S | high | verified (code) |
| 6.2 | **First-purchase explainer never appears.** `FirstPurchaseEducation` is rendered inside the "How it is doing" `Section`, which is `collapsible defaultOpen={false}`, so after the first holding of a type is added the card mounts into a closed section below the list. The code comment says "right after the add, above the list". | The "what have I just done" moment the feature exists for passes with nothing shown. | Render it directly above the holdings list (outside the collapsible) and move focus to its title when it appears. | S | high | verified (code: HoldingsPage.jsx:526–562, Section.jsx) |
| 6.3 | **Holdings form fields have no labels**, only placeholders (type, symbol, quantity, name, purchase amount, current value). Once filled, "purchase amount" and "current value" — two number fields one under the other — cannot be told apart; a listing hand-off (`prefillHolding`) opens the form already filled, i.e. numbers with no labels at all. | This is where a beginner types real money amounts; mixing up "what I paid" and "what it is worth" silently corrupts every gain/loss figure after it. | A visible `<label>` above each field (placeholder text moves into the label); `inputMode="decimal"` on the money fields. | S | high | verified (code) |
| 6.4 | **Currency card recommends.** At ≥80% home currency it shows a red "Risk: High" badge and says "Consider adding foreign-currency assets" (`fx.highMsg`, all 3 locales) — the same rule for a German reader holding euros. | "Describe, never recommend": a direct portfolio instruction, in red, triggered by an ordinary position. | Owner/copy decision (as 1.18): describe the exposure and what would move it; drop "Consider…". "Concentrated" should not be `--red`. | S | high | verified (copy + code) |
| 6.5 | Holdings load failure with no cache: `loaded` never becomes true on error, so the loading spinner stays forever and the error line appears further down, under the add button. With a cache, stale numbers show with that error far below and nothing says they are old. | An endless spinner reads as "my money is gone"; stale values read as current. | `setLoaded(true)` in the catch; error + Retry in place of the spinner; with cached data, "showing your last saved values". | S | med | verified (code: HoldingsPage.jsx:84–97, 352) |
| 6.6 | Deleting a holding: `remove()` has no try/catch — a failed delete is an unhandled rejection, no message, the row just stays. Tapping ✕ swaps in a new "confirm" button, so focus drops to `<body>`; the 4s revert is silent for screen readers. | A tap that seems to do nothing makes people tap again or assume the app is broken. | try/catch → error line (new `holdings.deleteError`); `autoFocus` on the confirm button; `aria-live="polite"`. **Same pattern as AssetCard #5.** | S | med | verified (code) |
| 6.7 | Text dimmed with `opacity` instead of a token: holding row meta (12px, 0.7) **3.5:1**; "live / index estimate" tag (10px, 0.6×0.7) **2.0:1**; `liveHint` (10px, 0.55×0.7) **1.9:1**; PathSwitcher description 3.8:1, note 3.2:1; FirstPurchaseEducation subtitle 4.2:1. 10px is also below `--t-micro`. **Cross-batch:** the token raise does not reach these. | Whether a value is a live price or your own estimate is what tells a beginner how far to trust it — and it is the least readable text on the row. | No `opacity` on text; `--text-muted` or `--text-dim` and `--t-micro`. Grep `opacity: 0.[4-8]` on text in each batch. | S | med | verified (computed) |
| 6.8 | `holdings.liveHint` says "(add quantity or purchase date for live tracking)", but the form has no purchase-date field and a saved holding cannot be edited (rows only have delete). | The app asks for something the reader cannot do. | Drop "or purchase date" and say "delete and re-add with a quantity" — or add an edit action (M). | S / M | med | verified (code + copy) |
| 6.9 | Form numbers are unformatted: `computedNote` shows raw `{{quantity}} × {{price}} = {{total}}` (e.g. `12345.68`); `lookupPrice`/`lookupConverted` show a raw price and ISO code (`1234.5 TRY`). Everywhere else uses `money()`. | A TR/DE reader expects a decimal comma; "1.250" vs "1,250" is a thousand-fold misread on the field that sets the purchase amount. | Format with `money()` / `Intl.NumberFormat` before `t()`. | S | med | verified (code) |
| 6.10 | Delete-account confirm input has no `className="input"` (and no global `input` rule), so it renders as the browser's default light ~13px field on the dark card; iOS Safari zooms when a field under 16px gets focus. | The last screen before an irreversible step looks broken and jumps. | `className="input"`. | S | med | verified (code); iOS zoom suspected |
| 6.11 | Account deletion reports a partial delete and a still-active App Store subscription with two consecutive `window.alert`s: browser chrome ("… says"), untranslated OK, the second easy to dismiss unread. | The subscription warning is the one that costs money if missed. | One in-app message listing both, shown before `signOut`, with one "OK, sign me out". | S | med | verified (code) |
| 6.12 | After web checkout (`?paid=1`) the plan is re-read 6× over 18s, then polling stops silently; a slower webhook leaves "Thanks, switches on within a few seconds" above "Free — current". | Paid, and the screen says free. | After the last try, a "still confirming — refresh in a minute" line and a Refresh button. | S | low | verified (code) |
| 6.13 | Currency badge background is `` `${riskColor}18` `` with `var(--red)` → `var(--red)18`, invalid CSS, no tint (AssetCard #1 bug class). A holding without `current_value` falls back to `purchase_amount`, which may be in `h.currency`, and is summed as home currency. | The percentages are the card's whole point. | `color-mix(in srgb, … 10%, transparent)`; convert or skip the fallback. | S | low | badge verified; mixing suspected |
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
