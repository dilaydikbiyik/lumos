/**
 * Where a signed-in reader belongs when they open the app.
 *
 * The app's start address is "/", the marketing page, and it used to show
 * that page to everybody — a reader with a finished profile tapped "Start"
 * on every visit, then waited on a server round trip, before reaching their
 * own dashboard. A returning reader now goes straight to where they left
 * off, in the order the intro asks things:
 *
 *   finished risk profile      → /dashboard     (home)
 *   no investment path yet     → /path          (step 1)
 *   path, no fear check-in     → /fear-check-in (step 2)
 *   path and check-in, no quiz → /profile       (step 3)
 *
 * Pure, so the order is tested rather than remembered.
 */
export function homeRoute(me) {
  if (!me) return '/path'
  if (me.risk_score != null) return '/dashboard'
  if (!me.investment_path) return '/path'
  if (!me.primary_fear) return '/fear-check-in'
  return '/profile'
}

const flag = (userId) => `lumos-profile-${userId}`

/** The device remembers that this reader has a profile, so the next open
    goes to the dashboard without waiting on the server. */
export function rememberProfile(userId) {
  if (!userId) return
  try { localStorage.setItem(flag(userId), '1') } catch { /* storage blocked: the server answers instead */ }
}

export function hasRememberedProfile(userId) {
  if (!userId) return false
  try { return localStorage.getItem(flag(userId)) === '1' } catch { return false }
}
