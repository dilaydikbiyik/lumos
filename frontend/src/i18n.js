import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'
import tr from './locales/tr.json'
import en from './locales/en.json'

/**
 * Language is a DEVICE preference, deliberately separate from the market:
 * an expat in Istanbul wants the English UI with Turkish market data, and a
 * Turk in Berlin may want the opposite. Neither should imply the other.
 *
 * Persisted under a plain (non-user) key because it belongs to the device,
 * like the OS language — switching accounts must not flip the UI language.
 */
const STORAGE_KEY = 'lumos-language'
export const LANGUAGES = [
  { code: 'tr', label: 'Türkçe' },
  { code: 'en', label: 'English' },
]

function initialLanguage() {
  try {
    // ?lang= override wins (used to test locales before the switcher ships)
    const fromUrl = new URLSearchParams(window.location.search).get('lang')
    if (fromUrl && LANGUAGES.some(l => l.code === fromUrl)) {
      localStorage.setItem(STORAGE_KEY, fromUrl)
      return fromUrl
    }
    const saved = localStorage.getItem(STORAGE_KEY)
    if (saved && LANGUAGES.some(l => l.code === saved)) return saved
  } catch { /* storage blocked — fall through */ }
  // First visit: follow the browser. Anything non-Turkish gets English —
  // a UI in a language you can't read is worse than a merely foreign one.
  const nav = (typeof navigator !== 'undefined' && navigator.language) || 'tr'
  return nav.toLowerCase().startsWith('tr') ? 'tr' : 'en'
}

i18n.use(initReactI18next).init({
  resources: { tr: { translation: tr }, en: { translation: en } },
  lng: initialLanguage(),
  fallbackLng: 'tr',   // untranslated keys show Turkish, never raw key names
  interpolation: { escapeValue: false },  // React already escapes
  returnEmptyString: false,
})

export function setLanguage(code) {
  if (!LANGUAGES.some(l => l.code === code)) return
  try { localStorage.setItem(STORAGE_KEY, code) } catch { /* fine */ }
  i18n.changeLanguage(code)
  document.documentElement.lang = code
}

document.documentElement.lang = i18n.language

export default i18n
