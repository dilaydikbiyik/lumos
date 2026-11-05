import { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import api from '../utils/api'
import { percent, signedPercent } from '../utils/format'

/**
 * Every kind of investment, side by side on one measure.
 *
 * Asked for so a reader can see where "lending to the US government for a
 * guaranteed return" sits next to cash, gold, the stock market and bitcoin —
 * and learn what "guaranteed" does and does not cover. Every figure comes
 * from GET /stocks/asset-classes, measured over the same five years in the
 * reader's own currency, inflation-adjusted. The order is the backend's
 * teaching order (calm to volatile), never a ranking, and nothing here says
 * buy: the lesson lines describe, they do not advise.
 */
export default function AssetClasses() {
  const { t } = useTranslation()
  const [data, setData] = useState(null)
  const [error, setError] = useState(false)
  const [open, setOpen] = useState(null)

  useEffect(() => {
    let cancelled = false
    api.get('/stocks/asset-classes')
      .then(res => { if (!cancelled) setData(res.data) })
      .catch(() => { if (!cancelled) setError(true) })
    return () => { cancelled = true }
  }, [])

  if (error) return <p style={{ fontSize: 13, color: 'var(--text-dim)' }}>{t('stocks.error')}</p>
  if (!data) return <div className="spinner" style={{ margin: '24px auto' }} />
  if (!data.available) return <p style={{ fontSize: 13 }}>{t('assetClasses.unavailable')}</p>

  const rows = data.classes
  const cash = rows.find(r => r.key === 'cash')
  const sharpest = rows.reduce((a, b) => (b.worst_drop_pct < a.worst_drop_pct ? b : a), rows[0])

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
      <div>
        <h2>{t('assetClasses.title')}</h2>
        <p style={{ fontSize: 13, marginTop: 4 }}>{t('assetClasses.subtitle')}</p>
      </div>

      <div className="card" style={{ borderColor: 'var(--firefly-dim)', fontSize: 12.5, lineHeight: 1.6 }}>
        <strong>{t('stocks.notAdviceTitle')}</strong>
        <p style={{ margin: '4px 0 0' }}>{t('assetClasses.basis', { currency: data.currency })}</p>
        <p style={{ margin: '6px 0 0', color: 'var(--text-dim)' }}>
          {t('stocks.asOf', { date: data.as_of, years: data.window_years })}
        </p>
      </div>

      <div className="card">
        {cash?.real_change_pct != null && (
          <strong style={{ fontSize: 15, display: 'block' }}>
            {t('assetClasses.headlineCash', { cash: percent(Math.abs(cash.real_change_pct)) })}
          </strong>
        )}
        <p style={{ fontSize: 12.5, lineHeight: 1.6, margin: '6px 0 0' }}>
          {t('assetClasses.headlineDrop', {
            name: t(`assetClasses.k.${sharpest.key}.name`),
            drop: percent(sharpest.worst_drop_pct),
          })}
        </p>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
        {rows.map(r => {
          const expanded = open === r.key
          const real = r.real_change_pct
          return (
            <div key={r.key} className="card" style={{ padding: 0 }}>
              <button type="button" onClick={() => setOpen(expanded ? null : r.key)}
                      aria-expanded={expanded}
                      style={{
                        width: '100%', background: 'none', border: 'none', cursor: 'pointer',
                        color: 'inherit', font: 'inherit', textAlign: 'left', padding: '12px 14px',
                        display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                        gap: 12, minHeight: 44,
                      }}>
                <span style={{ minWidth: 0 }}>
                  <strong style={{ fontSize: 14 }}>{t(`assetClasses.k.${r.key}.name`)}</strong>
                  <span style={{ display: 'block', fontSize: 11.5, color: 'var(--text-dim)' }}>
                    {r.ticker || r.currency}
                  </span>
                </span>
                <span style={{ textAlign: 'right', flexShrink: 0 }}>
                  <span className="num" style={{ fontSize: 13, fontWeight: 700,
                    color: real != null && real < 0 ? 'var(--red)' : 'inherit' }}>
                    {real == null ? '—' : signedPercent(real)}
                  </span>
                  <span style={{ display: 'block', fontSize: 10.5, color: 'var(--text-dim)' }}>
                    {t('assetClasses.real')}
                  </span>
                </span>
              </button>
              {expanded && (
                <div style={{ padding: '0 14px 14px', fontSize: 12.5, lineHeight: 1.65 }}>
                  <p style={{ margin: 0 }}>{t(`assetClasses.k.${r.key}.what`)}</p>
                  <dl style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 8, margin: '10px 0' }}>
                    {[['real', signedPercent(real)], ['worst', percent(r.worst_drop_pct)], ['vol', percent(r.volatility_pct)]].map(([k, v]) => (
                      <div key={k}>
                        <dt style={{ fontSize: 10.5, color: 'var(--text-dim)' }}>{t(`assetClasses.${k}`)}</dt>
                        <dd className="num" style={{ margin: 0, fontWeight: 700 }}>
                          {v || '—'}
                        </dd>
                      </div>
                    ))}
                  </dl>
                  <p style={{ margin: 0 }}>{t(`assetClasses.k.${r.key}.lesson`)}</p>
                  {r.live_yield_pct != null && (
                    <p style={{ margin: '6px 0 0', color: 'var(--text-dim)' }}>
                      {t('assetClasses.liveYield', { y: percent(r.live_yield_pct, { decimals: 1 }), currency: r.currency })}
                    </p>
                  )}
                  {!r.dividends_included && r.ticker && (
                    <p style={{ margin: '6px 0 0', color: 'var(--text-dim)' }}>{t('assetClasses.noDividends')}</p>
                  )}
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
