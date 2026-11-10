import { describe, expect, it } from 'vitest'
import { localToday } from './date'

describe('localToday', () => {
  it('is an ISO date in the local calendar', () => {
    const d = new Date(2026, 10, 10, 23, 30)      // 23:30 local, 10 Nov
    expect(localToday(d)).toBe('2026-11-10')
  })
})
