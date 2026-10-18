import api from './api'

/**
 * Turning a granted permission into a subscription the backend can send to.
 *
 * Pure-ish helpers kept out of the component, same reason as install.js:
 * the base64 conversion below is the single most error-prone line in the
 * whole feature and it deserves a test rather than a comment.
 */

/**
 * The VAPID public key arrives as unpadded URL-safe base64 and the browser
 * demands a Uint8Array. Getting this wrong produces no error — the
 * subscription simply never arrives, or arrives encrypted for nobody.
 *
 * Two substitutions, both required: URL-safe base64 uses - and _ where
 * standard base64 uses + and /, and atob refuses input that is not a
 * multiple of four characters, so the padding has to be put back.
 */
export function urlBase64ToUint8Array(base64String) {
  const padding = '='.repeat((4 - (base64String.length % 4)) % 4)
  const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/')
  // globalThis, not window: atob is a global in every context this could
  // run in, and `window` does not exist inside a service worker — so
  // reaching through it was both untestable and wrong for the one place
  // this code is most likely to be reused.
  const raw = globalThis.atob(base64)
  const output = new Uint8Array(raw.length)
  for (let i = 0; i < raw.length; i += 1) output[i] = raw.charCodeAt(i)
  return output
}

/** Can this browser receive push at all? */
export function pushSupported() {
  return typeof window !== 'undefined'
    && 'serviceWorker' in window.navigator
    && 'PushManager' in window
    && 'Notification' in window
}

/**
 * Ask, subscribe, and tell the backend. Returns true only if all three
 * happened.
 *
 * The order matters and is not negotiable: the permission prompt must come
 * from a user gesture, so this is called from a click handler and never
 * from an effect. A prompt on page load is both refused by Safari and the
 * fastest way to be denied permanently — "deny" is not a soft no, it is a
 * setting the reader has to go and find to undo.
 */
export async function subscribeToPush() {
  if (!pushSupported()) return false

  // Whether the server can send BEFORE asking the reader for anything. A
  // deployment with no VAPID keys would otherwise spend a permission grant
  // on a subscription nothing can use.
  const { data } = await api.get('/push/public-key')
  if (!data?.available || !data.public_key) return false

  const permission = await window.Notification.requestPermission()
  if (permission !== 'granted') return false

  const registration = await window.navigator.serviceWorker.ready
  const existing = await registration.pushManager.getSubscription()
  const subscription = existing || await registration.pushManager.subscribe({
    // Required to be true by every browser: a push that shows nothing is a
    // silent wake-up, and it is not allowed on the open web.
    userVisibleOnly: true,
    applicationServerKey: urlBase64ToUint8Array(data.public_key),
  })

  const json = subscription.toJSON()
  await api.post('/push/subscribe', {
    endpoint: json.endpoint,
    keys: { p256dh: json.keys.p256dh, auth: json.keys.auth },
  })
  return true
}
