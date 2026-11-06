/**
 * Parse a Turkish-formatted money string ("100.000", "1.250.000,50",
 * "30 000") into a number. A plain Number() call reads "30.000" as 30 —
 * that single character turned a 30.000 TL rent into a 7.200 TL home in
 * the rent-vs-buy tool.
 */
export function parseTL(value) {
  return parseAmount(value, 'tr-TR')
}

function separators(locale) {
  const parts = new Intl.NumberFormat(locale).formatToParts(12345.6)
  return {
    group: parts.find(p => p.type === 'group')?.value ?? ',',
    decimal: parts.find(p => p.type === 'decimal')?.value ?? '.',
  }
}

const escape = (c) => c.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')

/**
 * Parse a money string in the MARKET's own notation. parseTL was the only
 * parser, so an American typing "390,000" — their normal way to write it —
 * had the comma read as a Turkish decimal mark and got 390. Separators come
 * from Intl for the market's locale: "1.250.000,50" in Türkiye and
 * Germany, "1,250,000.50" in the US. A group separator only counts as one
 * in groups of three ("10.5" stays ten and a half everywhere).
 */
export function parseAmount(value, locale = 'tr-TR') {
  if (typeof value === 'number') return value
  const s = String(value ?? '').trim().replace(/[\s\u00a0\u202f]/g, '')
  if (!s) return NaN
  const { group, decimal } = separators(locale)
  if (s.includes(decimal)) {
    const at = s.lastIndexOf(decimal)
    const whole = s.slice(0, at).split(group).join('')
    return Number(`${whole}.${s.slice(at + 1)}`)
  }
  if (new RegExp(`^\\d{1,3}(${escape(group)}\\d{3})+$`).test(s)) {
    return Number(s.split(group).join(''))
  }
  return Number(s)
}
