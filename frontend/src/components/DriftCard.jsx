import { useEffect, useState } from 'react'
import api from '../utils/api'
import { CATEGORY_COLORS, COLORS } from '../utils/palette'
import Icon from './Icon'

const CATEGORY_TR = {
  stocks: 'Hisse / ETF', reit: 'Gayrimenkul', bond: 'Tahvil',
  fund: 'Fon', gold: 'Altın', cash: 'Nakit', other: 'Diğer',
}

const VERDICT = {
  balanced: { color: 'var(--green)', label: 'Dengede' },
  notable:  { color: 'var(--firefly)', label: 'Hafif sapma' },
  serious:  { color: 'var(--red)', label: 'Belirgin sapma' },
}

/**
 * Post-purchase advice: prices move at different speeds, so the mix you bought
 * slowly stops being the mix your risk profile called for. This shows the gap
 * and — importantly — usually says "do nothing yet".
 */
export default function DriftCard({ holdingsCount }) {
  const [data, setData] = useState(null)

  useEffect(() => {
    if (!holdingsCount) return
    let cancelled = false
    api.get('/holdings/drift')
      .then(res => { if (!cancelled) setData(res.data) })
      .catch(() => { /* non-critical */ })
    return () => { cancelled = true }
  }, [holdingsCount])

  if (!holdingsCount || !data?.available) return null
  const v = VERDICT[data.verdict] || VERDICT.balanced

  return (
    <div className="card">
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6 }}>
        <Icon name="target" size={18} color={v.color} />
        <strong style={{ fontSize: 'var(--t-lead)' }}>Portföyün dengede mi?</strong>
        <span className="badge" style={{
          marginLeft: 'auto', background: 'transparent',
          border: `1px solid ${v.color}55`, color: v.color, fontSize: 'var(--t-micro)',
        }}>
          {v.label}
        </span>
      </div>

      <p style={{ fontSize: 'var(--t-small)', lineHeight: 1.65, marginBottom: 12 }}>
        {data.message}
      </p>

      {/* Target vs actual, per category */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
        {data.rows.filter(r => r.actual_pct > 0 || r.target_pct > 0).map((r, i) => {
          const color = CATEGORY_COLORS[r.category] || COLORS[i % COLORS.length]
          return (
            <div key={r.category}>
              <div style={{
                display: 'flex', alignItems: 'baseline', gap: 8,
                fontSize: 'var(--t-micro)', marginBottom: 3,
              }}>
                <span style={{ color: 'var(--text-muted)', flex: 1 }}>
                  {CATEGORY_TR[r.category] || r.category}
                </span>
                <span className="num" style={{ color: 'var(--text-dim)' }}>
                  hedef %{r.target_pct}
                </span>
                <span className="num" style={{ color, fontWeight: 700, minWidth: 46, textAlign: 'right' }}>
                  şu an %{r.actual_pct}
                </span>
              </div>
              {/* target as a faint track, actual as the filled bar */}
              <div style={{ position: 'relative', height: 6, borderRadius: 4, background: 'var(--bg-input)' }}>
                <div style={{
                  position: 'absolute', left: 0, top: 0, bottom: 0,
                  width: `${Math.min(r.target_pct, 100)}%`,
                  borderRight: '2px dashed var(--text-dim)', opacity: 0.5,
                }} />
                <div style={{
                  position: 'absolute', left: 0, top: 0, bottom: 0,
                  width: `${Math.min(r.actual_pct, 100)}%`,
                  background: color, borderRadius: 4, opacity: 0.85,
                }} />
              </div>
            </div>
          )
        })}
      </div>

      <p style={{ fontSize: 'var(--t-micro)', color: 'var(--text-dim)', lineHeight: 1.6, marginTop: 12 }}>
        {data.honesty_note}
      </p>
    </div>
  )
}
