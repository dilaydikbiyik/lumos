import { describe, expect, it, beforeAll } from 'vitest'
import { renderToStaticMarkup } from 'react-dom/server'
import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'
import en from '../locales/en.json'
import RiskGauge from '../components/RiskGauge'
import { bandColor, RISK_BAND_COLORS } from './riskBand'

describe('bandColor', () => {
  it('has a colour token for each of the server\'s four band keys', () => {
    expect(Object.keys(RISK_BAND_COLORS).sort())
      .toEqual(['aggressive', 'balanced', 'conservative', 'growth'])
    for (const c of Object.values(RISK_BAND_COLORS)) expect(c).toMatch(/^var\(--/)
  })

  it('gives each band its own colour, none of them red', () => {
    const colors = Object.values(RISK_BAND_COLORS)
    expect(new Set(colors).size).toBe(colors.length)
    expect(colors).not.toContain('var(--red)')
  })

  it('falls back to a neutral colour for a profile cached without a band', () => {
    expect(bandColor(undefined)).toBe('var(--text-dim)')
  })
})

// The gauge once said "Growth-Focused" (server label) while the card under it
// said "Aggressive" (a client copy of the cut-offs). Both now take the server's
// band key and label; the gauge holds no threshold of its own.
describe('RiskGauge follows the server band', () => {
  beforeAll(async () => {
    await i18n.use(initReactI18next).init({
      lng: 'en', resources: { en: { translation: en } }, interpolation: { escapeValue: false },
    })
  })

  it.each([
    [3.4, 'balanced', 'Balanced'],
    [7, 'growth', 'Growth-Focused'],
  ])('score %s', (score, band, label) => {
    const html = renderToStaticMarkup(<RiskGauge score={score} band={band} label={label} />)
    expect(html).toContain(`stroke:${RISK_BAND_COLORS[band]}`)
    expect(html).toContain('fill:var(--text)')   // band colour is the arc only, never text
    expect(html).toContain(`<h3 style="margin-top:-4px">${label}</h3>`)
  })
})
