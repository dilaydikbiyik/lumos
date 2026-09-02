import { useState } from 'react'
import api, { extractErrorMessage } from '../utils/api'
import useMarket from '../hooks/useMarket'
import { Trans, useTranslation } from 'react-i18next'

/**
 * Practice portfolio — follow the recommended portfolio with virtual
 * 100.000 TL on real market data, without risking real money. The heart
 * of the fearless start.
 * Note: the virtual basket is TL-denominated (XU100 + TL-priced data),
 * hence money(n, 'TRY').
 */
export default function PracticeMode({ allocations }) {
  const { t } = useTranslation()
  const { money } = useMarket()
  const [snapshot, setSnapshot] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  async function start() {
    setLoading(true)
    setError(null)
    try {
      const weights = Object.fromEntries(allocations.map(a => [a.ticker, a.weight]))
      const res = await api.post('/practice/snapshot', { weights })
      setSnapshot(res.data)
    } catch (err) {
      setError(extractErrorMessage(err, t('practice.error')))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="card" style={{ border: '1px dashed var(--accent, #8b8bf5)' }}>
      <h3 style={{ marginBottom: 4 }}>{t('practice.title')}</h3>
      <p style={{ fontSize: 13, opacity: 0.8, marginBottom: 12 }}>
        {t('practice.subtitle')}
      </p>

      {!snapshot && (
        <button className="btn btn-primary btn-full" onClick={start} disabled={loading}>
          {loading ? <span className="spinner" style={{ width: 18, height: 18 }} /> : t('practice.start')}
        </button>
      )}

      {snapshot && (
        <>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
            <div>
              <div style={{ fontSize: 12, opacity: 0.7 }}>{t('practice.virtualNow')}</div>
              <div style={{ fontSize: 20, fontWeight: 700 }}>{money(snapshot.current_value, 'TRY')}</div>
            </div>
            <div>
              <div style={{ fontSize: 12, opacity: 0.7 }}>{t('practice.thisWeek')}</div>
              <div style={{
                fontSize: 20, fontWeight: 700,
                color: snapshot.weekly_change_pct >= 0 ? 'var(--green, #4ade80)' : 'var(--red)',
              }}>
                {snapshot.weekly_change_pct >= 0 ? '+' : ''}{money(snapshot.weekly_change_amount, 'TRY')}
              </div>
            </div>
          </div>
          <p style={{ fontSize: 13, marginTop: 10, lineHeight: 1.6 }}>
            <Trans i18nKey="practice.mover"
                   values={{
                     ticker: snapshot.biggest_mover.ticker,
                     pct: (snapshot.biggest_mover.weekly_change_pct > 0 ? '+' : '') + snapshot.biggest_mover.weekly_change_pct,
                   }}
                   components={[<strong key="a" />]} />
          </p>
          <p style={{ fontSize: 11.5, color: 'var(--text-dim)', marginTop: 6, lineHeight: 1.5 }}>
            {t('practice.honesty')}
          </p>
        </>
      )}
      {error && <p style={{ color: 'var(--red)', fontSize: 13, marginTop: 10 }}>{error}</p>}
    </div>
  )
}
