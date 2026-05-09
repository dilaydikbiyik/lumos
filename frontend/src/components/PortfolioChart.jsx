import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend } from 'recharts'
import AssetCard from './AssetCard'
import { useState } from 'react'

const COLORS = ['#7C6FF7', '#5B8EF0', '#3DD68C', '#F5A524', '#F5515F', '#A78BFA', '#34D399']

const CATEGORY_COLORS = {
  stocks: '#7C6FF7',
  reit:   '#5B8EF0',
  fund:   '#3DD68C',
  gold:   '#F5A524',
  cash:   '#8B8CA8',
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
      <h3 style={{ marginBottom: 16 }}>Portfolio Allocation</h3>
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
            <span style={{ fontSize: 13, fontWeight: 600, color: 'var(--accent)' }}>{d.value}%</span>
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
