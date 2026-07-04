import { useState } from 'react'
import api, { extractErrorMessage } from '../utils/api'

const fmt = n => new Intl.NumberFormat('tr-TR', { maximumFractionDigits: 0 }).format(n)

/**
 * Hedef bazlı yatırım — "3 yılda ev peşinatı 800.000 TL" gibi bir hedefi
 * somut aylık katkıya çevirir; mevcut tempoyla gecikme uyarısı verir.
 */
export default function GoalPlanner() {
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
      setError(extractErrorMessage(err, 'Hesaplanamadı'))
    }
  }

  return (
    <div className="card">
      <h3 style={{ marginBottom: 4 }}>🎯 Hedefim</h3>
      <p style={{ fontSize: 13, opacity: 0.8, marginBottom: 12 }}>
        "3 yılda ev peşinatı" gibi bir hedefi somut aylık plana çevirelim.
      </p>
      <form onSubmit={run} style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
        <input className="input" type="number" placeholder="Hedef tutar (TL, örn: 800000)" required min="1"
               value={form.target_amount} onChange={e => setForm({ ...form, target_amount: e.target.value })} />
        <div style={{ display: 'flex', gap: 8 }}>
          <select className="input" style={{ flex: 1 }} value={form.years}
                  onChange={e => setForm({ ...form, years: e.target.value })}>
            {[1, 2, 3, 5, 10].map(y => <option key={y} value={y}>{y} yıl içinde</option>)}
          </select>
          <input className="input" type="number" placeholder="Mevcut birikim (ops.)" min="0" style={{ flex: 1 }}
                 value={form.current_savings} onChange={e => setForm({ ...form, current_savings: e.target.value })} />
        </div>
        <input className="input" type="number" placeholder="Şu an ayda ne kadar biriktiriyorsun? (ops.)" min="0"
               value={form.monthly} onChange={e => setForm({ ...form, monthly: e.target.value })} />
        <button className="btn btn-primary" type="submit">Planla</button>
      </form>

      {plan && (
        <div style={{ marginTop: 14 }}>
          {plan.already_on_track ? (
            <p style={{ fontSize: 14, color: 'var(--green, #4ade80)' }}>
              🎉 Mevcut birikimin hedefe kendi kendine ulaşıyor — ekstra katkı gerekmiyor.
            </p>
          ) : (
            <p style={{ fontSize: 14 }}>
              Hedefe zamanında ulaşmak için ayda yaklaşık{' '}
              <strong style={{ fontSize: 17 }}>{fmt(plan.monthly_contribution)} TL</strong> biriktirmelisin.
            </p>
          )}

          {progress && (
            <div style={{ marginTop: 10, padding: 10, borderRadius: 10, border: '1px solid var(--border)' }}>
              <div style={{ fontSize: 13, marginBottom: 6 }}>
                Mevcut temponla ({fmt(form.monthly)} TL/ay):
              </div>
              {progress.on_track ? (
                <p style={{ fontSize: 14, color: 'var(--green, #4ade80)' }}>✓ Hedefe zamanında ulaşıyorsun.</p>
              ) : (
                <p style={{ fontSize: 14, color: 'var(--red)' }}>
                  ⏳ Bu tempoda hedefin yaklaşık <strong>{progress.delay_months} ay</strong> gecikir.
                </p>
              )}
              <div style={{ marginTop: 8, height: 8, borderRadius: 4, background: 'var(--border)', overflow: 'hidden' }}>
                <div style={{
                  width: `${progress.progress_pct}%`, height: '100%',
                  background: 'linear-gradient(90deg, #8b8bf5, #4ade80)',
                }} />
              </div>
              <div style={{ fontSize: 12, opacity: 0.7, marginTop: 4 }}>İlerleme: %{progress.progress_pct}</div>
            </div>
          )}
        </div>
      )}
      {error && <p style={{ color: 'var(--red)', fontSize: 13, marginTop: 10 }}>{error}</p>}
    </div>
  )
}
