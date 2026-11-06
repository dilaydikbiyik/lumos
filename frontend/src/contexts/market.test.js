import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { describe, expect, it } from 'vitest'

const code = (rel) => readFileSync(fileURLToPath(new URL(rel, import.meta.url)), 'utf8')

/**
 * A reader switched the header to TR and the Explore page kept ranking New
 * Jersey and Connecticut: the switch was optimistic (the header flipped
 * before the server saved it) and no page re-fetched on a market change.
 * These pin both halves of the fix.
 */
describe('a market switch reaches every page', () => {
  it('the market pages read is set only after the server has saved it', () => {
    const source = code('./MarketContext.jsx')
    const body = source.slice(source.indexOf('const setMarket'), source.indexOf('}, [marketCode, packs])'))
    const saved = body.indexOf("api.patch('/users/me/market'")
    const applied = body.indexOf('setMarketCode(code)')
    expect(saved).toBeGreaterThan(-1)
    expect(applied).toBeGreaterThan(saved)
  })

  it('the routed pages are remounted per market', () => {
    const app = code('../App.jsx')
    expect(app).toMatch(/<Fragment key=\{market\}>/)
    const routes = app.indexOf('<Routes>')
    expect(app.lastIndexOf('<MarketScoped>', routes)).toBeGreaterThan(-1)
  })
})
