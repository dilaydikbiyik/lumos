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
 * Strings that still name a currency, recorded so the suite is honest rather
 * than green by omission. THIS LIST MAY ONLY SHRINK — anything new fails.
 *
 * Two different problems are parked here and they need different fixes:
 *
 *   GENUINELY ABOUT THE LIRA. The inflation glossary works an example in
 *   lira, and the SPY risk note is about what happens to a Turkish reader's
 *   purchasing power when the dollar moves. Rewriting those to a generic
 *   unit would make them vaguer, not more correct — they need a per-market
 *   example, which is a content change rather than a formatting one.
 *
 *   ACTUAL BUGS, same shape as the one this file was written for: the
 *   what-if prompts and the quiz intro hardcode a unit into copy and will
 *   show TL to a German reader exactly as the explore card did.
 */
const KNOWN_OFFENDERS = [
  'dailyTip.tips.inflation.body',
  'explainer.byTicker.SPY.risk',
  'explainer.byTicker.SPY.why',
  'glossary.enflasyon.text',
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
