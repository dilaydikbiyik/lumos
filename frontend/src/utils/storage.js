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

/**
 * Remove everything this device keeps for one account — holdings, portfolio,
 * history, quiz draft, chat drafts, the profile flag — on sign-out.
 *
 * Only account deletion used to clear them, so on a shared device the next
 * person could open the browser's storage and read the previous reader's
 * budget, income and debt. Keys are `lumos-<name>-<userId>` (userKey) or
 * `lumos-profile-<userId>`; device-wide keys (language, market cache,
 * disclaimer) carry no user id and stay.
 */
export function forgetUser(userId) {
  if (!userId) return
  try {
    const doomed = []
    for (let i = 0; i < localStorage.length; i += 1) {
      const key = localStorage.key(i)
      if (key && key.startsWith('lumos-') && key.endsWith(`-${userId}`)) doomed.push(key)
    }
    doomed.forEach(key => localStorage.removeItem(key))
  } catch { /* storage blocked: nothing was kept */ }
}
