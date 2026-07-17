/**
 * Professional app-flow captures for README / LinkedIn.
 * Usage: node demo/capture.mjs   (expects a Clerk sign-in token in /tmp/lumos_demo_ticket.txt)
 * Outputs: demo/screens/*.png (iPhone 3x + one desktop) and demo/video/*.webm
 */
import { chromium, devices } from 'playwright'
import { mkdirSync } from 'fs'

const APP = 'https://lumos-sooty.vercel.app'
const PORTAL = 'https://peaceful-drake-17.accounts.dev'
const CLERK = 'https://api.clerk.com/v1'
const SECRET = process.env.CLERK_SECRET_KEY
const DEMO_USER = process.env.DEMO_USER_ID
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

async function signIn(page) {
  const ticket = await freshTicket()
  await page.goto(`${PORTAL}/sign-in?__clerk_ticket=${ticket}`)
  await page.waitForTimeout(6000)
  const cookies = await page.context().cookies(PORTAL)
  const db = cookies.find(c => c.name === '__clerk_db_jwt')
  if (!db) throw new Error('clerk dev-browser cookie missing — ticket expired?')
  await page.goto(`${APP}/?__clerk_db_jwt=${db.value}`)
  await page.waitForTimeout(5000)
  // Confirm the session actually restored before shooting anything
  const ok = await page.evaluate(() => !!(window.Clerk && window.Clerk.user))
  if (!ok) throw new Error('sign-in did not restore a Clerk session')
  await page.evaluate(() => localStorage.setItem('lumos-disclaimer-ok', '1'))
  await page.goto(`${APP}/`)
  await page.waitForTimeout(2500)
}

async function shoot(page, path, name, { settle = 3500, fullPage = false } = {}) {
  await page.goto(`${APP}${path}`)
  await page.waitForTimeout(settle)
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
  await shoot(page, '/recommend', '03-portfoy', { settle: 12000 })
  // slice detail card — tap the first legend row
  try {
    await page.locator('text=S&P 500 ETF').first().click()
    await page.waitForTimeout(1200)
    await page.screenshot({ path: 'demo/screens/04-varlik-karti.png' })
    console.log('✓ 04-varlik-karti')
  } catch { console.log('… varlık kartı atlandı') }
  await shoot(page, '/holdings', '05-varliklarim', { settle: 9000 })
  await shoot(page, '/dashboard', '06-panel', { settle: 7000 })
  await shoot(page, '/explore', '07-emlak-kesfet', { settle: 7000 })

  // advisor chat with a real AI answer
  try {
    await page.goto(`${APP}/dashboard`)
    await page.waitForTimeout(4000)
    await page.getByLabel('Danışmana sor').click()
    await page.waitForTimeout(1000)
    await page.getByPlaceholder('Bir şey sor…').fill('ETF nedir, kısaca anlatır mısın?')
    await page.keyboard.press('Enter')
    await page.waitForTimeout(15000)
    await page.screenshot({ path: 'demo/screens/08-danisman.png' })
    console.log('✓ 08-danisman')
  } catch (e) { console.log('… danışman atlandı:', e.message) }
  await ctx.close()
}

// ── Desktop hero ─────────────────────────────────────────────────────────────
{
  const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 2 })
  const page = await ctx.newPage()
  await signIn(page)
  await shoot(page, '/dashboard', '09-desktop-panel', { settle: 7000 })
  await shoot(page, '/recommend', '10-desktop-portfoy', { settle: 12000 })
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
  console.log('✓ video kaydedildi')
}

await browser.close()
console.log('BİTTİ')
