import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { ClerkProvider } from '@clerk/clerk-react'
import App from './App.jsx'
import './index.css'
import { initI18n } from './i18n'

const PUBLISHABLE_KEY = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY

if (!PUBLISHABLE_KEY) {
  console.warn('⚠️  VITE_CLERK_PUBLISHABLE_KEY is not set — auth features will not work. Add it to frontend/.env')
}

// Wake the backend the moment the app loads (free tier spins down when
// idle). Fire-and-forget: by the time the user types anything the server
// is warm, with no loading banner needed.
// Versioned like every other call. The backend still answers the bare path,
// but that mount is deprecated, and a warm-up ping that quietly 404s once it
// is removed would cost the first real request a cold start with no symptom
// anyone would notice.
const backend = import.meta.env.VITE_BACKEND_URL
if (backend) {
  fetch(`${backend.replace(/\/+$/, '')}/api/v1/health`).catch(() => {})
}

// PWA: register service worker (production builds only — dev uses HMR)
if ('serviceWorker' in navigator && import.meta.env.PROD) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js').catch(() => {})
  })
}

// The reader's locale is fetched before the first render. index.html paints
// its own splash meanwhile, so the wait is covered rather than blank — and
// nobody sees a frame of the wrong language.
// If the locale still cannot be loaded after the retries in initI18n, the
// app is NOT rendered: it used to render anyway on the theory that raw keys
// beat a white screen, and a reader on a weak phone connection got a page
// of "onboarding.heroPrefix" and "common.start". Reload once (the usual
// cure for a dropped chunk or a page left open across a deploy); if that
// fails too, say so plainly in all three languages, since which one the
// reader reads is exactly what could not be loaded.
const RELOAD_FLAG = 'lumos-locale-reload'

/** True the first time in this tab; false after, or when storage is blocked
    (no flag to stop it means a reload could loop forever). */
function markReloadOnce() {
  try {
    if (sessionStorage.getItem(RELOAD_FLAG) === '1') return false
    sessionStorage.setItem(RELOAD_FLAG, '1')
    return true
  } catch {
    return false
  }
}

function showLoadFailure() {
  const splash = document.getElementById('splash')
  if (!splash) return
  splash.removeAttribute('aria-hidden')
  splash.setAttribute('role', 'alert')
  splash.style.cssText += ';flex-direction:column;gap:16px;padding:24px;text-align:center;color:#E8E6F0;font:15px/1.5 system-ui,sans-serif'
  splash.innerHTML = ''
  for (const line of ['Bağlantı kurulamadı.', 'Could not connect.', 'Keine Verbindung.']) {
    const p = document.createElement('p')
    p.textContent = line
    p.style.margin = '0'
    splash.append(p)
  }
  const button = document.createElement('button')
  button.textContent = '↻'
  button.setAttribute('aria-label', 'Yeniden dene / Try again / Erneut versuchen')
  button.style.cssText = 'min-width:88px;min-height:44px;border-radius:12px;border:0;background:#F5A524;color:#0C0D14;font-size:20px;cursor:pointer'
  button.onclick = () => window.location.reload()
  splash.append(button)
}

initI18n()
  .then(() => {
    try { sessionStorage.removeItem(RELOAD_FLAG) } catch { /* fine */ }
    document.getElementById('splash')?.remove()
    createRoot(document.getElementById('root')).render(
      <StrictMode>
        <ClerkProvider
          publishableKey={PUBLISHABLE_KEY || 'pk_test_placeholder'}
          afterSignOutUrl="/"
        >
          <App />
        </ClerkProvider>
      </StrictMode>,
    )
  })
  .catch(() => {
    if (markReloadOnce()) window.location.reload()
    else showLoadFailure()
  })
