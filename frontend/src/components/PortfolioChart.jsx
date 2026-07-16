import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from 'recharts'
import AssetCard from './AssetCard'
import { useState } from 'react'

const COLORS = ['#7C6FF7', '#5B8EF0', '#3DD68C', '#F5A524', '#F5515F', '#A78BFA', '#34D399']

// Pie-slice palette — gece / ateşböceği(altın) / kahve / ember / teal / mor.
// Gold stays amber (a gold asset shown in any other colour reads wrong).
const CATEGORY_COLORS = {
  gold:   '#F5A524',  // ateşböceği amber
  stocks: '#E8663F',  // ember
  reit:   '#7A4A93',  // mor / erik
  bond:   '#1FB2A6',  // teal
  cash:   '#9C5A34',  // kahve (V5 palette)
  fund:   '#3DD68C',
}

export default function PortfolioChart({ allocations = [], onSliceClick }) {
  const [active, setActive] = useState(null)

  const data = allocations.map(a => ({
    name: a.name,
    ticker: a.ticker,
    value: parseFloat((a.weight * 100).toFixed(1)),
    category: a.category,
  }))

  function handleClick(entry) {
    const ticker = entry.ticker
    setActive(ticker === active ? null : ticker)
    onSliceClick?.(ticker === active ? null : ticker)
  }

  const selectedAllocation = allocations.find(a => a.ticker === active)

  return (
    <div className="card">
      <h3 style={{ marginBottom: 16 }}>Dağılımın</h3>
      <ResponsiveContainer width="100%" height={240}>
        <PieChart>
          <Pie
            data={data}
            cx="50%" cy="50%"
            innerRadius={60} outerRadius={95}
            paddingAngle={3}
            dataKey="value"
            onClick={handleClick}
            cursor="pointer"
          >
            {data.map((entry, i) => (
              <Cell
                key={entry.ticker}
                fill={CATEGORY_COLORS[entry.category] || COLORS[i % COLORS.length]}
                opacity={active && active !== entry.ticker ? 0.4 : 1}
                stroke={active === entry.ticker ? '#fff' : 'transparent'}
                strokeWidth={2}
              />
            ))}
          </Pie>
          <Tooltip
            formatter={(v) => [`${v}%`]}
            contentStyle={{ background: '#13141F', border: '1px solid #2A2B3D', borderRadius: 8, fontSize: 13 }}
          />
        </PieChart>
      </ResponsiveContainer>

      {/* Legend rows */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 6, marginTop: 8 }}>
        {data.map((d, i) => (
          <div
            key={d.ticker}
            style={{
              display: 'flex', alignItems: 'center', gap: 10,
              cursor: 'pointer', opacity: active && active !== d.ticker ? 0.5 : 1,
              padding: '4px 8px', borderRadius: 6,
              background: active === d.ticker ? 'var(--bg-input)' : 'transparent',
            }}
            onClick={() => handleClick(d)}
          >
            <span style={{ width: 10, height: 10, borderRadius: '50%', background: CATEGORY_COLORS[d.category] || COLORS[i % COLORS.length], flexShrink: 0 }} />
            <span style={{ fontSize: 13, flex: 1 }}>{d.name}</span>
            {/* Percentage in the exact slice colour — the legend and pie read as one */}
            <span style={{ fontSize: 13, fontWeight: 700, color: CATEGORY_COLORS[d.category] || COLORS[i % COLORS.length] }}>{d.value}%</span>
          </div>
        ))}
      </div>

      {/* Asset detail card */}
      {selectedAllocation && (
        <AssetCard allocation={selectedAllocation} onClose={() => setActive(null)} />
      )}
    </div>
  )
}
