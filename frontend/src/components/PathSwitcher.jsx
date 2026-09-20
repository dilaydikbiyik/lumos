import { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import api from '../utils/api'

const PATHS = ['stocks', 'real_estate', 'hybrid', 'undecided']

const PATH_ICON = {
  stocks: '🏦',
  real_estate: '🏘️',
  hybrid: '⚖️',
  undecided: '🤷',
}

/**
 * Change the investment path, at any time.
 *
 * The onboarding screen already promised this — "you can change path at any
 * time, this is a starting point, not a commitment" — and there was nowhere
 * to do it. The path decides which half of the app you can even see: picking
 * "stocks only" hid Explore permanently, with no way back short of asking
 * support. A promise the app could not keep is worse than not making it.
 *
 * Never forced and never nagged: it sits in the profile, it says what will
 * change, and it stays on whatever the reader picked.
 */
export default function PathSwitcher({ onChanged }) {
  const { t } = useTranslation()
  const [current, setCurrent] = useState(null)
  const [saving, setSaving] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    let cancelled = false
    api.get('/users/me')
      .then(res => { if (!cancelled) setCurrent(res.data.investment_path) })
      .catch(() => { /* the switcher simply shows nothing as selected */ })
    return () => { cancelled = true }
  }, [])

  async function choose(pathId) {
    if (pathId === current || saving) return
    const previous = current
    setSaving(pathId)
    setError(null)
    setCurrent(pathId)              // optimistic — the UI responds at once
    try {
      await api.patch('/users/me/investment-path', { investment_path: pathId })
      onChanged?.(pathId)
    } catch {
      setCurrent(previous)          // a failed save must not leave a lie on screen
      setError(t('pathSwitch.failed'))
    } finally {
      setSaving(null)
    }
  }

  return (
    <div className="card" style={{ marginTop: '1rem' }}>
      <h3 style={{ margin: '0 0 4px', fontSize: '1rem' }}>{t('pathSwitch.title')}</h3>
      <p style={{ fontSize: 13, opacity: 0.8, marginTop: 0 }}>{t('pathSwitch.subtitle')}</p>

      <div style={{ display: 'grid', gap: 8 }}>
        {PATHS.map(id => {
          const active = current === id
          return (
            <button
              key={id}
              type="button"
              onClick={() => choose(id)}
              aria-pressed={active}
              disabled={!!saving}
              style={{
                display: 'flex', alignItems: 'center', gap: 10, width: '100%',
                textAlign: 'left', padding: '10px 12px', borderRadius: 10,
                cursor: saving ? 'wait' : 'pointer',
                background: active ? 'var(--bg-card-hover, rgba(255,255,255,0.05))' : 'transparent',
                border: `1px solid ${active ? 'var(--firefly)' : 'var(--border)'}`,
                color: 'inherit', font: 'inherit',
              }}
            >
              <span style={{ fontSize: 20 }} aria-hidden="true">{PATH_ICON[id]}</span>
              <span style={{ flex: 1 }}>
                <strong style={{ fontSize: 14 }}>{t(`path.options.${id}.title`)}</strong>
                <span style={{ display: 'block', fontSize: 12, opacity: 0.75, marginTop: 2 }}>
                  {t(`path.options.${id}.desc`)}
                </span>
              </span>
              {active && <span aria-hidden="true" style={{ color: 'var(--firefly)' }}>✓</span>}
            </button>
          )
        })}
      </div>

      {error && (
        <p role="alert" style={{ color: 'var(--red, #f87171)', fontSize: 13 }}>{error}</p>
      )}
      <p style={{ fontSize: 12, opacity: 0.65, marginBottom: 0 }}>
        {t('pathSwitch.note')}
      </p>
    </div>
  )
}
