import { describe, it, expect } from 'vitest'
import { withAlpha } from './palette'

describe('withAlpha', () => {
  it('works for hex, hsl() and CSS variables alike', () => {
    expect(withAlpha('#F5A524', 33)).toBe('color-mix(in srgb, #F5A524 33%, transparent)')
    expect(withAlpha('hsl(30 90% 50%)', 10)).toBe('color-mix(in srgb, hsl(30 90% 50%) 10%, transparent)')
    expect(withAlpha('var(--red)', 9)).toBe('color-mix(in srgb, var(--red) 9%, transparent)')
  })
})
