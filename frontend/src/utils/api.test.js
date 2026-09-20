/**
 * Cold-start retry logic — tests the REAL decision function used by the
 * axios interceptor. The safety property that must never regress: a POST
 * that may have been processed is never retried (duplicate holdings must
 * be impossible), while proxy-level 502/503 retries any method.
 */
import { describe, expect, it } from 'vitest'
import { RETRY_DELAYS_MS, shouldRetry } from './api'

describe('cold-start retry decision', () => {
  it('retries proxy 502/503 for any method (request never reached the app)', () => {
    for (const status of [502, 503]) {
      expect(shouldRetry({ hasResponse: true, status, method: 'post', retryCount: 0 })).toBe(true)
      expect(shouldRetry({ hasResponse: true, status, method: 'get', retryCount: 0 })).toBe(true)
    }
  })

  it('never retries a POST on network error or 504 — it may have been processed', () => {
    expect(shouldRetry({ hasResponse: false, status: undefined, method: 'post', retryCount: 0 })).toBe(false)
    expect(shouldRetry({ hasResponse: true, status: 504, method: 'post', retryCount: 0 })).toBe(false)
  })

  it('retries idempotent methods on network error / 504', () => {
    expect(shouldRetry({ hasResponse: false, status: undefined, method: 'get', retryCount: 0 })).toBe(true)
    expect(shouldRetry({ hasResponse: true, status: 504, method: 'patch', retryCount: 0 })).toBe(true)
  })

  it('gives up after the backoff schedule is exhausted', () => {
    expect(shouldRetry({ hasResponse: true, status: 502, method: 'get', retryCount: RETRY_DELAYS_MS.length })).toBe(false)
  })

  it('does not retry real errors (401/422/500)', () => {
    for (const status of [401, 422, 500]) {
      expect(shouldRetry({ hasResponse: true, status, method: 'get', retryCount: 0 })).toBe(false)
    }
  })
})

describe('in-flight GET coalescing', () => {
  it('two simultaneous identical GETs make one request', async () => {
    const api = (await import('./api')).default
    let calls = 0
    // Patch the adapter rather than api.get, so the coalescing layer is
    // exactly what is under test.
    api.defaults.adapter = async (config) => {
      calls += 1
      await new Promise(r => setTimeout(r, 20))
      return { data: { ok: true }, status: 200, statusText: 'OK', headers: {}, config }
    }

    const [a, b] = await Promise.all([
      api.get('/holdings/summary'),
      api.get('/holdings/summary'),
    ])
    expect(calls).toBe(1)
    expect(a).toBe(b)   // the same promise resolved once

    // A later call is a new request: this coalesces, it does not cache.
    await api.get('/holdings/summary')
    expect(calls).toBe(2)
  })

  it('different params are different requests', async () => {
    const api = (await import('./api')).default
    let calls = 0
    api.defaults.adapter = async (config) => {
      calls += 1
      await new Promise(r => setTimeout(r, 20))
      return { data: {}, status: 200, statusText: 'OK', headers: {}, config }
    }

    await Promise.all([
      api.get('/holdings/history', { params: { days: 30 } }),
      api.get('/holdings/history', { params: { days: 90 } }),
    ])
    expect(calls).toBe(2)
  })

  it('a failed request is not left behind to poison the next one', async () => {
    const api = (await import('./api')).default
    const { inFlightCount } = await import('./api')
    let calls = 0
    // A 400 is a definitive answer, so the retry layer leaves it alone — the
    // point here is the coalescing map, not the backoff.
    api.defaults.adapter = async (config) => {
      calls += 1
      throw Object.assign(new Error('boom'), {
        config, response: { status: 400, data: {}, headers: {}, config },
      })
    }

    await Promise.allSettled([api.get('/nope'), api.get('/nope')])
    expect(calls).toBe(1)
    expect(inFlightCount()).toBe(0)
  })
})
