import { describe, it, expect } from 'vitest'
import tr from './tr.json'
import en from './en.json'
import de from './de.json'

/**
 * No UI string may name a currency.
 *
 * THE BUG THIS EXISTS FOR. A reader in the GERMAN market, using the Turkish
 * UI, was shown "100000 TL ile 127 şehirde konut alsaydım". The code was
 * fine; the Turkish translation had " TL" typed into it, so the unit came
 * from the LANGUAGE instead of the MARKET. Language and market are
 * independent axes, and a currency belongs to the market — every other
 * market-coupling bug in this app has been the same mistake wearing a
 * different hat.
 *
 * The rule: format amounts with `money()`, which reads the market pack, and
 * never write a unit into copy. A string that needs a unit is a string that
 * has decided which country its reader is in.
 */
const FORBIDDEN = [
  { name: 'TL', re: /(^|[\s(])TL([\s.,;:!?)]|$)/ },
  { name: '₺', re: /₺/ },
  { name: 'TRY', re: /(^|[\s(])TRY([\s.,;:!?)]|$)/ },
  { name: '$', re: /\$(?!\{)/ },
  { name: 'USD', re: /(^|[\s(])USD([\s.,;:!?)]|$)/ },
  { name: '€', re: /€/ },
  { name: 'EUR', re: /(^|[\s(])EUR([\s.,;:!?)]|$)/ },
]

// Keys that legitimately NAME a currency rather than denominate an amount —
// the currency-exposure chart's own legend, for instance, is about the
// currencies themselves. Each one is listed deliberately; the point of an
// allowlist is that adding to it is a decision somebody makes on purpose.
const ALLOWED_KEYS = [
  /^fx\./,            // currency exposure: the subject IS the currency
  /^market\./,        // the market picker names markets and their currencies
  /^currency\./,
]

/**
 * Strings that still name a currency. THE LIST IS EMPTY, and may only grow
 * by a decision somebody makes on purpose.
 *
 * It held fifteen entries. Most were the reported bug on other screens — a
 * unit typed into Turkish copy, so it followed the LANGUAGE rather than the
 * MARKET. The last two were the SPY notes, which were a different problem
 * wearing the same hat: the Turkish text framed a dollar ETF as "a shield
 * against the lira melting" and the English text said nothing, so a Turkish
 * reader in the US market was warned about an exposure they do not have and
 * an English reader in the Turkish market, who carries it in full, was not
 * warned at all. Currency risk now comes from the asset's own currency
 * against the reader's market — see `explainer.fxExposure`.
 */
const KNOWN_OFFENDERS = [
]

function flatten(obj, prefix = '') {
  return Object.entries(obj).flatMap(([k, v]) => {
    const key = prefix ? `${prefix}.${k}` : k
    return typeof v === 'object' && v !== null
      ? flatten(v, key)
      : [[key, String(v)]]
  })
}

describe.each([['tr', tr], ['en', en], ['de', de]])('%s copy', (lang, bundle) => {
  it('never writes a currency unit into a translated string', () => {
    const offenders = []
    for (const [key, value] of flatten(bundle)) {
      if (ALLOWED_KEYS.some(re => re.test(key))) continue
      if (KNOWN_OFFENDERS.includes(key)) continue
      for (const { name, re } of FORBIDDEN) {
        if (re.test(value)) offenders.push(`${key} contains ${name}: "${value.slice(0, 80)}"`)
      }
    }
    expect(offenders, offenders.join('\n')).toEqual([])
  })
})

/**
 * No TEACHING EXAMPLE may hardcode a market-scale rate.
 *
 * The same bug as the currency one, one step further out. "You made 45% but
 * inflation was 60%" and "I gained 300% but inflation was 320%" were written
 * into all three languages, so this was never a translation slip — the
 * EXAMPLE itself was Türkiye-scale. To a German reader whose inflation runs
 * near 2% those figures are not a lesson, they are noise. The point being
 * taught survives at any scale once the numbers come from the reader's own
 * market, which is what `realReturnExample` and `inflationExample` do.
 *
 * Scoped to the keys that WORK AN EXAMPLE. Plenty of other copy names a
 * number legitimately — QQQ really did fall 33% in 2022, EUNL really is
 * about 70% United States — and those are facts about an asset rather than
 * assumptions about a reader.
 */
const EXAMPLE_KEYS = [
  'glossary.reel getiri.text',
  'glossary.enflasyon.text',
  'dailyTip.tips.reel-return.body',
  'dailyTip.tips.inflation.body',
  'onboarding.features.realReturn.desc',
]

describe.each([['tr', tr], ['en', en], ['de', de]])('%s teaching examples', (lang, bundle) => {
  it('take their rates from the market rather than hardcoding them', () => {
    const flat = Object.fromEntries(flatten(bundle))
    const offenders = []
    for (const key of EXAMPLE_KEYS) {
      const value = flat[key]
      expect(value, `${key} is missing from ${lang}`).toBeDefined()
      // A bare two-or-three digit percentage means a rate was written down.
      const bare = value.replace(/\{\{\w+\}\}/g, '')
      if (/%\s?\d{2,}|\b\d{2,}\s?%/.test(bare)) offenders.push(`${key}: "${value.slice(0, 80)}"`)
    }
    expect(offenders, offenders.join('\n')).toEqual([])
  })
})
