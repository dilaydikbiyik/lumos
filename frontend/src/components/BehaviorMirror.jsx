import { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import api from '../utils/api'

/**
 * A mirror, not a verdict.
 *
 * Every purchase can be tagged with the feeling behind it. This reads those
 * tags back against what the reader SAID their loss tolerance was — someone
 * who described themselves as cautious and then bought three things on a
 * rush is not being caught out, they are being shown something they cannot
 * see from inside a single decision.
 *
 * Three deliberate restraints:
 *
 *   IT STAYS QUIET UNLESS THERE IS SOMETHING TO SAY. The server returns a
 *   note only when stated tolerance and actual behaviour actually diverge.
 *   A permanent panel scoring someone's feelings would make the app another
 *   thing to be anxious about.
 *
 *   IT NEEDS ENOUGH TAGS TO BE FAIR. One tagged purchase is a mood, not a
 *   pattern, and telling a beginner they are impulsive on that evidence is
 *   both wrong and the kind of thing people believe.
 *
 *   NO NUMBERS IN THE HEADLINE. "2 of 3 purchases were FOMO" invites the
 *   reader to optimise the metric rather than notice the habit.
 */
const MIN_TAGS_TO_SPEAK = 3

export default function BehaviorMirror() {
  const { t } = useTranslation()
  const [data, setData] = useState(null)

  useEffect(() => {
    let cancelled = false
    api.get('/coach/behavior-mirror')
      .then(res => { if (!cancelled) setData(res.data) })
      // Silent: this is a supporting observation, and an error banner where
      // a gentle note would have gone is worse than nothing at all.
      .catch(() => {})
    return () => { cancelled = true }
  }, [])

  if (!data?.note || (data.tagged_count || 0) < MIN_TAGS_TO_SPEAK) return null

  const { plan = 0, fomo = 0, panik = 0 } = data.by_emotion || {}

  return (
    <div className="card" style={{ borderColor: 'var(--firefly)' }}>
      <h3 style={{ margin: '0 0 6px', fontSize: '1rem' }}>
        🪞 {t('mirror.title')}
      </h3>
      <p style={{ fontSize: 13, lineHeight: 1.7, margin: 0, opacity: 0.9 }}>
        {data.note}
      </p>

      {/* The counts are available but secondary — below the observation and
          visually quieter, so the sentence is what gets read. */}
      <div style={{
        display: 'flex', gap: 12, marginTop: 10, paddingTop: 10,
        borderTop: '1px solid var(--border)', fontSize: 11.5, opacity: 0.7,
      }}>
        <span>{t('mirror.plan', { count: plan })}</span>
        <span>{t('mirror.fomo', { count: fomo })}</span>
        <span>{t('mirror.panic', { count: panik })}</span>
      </div>
    </div>
  )
}
