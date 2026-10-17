import { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import api from '../utils/api'

/**
 * The ways into a home here — including the one the calculator ignored.
 *
 * Rent-versus-buy is an incomplete question in Türkiye. A large number of
 * people get into a home through savings-based financing: pay monthly, wait
 * your turn, no interest. The app offered two routes and was silent on the
 * third, which is the one a sizeable part of its own audience is actually
 * taking.
 *
 * Sits directly beneath the rent-versus-buy card, because that is the
 * moment the question is in front of the reader — and a third option
 * introduced anywhere else reads as trivia rather than as a choice.
 *
 * Collapsed: this is reference for a decision, not something to meet while
 * scrolling past a price.
 */
export default function HomeRoutes() {
  const { t } = useTranslation()
  const [data, setData] = useState(null)
  const [open, setOpen] = useState(false)

  useEffect(() => {
    let cancelled = false
    api.get('/planning/home-routes')
      .then(res => { if (!cancelled) setData(res.data) })
      .catch(() => {})
    return () => { cancelled = true }
  }, [])

  if (!data?.available || !data.routes?.length) return null

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
          <strong style={{ fontSize: '1rem' }}>🔑 {t('homeRoutes.title')}</strong>
          <span aria-hidden="true" style={{ opacity: 0.6 }}>{open ? '▲' : '▼'}</span>
        </div>
        <p style={{ fontSize: 13, opacity: 0.8, margin: '4px 0 0' }}>
          {t('homeRoutes.subtitle')}
        </p>
      </button>

      {open && (
        <ol style={{ margin: '14px 0 0', paddingLeft: 20 }}>
          {data.routes.map((route, i) => (
            <li key={i} style={{ marginBottom: 12 }}>
              <strong style={{ fontSize: 13.5 }}>{route.title}</strong>
              <p style={{ fontSize: 12.5, lineHeight: 1.65, margin: '3px 0 0', opacity: 0.88 }}>
                {route.body}
              </p>
            </li>
          ))}
        </ol>
      )}
    </div>
  )
}
