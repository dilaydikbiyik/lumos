/**
 * The numbers a teaching example about inflation needs, from the reader's own
 * market rather than from Türkiye.
 *
 * The copy used to read "%50 enflasyonda 100 TL" — both the rate and the unit
 * were Turkish facts, so a German reader whose inflation runs near 2% was
 * being taught with someone else's arithmetic. `eroded` is what 100 is worth
 * after a year at that rate, computed rather than written down so the
 * sentence cannot contradict its own figure.
 */
export function inflationExample(pack) {
  const rate = pack?.inflation_pct ?? 40
  return {
    rate: Math.round(rate),
    eroded: Math.round(100 / (1 + rate / 100)),
  }
}
