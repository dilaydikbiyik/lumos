import { describe, it, expect } from 'vitest'
import tr from './tr.json'
import en from './en.json'
import de from './de.json'

/**
 * The locale files are a contract, not three independent documents.
 *
 * A key present in one and missing in another is invisible in development —
 * i18next quietly falls back and the page still renders, in the wrong
 * language. That is exactly how 163 German keys sat unnoticed behind the
 * English fallback, and how a converted page shipped referencing keys nobody
 * had written.
 *
 * Completeness is also what lets the app ship only the reader's locale: if
 * the fallback chain never has to fire, the other two files need never be
 * downloaded.
 */

const LOCALES = { tr, en, de }

function flatten(value, prefix = '') {
  const out = {}
  for (const [key, inner] of Object.entries(value)) {
    const path = prefix ? `${prefix}.${key}` : key
    if (inner && typeof inner === 'object' && !Array.isArray(inner)) {
      Object.assign(out, flatten(inner, path))
    } else {
      out[path] = inner
    }
  }
  return out
}

const FLAT = Object.fromEntries(
  Object.entries(LOCALES).map(([code, value]) => [code, flatten(value)]),
)

const placeholders = (text) =>
  new Set(String(text).match(/\{\{\s*\w+\s*\}\}/g) ?? [])

const components = (text) =>
  new Set(String(text).match(/<\d+\s*\/?>/g) ?? [])

describe('locale files', () => {
  it('every locale has exactly the same keys', () => {
    const reference = Object.keys(FLAT.tr).sort()
    for (const code of ['en', 'de']) {
      expect({ [code]: Object.keys(FLAT[code]).sort() })
        .toEqual({ [code]: reference })
    }
  })

  it('no value is empty', () => {
    for (const [code, entries] of Object.entries(FLAT)) {
      const blank = Object.entries(entries)
        .filter(([, value]) => typeof value === 'string' && value.trim() === '')
        .map(([key]) => key)
      expect({ [code]: blank }).toEqual({ [code]: [] })
    }
  })

  it('interpolation placeholders match across locales', () => {
    // A translation that drops {{amount}} renders a sentence with a hole in
    // it; one that invents {{total}} renders the literal braces.
    for (const [key, value] of Object.entries(FLAT.tr)) {
      for (const code of ['en', 'de']) {
        expect({ key, code, p: [...placeholders(FLAT[code][key])].sort() })
          .toEqual({ key, code, p: [...placeholders(value)].sort() })
      }
    }
  })

  it('Trans component slots match across locales', () => {
    // <0> without a matching component swallows the text inside it.
    for (const [key, value] of Object.entries(FLAT.tr)) {
      for (const code of ['en', 'de']) {
        expect({ key, code, c: [...components(FLAT[code][key])].sort() })
          .toEqual({ key, code, c: [...components(value)].sort() })
      }
    }
  })

  it('the glossary carries a label as well as an explanation', () => {
    // The term is an identifier, not display text: rendering the key itself
    // put "reel getiri" in the middle of an English sentence.
    for (const [code, value] of Object.entries(LOCALES)) {
      for (const [term, entry] of Object.entries(value.glossary)) {
        expect({ code, term, hasLabel: typeof entry.label === 'string' && entry.label.length > 0 })
          .toEqual({ code, term, hasLabel: true })
        expect({ code, term, hasText: typeof entry.text === 'string' && entry.text.length > 0 })
          .toEqual({ code, term, hasText: true })
      }
    }
  })

  it('non-Turkish locales are not left holding Turkish sentences', () => {
    // Turkish characters alone are a bad signal: "Keşan", "Gölbaşı" and
    // "Borsa İstanbul" are place names that belong in every language. Turkish
    // FUNCTION words are the real tell — no proper noun contains them, and no
    // English or German sentence does either.
    const turkishWords = /\b(ve|bir|için|değil|olarak|kadar|daha|gibi|ama|yok|var|ile|senin|bu|şu|ne|çok|her|tüm|sonra|önce|hangi|neden)\b/gi

    for (const code of ['en', 'de']) {
      const suspicious = Object.entries(FLAT[code])
        .filter(([, value]) => {
          if (typeof value !== 'string') return false
          const hits = value.match(turkishWords) ?? []
          // "Bu" appears in German as nothing, but "var" and "ne" occur in
          // other words' company rarely — two independent hits is the bar.
          return hits.length >= 2
        })
        .map(([key]) => key)
      expect({ [code]: suspicious }).toEqual({ [code]: [] })
    }
  })
})
