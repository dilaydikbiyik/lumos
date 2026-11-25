import { describe, it, expect } from 'vitest'
import { getCurrency } from './holdingCurrency'

describe('getCurrency', () => {
  it('reads cash, property and vehicles in the currency they were recorded in', () => {
    expect(getCurrency({ asset_type: 'cash', currency: 'USD' }, 'TRY')).toBe('USD')
    expect(getCurrency({ asset_type: 'real_estate', currency: 'EUR' }, 'TRY')).toBe('EUR')
  })
  it('treats legacy rows with no currency as home currency', () => {
    expect(getCurrency({ asset_type: 'cash', currency: null }, 'TRY')).toBe('TRY')
  })
  it('follows the listing, not the purchase currency, for tickers', () => {
    expect(getCurrency({ asset_type: 'stock', ticker: 'AAPL', currency: 'TRY' }, 'TRY')).toBe('USD')
    expect(getCurrency({ asset_type: 'stock', ticker: 'THYAO.IS', currency: 'USD' }, 'EUR')).toBe('TRY')
  })
})
