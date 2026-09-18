import { describe, it, expect } from 'vitest'
import { readFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

/**
 * Language and market are independent axes.
 *
 * An expat in Istanbul wants the English UI with Turkish market data; a Turk
 * in Berlin may want the opposite. Neither setting may imply the other —
 * picking the Turkish market must not flip anyone into Turkish, and reading
 * in English must not move anyone's money to the US.
 *
 * This is checked at the source level rather than by rendering, because the
 * failure mode is one line of coupling being added back later: a
 * `setLanguage(pack.languages[0])` inside the market switcher would look
 * helpful and quietly undo the whole separation.
 */

const here = dirname(fileURLToPath(import.meta.url))
const read = (path) => readFileSync(resolve(here, path), 'utf8')

/** Source with comments stripped: a doc comment explaining the separation
    must not read as the coupling it is warning against. */
const code = (path) => read(path)
  .replace(/\/\*[\s\S]*?\*\//g, '')
  .replace(/^\s*\/\/.*$/gm, '')

describe('language and market stay independent', () => {
  it('the market layer never changes the language', () => {
    for (const path of ['./contexts/MarketContext.jsx', './components/MarketSwitcher.jsx']) {
      const source = code(path)
      expect({ path, touchesLanguage: /setLanguage|changeLanguage|from '\.\.?\/i18n'/.test(source) })
        .toEqual({ path, touchesLanguage: false })
    }
  })

  it('the language layer never changes the market', () => {
    for (const path of ['./i18n.js', './components/LanguageSwitcher.jsx']) {
      const source = code(path)
      expect({ path, touchesMarket: /setMarket|useMarket|MarketContext/.test(source) })
        .toEqual({ path, touchesMarket: false })
    }
  })

  it('the initial language comes from the device, never from a market', () => {
    const source = code('./i18n.js')
    // Browser language and the stored preference are the only inputs.
    expect(source).toMatch(/navigator\.language/)
    expect(source).toMatch(/lumos-language/)
    expect(source).not.toMatch(/market/i)
  })

  it('both switchers are offered together, so neither looks like the other', () => {
    // If only one were reachable on a surface, users would reasonably assume
    // the missing one follows from it.
    for (const path of ['./components/AppHeader.jsx', './components/AppNav.jsx']) {
      const source = read(path)
      expect({ path, hasBoth: /MarketSwitcher/.test(source) && /LanguageSwitcher/.test(source) })
        .toEqual({ path, hasBoth: true })
    }
  })
})
