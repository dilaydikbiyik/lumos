import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '@clerk/clerk-react'
import api, { extractErrorMessage } from '../utils/api'
import useMarket from '../hooks/useMarket'
import { readJSON, userKey } from '../utils/storage'

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
  const { userId } = useAuth()
  const [saving, setSaving] = useState(false)
  const [addingMore, setAddingMore] = useState(false)
  const [error, setError] = useState(null)

  const isRecorded = holdings =>
    Array.isArray(holdings) && allocations.some(a => {
      const owned = new Set(holdings.map(h => h.ticker || h.name).filter(Boolean))
      return owned.has(a.ticker) || owned.has(a.name)
    })

  // Start from the holdings snapshot the app already has, so a portfolio that
  // is clearly recorded never flashes the "Aldım" button first. null = we
  // genuinely don't know yet, and offering the button in that state could
  // invite a duplicate transfer — so we show neither until we do.
  const [alreadyRecorded, setAlreadyRecorded] = useState(() => {
    const cached = readJSON(userKey('holdings', userId))
    return cached ? isRecorded(cached.holdings) : null
  })

  useEffect(() => {
    let cancelled = false
    ;(async () => {
      try {
        const res = await api.get('/holdings')
        if (!cancelled) setAlreadyRecorded(isRecorded(res.data))
      } catch {
        // Network is down: fall back to "not recorded" so the user is never
        // stuck with no way forward — the backend still de-duplicates.
        if (!cancelled) setAlreadyRecorded(prev => (prev === null ? false : prev))
      }
    })()
    return () => { cancelled = true }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [allocations, userId])

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

  if (alreadyRecorded === null) {
    return (
      <div className="card" style={{ opacity: 0.6 }}>
        <p style={{ fontSize: 'var(--t-small)' }}>Varlıklarım kontrol ediliyor…</p>
      </div>
    )
  }

  if (alreadyRecorded && !addingMore) {
    return (
      <div className="card">
        <h3 style={{ marginBottom: 4 }}>Bu portföy Varlıklarım&apos;da ✓</h3>
        <p style={{ fontSize: 'var(--t-small)', opacity: 0.8, marginBottom: 12 }}>
          Bu varlıkları daha önce işledin — güncel değerlerini Varlıklarım&apos;dan takip
          edebilirsin.
        </p>
        <button className="btn btn-ghost btn-full" onClick={() => navigate('/holdings')}>
          Varlıklarım&apos;a git →
        </button>
        {/* Regular investors buy the same mix again every month; "already
            recorded" must inform, never block. */}
        <button
          className="btn btn-ghost btn-full"
          style={{ marginTop: 8, fontSize: 'var(--t-micro)', color: 'var(--text-dim)' }}
          onClick={() => setAddingMore(true)}
        >
          Yeni bir alım daha işlemek istiyorum
        </button>
      </div>
    )
  }

  return (
    <div className="card">
      <h3 style={{ marginBottom: 4 }}>
        {addingMore ? 'Yeni alımını işle' : 'Bu portföyü aldın mı?'}
      </h3>
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
