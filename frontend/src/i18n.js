import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'

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
  { code: 'de', label: 'Deutsch' },
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
  const nav = ((typeof navigator !== 'undefined' && navigator.language) || 'tr').toLowerCase()
  if (nav.startsWith('tr')) return 'tr'
  if (nav.startsWith('de')) return 'de'
  return 'en'
}

/**
 * Locales are loaded one at a time.
 *
 * All three used to be bundled into the entry chunk: a Turkish reader
 * downloaded ~100 kB of English and German before the first sentence
 * rendered. Shipping only the active one is safe because locales.test.js
 * enforces that the three files carry identical keys — the fallback chain
 * below is a backstop that, by contract, never has to fire.
 *
 * The static analyser needs to see literal paths, so this is a map rather
 * than a template string.
 */
const LOADERS = {
  tr: () => import('./locales/tr.json'),
  en: () => import('./locales/en.json'),
  de: () => import('./locales/de.json'),
}

const loaded = new Set()

async function loadLocale(code) {
  if (loaded.has(code)) return
  const module = await LOADERS[code]()
  i18n.addResourceBundle(code, 'translation', module.default, true, true)
  loaded.add(code)
}

/**
 * Initialise i18n with the reader's language already in place.
 *
 * Awaited before the app renders: initialising with a placeholder locale and
 * swapping afterwards would show the wrong language for a frame, which is the
 * exact problem the language work set out to remove.
 */
export async function initI18n() {
  const lng = initialLanguage()
  const { default: resources } = await LOADERS[lng]()

  await i18n.use(initReactI18next).init({
    resources: { [lng]: { translation: resources } },
    lng,
    // A missing German key falls to English, not Turkish: showing a German
    // reader Turkish is worse than showing them English. Turkish stays the
    // final backstop because it is the reference file.
    fallbackLng: { de: ['en', 'tr'], en: ['tr'], default: ['tr'] },
    interpolation: { escapeValue: false },  // React already escapes
    returnEmptyString: false,
    // Nothing to fetch on a miss: the bundle for the active language is
    // already in memory, and the others are a deliberate non-download.
    partialBundledLanguages: true,
  })
  loaded.add(lng)
  applyDocumentLanguage(lng)
  return i18n
}

/** index.html can only carry one language; the tab title and the description
    a link preview shows should follow the reader's choice, not the file. */
function applyDocumentLanguage(code) {
  document.documentElement.lang = code
  document.title = i18n.t('meta.title')
  document.querySelector('meta[name="description"]')
    ?.setAttribute('content', i18n.t('meta.description'))
}

export async function setLanguage(code) {
  if (!LANGUAGES.some(l => l.code === code)) return
  try { localStorage.setItem(STORAGE_KEY, code) } catch { /* fine */ }
  // Fetch first, switch second: changing the language before its file has
  // arrived renders raw keys for as long as the request takes.
  await loadLocale(code)
  await i18n.changeLanguage(code)
  applyDocumentLanguage(code)
}

export default i18n
