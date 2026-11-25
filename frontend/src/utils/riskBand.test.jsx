import { describe, expect, it, beforeAll } from 'vitest'
import { renderToStaticMarkup } from 'react-dom/server'
import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'
import en from '../locales/en.json'
import RiskGauge from '../components/RiskGauge'
import { riskBand, RISK_BANDS } from './riskBand'

describe('riskBand', () => {
  it('puts each score in the band the server label uses', () => {
    expect(riskBand(1).key).toBe('low')
    expect(riskBand(3).key).toBe('low')
    expect(riskBand(3.4).key).toBe('medium')
    expect(riskBand(6).key).toBe('medium')
    expect(riskBand(6.1).key).toBe('high')
    expect(riskBand(10).key).toBe('high')
  })

  it('gives every band a colour and a label key', () => {
    for (const b of Object.values(RISK_BANDS)) {
      expect(b.color).toMatch(/^var\(--/)
      expect(b.label).toMatch(/^profile\.bands\./)
    }
  })
})

// The gauge and the Profile summary card once disagreed: the gauge rounded 3.4
// to 3 (green, "low") while the card said "Balanced". The card reads riskBand()
// directly; this checks the rendered gauge lands in the same band.
describe('RiskGauge agrees with the summary card', () => {
  beforeAll(async () => {
    await i18n.use(initReactI18next).init({
      lng: 'en', resources: { en: { translation: en } }, interpolation: { escapeValue: false },
    })
  })

  it.each([3.4, 3, 6, 6.6])('score %s', score => {
    const band = riskBand(score)
    const html = renderToStaticMarkup(<RiskGauge score={score} />)
    expect(html).toContain(`stroke:${band.color}`)
    expect(html).toContain('fill:var(--text)')   // band colour is the arc only, never text
    expect(html).toContain(`<h3 style="margin-top:-4px">${en.profile.bands[band.key]}</h3>`)
    for (const other of Object.values(RISK_BANDS).filter(b => b !== band)) {
      expect(html).not.toContain(other.color)
    }
  })
})
