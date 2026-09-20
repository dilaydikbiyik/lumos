import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import api, { extractErrorMessage } from '../utils/api'
import useMarket from '../hooks/useMarket'

/**
 * "A 500,000 plot, or a 500,000 portfolio?"
 *
 * The question the hybrid path exists to answer. Both sides are BACKWARD
 * looking — the region's own price index against a real backtest of the
 * reader's own allocation — because a forecast comparison is two guesses
 * dressed as an answer, and the side with the friendlier assumptions always
 * wins one of those.
 *
 * The cost lines are shown rather than folded into the total. Property pays
 * transfer tax, commission and upkeep that a portfolio does not, and a
 * reader who cannot see which costs were charged to which side has no reason
 * to believe the totals.
 */
export default function PropertyVsPortfolio({ regions = [] }) {
  const { t } = useTranslation()
  const { money, pack } = useMarket()
  const [region, setRegion] = useState('')
  const [amount, setAmount] = useState('')
  const [period, setPeriod] = useState('5y')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  async function run(e) {
    e.preventDefault()
    const value = Number(String(amount).replace(/[^\d]/g, ''))
    if (!region || !value || loading) return
    setLoading(true)
    setError(null)
    setResult(null)
    try {
      const { data } = await api.get('/planning/property-vs-portfolio', {
        params: { region, amount: value, period },
      })
      if (data.available === false) setError(data.reason)
      else setResult(data)
    } catch (err) {
      setError(extractErrorMessage(err))
    } finally {
      setLoading(false)
    }
  }

  const winner = result
    && (result.property.real_return_pct >= result.portfolio.real_return_pct
      ? 'property' : 'portfolio')

  return (
    <div className="card">
      <h3 style={{ margin: '0 0 4px', fontSize: '1rem' }}>⚖️ {t('vsCompare.title')}</h3>
      <p style={{ fontSize: 13, opacity: 0.8, marginTop: 0 }}>{t('vsCompare.subtitle')}</p>

      <form onSubmit={run} style={{ display: 'grid', gap: 8, marginTop: 10 }}>
        <select
          value={region}
          onChange={e => setRegion(e.target.value)}
          aria-label={t(`explore.areaKind.${pack?.area_kind || 'region'}`, {
            defaultValue: t('vsCompare.area'),
          })}
        >
          <option value="">{t('vsCompare.pickArea')}</option>
          {regions.map(r => (
            <option key={r.code} value={r.code}>{r.name}</option>
          ))}
        </select>

        <input
          value={amount}
          onChange={e => setAmount(e.target.value)}
          inputMode="numeric"
          placeholder={t('vsCompare.amountPlaceholder')}
          aria-label={t('vsCompare.amountPlaceholder')}
        />

        <div style={{ display: 'flex', gap: 6 }}>
          {['1y', '3y', '5y'].map(p => (
            <button
              key={p}
              type="button"
              onClick={() => setPeriod(p)}
              className="btn btn-ghost"
              aria-pressed={period === p}
              style={{
                flex: 1, fontSize: 12,
                borderColor: period === p ? 'var(--firefly)' : 'var(--border)',
              }}
            >
              {t(`vsCompare.periods.${p}`)}
            </button>
          ))}
        </div>

        <button className="btn btn-primary btn-full" type="submit" disabled={loading}>
          {loading ? <span className="spinner" style={{ width: 18, height: 18 }} /> : t('vsCompare.run')}
        </button>
      </form>

      {error && (
        <p role="alert" style={{ color: 'var(--text-dim)', fontSize: 13, marginTop: 10 }}>{error}</p>
      )}

      {result && (
        <div style={{ marginTop: 14 }}>
          {[
            { key: 'property', data: result.property, icon: '🏘️' },
            { key: 'portfolio', data: result.portfolio, icon: '📈' },
          ].map(({ key, data, icon }) => (
            <div key={key} style={{
              padding: '10px 12px', borderRadius: 10, marginBottom: 8,
              border: `1px solid ${winner === key ? 'var(--firefly)' : 'var(--border)'}`,
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', gap: 8 }}>
                <strong style={{ fontSize: 14 }}>{icon} {t(`vsCompare.${key}`)}</strong>
                <span style={{ fontSize: 14, fontWeight: 600 }}>{money(data.real_value)}</span>
              </div>
              <div style={{ fontSize: 12, opacity: 0.75, marginTop: 2 }}>
                {t('vsCompare.realReturn', { pct: data.real_return_pct })}
                {' · '}
                {t('vsCompare.nominal', { value: money(data.value) })}
              </div>
            </div>
          ))}

          {/* The costs only one side pays, itemised rather than buried. */}
          <ul style={{ margin: '10px 0 0', paddingLeft: 18, fontSize: 12, lineHeight: 1.7, opacity: 0.85 }}>
            <li>{t('vsCompare.entryCosts', { value: money(result.property.entry_costs) })}</li>
            <li>{t('vsCompare.upkeep', { value: money(result.property.upkeep_paid) })}</li>
            <li>{t('vsCompare.rent', { value: money(result.property.rent_received) })}</li>
            <li>{t('vsCompare.inflation', { pct: result.inflation_pct, years: result.years })}</li>
          </ul>

          <p style={{ fontSize: 11.5, opacity: 0.65, marginTop: 10 }}>{result.note}</p>
        </div>
      )}
    </div>
  )
}
