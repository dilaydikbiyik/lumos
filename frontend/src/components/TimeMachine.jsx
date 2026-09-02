import { useState } from 'react'
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'
import api from '../utils/api'
import IsikTut from './IsikTut'
import useMarket from '../hooks/useMarket'
import { Trans, useTranslation } from 'react-i18next'

/**
 * Time Machine — "what if you had built this portfolio N years ago?"
 * Honest framing: shows the worst moment with the user's own money,
 * not just the happy final number.
 */
export default function TimeMachine({ allocations, budget }) {
  const { t } = useTranslation()
  const { money } = useMarket()
  const [result, setResult] = useState(null)
  const [period, setPeriod] = useState('5y')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  async function run(selected) {
    setPeriod(selected)
    setLoading(true)
    setError(null)
    try {
      const weights = Object.fromEntries(allocations.map(a => [a.ticker, a.weight]))
      const res = await api.post('/backtest', { weights, budget, period: selected })
      setResult(res.data)
    } catch {
      setError(t('timeMachine.error'))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="card">
      <h3 style={{ marginBottom: 4 }}>{t('timeMachine.title')}</h3>
      <p style={{ fontSize: 13, marginBottom: 12, opacity: 0.8 }}>
        <Trans i18nKey="timeMachine.subtitle"
               components={[<IsikTut key="a" term="drawdown" />]} />
      </p>

      <div style={{ display: 'flex', gap: 8, marginBottom: 12 }}>
        {['1y', '3y', '5y'].map(p => (
          <button
            key={p}
            className={`btn ${result && period === p ? 'btn-primary' : 'btn-ghost'}`}
            onClick={() => run(p)}
            disabled={loading}
            style={{ flex: 1 }}
          >
            {t('timeMachine.years', { n: p.replace('y', '') })}
          </button>
        ))}
      </div>

      {loading && (
        <div style={{ textAlign: 'center', padding: 20 }}>
          <span className="spinner" style={{ width: 26, height: 26 }} />
        </div>
      )}
      {error && <p style={{ color: 'var(--red)', fontSize: 13 }}>{error}</p>}

      {result && !loading && (
        <>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10, marginBottom: 12 }}>
            <div>
              <div style={{ fontSize: 12, opacity: 0.7 }}>{t('timeMachine.wouldBe', { amount: money(result.start_value) })}</div>
              <div style={{
                fontSize: 20, fontWeight: 700,
                color: result.total_return_pct >= 0 ? 'var(--green, #4ade80)' : 'var(--red)',
              }}>
                {money(result.final_value)} ({result.total_return_pct > 0 ? '+' : ''}{result.total_return_pct}%)
              </div>
              {result.real_return_pct != null && (
                <div style={{ fontSize: 11, opacity: 0.65, marginTop: 2 }}>
                  <Trans i18nKey="timeMachine.afterInflation"
                         components={[<IsikTut key="a" term="reel getiri" />]} />: {result.real_return_pct > 0 ? '+' : ''}{result.real_return_pct}%
                </div>
              )}
            </div>
            <div>
              <div style={{ fontSize: 12, opacity: 0.7 }}>{t('timeMachine.worstMoment')}</div>
              <div style={{ fontSize: 20, fontWeight: 700, color: 'var(--red)' }}>
                {money(result.worst_value)} ({result.max_drawdown_pct}%)
              </div>
            </div>
          </div>

          <div style={{ height: 160 }}>
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={result.chart}>
                <XAxis dataKey="date" hide />
                <YAxis hide domain={['auto', 'auto']} />
                <Tooltip formatter={v => [money(v), t('common.value')]} labelStyle={{ color: '#333' }} />
                <Line type="monotone" dataKey="value" stroke="#8b8bf5" dot={false} strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </div>

          <p style={{ fontSize: 13, marginTop: 10, lineHeight: 1.6 }}>
            {result.max_drawdown_pct <= -15
              ? t('timeMachine.roughRide', {
                  lost: money(result.start_value - result.worst_value),
                  outcome: result.total_return_pct >= 0
                    ? t('timeMachine.inProfit') : t('timeMachine.recovering'),
                })
              : t('timeMachine.calmRide')}
          </p>
        </>
      )}
    </div>
  )
}
