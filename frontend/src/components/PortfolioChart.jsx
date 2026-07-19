import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from 'recharts'
import { allocationColors } from '../utils/palette'
import AssetCard from './AssetCard'
import { useState } from 'react'




export default function PortfolioChart({ allocations = [], onSliceClick }) {
  const [active, setActive] = useState(null)

  const selectedIndex = allocations.findIndex(a => a.ticker === active)
  const selectedAllocation = selectedIndex >= 0 ? allocations[selectedIndex] : null

  const data = allocations.map(a => ({
    name: a.name,
    ticker: a.ticker,
    value: parseFloat((a.weight * 100).toFixed(1)),
    category: a.category,
  }))

  // Computed once for the whole list so the pie, the legend dot and the
  // percentage of a given asset are always the same colour.
  const colors = allocationColors(allocations)

  function handleClick(entry) {
    const ticker = entry.ticker
    setActive(ticker === active ? null : ticker)
    onSliceClick?.(ticker === active ? null : ticker)
  }


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
            animationDuration={500}
            onClick={handleClick}
            cursor="pointer"
          >
            {data.map((entry, i) => (
              <Cell
                key={entry.ticker}
                fill={colors[i]}
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
            <span style={{ width: 10, height: 10, borderRadius: '50%', background: colors[i], flexShrink: 0 }} />
            <span style={{ fontSize: 13, flex: 1 }}>{d.name}</span>
            {/* Percentage in the exact slice colour — the legend and pie read as one */}
            <span style={{ fontSize: 13, fontWeight: 700, color: colors[i] }}>{d.value}%</span>
          </div>
        ))}
      </div>

      {/* Quick glance card — appears right under the chart, in the slice colour */}
      {selectedAllocation && (
        <AssetCard allocation={selectedAllocation} index={selectedIndex}
                   color={colors[selectedIndex]} onClose={() => setActive(null)} />
      )}

    </div>
  )
}
