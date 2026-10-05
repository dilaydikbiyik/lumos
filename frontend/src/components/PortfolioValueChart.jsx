import { useEffect, useState } from 'react'
import { Area, AreaChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { useAuth } from '@clerk/clerk-react'
import api from '../utils/api'
import useMarket from '../hooks/useMarket'
import { readJSON, writeJSON, userKey } from '../utils/storage'
import { useTranslation } from 'react-i18next'
import { percent, shortDate } from '../utils/format'

const RANGES = [
  { days: 30, label: 'chart.m1' },
  { days: 90, label: 'chart.m3' },
  { days: 365, label: 'chart.y1' },
]

// Below this the move is noise, and the coach stays quiet. A portfolio that
// is down 0.4% does not need talking down from a ledge.
const MATERIAL_MOVE_PCT = 5

/** Daily value of the user's REAL holdings since purchase — live tickers
    follow actual closes; cash/manual assets are carried flat (no fake wiggle). */
export default function PortfolioValueChart({ holdingsCount }) {
  const { t } = useTranslation()
  const { money } = useMarket()
  const { userId } = useAuth()
  const [days, setDays] = useState(30)
  const ck = userKey(`history-${days}`, userId)
  const [data, setData] = useState(() => readJSON(ck))
  const [error, setError] = useState(false)
  const [coach, setCoach] = useState(null)

  useEffect(() => {
    if (!holdingsCount) return
    let cancelled = false
    api.get('/holdings/history', { params: { days } })
      .then(res => {
        if (cancelled) return
        setData(res.data); setError(false)
        writeJSON(ck, res.data)
      })
      .catch(() => { if (!cancelled) setError(true) })
    return () => { cancelled = true }
  }, [days, holdingsCount, ck])

  const up = (data?.change_amount ?? 0) >= 0
  const color = up ? '#3DD68C' : '#F5515F'
  const move = data?.change_pct ?? 0

  // The grounding note is fetched only when the chart shows a move big
  // enough to unsettle somebody. A calming message beside a 0.4% wobble
  // teaches the reader that the app panics easily; below the threshold the
  // honest response is to say nothing at all.
  const material = Math.abs(move) >= MATERIAL_MOVE_PCT
  useEffect(() => {
    if (!material) return       // nothing fetched, and nothing rendered below
    let cancelled = false
    api.post('/coach/market-move', {
      direction: move < 0 ? 'drop' : 'rise',
      drawdown_pct: Number(move.toFixed(2)),
    })
      .then(res => { if (!cancelled) setCoach(res.data) })
      .catch(() => { /* supporting content; a failure stays invisible */ })
    return () => { cancelled = true }
  }, [move, material])

  if (!holdingsCount) return null

  return (
    <div className="card">
      {/* Title and range on SEPARATE rows. Floated right, the range buttons
          sat in the bottom-right corner of the viewport whenever this card
          scrolled there — the same column the chat and panic buttons occupy,
          which covered "1 Yıl" by roughly 400 square pixels. Measured, not
          guessed. On its own row the control is wider, easier to hit, and
          never under anything. */}
      <div style={{ marginBottom: 8 }}>
        <strong style={{ fontSize: 14 }}>{t('chart.title')}</strong>
        <div style={{ display: 'flex', gap: 4, marginTop: 8 }}>
          {RANGES.map(r => (
            <button key={r.days} className="btn btn-ghost"
              onClick={() => setDays(r.days)}
              style={{
                padding: '3px 10px', fontSize: 11,
                background: days === r.days ? 'var(--firefly-dim)' : 'transparent',
                color: days === r.days ? 'var(--firefly)' : 'var(--text-dim)',
                flex: 1,
              }}>
              {t(r.label)}
            </button>
          ))}
        </div>
      </div>

      {error && <p style={{ fontSize: 12, color: 'var(--text-dim)' }}>{t('chart.error')}</p>}

      {data && data.series.length >= 2 && (
        <>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: 10, marginBottom: 8 }}>
            <span className="num-lead">
              {money(data.series[data.series.length - 1].value)}
            </span>
            <span className="num" style={{ fontSize: 'var(--t-small)', fontWeight: 700, color }}>
              {up ? '▲' : '▼'} {money(Math.abs(data.change_amount))} ({percent(Math.abs(data.change_pct))})
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
                formatter={v => [money(v), t('common.value')]}
                labelFormatter={d => shortDate(d)}
              />
              <Area type="monotone" dataKey="value" stroke={color} strokeWidth={2}
                    fill="url(#pvFill)" animationDuration={500} />
            </AreaChart>
          </ResponsiveContainer>
          <p style={{ fontSize: 11, color: 'var(--text-dim)', marginTop: 6, lineHeight: 1.5 }}>
            {data.live_count > 0 && t('chart.liveNote', { count: data.live_count })}
            {data.live_count > 0 && data.flat_count > 0 && ' · '}
            {data.flat_count > 0 && t('chart.flatNote', { count: data.flat_count })}
            {'. '}{t('chart.dipNote')}
          </p>

          {/* Sits WITH the move rather than on a separate screen: the moment
              somebody needs this is the moment they are looking at the red
              number, and a calming note they have to navigate to is a note
              they read after they have already sold. The wording is keyed to
              their own stated loss tolerance, not to the size of the drop. */}
          {material && coach?.message && (
            <div style={{
              marginTop: 10, padding: '10px 12px', borderRadius: 10,
              border: '1px solid var(--border)', background: 'var(--bg-input)',
              fontSize: 12.5, lineHeight: 1.7,
            }}>
              {coach.message}
            </div>
          )}
        </>
      )}
      {data && data.series.length < 2 && !error && (
        <p style={{ fontSize: 12, color: 'var(--text-dim)' }}>
          {t('chart.pending')}
        </p>
      )}
    </div>
  )
}
