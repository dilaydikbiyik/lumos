/**
 * Currency-truth tests for the market formatter fallback (the exact object
 * components get outside the provider, e.g. in isolated renders).
 * money(n, 'TRY') pinning is what keeps TCMB TL data honest when the user
 * switches markets — it must never drift.
 */
import { describe, expect, it } from 'vitest'
import { FALLBACK_MARKET } from './useMarket'

// The exported fallback IS the object components receive outside the
// provider — plain data we can assert on directly.
const market = FALLBACK_MARKET

describe('market formatter fallback (TR)', () => {
  it('formats numbers with Turkish grouping', () => {
    expect(market.fmt(100000)).toBe('100.000')
  })

  it('formats TRY money in the Turkish convention', () => {
    expect(market.money(100000)).toBe('100.000 TL')
  })

  it('rounds money to whole lira', () => {
    expect(market.money(99999.6)).toBe('100.000 TL')
  })

  it('exposes the TL unit label for big-number layouts', () => {
    expect(market.unit).toBe('TL')
  })

  it('defaults to the TR pack with live data flags', () => {
    expect(market.pack.code).toBe('TR')
    expect(market.pack.live_housing_index).toBe(true)
  })
})
