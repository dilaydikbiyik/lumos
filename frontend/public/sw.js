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
