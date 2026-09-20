/**
 * Whether what the user typed is the confirmation word.
 *
 * Case-folded with an EXPLICIT locale. Both halves of that matter.
 *
 * Explicit, because the obvious `toLocaleUpperCase()` uses whatever locale
 * the runtime happens to be in: `'sil'.toLocaleUpperCase()` is "SIL" with a
 * dotless I, which is not the Turkish confirm word "SİL". A Turkish user
 * typing in lower case could not arm the button at all, and nothing on screen
 * explained why.
 *
 * And a locale rather than a collation comparison, because `localeCompare`
 * with base sensitivity answers differently depending on the ambient locale —
 * it matched "SIL" to "SİL" under Node's default and refused under the
 * browser's Turkish one. The last gate before an irreversible delete cannot
 * behave differently on two devices.
 *
 * Case is ignored. Diacritics are not: "loschen" is not "LÖSCHEN", and "SIL"
 * is not "SİL". The word still has to be the right word.
 */
export function confirmationMatches(typed, phrase, lang = 'en') {
  const value = (typed || '').trim()
  if (!value || !phrase) return false
  return value.toLocaleUpperCase(lang) === phrase.toLocaleUpperCase(lang)
}
