/**
 * Parse a Turkish-formatted money string ("100.000", "1.250.000,50",
 * "30 000") into a number. A plain Number() call reads "30.000" as 30 —
 * that single character turned a 30.000 TL rent into a 7.200 TL home in
 * the rent-vs-buy tool.
 */
export function parseTL(value) {
  if (typeof value === 'number') return value
  const s = String(value ?? '').trim().replace(/\s/g, '')
  if (!s) return NaN
  if (s.includes(',')) {
    // Turkish notation: dots are thousands, comma is the decimal mark
    return Number(s.replace(/\./g, '').replace(',', '.'))
  }
  // No comma: a dot followed by exactly 3 digits is a thousands separator
  // ("100.000" → 100000); anything else ("10.5") is a decimal point.
  if (/^\d{1,3}(\.\d{3})+$/.test(s)) {
    return Number(s.replace(/\./g, ''))
  }
  return Number(s)
}
