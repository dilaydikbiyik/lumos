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
initI18n()
  .catch(() => { /* render anyway: raw keys beat a white screen */ })
  .finally(() => {
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
