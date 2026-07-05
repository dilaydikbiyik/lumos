import { useState } from 'react'
import api, { extractErrorMessage } from '../utils/api'
import IsikTut from './IsikTut'

const fmt = n => new Intl.NumberFormat('tr-TR', { maximumFractionDigits: 0 }).format(n)

function BandRow({ label, tone, data, amount }) {
  const colors = { bad: 'var(--red)', mid: 'var(--firefly, #F5A524)', good: 'var(--green, #3DD68C)' }
  const gain = data.value - amount
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '8px 0' }}>
      <span style={{ fontSize: 12, width: 76, opacity: 0.75 }}>{label}</span>
      <div style={{ flex: 1, height: 6, borderRadius: 3, background: 'var(--bg-input)', overflow: 'hidden' }}>
        <div style={{
          width: `${Math.min(Math.max((data.return_pct + 100) / 3, 4), 100)}%`,
          height: '100%', background: colors[tone], opacity: 0.75,
        }} />
      </div>
      <div style={{ textAlign: 'right', minWidth: 120 }}>
        <span style={{ fontSize: 14, fontWeight: 700, color: colors[tone] }}>{fmt(data.value)} TL</span>
        <span style={{ fontSize: 11, opacity: 0.65, display: 'block' }}>
          {gain >= 0 ? '+' : ''}{fmt(gain)} ({data.return_pct > 0 ? '+' : ''}{data.return_pct}%)
        </span>
      </div>
    </div>
  )
}

/**
 * Gelecek Senaryoları — "SPY'a param 5 yılda ne olur?" sorusunun dürüst hali.
 * Tahmin yok: varlığın kendi geçmişindeki tüm N-yıllık pencerelerin dağılımı.
 */
export default function FutureScenarios({ allocations, budget }) {
  const [ticker, setTicker] = useState(allocations?.[0]?.ticker || '')
  const [years, setYears] = useState(5)
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  async function run() {
    setLoading(true)
    setError(null)
    try {
      const res = await api.post('/planning/projection/asset', {
        ticker, amount: budget, years,
      })
      setResult(res.data)
    } catch (err) {
      setError(extractErrorMessage(err, 'Senaryolar şu an hesaplanamadı'))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="card">
      <h3 style={{ marginBottom: 4 }}>🔮 Gelecek Senaryoları</h3>
      <p style={{ fontSize: 13, opacity: 0.8, marginBottom: 12 }}>
        "Param {years} yılda ne olur?" — <IsikTut term="volatilite">tahmin değil</IsikTut>,
        varlığın kendi geçmişinde yaşanmış tüm {years} yıllık dönemlerin aralığı.
      </p>

      <div style={{ display: 'flex', gap: 8, marginBottom: 12 }}>
        <select className="input" style={{ flex: 2 }} value={ticker}
                onChange={e => { setTicker(e.target.value); setResult(null) }}>
          {allocations?.map(a => (
            <option key={a.ticker} value={a.ticker}>{a.name} ({a.ticker})</option>
          ))}
        </select>
        <select className="input" style={{ flex: 1 }} value={years}
                onChange={e => { setYears(Number(e.target.value)); setResult(null) }}>
          {[1, 3, 5].map(y => <option key={y} value={y}>{y} yıl</option>)}
        </select>
        <button className="btn btn-primary" onClick={run} disabled={loading || !ticker}>
          {loading ? <span className="spinner" style={{ width: 16, height: 16 }} /> : 'Göster'}
        </button>
      </div>

      {error && <p style={{ color: 'var(--red)', fontSize: 13 }}>{error}</p>}

      {result && !result.available && (
        <p style={{ fontSize: 13, opacity: 0.8 }}>{result.reason}</p>
      )}

      {result?.available && (
        <>
          <p style={{ fontSize: 13, marginBottom: 4 }}>
            <strong>{fmt(budget)} TL</strong>, {result.ticker} içinde {years} yıl kalsaydı
            (geçmiş {result.history_years} yılın {result.windows_analysed} dönemine göre):
          </p>
          <BandRow label="Kötü dönem"  tone="bad"  data={result.pessimistic} amount={budget} />
          <BandRow label="Tipik dönem" tone="mid"  data={result.typical}     amount={budget} />
          <BandRow label="İyi dönem"   tone="good" data={result.optimistic}  amount={budget} />
          <p style={{ fontSize: 12, opacity: 0.6, marginTop: 8, lineHeight: 1.5 }}>
            ⚠️ {result.honesty_note}
          </p>
        </>
      )}
    </div>
  )
}
