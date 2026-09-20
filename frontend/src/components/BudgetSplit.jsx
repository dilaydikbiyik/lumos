import { useCallback, useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import api from '../utils/api'
import useMarket from '../hooks/useMarket'

/**
 * "I have this much — what goes where?"
 *
 * The three bars are drawn in the order the engine decides them, because the
 * order is the lesson: the reserve comes off the top and is not an investment
 * competing with the others, it is what stops a bad month becoming a forced
 * sale.
 *
 * The reasons are not decoration. Someone told to put six tenths of their
 * savings into a flat should be able to read why and disagree with it.
 */
const SEGMENTS = [
  { key: 'reserve', amount: 'reserve', pct: 'reserve_pct', color: 'var(--text-dim)' },
  { key: 'property', amount: 'property_amount', pct: 'property_pct', color: 'var(--green)' },
  { key: 'market', amount: 'market_amount', pct: 'market_pct', color: 'var(--accent)' },
]

export default function BudgetSplit() {
  const { t } = useTranslation()
  const { money } = useMarket()
  const [plan, setPlan] = useState(null)
  const [outgoings, setOutgoings] = useState('')
  const [saving, setSaving] = useState(false)

  const load = useCallback(() => {
    return api.get('/planning/budget-split')
      .then(res => setPlan(res.data))
      .catch(() => { /* no plan is a fine outcome */ })
  }, [])

  useEffect(() => { load() }, [load])

  // The reserve is six months of SPENDING. Without that figure the engine
  // falls back to a flat 10% and says so — this is where the reader can
  // replace the assumption with the real number.
  async function saveOutgoings(e) {
    e.preventDefault()
    const value = Number(String(outgoings).replace(/[^\d]/g, ''))
    if (!value || saving) return
    setSaving(true)
    try {
      await api.patch('/users/me/outgoings', { monthly_outgoings: value })
      await load()
      setOutgoings('')
    } catch { /* the assumed reserve stays; nothing is lost */ }
    finally { setSaving(false) }
  }

  if (!plan) return null
  const total = plan.reserve + plan.property_amount + plan.market_amount
  if (total <= 0) return null

  return (
    <div className="card">
      <h3 style={{ margin: '0 0 4px', fontSize: '1rem' }}>🧮 {t('budgetSplit.title')}</h3>
      <p style={{ fontSize: 13, opacity: 0.8, marginTop: 0 }}>
        {t('budgetSplit.subtitle', { total: money(total) })}
      </p>

      {/* One bar, three parts — the proportions are the point. */}
      <div style={{
        display: 'flex', height: 12, borderRadius: 6, overflow: 'hidden',
        margin: '12px 0 14px', background: 'var(--border)',
      }} aria-hidden="true">
        {SEGMENTS.map(seg => (
          <div key={seg.key} style={{ width: `${plan[seg.pct]}%`, background: seg.color }} />
        ))}
      </div>

      <dl style={{ margin: 0 }}>
        {SEGMENTS.filter(seg => plan[seg.amount] > 0).map(seg => (
          <div key={seg.key} style={{
            display: 'flex', alignItems: 'baseline', gap: 8, marginBottom: 10,
          }}>
            <span aria-hidden="true" style={{
              width: 10, height: 10, borderRadius: 3, background: seg.color, flexShrink: 0,
            }} />
            <dt style={{ fontWeight: 600, fontSize: 13, flex: 1 }}>
              {t(`budgetSplit.parts.${seg.key}.label`)}
              <span style={{ display: 'block', fontWeight: 400, opacity: 0.7, fontSize: 12 }}>
                {/* The property row explains its VEHICLE; the others carry a
                    fixed hint. `defaultValue` keeps a missing one blank rather
                    than printing the key at the reader. */}
                {seg.key === 'property'
                  ? t(`budgetSplit.vehicle.${plan.property_vehicle}`, { defaultValue: '' })
                  : t(`budgetSplit.parts.${seg.key}.hint`, { defaultValue: '' })}
              </span>
            </dt>
            <dd style={{ margin: 0, fontWeight: 600, fontSize: 13, whiteSpace: 'nowrap' }}>
              {money(plan[seg.amount])}
              <span style={{ opacity: 0.6, fontWeight: 400 }}> · {plan[seg.pct]}%</span>
            </dd>
          </div>
        ))}
      </dl>

      <ul style={{
        margin: '10px 0 0', paddingLeft: 18, fontSize: 12.5,
        lineHeight: 1.65, opacity: 0.85,
      }}>
        {plan.reasons.map((reason, i) => <li key={i} style={{ marginBottom: 6 }}>{reason}</li>)}
      </ul>

      {plan.reserve_is_assumed && (
        <form onSubmit={saveOutgoings} style={{ display: 'flex', gap: 8, marginTop: 10 }}>
          <input
            value={outgoings}
            onChange={e => setOutgoings(e.target.value)}
            inputMode="numeric"
            placeholder={t('budgetSplit.outgoingsPlaceholder')}
            aria-label={t('budgetSplit.outgoingsPlaceholder')}
            style={{ flex: 1 }}
          />
          <button className="btn btn-ghost" type="submit" disabled={saving}>
            {saving ? '…' : t('common.save')}
          </button>
        </form>
      )}

      <p style={{ fontSize: 11.5, opacity: 0.6, margin: '10px 0 0' }}>
        {t('budgetSplit.disclaimer')}
      </p>
    </div>
  )
}
