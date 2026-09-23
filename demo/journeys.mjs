/**
 * End-to-end journey checks.
 *
 * Why this exists: every bug reported from the app so far has been a STATE
 * TRANSITION bug — the right screen for the wrong account state. A profile
 * that has not loaded yet showing the quiz. "Redo" reopening the questions
 * you already answered. Cards rendered inside a drawer that only opens once
 * you own a holding. Unit tests pass through all of those, because each
 * piece works; it is the combination that does not.
 *
 * So this walks the real app, in a browser, through the states a real
 * account actually passes through, and asserts what should be on screen in
 * each one. It talks to a LOCAL backend against a throwaway SQLite file:
 * these journeys write profiles, paths and holdings, and none of that
 * belongs in anyone's real account.
 *
 *   node demo/journeys.mjs
 *
 * Exit code is the number of failed assertions, so CI can gate on it.
 */
import { createRequire } from 'module'
const req = createRequire(new URL('../frontend/package.json', import.meta.url))
const { chromium, devices } = req('playwright')

const APP = process.env.APP_URL || 'http://localhost:5173'
const API = process.env.API_URL || 'http://localhost:8000/api/v1'
const PORTAL = 'https://peaceful-drake-17.accounts.dev'
const CLERK = 'https://api.clerk.com/v1'
const SECRET = process.env.CLERK_SECRET_KEY
const DEMO_USER = process.env.DEMO_USER_ID
const LANG = process.env.LANG_UI || 'en'

if (!SECRET || !DEMO_USER) throw new Error('CLERK_SECRET_KEY and DEMO_USER_ID required')

let failures = 0
const results = []

function check(name, condition, detail = '') {
  const ok = !!condition
  if (!ok) failures += 1
  results.push({ name, ok, detail })
  console.log(`   ${ok ? '✓' : '✗'} ${name}${ok || !detail ? '' : ` — ${detail}`}`)
}

async function ticket() {
  const res = await fetch(`${CLERK}/sign_in_tokens`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${SECRET}`, 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_id: DEMO_USER, expires_in_seconds: 900 }),
  })
  const json = await res.json()
  if (!json.token) throw new Error('ticket mint failed: ' + JSON.stringify(json).slice(0, 200))
  return json.token
}

const browser = await chromium.launch()
const ctx = await browser.newContext({
  viewport: { width: 390, height: 844 },
  isMobile: true, hasTouch: true,
  userAgent: devices['iPhone 13'].userAgent,
})
const page = await ctx.newPage()

// Surface anything the page itself complains about: a console error during a
// journey is a finding even when the assertions pass.
const consoleErrors = []
page.on('console', m => { if (m.type() === 'error') consoleErrors.push(m.text()) })
page.on('pageerror', e => consoleErrors.push(String(e)))

await page.goto(`${PORTAL}/sign-in?__clerk_ticket=${await ticket()}`)
await page.waitForTimeout(6000)
const dbCookie = (await ctx.cookies(PORTAL)).find(c => c.name === '__clerk_db_jwt')
await page.goto(`${APP}/?__clerk_db_jwt=${dbCookie.value}`)
await page.waitForTimeout(6000)
await page.evaluate(l => {
  localStorage.setItem('lumos-disclaimer-ok', '1')
  localStorage.setItem('lumos-language', l)
}, LANG)

/** Call the API as the signed-in user, from inside the page. */
const call = (path, options = {}) => page.evaluate(async ([api, p, o]) => {
  const token = await window.Clerk.session.getToken()
  const res = await fetch(`${api}${p}`, {
    ...o,
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
      'X-Lumos-Lang': document.documentElement.lang || 'en',
      ...(o.headers || {}),
    },
  })
  const text = await res.text()
  try { return { status: res.status, body: JSON.parse(text) } }
  catch { return { status: res.status, body: text } }
}, [API, path, options])

const text = () => page.evaluate(() => document.body.innerText)

/** Put the account into a known state before a journey runs. */
async function setState({ profile, path: investmentPath, clearDrafts = true }) {
  if (clearDrafts) {
    await page.evaluate(() => {
      for (const k of Object.keys(localStorage)) {
        if (k.includes('quiz-draft') || k.includes('profile')) localStorage.removeItem(k)
      }
    })
  }
  if (profile) await call('/profile', { method: 'POST', body: JSON.stringify(profile) })
  if (investmentPath) {
    await call('/users/me/investment-path', {
      method: 'PATCH', body: JSON.stringify({ investment_path: investmentPath }),
    })
  }
}

const PROFILE = {
  budget: 3000000, monthly_contribution: 20000, time_horizon: 'long',
  loss_tolerance: 'medium', goal: 'growth', experience: 'none', age: 34,
}

// ── Journey 1: a brand-new account completes the quiz with NO model calls ──
// The whole point of the restructure: nine chat calls became zero, and the
// flow every reported bug lived in no longer has a model in it.
console.log('\n1. the quiz completes without a model')
await page.evaluate(() => {
  for (const k of Object.keys(localStorage)) {
    if (k.includes('quiz-draft') || k.includes('profile')) localStorage.removeItem(k)
  }
})

const chatCalls = []
await page.route('**/chat**', route => { chatCalls.push(route.request().url()); route.continue() })

await page.goto(`${APP}/profile`)
await page.waitForTimeout(8000)

// The account may already carry a profile from an earlier run, and a journey
// that only passes against a freshly created database is a journey nobody
// will trust. If a result is on screen, take the route a real returning user
// would to reach the quiz.
if (/Redo|Yeniden|Erneut/i.test(await text())) {
  await page.getByRole('button', { name: /Redo|Yeniden|Erneut/i }).first().click()
  await page.waitForTimeout(2000)
}

// The quiz fetches its questions, so wait for one rather than sampling the
// page header while it is still loading.
for (let i = 0; i < 25; i++) {
  const body = await text()
  if (/question \d+ of|soru \d+ \/|frage \d+ von/i.test(body)) break
  await page.waitForTimeout(1000)
}
const quizText = await text()
const onQuiz = /question 1 of|soru 1 \/|frage 1 von/i.test(quizText)
check('a fresh account lands on the structured quiz', onQuiz, quizText.slice(0, 120))

if (onQuiz) {
  // Answer every step: a choice picks the first option, an amount types one.
  for (let i = 0; i < 12; i++) {
    const done = await page.evaluate(() =>
      !/question \d+ of|soru \d+ \/|frage \d+ von/i.test(document.body.innerText))
    if (done) break
    const option = page.locator('button:has(strong)').first()
    const input = page.locator('input[inputmode="numeric"]').first()
    if (await input.count()) {
      const max = await input.getAttribute('max')
      await input.fill(max ? String(Math.min(Number(max), 34)) : '100000')
      await page.getByRole('button', { name: /Next|Devam|Weiter/i }).first().click()
    } else if (await option.count()) {
      await option.click()
    }
    await page.waitForTimeout(700)
  }
  await page.waitForTimeout(6000)
  const after = await text()
  check('the quiz produced a risk profile',
    /Redo|Yeniden|Erneut/i.test(after), after.slice(0, 140))
  check('no chat call was made during the quiz',
    chatCalls.length === 0, `${chatCalls.length} call(s): ${chatCalls[0] || ''}`)
}
await page.unroute('**/chat**')

// ── Journey 2: a returning user opens their profile ─────────────────────────
// The bug this guards: the quiz rendering while the saved profile is still in
// flight, so somebody who finished it weeks ago is asked question one again.
console.log('\n2. returning user opens /profile')
await setState({ profile: PROFILE, path: 'hybrid' })
await page.goto(`${APP}/profile`)
await page.waitForTimeout(2000)
const early = await text()
check('no quiz input while the saved profile loads',
  !early.includes('Type your answer'), early.slice(0, 120))
await page.waitForTimeout(9000)
const settled = await text()
check('the saved result is shown, not the quiz',
  !settled.includes('Type your answer'), settled.slice(0, 120))
check('the path switcher is reachable', settled.includes('Your path'))

// ── Journey 3: "redo the risk analysis" starts clean ────────────────────────
// The reported bug: redo reopened the half-finished conversation, showing
// questions that had already been answered under a result computed from them.
console.log('\n3. redo the risk analysis')
await page.evaluate(() => {
  // A draft left over from a previous session, exactly as the bug had it.
  const key = Object.keys(localStorage).find(k => k.includes('quiz-draft'))
    || 'lumos-quiz-draft-seed'
  localStorage.setItem(key, JSON.stringify([
    { role: 'assistant', content: 'PREVIOUS QUESTION ONE' },
    { role: 'user', content: '30' },
  ]))
})
await page.goto(`${APP}/profile`)
await page.waitForTimeout(9000)
const retake = page.getByRole('button', { name: /Redo|Yeniden|Erneut/i }).first()
if (await retake.count()) {
  await retake.click()
  await page.waitForTimeout(2500)
  const afterRedo = await text()
  check('redo does not replay already-answered questions',
    !afterRedo.includes('PREVIOUS QUESTION ONE'), afterRedo.slice(0, 160))
} else {
  check('redo button present', false, 'not found on the result screen')
}

// ── Journey 4: a stocks-only reader never meets the property half ───────────
console.log('\n4. stocks-only path')
await setState({ path: 'stocks' })
await page.goto(`${APP}/dashboard`)
await page.waitForTimeout(8000)
const stocksNav = await page.evaluate(() =>
  [...document.querySelectorAll('nav a, nav button')].map(e => e.textContent.trim()).join('|'))
check('explore is hidden for a stocks-only reader',
  !/Explore|Keşfet|Entdecken/i.test(stocksNav), stocksNav)

// ── Journey 5: a real-estate reader is not handed a stock portfolio ─────────
console.log('\n5. real-estate path lands on /recommend')
await setState({ path: 'real_estate' })
await page.goto(`${APP}/recommend`)
await page.waitForTimeout(8000)
const reco = await text()
check('a real-estate reader gets the notice, not a forced allocation',
  /real-estate path|emlak yolunu|Immobilienweg/i.test(reco), reco.slice(0, 160))

// ── Journey 6: the planning cards are reachable without owning anything ─────
console.log('\n6. new account sees the planning cards')
await setState({ path: 'undecided' })
await page.goto(`${APP}/dashboard`)
await page.waitForTimeout(10000)
const dash = await text()
check('budget split is on the dashboard',
  /Where your budget goes|Bütçen nereye|Wohin dein Budget/i.test(dash))
check('path suggestion is on the dashboard',
  /Where to start|Nereden başlamalı|Womit anfangen/i.test(dash))

// ── Journey 7: every main route renders something ───────────────────────────
console.log('\n7. every route renders')
await setState({ path: 'hybrid' })
for (const route of ['/', '/profile', '/recommend', '/holdings', '/explore', '/dashboard']) {
  await page.goto(`${APP}${route}`)
  await page.waitForTimeout(7000)
  const body = await text()
  // The error boundary is the thing to look for FIRST. A crashed page still
  // "renders content" — it renders the fallback — and the reported symptom
  // was "the states load slowly", not "the page is broken", because a boundary
  // makes a crash look like a page that never finished.
  check(`${route} did not crash`,
    !/Something went wrong|Bir şeyler ters gitti|Etwas ist schiefgelaufen/i.test(body),
    body.trim().slice(0, 100))
  check(`${route} renders content`, body.trim().length > 120, `${body.trim().length} chars`)
  check(`${route} shows no raw i18n key`, !/\b[a-z]+\.[a-z]+\.[a-zA-Z]+\b(?!\s)/.test(
    body.split('\n').find(l => /^[a-z]+\.[a-z.]+$/.test(l.trim())) || ''))
}

// ── Journey 8: Explore in every market ──────────────────────────────────────
console.log('\n8. explore renders in every market')
for (const market of ['TR', 'US', 'DE']) {
  await call('/users/me/market', {
    method: 'PATCH', body: JSON.stringify({ market }),
  })
  await page.goto(`${APP}/explore`)
  await page.waitForTimeout(9000)
  const body = await text()
  check(`${market}: explore did not crash`,
    !/Something went wrong|Bir şeyler ters gitti|Etwas ist schiefgelaufen/i.test(body),
    body.trim().slice(0, 100))
  check(`${market}: explore says something about its data`,
    body.trim().length > 300, `${body.trim().length} chars`)
}

console.log(`\nconsole errors during the run: ${consoleErrors.length}`)
consoleErrors.slice(0, 5).forEach(e => console.log('   !', e.slice(0, 140)))

console.log(`\n${results.filter(r => r.ok).length}/${results.length} checks passed`)
await browser.close()
process.exit(failures)
