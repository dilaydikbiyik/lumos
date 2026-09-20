import { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import api from '../utils/api'

/**
 * What to check before buying property in THIS market.
 *
 * Collapsed by default: it is reference material for the moment somebody is
 * actually looking at a listing, not something to put in front of a reader
 * who is still deciding whether to invest at all.
 *
 * Market-keyed content, fetched rather than translated, because the checks
 * that matter are local: a deed office in one country, a Baulastenverzeichnis
 * in another, a flood map in a third. Translating one country's list into
 * three languages would produce confident, useless advice in two of them.
 */
export default function PurchaseChecks() {
  const { t } = useTranslation()
  const [data, setData] = useState(null)
  const [open, setOpen] = useState(false)

  useEffect(() => {
    let cancelled = false
    api.get('/planning/purchase-checks')
      .then(res => { if (!cancelled) setData(res.data) })
      .catch(() => { /* no checklist is better than another country's */ })
    return () => { cancelled = true }
  }, [])

  if (!data?.available || !data.checks?.length) return null

  return (
    <div className="card">
      <button
        onClick={() => setOpen(!open)}
        aria-expanded={open}
        style={{
          width: '100%', background: 'none', border: 'none', padding: 0,
          cursor: 'pointer', textAlign: 'left', color: 'inherit', font: 'inherit',
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', gap: 8 }}>
          <strong style={{ fontSize: '1rem' }}>📋 {t('purchaseChecks.title')}</strong>
          <span aria-hidden="true" style={{ opacity: 0.6 }}>{open ? '▲' : '▼'}</span>
        </div>
        <p style={{ fontSize: 13, opacity: 0.8, margin: '4px 0 0' }}>
          {t('purchaseChecks.subtitle', { count: data.checks.length })}
        </p>
      </button>

      {open && (
        <ol style={{ margin: '14px 0 0', paddingLeft: 20 }}>
          {data.checks.map((check, i) => (
            <li key={i} style={{ marginBottom: 12 }}>
              <strong style={{ fontSize: 13.5 }}>{check.title}</strong>
              <p style={{ fontSize: 12.5, lineHeight: 1.65, margin: '3px 0 0', opacity: 0.88 }}>
                {check.body}
              </p>
            </li>
          ))}
        </ol>
      )}
    </div>
  )
}
