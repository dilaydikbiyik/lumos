import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  // A production build with no backend URL is refused, not shipped.
  //
  // src/utils/api.js falls back to http://localhost:8000 when
  // VITE_BACKEND_URL is unset, which is right for `npm run dev` and silently
  // wrong everywhere else. frontend/.env.production is gitignored, so a build
  // from a fresh clone — or from CI, which was setting VITE_API_BASE_URL, a
  // name nothing reads — produced an app that talks to localhost. On the web
  // that never mattered because Vercel injects the variable. In the App Store
  // and Play Store builds the bundle IS the app, and a phone has no
  // localhost:8000: the result is a blank app with nothing pointing at why.
  if (mode === 'production') {
    const env = loadEnv(mode, import.meta.dirname, 'VITE_')
    const url = env.VITE_BACKEND_URL || ''
    // Presence alone is not enough: Vite loads .env in production mode too,
    // and .env holds the DEVELOPMENT value. The first version of this check
    // passed a build on a machine without .env.production because .env
    // supplied http://localhost:8000 — exactly the bundle it exists to stop.
    if (!url || /^https?:\/\/(localhost|127\.0\.0\.1)(:|\/|$)/.test(url)) {
      throw new Error(
        `Production build refused: VITE_BACKEND_URL is "${url || 'unset'}". `
        + 'Set it to the deployed API in the environment or in '
        + 'frontend/.env.production — a store build pointing at localhost is '
        + 'a blank app on a phone.',
      )
    }
  }
  return {
    plugins: [react()],
  }
})
