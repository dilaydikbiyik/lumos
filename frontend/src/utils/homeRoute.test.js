import { describe, expect, it } from 'vitest'
import { homeRoute } from './homeRoute'

describe('where a signed-in reader lands', () => {
  it('a finished profile goes home, whatever else is missing', () => {
    expect(homeRoute({ risk_score: 6.2, investment_path: null, primary_fear: null })).toBe('/dashboard')
  })

  it('an unfinished intro resumes at the first unanswered step', () => {
    expect(homeRoute({ risk_score: null, investment_path: null })).toBe('/path')
    expect(homeRoute({ risk_score: null, investment_path: 'hybrid', primary_fear: null })).toBe('/fear-check-in')
    expect(homeRoute({ risk_score: null, investment_path: 'stocks', primary_fear: 'anlamiyorum' })).toBe('/profile')
  })

  it('no answer from the server starts the intro, never a page that needs a profile', () => {
    expect(homeRoute(null)).toBe('/path')
  })
})

describe('the first tab is where a returning reader lands', () => {
  it('the navigation opens with the home screen', async () => {
    const { NAV_ITEMS } = await import('../components/navItems.js')
    expect(NAV_ITEMS[0].path).toBe(homeRoute({ risk_score: 5 }))
    expect(NAV_ITEMS.at(-1).path).toBe('/profile')
  })
})
