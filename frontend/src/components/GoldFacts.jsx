import { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import api from '../utils/api'

/**
 * What you are actually holding when you hold gold.
 *
 * The app recommends gold in every portfolio it builds, and until now it
 * never said what the holding is. Metal in a drawer, a number in a bank
 * app and a fund share are all called "gold" and fail in different ways:
 * one can be stolen, one is a claim on an institution, one is a fund.
 *
 * In Germany the common gold product is an ETC — a debt security, not a
 * fund — so a reader who applies the fund lesson here gets it exactly
 * backwards. That is the one thing the German text leads with.
 *
 * COLLAPSED BY DEFAULT, like the other reference cards: this is what you
 * open while deciding, not something to meet while reading a price.
 */
export default function GoldFacts() {
  const { t } = useTranslation()
  const [data, setData] = useState(null)
  const [open, setOpen] = useState(false)

  useEffect(() => {
    let cancelled = false
    api.get('/planning/gold-facts')
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
          <strong style={{ fontSize: '1rem' }}>🪙 {t('goldFacts.title')}</strong>
          <span aria-hidden="true" style={{ opacity: 0.6 }}>{open ? '▲' : '▼'}</span>
        </div>
        <p style={{ fontSize: 13, opacity: 0.8, margin: '4px 0 0' }}>
          {t('goldFacts.subtitle')}
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
