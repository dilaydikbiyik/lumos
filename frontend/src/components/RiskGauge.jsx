/* SVG arc gauge showing risk score 1-10 */
export default function RiskGauge({ score = 5, label = 'Moderate' }) {
  const pct = (score - 1) / 9          // 0–1
  const angle = pct * 180              // 0–180 degrees arc
  const r = 70, cx = 100, cy = 90
  const startAngle = Math.PI           // left
  const endAngle = startAngle - (angle * Math.PI / 180)

  const x1 = cx + r * Math.cos(startAngle)
  const y1 = cy + r * Math.sin(startAngle)
  const x2 = cx + r * Math.cos(endAngle)
  const y2 = cy + r * Math.sin(endAngle)

  const largeArc = angle > 180 ? 1 : 0

  const colorMap = [
    '#3DD68C', '#3DD68C', '#3DD68C',   // 1-3 green
    '#F5A524', '#F5A524', '#F5A524',   // 4-6 amber
    '#F5515F', '#F5515F', '#F5515F', '#F5515F' // 7-10 red
  ]
  const color = colorMap[Math.round(score) - 1] || '#7C6FF7'

  return (
    <div className="card" style={{ textAlign: 'center' }}>
      <svg viewBox="0 0 200 110" style={{ width: '100%', maxWidth: 240, margin: '0 auto' }}>
        {/* Track */}
        <path
          d={`M ${cx - r} ${cy} A ${r} ${r} 0 0 1 ${cx + r} ${cy}`}
          fill="none" stroke="#2A2B3D" strokeWidth={12} strokeLinecap="round"
        />
        {/* Fill */}
        {angle > 0 && (
          <path
            d={`M ${x1} ${y1} A ${r} ${r} 0 ${largeArc} 0 ${x2} ${y2}`}
            fill="none" stroke={color} strokeWidth={12} strokeLinecap="round"
          />
        )}
        {/* Score text */}
        <text x={cx} y={cy - 4} textAnchor="middle" fontSize={28} fontWeight={700} fill={color}>
          {score.toFixed(1)}
        </text>
        <text x={cx} y={cy + 18} textAnchor="middle" fontSize={12} fill="#8B8CA8">
          / 10
        </text>
      </svg>

      <h3 style={{ marginTop: -4 }}>{label}</h3>
      <p style={{ fontSize: 12, marginTop: 4 }}>Your risk score</p>
    </div>
  )
}
