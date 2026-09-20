import i18n from '../i18n'

/**
 * Locale-correct number, percent and date formatting.
 *
 * Percent placement is a property of the READING LANGUAGE, not of the market:
 * Turkish writes %25, English 25%, German 25 %. Seven components had the
 * Turkish form hardcoded as a literal "%" before the number, so an English
 * reader looking at a US portfolio was shown "%60" — the same category of
 * mistake as pricing Texas in lira, just smaller and easier to miss.
 *
 * Dates have the matching bug in the other direction: a bare
 * `toLocaleDateString()` follows the BROWSER's locale, so the app's language
 * had no say at all.
 */

/**
 * Whether a value is a real number we can state.
 *
 * `Number('')` is 0, not NaN, so a blank field would otherwise render "0%" —
 * and "0%" is an assertion about someone's portfolio, not an empty space.
 */
function missing(value) {
  return value == null || value === '' || Number.isNaN(Number(value))
}

function lang() {
  // i18n.language can carry a region ("en-GB"); Intl handles that fine, and
  // falling back to "en" keeps this working before i18n has initialised.
  return i18n?.language || 'en'
}

/** "25%" / "%25" / "25 %" — from a 0–100 number, the way the app states them. */
export function percent(value, { decimals = 0 } = {}) {
  if (missing(value)) return ''
  return new Intl.NumberFormat(lang(), {
    style: 'percent',
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(Number(value) / 100)
}

/** The same, from a 0–1 weight, which is how allocations arrive. */
export function percentFromWeight(weight, options) {
  if (missing(weight)) return ''
  return percent(Number(weight) * 100, options)
}

/** A date in the app's language rather than the browser's. */
export function shortDate(value, options = { day: 'numeric', month: 'short', year: 'numeric' }) {
  if (!value) return ''
  const date = value instanceof Date ? value : new Date(value)
  if (Number.isNaN(date.getTime())) return ''
  return new Intl.DateTimeFormat(lang(), options).format(date)
}
