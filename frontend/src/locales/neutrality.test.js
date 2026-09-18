import { describe, it, expect } from 'vitest'
import { readFileSync, readdirSync } from 'node:fs'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import tr from './tr.json'
import en from './en.json'
import de from './de.json'

/**
 * Shared copy may not name one country's institutions.
 *
 * Every defect the US and German markets produced was this shape. A Texas
 * card priced in lira, because a module-level formatter was pinned to tr-TR
 * back when the page was Türkiye-only. "e.g. Keşan" offered as a Texan
 * district. "Housing index, 81 provinces" on a landing page shown before any
 * market is chosen. "DASK" — Türkiye's compulsory earthquake insurance —
 * inside a footnote read by Americans.
 *
 * Each was found by a person opening the app and noticing, which does not
 * scale. Country facts belong in the market pack; this file is what stops
 * them drifting back into shared strings.
 */

const here = dirname(fileURLToPath(import.meta.url))
const SRC = resolve(here, '..')

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

// Institutions, taxes, portals and coverage claims that belong to exactly one
// country. Place names are deliberately absent: "Keşan" and "Berlin" are fine
// anywhere, and the pack supplies them as examples.
const COUNTRY_TERMS = {
  'TR': /\b(TCMB|SPK|BIST|tapu|Sahibinden|Emlakjet|DASK|TEFAS|81 il|81 provinces)\b/,
  'US': /\b(FHFA|FRED|SIPC|401\(k\)|Roth IRA|Zillow|Realtor|Case-Shiller)\b/,
  'DE': /\b(Grunderwerbsteuer|Abgeltungsteuer|Sparer-Pauschbetrag|ImmoScout24|Immowelt|BaFin)\b/,
}

// Keys that may name a country, because they are explicitly about one: the
// per-ticker explainers, the Türkiye-specific broker guide, the glossary.
const COUNTRY_SCOPED = new RegExp([
  '^explainer\\.byTicker',
  '^guide\\.',
  '^dailyTip\\.tips\\.',
  '^glossary\\.',
  '^reit\\.',
  '^market\\.',
].join('|'))

function sourceFiles(dir) {
  const out = []
  for (const entry of readdirSync(dir, { withFileTypes: true })) {
    const full = join(dir, entry.name)
    if (entry.isDirectory()) {
      if (entry.name !== 'locales') out.push(...sourceFiles(full))
    } else if (/\.jsx?$/.test(entry.name) && !entry.name.includes('.test.')) {
      out.push(full)
    }
  }
  return out
}

const SOURCES = sourceFiles(SRC)
const stripComments = (text) => text
  .replace(/\/\*[\s\S]*?\*\//g, '')
  .replace(/^\s*\/\/.*$/gm, '')

describe('shared copy stays country-neutral', () => {
  it('no shared string names one country\'s institutions', () => {
    const leaks = []
    for (const [lang, entries] of Object.entries(FLAT)) {
      for (const [key, value] of Object.entries(entries)) {
        if (typeof value !== 'string' || COUNTRY_SCOPED.test(key)) continue
        for (const [country, pattern] of Object.entries(COUNTRY_TERMS)) {
          const hit = value.match(pattern)
          if (hit) leaks.push(`${lang}:${key} names ${country} ("${hit[0]}")`)
        }
      }
    }
    expect(leaks).toEqual([])
  })

  it('no locale key is named after a country instead of a concept', () => {
    // `province.note_tr` / `note_us` meant a fourth market reading an index
    // would be handed "the US note". Name them for what they describe.
    const named = Object.keys(FLAT.tr).filter(
      key => /(?:^|[._])(?:turkish|turkiye)(?:[._]|$)/i.test(key))
    expect(named).toEqual([])
  })
})

describe('components never hardcode a country', () => {
  it('no component pins a locale to format with', () => {
    // A module-level `new Intl.NumberFormat('tr-TR')` is how a Texas scenario
    // came out as "1.045.283 TL". Formatting comes from the market.
    const offenders = []
    for (const file of SOURCES) {
      if (/useMarket\.js$|MarketContext\.jsx$/.test(file)) continue   // the market layer itself
      const code = stripComments(readFileSync(file, 'utf8'))
      if (/new Intl\.\w+\(\s*['"][a-z]{2}-[A-Z]{2}['"]/.test(code)) {
        offenders.push(file.replace(SRC, 'src'))
      }
    }
    expect(offenders).toEqual([])
  })

  it('no component branches on a specific market code', () => {
    // `pack.code === 'US'` does not generalise to a fourth market. What the
    // branch wanted is a fact the pack should declare.
    const offenders = []
    for (const file of SOURCES) {
      if (/MarketSwitcher\.jsx$|MarketContext\.jsx$/.test(file)) continue
      const code = stripComments(readFileSync(file, 'utf8'))
      const match = code.match(/(?:code|market)\s*===?\s*['"][A-Z]{2}['"]/)
      if (match) offenders.push(`${file.replace(SRC, 'src')}: ${match[0]}`)
    }
    expect(offenders).toEqual([])
  })

  it('the market fallback carries every field a consumer reads', () => {
    // A missing field renders the literal string "undefined" in a
    // placeholder, and a fallback missing `currency_symbol` prints nothing.
    const required = [
      'code', 'name', 'currency', 'currency_symbol', 'locale',
      'live_inflation', 'live_housing_index', 'regional_housing_breakdown',
      'area_kind', 'example_district', 'example_locality',
      'example_ticker', 'example_asset_name',
    ]
    for (const file of ['hooks/useMarket.js', 'contexts/MarketContext.jsx']) {
      const code = readFileSync(join(SRC, file), 'utf8')
      const missing = required.filter(field => !new RegExp(`\\b${field}\\b`).test(code))
      expect({ file, missing }).toEqual({ file, missing: [] })
    }
  })
})
