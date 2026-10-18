import { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import api from '../utils/api'

/**
 * One card of structural reference about a kind of holding.
 *
 * There were three of these — funds, gold, crypto — as three near-identical
 * files, each with its own collapse toggle, stacked in a row under no
 * header. That is a pile by the definition in Section.jsx: equal-weight
 * cards with nothing saying what they are for, and the reader has to open
 * all three to learn which one answers their question.
 *
 * So the toggle moved OUT, to one band above all of them, and the card
 * became plain. Inside an opened band a card that still needs its own tap
 * is a second lock on an unlocked door.
 *
 * Driven by props rather than copied per subject, because the three copies
 * had already begun to disagree: one had a different docstring, one a
 * different emoji size, and a fourth copy is where they would have drifted
 * apart for real.
 */
export default function ReferenceFacts({ endpoint, icon, titleKey, subtitleKey }) {
  const { t } = useTranslation()
  const [data, setData] = useState(null)

  useEffect(() => {
    let cancelled = false
    api.get(endpoint)
      .then(res => { if (!cancelled) setData(res.data) })
      .catch(() => { /* reference material; its absence is not an error */ })
    return () => { cancelled = true }
  }, [endpoint])

  if (!data?.available || !data.facts?.length) return null

  return (
    <div className="card">
      <strong style={{ fontSize: '1rem' }}>{icon} {t(titleKey)}</strong>
      <p style={{ fontSize: 13, opacity: 0.8, margin: '4px 0 0' }}>
        {t(subtitleKey)}
      </p>
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
    </div>
  )
}
