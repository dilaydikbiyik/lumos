/* Lumos service worker — app-shell cache with network-first strategy.
   API calls are never cached (financial data must be fresh). */
const CACHE = 'lumos-shell-v2'  // v2: cross-origin skip — clears any v1-cached API data
const SHELL = ['/', '/manifest.webmanifest', '/favicon.svg']

self.addEventListener('install', event => {
  event.waitUntil(caches.open(CACHE).then(c => c.addAll(SHELL)))
  self.skipWaiting()
})

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))
    )
  )
  self.clients.claim()
})

self.addEventListener('fetch', event => {
  const url = new URL(event.request.url)

  // Never intercept API traffic or non-GET requests. The production backend
  // lives on ANOTHER origin (e.g. onrender.com) — matching only dev port 8000
  // would have cached live financial data in production, so any cross-origin
  // request is skipped entirely.
  if (
    event.request.method !== 'GET' ||
    url.origin !== self.location.origin ||
    url.pathname.startsWith('/api')
  ) {
    return
  }

  // Network-first, cache fallback (offline shell)
  event.respondWith(
    fetch(event.request)
      .then(res => {
        const copy = res.clone()
        caches.open(CACHE).then(c => c.put(event.request, copy)).catch(() => {})
        return res
      })
      .catch(() => caches.match(event.request).then(hit => hit || caches.match('/')))
  )
})

/* ── Web Push ──────────────────────────────────────────────────────────────
   Why this is here rather than behind a native app: the behavioural coach's
   one message that has to arrive in real time is "the market dropped, here is
   why not to sell", and a message that waits for the reader to open the app
   arrives after they have already sold.

   That was blocked on an Apple and a Play account until iOS 16.4 (March 2023)
   gave home-screen web apps the Push API; as of iOS 26 a site added to the
   Home Screen opens as a web app by default. Android Chrome has carried it
   for years. So the carrier exists with no store account, no yearly fee and
   no native wrapper — for readers who INSTALL the app, which the UI has to
   say plainly rather than asking for permission and hoping.

   Deliberately conservative: a push from this app is a market event, never
   marketing, and the payload carries no figure the reader has not already
   asked to see. */

self.addEventListener('push', event => {
  // A malformed payload must not throw inside the handler: an uncaught error
  // here shows the browser's own "this site has been updated in the
  // background" notice, which is worse than staying silent. The catch leaves
  // the empty default in place rather than reassigning it.
  let payload = {}
  try {
    payload = event.data ? event.data.json() : {}
  } catch { /* keep the empty default */ }
  if (!payload.title) return

  event.waitUntil(self.registration.showNotification(payload.title, {
    body: payload.body || '',
    icon: '/icons/icon-192.png',
    badge: '/icons/badge-72.png',
    // Same tag replaces rather than stacks: three notifications about one
    // market drop is the app panicking at somebody.
    tag: payload.tag || 'lumos',
    data: { url: payload.url || '/' },
    // Never true. A financial app that overrides Do Not Disturb to say the
    // market moved has misunderstood which of those matters more.
    requireInteraction: false,
  }))
})

self.addEventListener('notificationclick', event => {
  event.notification.close()
  const target = event.notification.data?.url || '/'
  event.waitUntil(
    self.clients.matchAll({ type: 'window', includeUncontrolled: true })
      .then(list => {
        // Reuse an open tab rather than stacking another copy of the app.
        for (const client of list) {
          if ('focus' in client) { client.navigate(target); return client.focus() }
        }
        return self.clients.openWindow(target)
      })
  )
})
