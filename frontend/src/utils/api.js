import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000',
  // Bound infinite hangs (Render cold-start + slow AI) — a timed-out request
  // becomes a retryable "no response" for idempotent calls below.
  timeout: 60000,
})

/**
 * Clerk session tokens expire in ~1 minute. Fetching a token once and
 * storing it produces "Signature has expired" errors. Solution: AuthBridge
 * (App.jsx) registers Clerk's getToken here; the interceptor pulls a fresh
 * token on EVERY request — free, since Clerk caches and auto-refreshes
 * internally.
 */
let tokenGetter = null

export function registerTokenGetter(fn) {
  tokenGetter = fn
}

api.interceptors.request.use(async (config) => {
  if (tokenGetter) {
    try {
      const token = await tokenGetter()
      if (token) config.headers.Authorization = `Bearer ${token}`
    } catch {
      // if the token can't be fetched, send the request anyway — backend answers 401
    }
  }
  return config
})

// Backwards compatibility: old page-load calls are now harmless
// (the interceptor overwrites this with a fresh token on every request).
export function setAuthToken(token) {
  if (token) {
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`
  } else {
    delete api.defaults.headers.common['Authorization']
  }
}

/**
 * Cold-start resilience: Render's free tier spins the backend down after
 * inactivity; the first request during wake-up can hit the proxy's 502/503
 * (or take ~30-50s). Instead of surfacing an error, retry with backoff.
 *
 * Retry safety: 502/503 come from Render's proxy BEFORE the app processes
 * the request, so any method is safe to retry. On pure network errors and
 * 504 the app may have processed the request, so only idempotent methods
 * are retried (never POST — e.g. a duplicate holding must be impossible).
 */
const RETRY_DELAYS_MS = [2000, 5000, 10000, 20000]
const IDEMPOTENT = new Set(['get', 'head', 'options', 'put', 'delete', 'patch'])

api.interceptors.response.use(
  (res) => res,
  async (error) => {
    const cfg = error.config
    if (!cfg || error.code === 'ERR_CANCELED') return Promise.reject(error)

    const status = error.response?.status
    const method = (cfg.method || 'get').toLowerCase()
    const proxyLevel = status === 502 || status === 503
    const maybeProcessed = !error.response || status === 504
    const retryable = proxyLevel || (maybeProcessed && IDEMPOTENT.has(method))

    cfg.__retryCount = cfg.__retryCount || 0
    if (!retryable || cfg.__retryCount >= RETRY_DELAYS_MS.length) {
      return Promise.reject(error)
    }

    const delay = RETRY_DELAYS_MS[cfg.__retryCount]
    cfg.__retryCount += 1
    await new Promise(r => setTimeout(r, delay))
    return api.request(cfg)
  }
)

/**
 * FastAPI error 'detail' is a string for our own HTTPExceptions, but
 * Pydantic validation errors (422) return an array of objects — render
 * either safely instead of letting React print "[object Object]".
 */
export function extractErrorMessage(err, fallback) {
  const detail = err?.response?.data?.detail
  if (!detail) return fallback
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) {
    return detail.map(d => d.msg || JSON.stringify(d)).join(', ')
  }
  return fallback
}

export default api
