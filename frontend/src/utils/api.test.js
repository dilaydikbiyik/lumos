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
