// Single source of truth for risk-score bands (1–10) and their colours.
// The cut-offs mirror the server's label (`_label` in backend/services/risk_engine.py:
// ≤3 conservative, ≤6 balanced), so the gauge, the summary card and the allocation
// rationale can never put the same score in different bands.
export const RISK_BANDS = {
  low:    { key: 'low',    max: 3,        color: 'var(--green)',   label: 'profile.bands.low' },
  medium: { key: 'medium', max: 6,        color: 'var(--firefly)', label: 'profile.bands.medium' },
  high:   { key: 'high',   max: Infinity, color: 'var(--accent)',  label: 'profile.bands.high' },
}

export function riskBand(score) {
  if (score <= RISK_BANDS.low.max) return RISK_BANDS.low
  if (score <= RISK_BANDS.medium.max) return RISK_BANDS.medium
  return RISK_BANDS.high
}
