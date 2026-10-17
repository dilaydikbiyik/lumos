import { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import api from '../utils/api'

/**
 * What a fund is here, and what its protections do not cover.
 *
 * Written after 131 Turkish funds were closed to trading at once in
 * September 2026. The app already recommends funds — SPY, QQQ and GLD are
 * all funds, and the German universe is entirely UCITS — but it taught only
 * one kind of liquidity: how fast an asset sells. What actually happened to
 * nearly half a million people was the other kind. The asset inside was
 * fine; the wrapper froze.
 *
 * COLLAPSED BY DEFAULT, like the purchase checklist. This is reference a
 * reader opens when they are deciding, not something to meet while they are
 * reading a price.
 *
 * Deliberately NOT a list of funds. Naming funds weeks after that happened
 * would be the opposite of this app's purpose: the structure is what a
 * beginner needs explained, and fund selection is not what this app does.
 */
export default function FundFacts() {
  const { t } = useTranslation()
  const [data, setData] = useState(null)
  const [open, setOpen] = useState(false)

  useEffect(() => {
    let cancelled = false
    api.get('/planning/fund-facts')
      .then(res => { if (!cancelled) setData(res.data) })
      .catch(() => { /* reference material; its absence is not an error */ })
    return () => { cancelled = true }
  }, [])

  if (!data?.available || !data.facts?.length) return null

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
          <strong style={{ fontSize: '1rem' }}>🏛️ {t('fundFacts.title')}</strong>
          <span aria-hidden="true" style={{ opacity: 0.6 }}>{open ? '▲' : '▼'}</span>
        </div>
        <p style={{ fontSize: 13, opacity: 0.8, margin: '4px 0 0' }}>
          {t('fundFacts.subtitle')}
        </p>
      </button>

      {open && (
        <ol style={{ margin: '14px 0 0', paddingLeft: 20 }}>
          {data.facts.map((fact, i) => (
            <li key={i} style={{ marginBottom: 12 }}>
              <strong style={{ fontSize: 13.5 }}>{fact.title}</strong>
              <p style={{ fontSize: 12.5, lineHeight: 1.65, margin: '3px 0 0', opacity: 0.88 }}>
                {fact.body}
              </p>
            </li>
          ))}
        </ol>
      )}
    </div>
  )
}
