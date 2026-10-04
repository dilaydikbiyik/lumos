import { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import api from '../utils/api'
import { signedPercent } from '../utils/format'

/**
 * Where people are actually moving.
 *
 * The one thing a beginner can check about a region that is not a price.
 * Prices say what already happened; a region gaining working-age residents
 * year after year is a statement about demand that has to live somewhere.
 *
 * THE CAVEAT IS NOT A FOOTNOTE. It sits above the table, because a reader who
 * sees "+10%" and misses it has been told something the data does not say: a
 * region can gain people and still lose value after inflation, which is most
 * of Türkiye over the last decade. The real price change lives one card away
 * and this is meant to be read next to it, never instead of it.
 *
 * The granularity is printed too. These are NUTS-2 regions — "Tekirdağ,
 * Edirne, Kırklareli" is a single row — and letting someone attach that to
 * one district's listing would be the false precision the rest of the app
 * refuses.
 */
const DIRECTION_COLOR = {
  growing: 'var(--green, #3DD68C)',
  shrinking: 'var(--red, #f87171)',
  flat: 'var(--text-dim)',
}

export default function PopulationTrend() {
  const { t } = useTranslation()
  const [data, setData] = useState(null)

  useEffect(() => {
    let cancelled = false
    api.get('/planning/population-trend')
      .then(res => { if (!cancelled) setData(res.data) })
      .catch(() => { /* a supporting signal; its absence is not an error */ })
    return () => { cancelled = true }
  }, [])

  // Markets with no declared source render nothing at all rather than an
  // empty table explaining itself.
  if (!data?.available || !data.regions?.length) return null

  return (
    <div className="card">
      <h3 style={{ margin: '0 0 4px', fontSize: '1rem' }}>👥 {t('population.title')}</h3>
      <p style={{ fontSize: 12.5, lineHeight: 1.65, opacity: 0.85, marginTop: 0 }}>
        {data.caveat}
      </p>

      <div style={{ marginTop: 12 }}>
        {data.regions.map(r => (
          <div
            key={r.code}
            style={{
              display: 'flex', alignItems: 'baseline', gap: 8,
              padding: '7px 0', borderBottom: '1px solid var(--border)',
            }}
          >
            <span style={{ flex: 1, fontSize: 13 }}>{r.region}</span>
            {r.working_age_share_pct != null && (
              <span style={{ fontSize: 11, opacity: 0.6 }}>
                {t('population.workingAge', { pct: r.working_age_share_pct })}
              </span>
            )}
            <strong style={{
              fontSize: 13, minWidth: 54, textAlign: 'right',
              color: DIRECTION_COLOR[r.direction],
            }}>
              {signedPercent(r.change_pct, { decimals: 1 })}
            </strong>
          </div>
        ))}
      </div>

      <p style={{ fontSize: 11, opacity: 0.6, lineHeight: 1.6, marginTop: 10 }}>
        {data.source_note}
      </p>
    </div>
  )
}
