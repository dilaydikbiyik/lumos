import { useState } from 'react'
import api, { extractErrorMessage } from '../utils/api'
import useMarket from '../hooks/useMarket'

const SUGGESTIONS = [
  '10.000 TL daha eklesem ne değişir?',
  'Daha temkinli olsam portföyüm nasıl olurdu?',
  'Daha agresif olsam ne olurdu?',
]

/**
 * "What if?" assistant — tool-use: the AI never invents the math; it calls
 * the real portfolio engine twice (before/after) and only narrates the diff.
 */
export default function WhatIfAssistant({ riskScore, budget }) {
  const { money } = useMarket()
  const [question, setQuestion] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  async function ask(q) {
    const text = q || question
    if (!text.trim()) return
    setLoading(true)
    setError(null)
    setResult(null)
    try {
      const res = await api.post('/chat/what-if', {
        question: text, risk_score: riskScore, budget,
      })
      setResult(res.data)
      setQuestion('')
    } catch (err) {
      setError(extractErrorMessage(err, 'Şu an cevaplanamadı'))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="card">
      <h3 style={{ marginBottom: 4 }}>Ne olurdu?</h3>
      <p style={{ fontSize: 13, opacity: 0.8, marginBottom: 12 }}>
        Portföyünle ilgili "ya şöyle olsaydı" sorularını sor — cevap gerçek
        hesaplamadan gelir, tahmin değil.
      </p>

      <div style={{ display: 'flex', gap: 8, marginBottom: 10 }}>
        <input
          className="input"
          style={{ flex: 1 }}
          placeholder="örn: 20.000 TL daha eklesem?"
          value={question}
          onChange={e => setQuestion(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && ask()}
        />
        <button className="btn btn-primary" onClick={() => ask()} disabled={loading}>
          {loading ? <span className="spinner" style={{ width: 16, height: 16 }} /> : 'Sor'}
        </button>
      </div>

      {!result && !loading && (
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
          {SUGGESTIONS.map(s => (
            <button key={s} className="btn btn-ghost" style={{ fontSize: 12 }} onClick={() => ask(s)}>
              {s}
            </button>
          ))}
        </div>
      )}

      {error && <p style={{ color: 'var(--red)', fontSize: 13 }}>{error}</p>}

      {result && !result.understood && (
        <p style={{ fontSize: 13, opacity: 0.8 }}>
          Bunu bütçe veya risk değişikliği sorusu olarak anlayamadım — "X TL eklesem" ya
          da "daha agresif/temkinli olsam" gibi sorabilirsin.
        </p>
      )}

      {result?.understood && (
        <>
          <p style={{ fontSize: 14, lineHeight: 1.6, marginBottom: 10 }}>{result.answer}</p>
          {result.diff.allocation_changes.length > 0 && (
            <div style={{ fontSize: 12, opacity: 0.8 }}>
              {result.diff.allocation_changes.slice(0, 4).map(c => (
                <div key={c.ticker} style={{ display: 'flex', justifyContent: 'space-between', padding: '3px 0' }}>
                  <span>{c.ticker}</span>
                  <span>%{c.before_pct} → %{c.after_pct}</span>
                </div>
              ))}
            </div>
          )}
          <p style={{ fontSize: 11, opacity: 0.55, marginTop: 8 }}>
            {money(result.diff.before_budget)} → {money(result.diff.after_budget)} ·
            Risk {result.diff.before_risk_score} → {result.diff.after_risk_score}
          </p>
        </>
      )}
    </div>
  )
}
