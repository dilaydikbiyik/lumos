import { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import api, { extractErrorMessage } from '../utils/api'
import useMarket from '../hooks/useMarket'

/**
 * The risk quiz as a form, one question at a time.
 *
 * It replaces nine chat calls with zero. The questions were written down in
 * the system prompt and a frontier model was paid to read them out — one
 * call per answer, on the most restricted tier, roughly ten calls from a
 * fifty-a-day quota before a new user saw anything. Every reported failure
 * lived in that flow: the Turkish sentence in an English session, the
 * nested-JSON profile that returned the wrong object, the cold reads.
 *
 * Deliberately still ONE QUESTION AT A TIME rather than a long form. The
 * pacing is the part that worked — a nervous beginner answering nine things
 * at once is a different experience from answering one, and the reason the
 * conversation was chosen in the first place.
 *
 * Talking is still offered, and phrased as a preference rather than a
 * fallback, because for some people it genuinely is the better way in.
 */
export default function StructuredQuiz({ onComplete, onPreferChat }) {
  const { t } = useTranslation()
  const { unit } = useMarket()
  const [questions, setQuestions] = useState(null)
  const [step, setStep] = useState(0)
  const [answers, setAnswers] = useState({})
  const [draft, setDraft] = useState('')
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    let cancelled = false
    api.get('/profile/questions')
      .then(res => { if (!cancelled) setQuestions(res.data.questions) })
      .catch(err => { if (!cancelled) setError(extractErrorMessage(err)) })
    return () => { cancelled = true }
  }, [])

  if (error && !questions) {
    return <p role="alert" style={{ fontSize: 13, color: 'var(--red, #f87171)' }}>{error}</p>
  }
  if (!questions) {
    return <div className="light-loader" style={{ width: 24, height: 24, margin: '40px auto' }} />
  }

  const question = questions[step]
  const isLast = step === questions.length - 1
  const digits = (value) => String(value).replace(/[^\d]/g, '')

  async function finish(collected) {
    setSaving(true)
    setError(null)
    try {
      // Already shaped like RiskProfileAnswers — nothing to extract, nothing
      // to parse, no model between the reader's answer and their profile.
      const { data } = await api.post('/profile', collected)
      onComplete?.(data)
    } catch (err) {
      setError(extractErrorMessage(err, t('quiz.saveError')))
      setSaving(false)
    }
  }

  function advance(value) {
    const collected = { ...answers }
    if (value !== undefined && value !== null && value !== '') {
      collected[question.field] = value
    }
    setAnswers(collected)
    setDraft('')
    if (isLast) finish(collected)
    else setStep(step + 1)
  }

  // Checked HERE rather than at the end. The question carries its own bounds
  // (age is 18–100), and the server enforces them — but only on submit, so an
  // out-of-range answer on question seven surfaced as a failure after all
  // nine were done, with nothing pointing at which one was wrong.
  function outOfRange(value) {
    if (value === undefined) return null
    if (question.min != null && value < question.min) return question.min
    if (question.max != null && value > question.max) return question.max
    return null
  }

  function submitTyped(e) {
    e.preventDefault()
    const raw = digits(draft)
    if (question.required && !raw) return
    const value = raw ? Number(raw) : undefined
    if (outOfRange(value) !== null) {
      setError(t('quiz.outOfRange', { min: question.min, max: question.max }))
      return
    }
    setError(null)
    advance(value)
  }

  return (
    <div className="card">
      {/* Progress as a count, not a bar: "3 of 9" tells a nervous person how
          much is left; a bar only tells them they are not finished. */}
      <p style={{
        fontSize: 12, letterSpacing: '0.1em', textTransform: 'uppercase',
        color: 'var(--firefly)', fontWeight: 700, margin: 0,
      }}>
        {t('quiz.progress', { step: step + 1, total: questions.length })}
      </p>

      <h3 style={{ margin: '8px 0 6px', fontSize: '1.05rem', lineHeight: 1.4 }}>
        {question.title}
      </h3>
      <p style={{ fontSize: 13, lineHeight: 1.65, opacity: 0.82, marginTop: 0 }}>
        {question.help}
      </p>

      {question.type === 'choice' ? (
        <div style={{ display: 'grid', gap: 8, marginTop: 12 }}>
          {question.options.map(option => (
            <button
              key={option.value}
              type="button"
              onClick={() => advance(option.value)}
              disabled={saving}
              style={{
                textAlign: 'left', padding: '10px 12px', borderRadius: 10,
                border: '1px solid var(--border)', background: 'transparent',
                color: 'inherit', font: 'inherit', cursor: 'pointer',
              }}
            >
              <strong style={{ fontSize: 13.5 }}>{option.label}</strong>
              <span style={{ display: 'block', fontSize: 12, opacity: 0.75, marginTop: 2 }}>
                {option.help}
              </span>
            </button>
          ))}
        </div>
      ) : (
        <form onSubmit={submitTyped} style={{ display: 'flex', gap: 8, marginTop: 12 }}>
          <input
            value={draft}
            onChange={e => setDraft(e.target.value)}
            inputMode="numeric"
            autoFocus
            min={question.min}
            max={question.max}
            placeholder={question.type === 'amount' ? unit : t('quiz.yearsPlaceholder')}
            aria-label={question.title}
            style={{ flex: 1 }}
          />
          <button className="btn btn-primary" type="submit" disabled={saving}>
            {saving ? '…' : t('common.next')}
          </button>
        </form>
      )}

      {/* A question the schema lets you skip must be skippable here, or the
          form is stricter than the thing it feeds — and people abandon forms
          that demand what they do not have. */}
      {!question.required && (
        <button
          type="button"
          className="btn btn-ghost btn-full"
          style={{ marginTop: 8, opacity: 0.75 }}
          onClick={() => advance(undefined)}
          disabled={saving}
        >
          {t('quiz.skip')}
        </button>
      )}

      {error && (
        <p role="alert" style={{ color: 'var(--red, #f87171)', fontSize: 13, marginTop: 10 }}>
          {error}
        </p>
      )}

      <div style={{
        display: 'flex', justifyContent: 'space-between', gap: 8,
        marginTop: 14, paddingTop: 12, borderTop: '1px solid var(--border)',
      }}>
        <button
          type="button"
          onClick={() => setStep(Math.max(step - 1, 0))}
          disabled={step === 0 || saving}
          style={{
            background: 'none', border: 'none', color: 'var(--text-dim)',
            cursor: step === 0 ? 'default' : 'pointer', font: 'inherit',
            fontSize: 12, padding: 0, opacity: step === 0 ? 0.3 : 1,
          }}
        >
          {t('common.back')}
        </button>
        <button
          type="button"
          onClick={onPreferChat}
          style={{
            background: 'none', border: 'none', color: 'var(--text-dim)',
            cursor: 'pointer', font: 'inherit', fontSize: 12, padding: 0,
          }}
        >
          {t('quiz.preferChat')}
        </button>
      </div>
    </div>
  )
}
