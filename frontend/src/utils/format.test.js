import { describe, expect, it, vi, beforeEach } from 'vitest'
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

vi.mock('../i18n', () => ({ default: { language: 'en' } }))

const { percent, percentFromWeight, shortDate } = await import('./format')
const i18n = (await import('../i18n')).default

const SRC = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')

beforeEach(() => { i18n.language = 'en' })

describe('percent placement follows the reading language', () => {
  it('puts the sign where each language puts it', () => {
    i18n.language = 'en'
    expect(percent(25)).toBe('25%')

    // Turkish writes the sign FIRST. Seven components had this form
    // hardcoded, so an English reader saw "%60" on a US portfolio.
    i18n.language = 'tr'
    expect(percent(25)).toBe('%25')

    // German separates it with a (non-breaking) space.
    i18n.language = 'de'
    expect(percent(25).replace(/\s/g, ' ')).toBe('25 %')
  })

  it('converts a 0–1 allocation weight, not just a 0–100 number', () => {
    i18n.language = 'en'
    expect(percentFromWeight(0.6)).toBe('60%')
    expect(percent(60)).toBe('60%')
  })

  it('renders nothing rather than NaN for a missing value', () => {
    for (const bad of [null, undefined, '', 'abc']) {
      expect(percent(bad)).toBe('')
      expect(percentFromWeight(bad)).toBe('')
      expect(shortDate(bad)).toBe('')
    }
  })
})

describe('dates follow the app language, not the browser', () => {
  it('formats the same instant differently per language', () => {
    const iso = '2026-03-09'
    i18n.language = 'en'
    const en = shortDate(iso)
    i18n.language = 'de'
    const de = shortDate(iso)
    expect(en).not.toBe(de)
    // Both must name the same day; only the wording changes.
    expect(en).toContain('2026')
    expect(de).toContain('2026')
  })

  it('survives an unparseable date', () => {
    expect(shortDate('not-a-date')).toBe('')
  })
})

describe('no component hardcodes a percent sign', () => {
  it('has no "%{" literal left in any source file', () => {
    const offenders = []
    const walk = (dir) => {
      for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
        const full = path.join(dir, entry.name)
        if (entry.isDirectory()) { walk(full); continue }
        if (!/\.(jsx?|tsx?)$/.test(entry.name) || entry.name.includes('.test.')) continue
        const text = fs.readFileSync(full, 'utf8')
        // "%{" in JSX is the Turkish prefix glued to an interpolation. It is
        // correct Turkish and wrong in every other language the app ships.
        if (text.includes('%{')) offenders.push(path.relative(SRC, full))
      }
    }
    walk(SRC)
    expect(offenders).toEqual([])
  })
})
