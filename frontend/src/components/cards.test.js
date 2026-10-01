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
