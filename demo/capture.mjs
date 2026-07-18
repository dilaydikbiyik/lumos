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
          await page.evaluate(() => localStorage.setItem('lumos-disclaimer-ok', '1'))
          await page.goto(`${APP}/`)
          await page.waitForTimeout(2500)
          return
        }
        await page.waitForTimeout(1500)
      }
    }
    console.log(`  … sign-in denemesi ${attempt} başarısız, tekrar`)
    await page.waitForTimeout(8000)  // let the rate-limit window pass
  }
  throw new Error('sign-in did not restore a Clerk session after retries')
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
  // Real-estate projection: İstanbul 5-year scenario band
  try {
    await page.goto(`${APP}/explore`)
    await page.waitForSelector('input[aria-label="İl ara"]', { timeout: 20000 })
    await page.locator('input[aria-label="İl ara"]').fill('İstanbul')
    await page.waitForTimeout(2500)
    const card = page.locator('.card', { hasText: 'İstanbul' }).first()
    await card.scrollIntoViewIfNeeded()
    await card.click({ force: true })
    await page.waitForTimeout(1500)
    const projBtn = page.locator('button', { hasText: 'olurdu' }).first()
    await projBtn.waitFor({ timeout: 8000 })
    await projBtn.click({ force: true })
    await page.waitForTimeout(9000)
    await card.scrollIntoViewIfNeeded()
    await page.screenshot({ path: 'demo/screens/04-emlak-istanbul.png' })
    console.log('✓ 04-emlak-istanbul')
  } catch (e) { console.log('… İstanbul projeksiyonu atlandı:', e.message) }
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
