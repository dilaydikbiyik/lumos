/**
 * Local snapshot storage.
 *
 * Five components were each hand-rolling the same try/JSON.parse/catch dance,
 * so a fix in one (private mode, quota exceeded, corrupt entry) never reached
 * the others. Reads and writes are best-effort by design: a cache that throws
 * is worse than a cache that misses.
 */

/** Namespaced key so two accounts on one device never read each other's data. */
export function userKey(name, userId) {
  return userId ? `lumos-${name}-${userId}` : null
}

export function readJSON(key, fallback = null) {
  if (!key) return fallback
  try {
    const raw = localStorage.getItem(key)
    return raw ? JSON.parse(raw) : fallback
  } catch {
    return fallback          // private mode, corrupt entry, disabled storage
  }
}

export function writeJSON(key, value) {
  if (!key) return false
  try {
    localStorage.setItem(key, JSON.stringify(value))
    return true
  } catch {
    return false             // quota exceeded — the app must still work
  }
}

export function removeKey(key) {
  if (!key) return
  try { localStorage.removeItem(key) } catch { /* nothing to recover from */ }
}

/** Plain (non-JSON) flags such as the accepted-disclaimer marker. */
export function readFlag(key) {
  try { return localStorage.getItem(key) } catch { return null }
}

export function writeFlag(key, value) {
  try { localStorage.setItem(key, value) } catch { /* best effort */ }
}
