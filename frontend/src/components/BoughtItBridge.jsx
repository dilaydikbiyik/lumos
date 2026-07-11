import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api, { extractErrorMessage } from '../utils/api'
import useMarket from '../hooks/useMarket'

// portfolio category -> holding asset type
const CATEGORY_TO_TYPE = {
  stocks: 'stock', reit: 'etf', fund: 'fund', gold: 'gold', cash: 'cash',
}
const NO_TICKER_TYPES = new Set(['cash'])

/**
 * "I bought it" bridge — the last link of our execution model: the user
 * buys at their own broker, then records the portfolio into holdings here
 * with one tap.
 */
export default function BoughtItBridge({ allocations, budget }) {
  const navigate = useNavigate()
  const { money } = useMarket()
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState(null)

  async function transfer() {
    setSaving(true)
    setError(null)
    try {
      for (const a of allocations) {
        const amount = Math.round(a.weight * budget)
        if (amount <= 0) continue
        const type = CATEGORY_TO_TYPE[a.category] || 'other'
        const body = {
          asset_type: type,
          name: a.name,
          purchase_amount: amount,
          // purchase date = today → live price tracking kicks in automatically
          purchase_date: new Date().toISOString().slice(0, 10),
        }
        if (!NO_TICKER_TYPES.has(type)) body.ticker = a.ticker
        await api.post('/holdings', body)
      }
      navigate('/holdings')
    } catch (err) {
      setError(extractErrorMessage(err, 'Aktarım tamamlanamadı — Varlıklarım sayfasından tek tek ekleyebilirsin.'))
      setSaving(false)
    }
  }

  return (
    <div className="card">
      <h3 style={{ marginBottom: 4 }}>✅ Bu portföyü aldın mı?</h3>
      <p style={{ fontSize: 13, opacity: 0.8, marginBottom: 12 }}>
        Alımını kendi aracı kurumunda yaptıysan, portföyü tek tıkla
        Varlıklarım'a işleyelim — kalan bütçen otomatik güncellenir.
      </p>
      <button className="btn btn-primary btn-full" onClick={transfer} disabled={saving}>
        {saving
          ? <span className="spinner" style={{ width: 18, height: 18 }} />
          : `Aldım — ${money(budget)}'lik dağılımı işle`}
      </button>
      {error && <p style={{ color: 'var(--red)', fontSize: 13, marginTop: 10 }}>{error}</p>}
    </div>
  )
}
