/**
 * Professional app-flow captures for README / LinkedIn.
 *
 * The UI language is set explicitly (LANG_UI, default "en") rather than left
 * to the browser, because every selector below is text — the shots and the
 * script that finds them have to agree on one language.
 *
 * Usage: CLERK_SECRET_KEY=... DEMO_USER_ID=... [LANG_UI=en] node demo/capture.mjs
 * Outputs: demo/screens/<lang>/*.png (iPhone 3x + one desktop),
 *          demo/video/<lang>/lumos-demo.{mp4,gif} (from the raw recording)
 */
import { mkdirSync, readdirSync, unlinkSync } from 'fs'
import { execFileSync } from 'child_process'
import { createRequire } from 'module'

// Both tools are devDependencies of the frontend package; resolve from there so
// this script needs no node_modules of its own at the repo root.
const req = createRequire(new URL('../frontend/package.json', import.meta.url))
const { chromium, devices } = req('playwright')
const ffmpeg = req('ffmpeg-static')

const APP = 'https://lumos-sooty.vercel.app'
const API = 'https://lumos-api-yowm.onrender.com'
const PORTAL = 'https://peaceful-drake-17.accounts.dev'
const CLERK = 'https://api.clerk.com/v1'
const SECRET = process.env.CLERK_SECRET_KEY
const DEMO_USER = process.env.DEMO_USER_ID
const LANG = process.env.LANG_UI || 'en'
// The gallery and the store listing want different pictures: the gallery
// wants whatever frames a feature best, the stores want exact canvas sizes
// and reject anything else. Off by default so a normal run stays quick.
const STORE = !!process.env.STORE

// Every string the script looks for, per language. Adding a language here is
// what it takes to capture the app in it.
const COPY = {
  en: {
    allocation: 'Your Portfolio Is Ready', rentVsBuy: 'Rent, or buy?', ifBuy: 'If you buy',
    loanCost: 'What the loan costs', compare: 'Compare',
    downPayment: 'Down payment', currentRent: 'current monthly rent',
    homePrice: "home's price", allMyCash: 'all my cash',
    debtFirst: 'talk about this first', holdings: 'My Assets',
    dashboard: 'Dashboard', askAdvisor: 'Ask the advisor',
    chatPlaceholder: 'Ask anything', question: 'What is an ETF, briefly?',
    selectMarket: 'Select market', explore: 'Explore',
    practice: 'Try It With Play Money First', timeMachine: 'Time Machine',
    scenarios: 'Future Scenarios', whatIf: 'What would happen?',
    goal: 'My Goal', fx: 'Currency Split', rationale: 'Why this split?',
    testLayer: 'Stress-test this portfolio', showDetails: 'Show details',
  },
  tr: {
    allocation: 'Portföyün Hazır', rentVsBuy: 'Kirada mı otur', ifBuy: 'Ev alırsan',
    loanCost: 'Kredinin maliyeti', compare: 'Karşılaştır',
    downPayment: 'Peşinat', currentRent: 'kiran', homePrice: 'Evin fiyatı',
    allMyCash: 'elimdeki tüm nakit',
    debtFirst: 'Önce şunu konuşalım', holdings: 'Varlıklarım',
    dashboard: 'Kontrol Paneli', askAdvisor: 'Danışmana sor',
    chatPlaceholder: 'Bir şey sor', question: 'ETF nedir, kısaca anlatır mısın?',
    selectMarket: 'Pazar seç', explore: 'Keşfet',
    practice: 'Önce Sahte Parayla Dene', timeMachine: 'Zaman Makinesi',
    scenarios: 'Gelecek Senaryoları', whatIf: 'Ne olurdu?',
    goal: 'Hedefim', fx: 'Kur Dağılımı', rationale: 'Neden bu dağılım?',
    testLayer: 'Bu portföyü sına', showDetails: 'Detayları Göster',
  },
  // Every needle below was read out of frontend/src/locales/de.json rather
  // than translated by hand — a guessed string fails silently as a skipped
  // screenshot, and the gallery then quietly misses a panel.
  de: {
    allocation: 'Dein Portfolio ist fertig', rentVsBuy: 'Mieten oder kaufen?',
    ifBuy: 'Wenn du kaufst', loanCost: 'Was der Kredit kostet',
    compare: 'Vergleichen', downPayment: 'Eigenkapital',
    currentRent: 'aktuelle Monatsmiete', homePrice: 'Preis der Immobilie',
    allMyCash: 'gesamtes Bargeld',
    debtFirst: 'zuerst darüber sprechen', holdings: 'Mein Vermögen',
    dashboard: 'Übersicht', askAdvisor: 'Den Berater fragen',
    chatPlaceholder: 'Frag etwas', question: 'Was ist ein ETF, kurz erklärt?',
    selectMarket: 'Markt wählen', explore: 'Entdecken',
    practice: 'Probier es erst mit Spielgeld', timeMachine: 'Zeitmaschine',
    scenarios: 'Zukunftsszenarien', whatIf: 'Was würde passieren?',
    goal: 'Mein Ziel', fx: 'Währungsaufteilung', rationale: 'Warum diese Aufteilung?',
    testLayer: 'Dieses Portfolio auf die Probe stellen', showDetails: 'Details anzeigen',
  },
}
const T = COPY[LANG] || COPY.en
if (!SECRET || !DEMO_USER) throw new Error('CLERK_SECRET_KEY and DEMO_USER_ID env required')

// Screens and video are per-LANGUAGE artifacts. They used to share one flat
// directory, so capturing German overwrote English and the repo could only
// ever show whichever UI ran last — which is exactly the claim the gallery
// is supposed to disprove.
const SCREENS = `demo/screens/${LANG}`
const VIDEO = `demo/video/${LANG}`
mkdirSync(SCREENS, { recursive: true })
mkdirSync(VIDEO, { recursive: true })
if (STORE) mkdirSync(`${SCREENS}/store`, { recursive: true })

// Sign-in tokens are single-use — mint a fresh one per browser context.
async function freshTicket() {
  const res = await fetch(`${CLERK}/sign_in_tokens`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${SECRET}`, 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_id: DEMO_USER, expires_in_seconds: 600 }),
  })
  const j = await res.json()
  if (!j.token) throw new Error('ticket mint failed: ' + JSON.stringify(j).slice(0, 200))
  return j.token
}

const iphone = {
  viewport: { width: 390, height: 844 },
  deviceScaleFactor: 3,
  isMobile: true,
  hasTouch: true,
  userAgent: devices['iPhone 13'].userAgent,
}

async function isSignedIn(page) {
  try { return await page.evaluate(() => !!(window.Clerk && window.Clerk.user)) }
  catch { return false }
}

async function signIn(page) {
  // Clerk's dev instance rate-limits back-to-back sign-ins, so a context can
  // land signed-out — retry the whole ticket→cookie→app dance a few times.
  for (let attempt = 1; attempt <= 4; attempt++) {
    const ticket = await freshTicket()
    await page.goto(`${PORTAL}/sign-in?__clerk_ticket=${ticket}`)
    await page.waitForTimeout(6000)
    const db = (await page.context().cookies(PORTAL)).find(c => c.name === '__clerk_db_jwt')
    if (db) {
      await page.goto(`${APP}/?__clerk_db_jwt=${db.value}`)
      for (let i = 0; i < 12; i++) {
        if (await isSignedIn(page)) {
          await page.evaluate(([lang]) => {
            localStorage.setItem('lumos-disclaimer-ok', '1')
            // Language is a device preference, so it is set the way a reader
            // would set it rather than by faking an Accept-Language header.
            localStorage.setItem('lumos-language', lang)
          }, [LANG])
          await page.goto(`${APP}/`)
          await page.waitForTimeout(2500)
          return
        }
        await page.waitForTimeout(1500)
      }
    }
    console.log(`  … sign-in attempt ${attempt} failed, retrying`)
    await page.waitForTimeout(8000)  // let the rate-limit window pass
  }
  throw new Error('sign-in did not restore a Clerk session after retries')
}

/** Poll until a piece of real content appears — pages that wait on the API
    (and an AI explanation) rendered blank when we shot them on a timer. */
async function waitForText(page, needle, maxSeconds = 60) {
  for (let i = 0; i < maxSeconds; i++) {
    let t = ''
    try { t = await page.evaluate(() => document.body.innerText) } catch { /* navigating */ }
    if (t.includes(needle)) return true
    await page.waitForTimeout(1000)
  }
  return false
}

async function shoot(page, path, name, { settle = 3500, fullPage = false, expect = null } = {}) {
  await page.goto(`${APP}${path}`)
  if (expect) {
    const ok = await waitForText(page, expect)
    if (!ok) console.log('  … content never arrived:', name)
  }
  await page.waitForTimeout(settle)
  await page.evaluate(() => window.scrollTo(0, 0))
  await page.waitForTimeout(800)
  await page.screenshot({ path: `${SCREENS}/${name}.png`, fullPage })
  console.log('✓', name)
}

// Frame ONE feature card by its own heading. Scroll offsets were the old way
// and they rot: a card that grows by a line slides out of frame silently and
// the gallery ends up showing half a component. A heading is stable.
async function shootCard(page, path, heading, name, { settle = 6000, anchor = null, open = null } = {}) {
  try {
    if (page.url().replace(APP, '').split('?')[0] !== path) {
      await page.goto(`${APP}${path}`)
      // A fixed wait is a guess, and on a free-tier instance it is usually
      // the wrong one: /recommend needed seven seconds on a warm cache and
      // rather more on a cold one, so every card below it was missed. Poll
      // for content the way the full-page shots already did.
      if (anchor) await waitForText(page, anchor)
      await page.waitForTimeout(settle)
    }
    // Several of these cards live inside a collapsed section. They were not
    // missing from the gallery because the selector was wrong — they were
    // never on screen, because nobody had opened the drawer.
    if (open) {
      const toggle = page.locator(`text=${open}`).first()
      if (await toggle.count()) {
        await toggle.click()
        await page.waitForTimeout(2500)
      }
    }
    const card = page.locator(`text=${heading}`).first()
    await card.scrollIntoViewIfNeeded({ timeout: 20000 })
    await page.evaluate(() => window.scrollBy(0, -80))
    await page.waitForTimeout(1500)
    await page.screenshot({ path: `${SCREENS}/${name}.png` })
    console.log(`\u2713 ${name}`)
  } catch (e) { console.log(`  … ${name} skipped:`, e.message.slice(0, 90)) }
}

const browser = await chromium.launch()

// ── Mobile stills ────────────────────────────────────────────────────────────
if (!STORE) {
  const ctx = await browser.newContext(iphone)
  const page = await ctx.newPage()
  await signIn(page)

  await shoot(page, '/', '01-karsilama')
  await shoot(page, '/profile', '02-risk-profili', { settle: 6000 })
  await shoot(page, '/recommend', '03-portfoy', { settle: 6000, expect: T.allocation })
  // Real-estate decision tool: the rent-vs-buy scenario with real numbers
  try {
    await page.goto(`${APP}/explore`)
    await waitForText(page, T.rentVsBuy)
    await page.locator(`input[placeholder*="${T.downPayment}"]`).fill('2.000.000')
    await page.locator(`input[placeholder*="${T.currentRent}"]`).fill('35.000')
    await page.locator(`input[placeholder*="${T.homePrice}"]`).fill('6.000.000')
    // "All my cash" — the fees come out of it, which is the number first-time
    // buyers forget. Worth showing, since it changes the answer.
    await page.locator(`text=${T.allMyCash}`).click()
    await page.getByRole('button', { name: T.compare }).click()
    await waitForText(page, T.ifBuy)
    await page.waitForTimeout(2500)
    // Frame the RESULT, not the form: the loan-cost card and the verdict are
    // the point, and they now sit below where the old shot was cropped.
    await page.locator(`text=${T.loanCost}`).scrollIntoViewIfNeeded()
    await page.waitForTimeout(1000)
    await page.screenshot({ path: `${SCREENS}/04-kira-vs-ev.png` })
    console.log('✓ 04-kira-vs-ev')
  } catch (e) { console.log('  … rent-vs-buy skipped:', e.message.slice(0, 80)) }
  // "Clear your debt first" — only renders for a profile that reports debt, so
  // set it on the demo account, shoot, and put it back. Restored in a finally
  // block: leaving the demo user in a debt state would poison every later run.
  try {
    const setDebt = amount => page.evaluate(async ([api, debt]) => {
      const token = await window.Clerk.session.getToken()
      const headers = { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' }
      const current = await (await fetch(`${api}/profile`, { headers })).json()
      await fetch(`${api}/profile`, {
        method: 'POST', headers,
        body: JSON.stringify({ ...current.answers, high_interest_debt: debt }),
      })
    }, [API, amount])

    try {
      await setDebt(45000)
      await page.goto(`${APP}/profile`)
      await waitForText(page, T.debtFirst)
      await page.waitForTimeout(4000)
      // Don't shoot from the top: the conclusion — repayment wins by X — is the
      // last line of the card and was hiding behind the bottom nav.
      await page.evaluate(() => window.scrollBy(0, 430))
      await page.waitForTimeout(1000)
      await page.screenshot({ path: `${SCREENS}/11-borc-once.png` })
      console.log('✓ 11-borc-once')
    } finally {
      await setDebt(null)
    }
  } catch (e) { console.log('  … debt card skipped:', e.message.slice(0, 80)) }

  // ── The three markets ────────────────────────────────────────────────────
  // The claim this project makes is that market and language are independent
  // axes: the SAME English UI prices Türkiye in lira, the US in dollars and
  // Germany in euros, off each country's own official data. A screenshot of
  // one market cannot show that, so shoot all three from the same session —
  // and switch through the visible selector rather than the API, because the
  // switcher is itself part of what is being demonstrated.
  const chooseMarket = async (code) => {
    await page.locator(`select[aria-label="${T.selectMarket}"]`).first().selectOption(code)
    await page.waitForTimeout(3000)
  }
  try {
    for (const [code, name] of [['US', 'abd'], ['DE', 'almanya']]) {
      await page.goto(`${APP}/explore`)
      await page.waitForTimeout(3000)
      await chooseMarket(code)
      await page.reload()
      // The regional table is the slowest thing on the page — 51 FRED series
      // on a cold cache — so give it room rather than shooting a spinner.
      await page.waitForTimeout(9000)
      await page.screenshot({ path: `${SCREENS}/12-pazar-${name}.png` })
      console.log(`\u2713 12-pazar-${name}`)
    }
  } catch (e) { console.log('  … market tour skipped:', e.message.slice(0, 80)) }
  finally {
    // Never leave the demo account parked in another market: every later
    // screenshot in every later run would silently be in the wrong currency.
    try { await chooseMarket('TR') } catch { /* best effort */ }
  }

  // ── The features that live below the fold ────────────────────────────────
  // Each of these is a distinct answer to a beginner's distinct fear, and all
  // of them were invisible in a gallery that only ever shot the top of a page.
  await shootCard(page, '/recommend', T.rationale, '13-neden-bu-dagilim', { anchor: T.allocation })
  // These four sit behind the "stress-test" drawer; it only has to be opened
  // once, and it stays open for the rest of them.
  await shootCard(page, '/recommend', T.practice, '14-sahte-para', { open: T.testLayer })
  await shootCard(page, '/recommend', T.timeMachine, '15-zaman-makinesi')
  await shootCard(page, '/recommend', T.scenarios, '16-senaryolar')
  await shootCard(page, '/recommend', T.whatIf, '17-ne-olurdu')
  await shootCard(page, '/dashboard', T.goal, '18-hedef',
                  { anchor: T.dashboard, open: T.showDetails })

  await shoot(page, '/holdings', '05-varliklarim', { settle: 7000, expect: T.holdings })
  await shootCard(page, '/holdings', T.fx, '19-kur-dagilimi', { anchor: T.holdings })
  await shoot(page, '/dashboard', '06-panel', { settle: 6000, expect: T.dashboard })
  await shoot(page, '/explore', '07-emlak-kesfet', { settle: 7000 })

  // advisor chat with a real AI answer
  try {
    await page.goto(`${APP}/dashboard`)
    await page.waitForTimeout(4000)
    await page.getByLabel(T.askAdvisor).click()
    await page.waitForTimeout(1000)
    await page.getByPlaceholder(new RegExp(T.chatPlaceholder)).fill(T.question)
    await page.keyboard.press('Enter')
    await page.waitForTimeout(15000)
    await page.screenshot({ path: `${SCREENS}/08-danisman.png` })
    console.log('✓ 08-danisman')
  } catch (e) { console.log('  … advisor skipped:', e.message) }
  await ctx.close()
}

// ── Desktop hero ─────────────────────────────────────────────────────────────
if (!STORE) {
  const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 2 })
  const page = await ctx.newPage()
  await signIn(page)
  await shoot(page, '/dashboard', '09-desktop-panel', { settle: 6000, expect: T.dashboard })
  await shoot(page, '/recommend', '10-desktop-portfoy', { settle: 6000, expect: T.allocation })
  // The desktop half of the gallery only ever showed the two stock screens,
  // which made a real-estate app look like a stock app on the web. Explore is
  // the widest page in the product and it is the one that benefits most from
  // a desktop frame.
  await shoot(page, '/explore', '20-desktop-emlak', { settle: 9000 })
  await shootCard(page, '/explore', T.rentVsBuy, '21-desktop-kira-vs-ev', { settle: 9000 })
  await ctx.close()
}

// ── Demo video (mobile tour) ─────────────────────────────────────────────────
if (!STORE) {
  const ctx = await browser.newContext({
    ...iphone,
    deviceScaleFactor: 2,
    recordVideo: { dir: VIDEO, size: { width: 390, height: 844 } },
  })
  const page = await ctx.newPage()
  await signIn(page)
  const tour = async (path, ms, scroll = true) => {
    await page.goto(`${APP}${path}`)
    await page.waitForTimeout(ms)
    if (scroll) {
      await page.mouse.wheel(0, 600); await page.waitForTimeout(1600)
      await page.mouse.wheel(0, 700); await page.waitForTimeout(1600)
      await page.mouse.wheel(0, -1300); await page.waitForTimeout(800)
    }
  }
  await tour('/', 3000)
  await tour('/profile', 5000)
  await tour('/recommend', 10000)
  await tour('/holdings', 8000)
  // The real-estate half of the app was missing from the tour entirely, which
  // left the video showing a stock app. It is half the product.
  await tour('/explore', 9000)
  // Then switch markets on camera. This is the one thing a still cannot show:
  // the same screen, the same language, a different country's official data
  // and currency. Restored to TR at the end so the next run starts clean.
  try {
    const pick = async (code) => {
      await page.locator(`select[aria-label="${T.selectMarket}"]`).first().selectOption(code)
      await page.waitForTimeout(4500)
    }
    await pick('US')
    await page.waitForTimeout(3500)
    await page.mouse.wheel(0, 700); await page.waitForTimeout(2500)
    await pick('DE')
    await page.waitForTimeout(4500)
    await pick('TR')
  } catch (e) { console.log('  … video market switch skipped:', e.message.slice(0, 80)) }
  await tour('/dashboard', 6000)
  await ctx.close()
  console.log('✓ video recorded')
}

await browser.close()

// ── Store-listing screenshots ────────────────────────────────────────────────
// Apple and Google both reject a screenshot that is one pixel off the
// required canvas, so the sizes below are the viewport × deviceScaleFactor
// arithmetic that lands exactly on each one — not a resize after the fact,
// which would blur text at the size a reviewer actually zooms into.
if (STORE) {
  const browser2 = await chromium.launch()
  const SIZES = [
    // Apple 6.7" — iPhone 15/16 Pro Max
    { name: 'ios-6.7', width: 430, height: 932, scale: 3 },
    // Apple 6.5" — iPhone 11 Pro Max
    { name: 'ios-6.5', width: 414, height: 896, scale: 3 },
    // Google Play phone
    { name: 'play-phone', width: 360, height: 640, scale: 3 },
  ]
  // Five screens that tell the story in order: what it is, what it built you,
  // why, the real-estate half, and the data behind it.
  const SHOTS = [
    ['/', 'a-welcome', null],
    ['/recommend', 'b-portfolio', T.allocation],
    ['/explore', 'c-real-estate', null],
    ['/holdings', 'd-holdings', T.holdings],
    ['/dashboard', 'e-dashboard', T.dashboard],
  ]

  for (const size of SIZES) {
    const ctx2 = await browser2.newContext({
      viewport: { width: size.width, height: size.height },
      deviceScaleFactor: size.scale,
      isMobile: true, hasTouch: true,
      userAgent: devices['iPhone 13'].userAgent,
    })
    const p2 = await ctx2.newPage()
    await signIn(p2)
    for (const [path, label, expect] of SHOTS) {
      try {
        await p2.goto(`${APP}${path}`)
        if (expect) await waitForText(p2, expect)
        await p2.waitForTimeout(7000)
        await p2.screenshot({ path: `${SCREENS}/store/${size.name}-${label}.png` })
        console.log(`\u2713 store/${size.name}-${label}`)
      } catch (e) { console.log(`  … store/${size.name}-${label} skipped:`, e.message.slice(0, 70)) }
    }
    await ctx2.close()
  }
  await browser2.close()
}


// ── webm → mp4 + gif ─────────────────────────────────────────────────────────
// Playwright only emits webm, which neither LinkedIn nor GitHub renders inline.
// Bundled ffmpeg binary, so regenerating assets needs no system install.
if (!STORE) {
  const raw = readdirSync(VIDEO).filter(f => f.endsWith('.webm')).pop()
  if (!raw) {
    console.log('  … no webm found, conversion skipped')
  } else {
    const src = `${VIDEO}/${raw}`
    const run = args => execFileSync(ffmpeg, ['-y', '-v', 'error', ...args], { stdio: 'inherit' })

    run(['-i', src, '-movflags', '+faststart', '-pix_fmt', 'yuv420p',
         '-vf', 'scale=780:-2:flags=lanczos', '-c:v', 'libx264',
         '-preset', 'slow', '-crf', '23', '-an', `${VIDEO}/lumos-demo.mp4`])
    console.log('✓ lumos-demo.mp4')

    // Two-pass palette keeps gradients from banding. 1.35x because nobody
    // watches a minute-long gif, and it halves the file.
    const gifChain = 'setpts=PTS/1.35,fps=9,scale=300:-1:flags=lanczos'
    run(['-i', src, '-vf', `${gifChain},palettegen=max_colors=96`, `${VIDEO}/palette.png`])
    run(['-i', src, '-i', `${VIDEO}/palette.png`,
         '-lavfi', `${gifChain}[x];[x][1:v]paletteuse=dither=bayer:bayer_scale=4`,
         `${VIDEO}/lumos-demo.gif`])
    unlinkSync(`${VIDEO}/palette.png`)
    unlinkSync(src)   // raw recording is an intermediate, not an asset
    console.log('✓ lumos-demo.gif')
  }
}

console.log(`DONE (language: ${LANG})`)
