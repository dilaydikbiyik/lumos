import { describe, it, expect } from 'vitest'
import { withAlpha, holdingTypeColors, CATEGORY_COLORS } from './palette'

describe('withAlpha', () => {
  it('works for hex, hsl() and CSS variables alike', () => {
    expect(withAlpha('#F5A524', 33)).toBe('color-mix(in srgb, #F5A524 33%, transparent)')
    expect(withAlpha('hsl(30 90% 50%)', 10)).toBe('color-mix(in srgb, hsl(30 90% 50%) 10%, transparent)')
    expect(withAlpha('var(--red)', 9)).toBe('color-mix(in srgb, var(--red) 9%, transparent)')
  })
})

// The dashboard mini-bar once coloured by position: whatever came second was
// REIT purple, so gold or a fund could show up as "REIT".
describe('holdingTypeColors', () => {
  it('gives a type the same colour whatever order the server returns', () => {
    const a = holdingTypeColors(['gold', 'stock', 'crypto', 'cash'])
    const b = holdingTypeColors(['cash', 'crypto', 'stock', 'gold'])
    expect(a).toEqual(b)
  })

  it('uses the category colour, never purple for a non-property type', () => {
    const c = holdingTypeColors(['fund', 'gold', 'stock'])
    expect(c.gold).toBe(CATEGORY_COLORS.gold)
    expect(c.stock).toBe(CATEGORY_COLORS.stocks)
    expect(Object.values(c)).not.toContain(CATEGORY_COLORS.reit)
  })

  it('keeps two types of one category apart, and covers every type', () => {
    const all = ['stock', 'fund', 'etf', 'real_estate', 'land', 'vehicle', 'gold', 'crypto', 'cash', 'other']
    const c = holdingTypeColors(all)
    expect(Object.keys(c).sort()).toEqual([...all].sort())
    expect(new Set(Object.values(c)).size).toBe(all.length)
  })
})
