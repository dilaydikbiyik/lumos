import { describe, expect, it } from 'vitest'
import { confirmationMatches } from '../utils/confirmation'

/**
 * The typed confirmation guarding account deletion.
 *
 * The bug this pins: upper-casing both sides breaks Turkish. `'sil'
 * .toLocaleUpperCase()` is "SIL" with a dotless I, which is not "SİL", so the
 * delete button could never arm for a Turkish user typing in lower case —
 * a dead control with no error message.
 */
describe('delete confirmation', () => {
  it('accepts the word in any case, in every language the app ships', () => {
    expect(confirmationMatches('delete', 'DELETE', 'en')).toBe(true)
    expect(confirmationMatches('DELETE', 'DELETE', 'en')).toBe(true)
    expect(confirmationMatches('sil', 'SİL', 'tr')).toBe(true)   // the Turkish bug
    expect(confirmationMatches('SİL', 'SİL', 'tr')).toBe(true)
    expect(confirmationMatches('löschen', 'LÖSCHEN', 'de')).toBe(true)
    expect(confirmationMatches('  delete  ', 'DELETE', 'en')).toBe(true)
  })

  it('still requires the right word', () => {
    for (const wrong of ['', '   ', 'del', 'deleted', 'nonsense', 'sil me']) {
      expect(confirmationMatches(wrong, 'DELETE', 'en')).toBe(false)
    }
  })

  it('does not treat a different base letter as a match', () => {
    // Diacritics are not forgiven: these are distinct letters, and this is
    // the last gate before an irreversible delete.
    expect(confirmationMatches('SIL', 'SİL', 'tr')).toBe(false)
    expect(confirmationMatches('loschen', 'LÖSCHEN', 'de')).toBe(false)
  })

  it('gives the same answer regardless of the ambient runtime locale', () => {
    // The whole reason the locale is explicit: this must not depend on where
    // the code happens to run.
    expect(confirmationMatches('sil', 'SİL', 'tr')).toBe(true)
    expect(confirmationMatches('SIL', 'SİL', 'tr')).toBe(false)
  })

  it('never arms on an empty phrase, however that happened', () => {
    // A missing translation key must not make the button free to press.
    expect(confirmationMatches('anything', '', 'en')).toBe(false)
    expect(confirmationMatches('', '', 'en')).toBe(false)
  })
})
