import { useTranslation } from 'react-i18next'
import { bandColor } from '../utils/riskBand'

/* SVG arc gauge showing risk score 1-10, in the reader's number format (6,6 / 6.6). */
export default function RiskGauge({ score = 5, band, label }) {
  const { t, i18n } = useTranslation()
  const pct = (score - 1) / 9          // 0–1
  const angle = pct * 180              // 0–180 degrees arc
  const r = 70, cx = 100, cy = 90
  const startAngle = Math.PI           // left
  // SVG y grows downward: the upper semicircle is traced by INCREASING the
  // angle from π (π → 2π). Subtracting drew the fill below the track.
  const endAngle = startAngle + (angle * Math.PI / 180)

  const x1 = cx + r * Math.cos(startAngle)
  const y1 = cy + r * Math.sin(startAngle)
  const x2 = cx + r * Math.cos(endAngle)
  const y2 = cy + r * Math.sin(endAngle)

  const color = bandColor(band)

  return (
    <div className="card" style={{ textAlign: 'center' }}>
      <svg viewBox="0 0 200 110" style={{ width: '100%', maxWidth: 240, margin: '0 auto' }}>
        {/* Track */}
        <path
          d={`M ${cx - r} ${cy} A ${r} ${r} 0 0 1 ${cx + r} ${cy}`}
          fill="none" stroke="#2A2B3D" strokeWidth={12} strokeLinecap="round"
        />
        {/* Fill — sweep=1: clockwise over the top, same direction as the track */}
        {angle > 0 && (
          <path
            d={`M ${x1} ${y1} A ${r} ${r} 0 0 1 ${x2} ${y2}`}
            fill="none" style={{ stroke: color }} strokeWidth={12} strokeLinecap="round"
          />
        )}
        {/* Score text */}
        <text x={cx} y={cy - 4} textAnchor="middle" fontSize={28} fontWeight={700} style={{ fill: 'var(--text)' }}>
          {new Intl.NumberFormat(i18n.language, { minimumFractionDigits: 1, maximumFractionDigits: 1 }).format(score)}
        </text>
        <text x={cx} y={cy + 18} textAnchor="middle" fontSize={12} fill="#8B8CA8">
          / 10
        </text>
      </svg>

      <h3 style={{ marginTop: -4 }}>{label}</h3>
      <p style={{ fontSize: 12, marginTop: 4 }}>{t('profile.riskScoreCaption')}</p>
    </div>
  )
}
