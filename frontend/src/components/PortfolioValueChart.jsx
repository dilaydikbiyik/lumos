import { useEffect, useState } from 'react'
import { Area, AreaChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { useAuth } from '@clerk/clerk-react'
import api from '../utils/api'
import useMarket from '../hooks/useMarket'
import { readJSON, writeJSON, userKey } from '../utils/storage'

const RANGES = [
  { days: 30, label: '1 Ay' },
  { days: 90, label: '3 Ay' },
  { days: 365, label: '1 Yıl' },
]

/** Daily value of the user's REAL holdings since purchase — live tickers
    follow actual closes; cash/manual assets are carried flat (no fake wiggle). */
export default function PortfolioValueChart({ holdingsCount }) {
  const { money } = useMarket()
  const { userId } = useAuth()
  const [days, setDays] = useState(30)
  const ck = userKey(`history-${days}`, userId)
  const [data, setData] = useState(() => readJSON(ck))
  const [error, setError] = useState(null)

  useEffect(() => {
    if (!holdingsCount) return
    let cancelled = false
    api.get('/holdings/history', { params: { days } })
      .then(res => {
        if (cancelled) return
        setData(res.data); setError(null)
        writeJSON(ck, res.data)
      })
      .catch(() => { if (!cancelled) setError('Değer geçmişi şu an yüklenemedi.') })
    return () => { cancelled = true }
  }, [days, holdingsCount, ck])

  if (!holdingsCount) return null

  const up = (data?.change_amount ?? 0) >= 0
  const color = up ? '#3DD68C' : '#F5515F'

  return (
    <div className="card">
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap', marginBottom: 4 }}>
        <strong style={{ fontSize: 14 }}>Portföyün Nasıl Gidiyor?</strong>
        <div style={{ marginLeft: 'auto', display: 'flex', gap: 4 }}>
          {RANGES.map(r => (
            <button key={r.days} className="btn btn-ghost"
              onClick={() => setDays(r.days)}
              style={{
                padding: '3px 10px', fontSize: 11,
                background: days === r.days ? 'var(--firefly-dim)' : 'transparent',
                color: days === r.days ? 'var(--firefly)' : 'var(--text-dim)',
              }}>
              {r.label}
            </button>
          ))}
        </div>
      </div>

      {error && <p style={{ fontSize: 12, color: 'var(--text-dim)' }}>{error}</p>}

      {data && data.series.length >= 2 && (
        <>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: 10, marginBottom: 8 }}>
            <span className="num-lead">
              {money(data.series[data.series.length - 1].value)}
            </span>
            <span className="num" style={{ fontSize: 'var(--t-small)', fontWeight: 700, color }}>
              {up ? '▲' : '▼'} {money(Math.abs(data.change_amount))} (%{Math.abs(data.change_pct)})
            </span>
          </div>
          <ResponsiveContainer width="100%" height={160}>
            <AreaChart data={data.series} margin={{ top: 4, right: 4, left: 4, bottom: 0 }}>
              <defs>
                <linearGradient id="pvFill" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor={color} stopOpacity={0.35} />
                  <stop offset="100%" stopColor={color} stopOpacity={0} />
                </linearGradient>
              </defs>
              <XAxis dataKey="date" hide />
              <YAxis domain={['auto', 'auto']} hide />
              <Tooltip
                contentStyle={{
                  background: 'var(--bg-card)', border: '1px solid var(--border)',
                  borderRadius: 8, fontSize: 12,
                }}
                formatter={v => [money(v), 'Değer']}
                labelFormatter={d => new Date(d).toLocaleDateString('tr-TR')}
              />
              <Area type="monotone" dataKey="value" stroke={color} strokeWidth={2}
                    fill="url(#pvFill)" animationDuration={500} />
            </AreaChart>
          </ResponsiveContainer>
          <p style={{ fontSize: 11, color: 'var(--text-dim)', marginTop: 6, lineHeight: 1.5 }}>
            {data.live_count > 0 && `${data.live_count} varlık gerçek piyasa kapanışlarını takip ediyor`}
            {data.live_count > 0 && data.flat_count > 0 && ' · '}
            {data.flat_count > 0 && `${data.flat_count} varlık (nakit/manuel) son bilinen değerinde sabit`}
            . Düşüş günleri normaldir — mesele o günlerde satmamak.
          </p>
        </>
      )}
      {data && data.series.length < 2 && !error && (
        <p style={{ fontSize: 12, color: 'var(--text-dim)' }}>
          Grafik, varlıkların birkaç gün veri biriktirince burada belirecek.
        </p>
      )}
    </div>
  )
}
