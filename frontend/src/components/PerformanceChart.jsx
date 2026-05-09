import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend } from 'recharts'

// Placeholder data — real data fetched from backend cache in Phase 5
function generateMockData(tickers = []) {
  const months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
  return months.map((month, i) => {
    const row = { month }
    tickers.slice(0, 4).forEach(t => {
      row[t] = parseFloat((100 * (1 + (Math.random() - 0.48) * 0.06) ** i).toFixed(2))
    })
    return row
  })
}

const LINE_COLORS = ['#7C6FF7', '#5B8EF0', '#3DD68C', '#F5A524']

export default function PerformanceChart({ tickers = [], selected }) {
  const data = generateMockData(tickers)
  const activeTickers = tickers.slice(0, 4)

  return (
    <div className="card">
      <h3 style={{ marginBottom: 4 }}>12-Month Performance</h3>
      <p style={{ fontSize: 12, marginBottom: 16 }}>Simulated · replace with live cache data</p>
      <ResponsiveContainer width="100%" height={220}>
        <LineChart data={data}>
          <XAxis dataKey="month" tick={{ fontSize: 11, fill: '#8B8CA8' }} axisLine={false} tickLine={false} />
          <YAxis tick={{ fontSize: 11, fill: '#8B8CA8' }} axisLine={false} tickLine={false} width={40} />
          <Tooltip
            contentStyle={{ background: '#13141F', border: '1px solid #2A2B3D', borderRadius: 8, fontSize: 12 }}
            formatter={(v) => [`${v}`, '']}
          />
          {activeTickers.map((t, i) => (
            <Line
              key={t}
              type="monotone"
              dataKey={t}
              stroke={LINE_COLORS[i % LINE_COLORS.length]}
              strokeWidth={selected === t ? 2.5 : 1.5}
              dot={false}
              opacity={selected && selected !== t ? 0.3 : 1}
            />
          ))}
          <Legend wrapperStyle={{ fontSize: 11, paddingTop: 12 }} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
