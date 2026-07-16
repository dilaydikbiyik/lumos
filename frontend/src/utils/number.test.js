import { describe, expect, it } from 'vitest'
import { parseTL } from './number'

describe('parseTL — Turkish money input parsing', () => {
  it('reads dotted thousands correctly (the 30.000 TL rent bug)', () => {
    expect(parseTL('30.000')).toBe(30000)
    expect(parseTL('100.000')).toBe(100000)
    expect(parseTL('1.250.000')).toBe(1250000)
  })
  it('supports comma decimals and mixed notation', () => {
    expect(parseTL('1.250.000,50')).toBe(1250000.5)
    expect(parseTL('30,5')).toBe(30.5)
  })
  it('keeps plain numbers and genuine decimals', () => {
    expect(parseTL('30000')).toBe(30000)
    expect(parseTL('10.5')).toBe(10.5)
    expect(parseTL(250)).toBe(250)
  })
  it('handles spaces and empties', () => {
    expect(parseTL('30 000')).toBe(30000)
    expect(Number.isNaN(parseTL(''))).toBe(true)
  })
})
