import { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import api from '../utils/api'
import useMarket from '../hooks/useMarket'

/**
 * The suggestion for someone who answered "not sure yet".
 *
 * Shown ONLY to the undecided. Someone who already chose is not second-guessed
 * — that would be the app overriding a decision it asked them to make.
 *
 * Presented as a suggestion with its reasoning visible, and applying it is a
 * separate, explicit tap. The reasons are the product here: a beginner told
 * which world to start in should be able to disagree with the argument rather
 * than just obey the output.
 */
export default function PathSuggestion({ onApplied }) {
  const { t } = useTranslation()
  const { money } = useMarket()
  const [data, setData] = useState(null)
  const [undecided, setUndecided] = useState(false)
  const [applying, setApplying] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    let cancelled = false
    // Both GETs; api.js coalesces in-flight ones, so the concurrent
    // /users/me here and in PathInvitation collapse into a single request.
    api.get('/users/me')
      .then(res => { if (!cancelled) setUndecided(res.data.investment_path === 'undecided') })
      .catch(() => { /* showing nothing is the safe default */ })
    api.get('/users/me/path-suggestion')
      .then(res => { if (!cancelled) setData(res.data) })
      .catch(() => { /* no suggestion is a fine outcome */ })
    return () => { cancelled = true }
  }, [])

  // Only for the undecided. Second-guessing someone who already chose would
  // be the app overriding a decision it asked them to make.
  if (!data || !undecided) return null

  async function apply() {
    setApplying(true)
    setError(null)
    try {
      await api.patch('/users/me/investment-path', { investment_path: data.path })
      onApplied?.(data.path)
    } catch {
      setError(t('pathSuggestion.failed'))
    } finally {
      setApplying(false)
    }
  }

  return (
    <div className="card" style={{ borderColor: 'var(--firefly)' }}>
      <h3 style={{ margin: '0 0 4px', fontSize: '1rem' }}>
        🧭 {t('pathSuggestion.title')}
      </h3>
      <p style={{ fontSize: 13, opacity: 0.8, marginTop: 0 }}>
        {data.confident
          ? t('pathSuggestion.confident', { path: t(`path.options.${data.path}.title`) })
          : t('pathSuggestion.tentative', { path: t(`path.options.${data.path}.title`) })}
      </p>

      <ul style={{ margin: '0 0 12px', paddingLeft: 18, fontSize: 13, lineHeight: 1.65 }}>
        {data.reasons.map((reason, i) => <li key={i} style={{ marginBottom: 6 }}>{reason}</li>)}
      </ul>

      {data.entry_threshold ? (
        <p style={{ fontSize: 12, opacity: 0.65 }}>
          {t('pathSuggestion.threshold', { amount: money(data.entry_threshold) })}
        </p>
      ) : null}

      {error && (
        <p role="alert" style={{ color: 'var(--red, #f87171)', fontSize: 13 }}>{error}</p>
      )}

      <button className="btn btn-primary btn-full" onClick={apply} disabled={applying}>
        {applying
          ? t('pathSuggestion.applying')
          : t('pathSuggestion.apply', { path: t(`path.options.${data.path}.title`) })}
      </button>
      <p style={{ fontSize: 12, opacity: 0.6, margin: '8px 0 0', textAlign: 'center' }}>
        {t('pathSuggestion.note')}
      </p>
    </div>
  )
}
