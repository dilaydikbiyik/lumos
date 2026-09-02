import { useState } from 'react'
import api, { extractErrorMessage } from '../utils/api'
import useMarket from '../hooks/useMarket'
import { Trans, useTranslation } from 'react-i18next'

/**
 * Goal-based investing — turns a goal like "800.000 TL house deposit in
 * 3 years" into a concrete monthly contribution, and warns about the
 * delay implied by the user's current pace.
 */
export default function GoalPlanner() {
  const { t } = useTranslation()
  const { money } = useMarket()
  const [form, setForm] = useState({ target_amount: '', years: 3, current_savings: '', monthly: '' })
  const [plan, setPlan] = useState(null)
  const [progress, setProgress] = useState(null)
  const [error, setError] = useState(null)

  async function run(e) {
    e.preventDefault()
    setError(null)
    setProgress(null)
    try {
      const body = {
        target_amount: Number(form.target_amount),
        years: Number(form.years),
        current_savings: Number(form.current_savings || 0),
      }
      const res = await api.post('/planning/goal-plan', body)
      setPlan(res.data)

      // If the user told us what they actually save monthly, check drift
      if (form.monthly) {
        const drift = await api.post('/planning/goal-progress', {
          target_amount: body.target_amount,
          years_remaining: body.years,
          current_savings: body.current_savings,
          actual_monthly_contribution: Number(form.monthly),
        })
        setProgress(drift.data)
      }
    } catch (err) {
      setError(extractErrorMessage(err, t('goal.error')))
    }
  }

  return (
    <div className="card">
      <h3 style={{ marginBottom: 4 }}>{t('goal.title')}</h3>
      <p style={{ fontSize: 13, opacity: 0.8, marginBottom: 12 }}>
        {t('goal.subtitle')}
      </p>
      <form onSubmit={run} style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
        <input className="input" type="number" placeholder={t('goal.targetPlaceholder')} required min="1"
               value={form.target_amount} onChange={e => setForm({ ...form, target_amount: e.target.value })} />
        <div style={{ display: 'flex', gap: 8 }}>
          <select className="input" style={{ flex: 1 }} value={form.years}
                  onChange={e => setForm({ ...form, years: e.target.value })}>
            {[1, 2, 3, 5, 10].map(y => <option key={y} value={y}>{t('goal.withinYears', { n: y })}</option>)}
          </select>
          <input className="input" type="number" placeholder={t('goal.savingsPlaceholder')} min="0" style={{ flex: 1 }}
                 value={form.current_savings} onChange={e => setForm({ ...form, current_savings: e.target.value })} />
        </div>
        <input className="input" type="number" placeholder={t('goal.monthlyPlaceholder')} min="0"
               value={form.monthly} onChange={e => setForm({ ...form, monthly: e.target.value })} />
        <button className="btn btn-primary" type="submit">{t('goal.plan')}</button>
      </form>

      {plan && (
        <div style={{ marginTop: 14 }}>
          {plan.already_on_track ? (
            <p style={{ fontSize: 14, color: 'var(--green, #4ade80)' }}>
              {t('goal.alreadyOnTrack')}
            </p>
          ) : (
            <p style={{ fontSize: 14 }}>
              <Trans i18nKey="goal.needMonthly"
                     values={{ amount: money(plan.monthly_contribution) }}
                     components={[<strong key="a" style={{ fontSize: 17 }} />]} />
            </p>
          )}

          {plan.target_real_value != null && (
            <p style={{ fontSize: 12, opacity: 0.7, marginTop: 8, lineHeight: 1.5 }}>
              ℹ️ <Trans i18nKey="goal.realValueNote"
                        values={{
                          inflation: plan.annual_inflation_pct,
                          target: money(Number(form.target_amount)),
                          real: money(plan.target_real_value),
                        }}
                        components={[<strong key="a" />]} />
            </p>
          )}

          {/* "What is this based on?" — every other engine in the app shows
              its formula; this one quietly did not, and a user asked. */}
          <details style={{ marginTop: 10 }}>
            <summary style={{ cursor: 'pointer', fontSize: 'var(--t-micro)', color: 'var(--text-dim)' }}>
              {t('goal.howTitle')}
            </summary>
            <div style={{
              marginTop: 6, fontSize: 'var(--t-micro)', color: 'var(--text-muted)', lineHeight: 1.7,
            }}>
              <p>{t('goal.howBody', {
                growth: plan.annual_growth_pct,
                inflation: plan.annual_inflation_pct,
                months: plan.months ?? Math.round(Number(form.years) * 12),
              })}</p>
              <p style={{ marginTop: 6, fontFamily: 'ui-monospace, SFMono-Regular, monospace' }}>
                {t('goal.howFormula')}
              </p>
              <p style={{ marginTop: 6 }}>{t('goal.howCaveat')}</p>
            </div>
          </details>

          {progress && (
            <div style={{ marginTop: 10, padding: 10, borderRadius: 10, border: '1px solid var(--border)' }}>
              <div style={{ fontSize: 13, marginBottom: 6 }}>
                {t('goal.atYourPace', { amount: money(form.monthly) })}
              </div>
              {progress.on_track ? (
                <p style={{ fontSize: 14, color: 'var(--green, #4ade80)' }}>{t('goal.onTrack')}</p>
              ) : (
                <p style={{ fontSize: 14, color: 'var(--red)' }}>
                  ⏳ <Trans i18nKey="goal.delayed" values={{ months: progress.delay_months }}
                            components={[<strong key="a" />]} />
                </p>
              )}
              <div style={{ marginTop: 8, height: 8, borderRadius: 4, background: 'var(--border)', overflow: 'hidden' }}>
                <div style={{
                  width: `${progress.progress_pct}%`, height: '100%',
                  background: 'linear-gradient(90deg, #8b8bf5, #4ade80)',
                }} />
              </div>
              <div style={{ fontSize: 12, opacity: 0.7, marginTop: 4 }}>{t('goal.progress', { pct: progress.progress_pct })}</div>
            </div>
          )}
        </div>
      )}
      {error && <p style={{ color: 'var(--red)', fontSize: 13, marginTop: 10 }}>{error}</p>}
    </div>
  )
}
