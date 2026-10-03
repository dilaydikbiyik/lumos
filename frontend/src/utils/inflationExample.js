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


/**
 * The numbers a REAL-RETURN example needs, from the reader's own market.
 *
 * The copy read "you made 45% but inflation was 60%" and "I gained 300% but
 * inflation was 320%" — in all three languages, so this was never a
 * translation slip. Those are Türkiye-scale figures, and to a German reader
 * whose inflation runs near 2% they are not a lesson, they are noise. The
 * point being taught is that a nominal gain BELOW inflation is a real loss,
 * and that point holds at any scale once the numbers are the reader's own.
 *
 * `nominal` sits visibly under `inflation` on purpose: the whole example
 * falls apart if the two round to the same figure.
 */
export function realReturnExample(pack) {
  const inflation = Math.max(Math.round(pack?.inflation_pct ?? 40), 2)
  return {
    inflation,
    nominal: Math.max(Math.round(inflation * 0.7), 1),
  }
}
