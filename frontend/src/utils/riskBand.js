// Colours for the risk band keys the server sends with every score
// (`risk_band` in backend/services/risk_engine.py: conservative ≤3,
// balanced ≤6, growth ≤8, aggressive). There are no cut-offs here on purpose:
// a second copy of the thresholds is how the gauge once said "Growth-Focused"
// while the card under it said "Aggressive". The name shown is the server's
// `label`; this file only picks the colour for a fill or a dot (never text).
export const RISK_BAND_COLORS = {
  conservative: 'var(--green)',
  balanced:     'var(--firefly)',
  growth:       'var(--accent)',
  // Deeper than growth's --accent, not red: a high tolerance is not a wrong answer.
  aggressive:   'var(--violet)',
}

// A profile cached before the server sent `band` has no key: neutral colour
// until the next fetch replaces it.
export function bandColor(key) {
  return RISK_BAND_COLORS[key] ?? 'var(--text-dim)'
}
