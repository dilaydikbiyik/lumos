import { describe, it, expect } from 'vitest'
import { readFileSync, readdirSync } from 'fs'
import { join } from 'path'

/**
 * Every field in a card uses the app's own input styling.
 *
 * REPORTED TWICE. "Plot or portfolio?" and "Check a listing's price" sat
 * under the rent-vs-buy card looking like a different app: they were written
 * with bare <input> and <select>, so they inherited none of `.input` — no
 * touch-target height, no background, no border, no 16px type (which is also
 * what stops iOS zooming on focus).
 *
 * A styling slip is invisible to every other test in this suite, and reading
 * a diff will not catch it either — the markup looks perfectly reasonable.
 * So it is checked as a rule over the source: a field inside a component is
 * either styled by the app or deliberately exempt.
 */
const DIR = 'src/components'

// Fields that legitimately carry their own styling. Each is a decision, and
// the point of naming them is that adding one is also a decision.
const EXEMPT = new Set([
  'DeleteAccount.jsx',   // the confirmation field in a danger zone
  'StructuredQuiz.jsx',  // the quiz lays its own single-question form out
  // The shared header control, deliberately compact: `.input` is sized for a
  // touch target in a form and would eat a third of a 375px header.
  'HeaderSelect.jsx',
])

function fields(source) {
  // Opening tags only, with whatever attributes follow on the same or the
  // next lines until the tag closes.
  return [...source.matchAll(/<(input|select)\b([^>]*)>/gs)]
}

describe('card fields use the app input styling', () => {
  const files = readdirSync(DIR).filter(f => f.endsWith('.jsx') && !EXEMPT.has(f))

  it.each(files)('%s', file => {
    const source = readFileSync(join(DIR, file), 'utf8')
    const offenders = fields(source)
      .filter(([, , attrs]) => {
        // Checkboxes and radios are not text fields and `.input` would size
        // them wrongly; they are styled where they are used.
        if (/type=["'](checkbox|radio)["']/.test(attrs)) return false
        return !/className=["'][^"']*\binput\b/.test(attrs)
      })
      .map(([match]) => match.replace(/\s+/g, ' ').slice(0, 70))

    expect(offenders, `${file} has unstyled field(s):\n${offenders.join('\n')}`)
      .toEqual([])
  })
})

/**
 * No component writes a percent sign next to a number.
 *
 * Percent placement belongs to the reading LANGUAGE: Turkish writes %45,
 * English 45%, German 45 %. `format.js` was written to fix exactly this and
 * says so in its own docstring — and twenty-one places still built the
 * English form by hand, `{value}%`, including the portfolio chart's legend.
 * So every Turkish reader, in the app's primary language, saw the wrong form
 * on most screens.
 *
 * `percent()` and `signedPercent()` produce it correctly, sign included, in
 * all three. This checks the rule over the source because the mistake is
 * invisible in English — which is the language a reviewer reads the diff in.
 */
const PERCENT_DIRS = ['src/components', 'src/pages']

describe('percent signs come from the formatter', () => {
  const files = PERCENT_DIRS.flatMap(dir =>
    readdirSync(dir).filter(f => f.endsWith('.jsx')).map(f => [dir, f]))

  it.each(files)('%s/%s', (dir, file) => {
    const source = readFileSync(join(dir, file), 'utf8')
    // Matched WITH leading context, because a bar's `width: ${pct}%` looks
    // identical to displayed text until you can see what precedes it — and
    // every one of those is a legitimate CSS percentage.
    const offenders = [...source.matchAll(/.{0,45}\{[^{}]+\}\s*%/gs)]
      .map(([m]) => m.replace(/\s+/g, ' ').trim())
      .filter(m => !/width|height|calc|translate|background|flex|top:|left:/.test(m))

    expect(offenders, `${file} writes a percent sign by hand:\n${offenders.join('\n')}`)
      .toEqual([])
  })
})

// ── touch targets ───────────────────────────────────────────────────────────
//
// Apple asks for 44x44pt and Google for 48dp. The onboarding footer's privacy
// and terms links were 118x15 with no padding at all — MEASURED in a 375px
// viewport, not guessed — and they are the two links a store reviewer taps
// first. The legal page's own back-links were 20px tall for the same reason.
//
// There is no DOM in this suite, so the rendered height cannot be asserted
// here. What CAN be asserted is the thing whose absence caused it: a link
// inside a <nav> that declares no minHeight is one nobody sized on purpose.
describe('navigation links are sized for a thumb', () => {
  // Relative, like DIR above — this file already runs from the frontend
  // root, and process.cwd() is not a global eslint allows here.
  const PAGES = 'src/pages'
  const pages = readdirSync(PAGES).filter(f => f.endsWith('.jsx'))

  for (const file of pages) {
    const code = readFileSync(join(PAGES, file), 'utf8')
    const navs = [...code.matchAll(/<nav[\s\S]*?<\/nav>/g)].map(m => m[0])
    if (!navs.length) continue

    it(`${file} sizes every nav link`, () => {
      const unsized = []
      for (const nav of navs) {
        for (const link of nav.match(/<(?:Link|a)\b[\s\S]*?>/g) || []) {
          if (!/minHeight/.test(link)) unsized.push(link.replace(/\s+/g, ' ').slice(0, 70))
        }
      }
      expect(unsized, 'nav links with no declared minHeight').toEqual([])
    })
  }
})
