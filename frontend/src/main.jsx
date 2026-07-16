import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { ClerkProvider } from '@clerk/clerk-react'
import App from './App.jsx'
import './index.css'

const PUBLISHABLE_KEY = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY

if (!PUBLISHABLE_KEY) {
  console.warn('⚠️  VITE_CLERK_PUBLISHABLE_KEY is not set — auth features will not work. Add it to frontend/.env')
}

// Wake the backend the moment the app loads (free tier spins down when
// idle). Fire-and-forget: by the time the user types anything the server
// is warm, with no loading banner needed.
const backend = import.meta.env.VITE_BACKEND_URL
if (backend) {
  fetch(`${backend}/health`).catch(() => {})
}

// PWA: register service worker (production builds only — dev uses HMR)
if ('serviceWorker' in navigator && import.meta.env.PROD) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js').catch(() => {})
  })
}

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
