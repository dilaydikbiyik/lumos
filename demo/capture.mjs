/**
 * Professional app-flow captures for README / LinkedIn.
 *
 * The UI language is set explicitly (LANG_UI, default "en") rather than left
 * to the browser, because every selector below is text — the shots and the
 * script that finds them have to agree on one language.
 *
 * Usage: CLERK_SECRET_KEY=... DEMO_USER_ID=... [LANG_UI=en] node demo/capture.mjs
 * Outputs: demo/screens/*.png (iPhone 3x + one desktop),
 *          demo/video/lumos-demo.{mp4,gif} (converted from the raw recording)
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
  },
  tr: {
    allocation: 'Portföyün Hazır', rentVsBuy: 'Kirada mı otur', ifBuy: 'Ev alırsan',
    loanCost: 'Kredinin maliyeti', compare: 'Karşılaştır',
    downPayment: 'Peşinat', currentRent: 'kiran', homePrice: 'Evin fiyatı',
    allMyCash: 'elimdeki tüm nakit',
    debtFirst: 'Önce şunu konuşalım', holdings: 'Varlıklarım',
    dashboard: 'Kontrol Paneli', askAdvisor: 'Danışmana sor',
    chatPlaceholder: 'Bir şey sor', question: 'ETF nedir, kısaca anlatır mısın?',
  },
}
const T = COPY[LANG] || COPY.en
if (!SECRET || !DEMO_USER) throw new Error('CLERK_SECRET_KEY and DEMO_USER_ID env required')

mkdirSync('demo/screens', { recursive: true })
mkdirSync('demo/video', { recursive: true })

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
  await page.screenshot({ path: `demo/screens/${name}.png`, fullPage })
  console.log('✓', name)
}

const browser = await chromium.launch()

// ── Mobile stills ────────────────────────────────────────────────────────────
{
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
    await page.screenshot({ path: 'demo/screens/04-kira-vs-ev.png' })
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
      await page.screenshot({ path: 'demo/screens/11-borc-once.png' })
      console.log('✓ 11-borc-once')
    } finally {
      await setDebt(null)
    }
  } catch (e) { console.log('  … debt card skipped:', e.message.slice(0, 80)) }

  await shoot(page, '/holdings', '05-varliklarim', { settle: 7000, expect: T.holdings })
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
    await page.screenshot({ path: 'demo/screens/08-danisman.png' })
    console.log('✓ 08-danisman')
  } catch (e) { console.log('  … advisor skipped:', e.message) }
  await ctx.close()
}

// ── Desktop hero ─────────────────────────────────────────────────────────────
{
  const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 2 })
  const page = await ctx.newPage()
  await signIn(page)
  await shoot(page, '/dashboard', '09-desktop-panel', { settle: 6000, expect: T.dashboard })
  await shoot(page, '/recommend', '10-desktop-portfoy', { settle: 6000, expect: T.allocation })
  await ctx.close()
}

// ── Demo video (mobile tour) ─────────────────────────────────────────────────
{
  const ctx = await browser.newContext({
    ...iphone,
    deviceScaleFactor: 2,
    recordVideo: { dir: 'demo/video', size: { width: 390, height: 844 } },
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
  await tour('/dashboard', 6000)
  await ctx.close()
  console.log('✓ video recorded')
}

await browser.close()

// ── webm → mp4 + gif ─────────────────────────────────────────────────────────
// Playwright only emits webm, which neither LinkedIn nor GitHub renders inline.
// Bundled ffmpeg binary, so regenerating assets needs no system install.
{
  const raw = readdirSync('demo/video').filter(f => f.endsWith('.webm')).pop()
  if (!raw) {
    console.log('  … no webm found, conversion skipped')
  } else {
    const src = `demo/video/${raw}`
    const run = args => execFileSync(ffmpeg, ['-y', '-v', 'error', ...args], { stdio: 'inherit' })

    run(['-i', src, '-movflags', '+faststart', '-pix_fmt', 'yuv420p',
         '-vf', 'scale=780:-2:flags=lanczos', '-c:v', 'libx264',
         '-preset', 'slow', '-crf', '23', '-an', 'demo/video/lumos-demo.mp4'])
    console.log('✓ lumos-demo.mp4')

    // Two-pass palette keeps gradients from banding. 1.35x because nobody
    // watches a minute-long gif, and it halves the file.
    const gifChain = 'setpts=PTS/1.35,fps=9,scale=300:-1:flags=lanczos'
    run(['-i', src, '-vf', `${gifChain},palettegen=max_colors=96`, 'demo/video/palette.png'])
    run(['-i', src, '-i', 'demo/video/palette.png',
         '-lavfi', `${gifChain}[x];[x][1:v]paletteuse=dither=bayer:bayer_scale=4`,
         'demo/video/lumos-demo.gif'])
    unlinkSync('demo/video/palette.png')
    unlinkSync(src)   // raw recording is an intermediate, not an asset
    console.log('✓ lumos-demo.gif')
  }
}

console.log(`DONE (language: ${LANG})`)
