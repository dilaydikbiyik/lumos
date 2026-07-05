import { useEffect, useState, useCallback } from 'react'
import LumosLogo from '../components/LumosLogo'
import CurrencyExposure from '../components/CurrencyExposure'
import { UserButton, useAuth } from '@clerk/clerk-react'
import api, { extractErrorMessage, setAuthToken } from '../utils/api'

const TYPE_LABELS = {
  stock: '📈 Hisse', fund: '🧺 Fon', etf: '🧺 ETF',
  real_estate: '🏠 Konut', land: '🌍 Arsa', vehicle: '🚗 Araç',
  gold: '🥇 Altın', crypto: '🪙 Kripto', cash: '💵 Nakit', other: '📦 Diğer',
}
const OFF_EXCHANGE = ['real_estate', 'land', 'vehicle', 'cash', 'other']

const EMPTY_FORM = {
  asset_type: 'stock', name: '', ticker: '',
  purchase_amount: '', manual_current_value: '', note: '', emotion_tag: '',
}

// 1-tık duygu etiketi — davranış koçunun veri kaynağı, tamamen opsiyonel
const EMOTIONS = [
  { value: '', label: 'Bu kararı ne verdirdi? (ops.)' },
  { value: 'plan', label: '📋 Planımın parçası' },
  { value: 'fomo', label: '🔥 Kaçırma korkusu (FOMO)' },
  { value: 'tuyo', label: '🗣️ Tüyo / tavsiye' },
  { value: 'panik', label: '😰 Panik / acele' },
]

const fmt = n => new Intl.NumberFormat('tr-TR', { maximumFractionDigits: 0 }).format(n)

export default function HoldingsPage() {
  const { getToken } = useAuth()
  const [holdings, setHoldings] = useState([])
  const [summary, setSummary] = useState(null)
  const [health, setHealth] = useState(null)
  const [form, setForm] = useState(EMPTY_FORM)
  const [showForm, setShowForm] = useState(false)
  const [error, setError] = useState(null)

  const refresh = useCallback(async () => {
    setAuthToken(await getToken())
    const [h, s, hs] = await Promise.all([
      api.get('/holdings'), api.get('/holdings/summary'), api.get('/holdings/health'),
    ])
    setHoldings(h.data)
    setSummary(s.data)
    setHealth(hs.data)
  }, [getToken])

  useEffect(() => {
    let cancelled = false
    async function load() {
      try {
        await refresh()
      } catch {
        if (!cancelled) setError('Varlıklar yüklenemedi')
      }
    }
    load()
    return () => { cancelled = true }
  }, [refresh])

  async function addHolding(e) {
    e.preventDefault()
    setError(null)
    try {
      const body = {
        asset_type: form.asset_type,
        name: form.name,
        purchase_amount: Number(form.purchase_amount),
      }
      if (form.ticker) body.ticker = form.ticker.toUpperCase()
      if (form.manual_current_value) body.manual_current_value = Number(form.manual_current_value)
      if (form.note) body.note = form.note
      if (form.emotion_tag) body.emotion_tag = form.emotion_tag
      await api.post('/holdings', body)
      setForm(EMPTY_FORM)
      setShowForm(false)
      await refresh()
    } catch (err) {
      setError(extractErrorMessage(err, 'Varlık eklenemedi'))
    }
  }

  async function remove(id) {
    await api.delete(`/holdings/${id}`)
    await refresh()
  }

  const needsTicker = !OFF_EXCHANGE.includes(form.asset_type)

  return (
    <div className="page">
      <header className="navbar">
        <LumosLogo />
        <UserButton afterSignOutUrl="/" />
      </header>

      <div className="page-content" style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
        <div>
          <h2>Varlıklarım</h2>
          <p style={{ fontSize: 13, marginTop: 4 }}>Borsa + emlak + aracın — tüm servetin tek resimde</p>
        </div>

        {/* Wealth summary */}
        {summary && (
          <div className="card" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
            <div>
              <div style={{ fontSize: 12, opacity: 0.7 }}>Toplam Değer</div>
              <div style={{ fontSize: 22, fontWeight: 700 }}>{fmt(summary.total_current_value)} TL</div>
            </div>
            <div>
              <div style={{ fontSize: 12, opacity: 0.7 }}>Kalan Bütçe</div>
              <div style={{ fontSize: 22, fontWeight: 700, color: 'var(--green, #4ade80)' }}>
                {summary.remaining_budget != null ? `${fmt(summary.remaining_budget)} TL` : '—'}
              </div>
            </div>
          </div>
        )}

        {/* Param eriyor mu? — idle cash real erosion */}
        {summary?.cash_erosion && (
          <div className="card" style={{ borderColor: 'var(--red)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
              <span style={{ fontSize: 18 }}>💧</span>
              <strong style={{ fontSize: 14 }}>Param eriyor mu?</strong>
            </div>
            <p style={{ fontSize: 13, lineHeight: 1.6 }}>
              Yatırılmamış {fmt(summary.remaining_budget || 0)} TL'nin bu ay enflasyon nedeniyle
              gerçek değeri ~{fmt(summary.cash_erosion.erosion_amount)} TL azaldı
              (aylık enflasyon %{summary.cash_erosion.monthly_inflation_pct}).
            </p>
          </div>
        )}

        {/* Fener — health score */}
        {health && (
          <div className="card">
            <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 8 }}>
              <span style={{ fontSize: 22 }}>🔦</span>
              <strong>Fener Skoru: {health.overall}/100</strong>
            </div>
            {health.notes.map((n, i) => (
              <p key={i} style={{ fontSize: 13, lineHeight: 1.6, opacity: 0.85 }}>{n}</p>
            ))}
          </div>
        )}

        {/* Kur dağılımı — TL vs döviz */}
        <CurrencyExposure holdings={holdings} />

        {/* Holdings list */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          {holdings.map(h => (
            <div key={h.id} className="card" style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
              <span style={{ fontSize: 14 }}>{TYPE_LABELS[h.asset_type] || h.asset_type}</span>
              <div style={{ flex: 1 }}>
                <div style={{ fontWeight: 600, fontSize: 14 }}>{h.name}</div>
                <div style={{ fontSize: 12, opacity: 0.7 }}>
                  Alış: {fmt(h.purchase_amount)} TL
                  {h.manual_current_value != null && ` · Güncel: ${fmt(h.manual_current_value)} TL`}
                </div>
              </div>
              <button className="btn btn-ghost" onClick={() => remove(h.id)} aria-label="Sil" style={{ padding: '4px 10px' }}>✕</button>
            </div>
          ))}
          {holdings.length === 0 && (
            <div className="card" style={{
              textAlign: 'center', padding: '36px 24px',
              position: 'relative', overflow: 'hidden',
            }}>
              {/* Arka plan ışıltı */}
              <div style={{
                position: 'absolute', top: '40%', left: '50%',
                width: 140, height: 140, borderRadius: '50%',
                background: 'radial-gradient(circle, rgba(245,165,36,0.10) 0%, transparent 70%)',
                transform: 'translate(-50%, -50%)',
                animation: 'pulse 3s ease-in-out infinite',
              }} />
              <div style={{ position: 'relative', zIndex: 1 }}>
                <div style={{
                  fontSize: 36, marginBottom: 10,
                  filter: 'drop-shadow(0 0 12px rgba(245,165,36,0.35))',
                }}>🪲</div>
                <p style={{ fontSize: 14, fontWeight: 600, marginBottom: 4 }}>
                  Henüz varlığın yok
                </p>
                <p style={{ fontSize: 13, color: 'var(--text-muted)', lineHeight: 1.6 }}>
                  İlk ışığı birlikte yakalayalım — bir varlık ekleyerek başla.
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Add form */}
        {showForm ? (
          <form className="card" onSubmit={addHolding} style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            <select className="input" value={form.asset_type}
                    onChange={e => setForm({ ...form, asset_type: e.target.value })}>
              {Object.entries(TYPE_LABELS).map(([v, label]) => <option key={v} value={v}>{label}</option>)}
            </select>
            <input className="input" placeholder="Ad (örn: Gölbaşı arsa, SPY ETF)" required
                   value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} />
            {needsTicker && (
              <input className="input" placeholder="Sembol (örn: SPY, THYAO.IS)" required
                     value={form.ticker} onChange={e => setForm({ ...form, ticker: e.target.value })} />
            )}
            <input className="input" type="number" placeholder="Alış tutarı (TL)" required min="1"
                   value={form.purchase_amount} onChange={e => setForm({ ...form, purchase_amount: e.target.value })} />
            <input className="input" type="number" placeholder="Güncel tahmini değer (opsiyonel)" min="1"
                   value={form.manual_current_value} onChange={e => setForm({ ...form, manual_current_value: e.target.value })} />
            <select className="input" value={form.emotion_tag}
                    onChange={e => setForm({ ...form, emotion_tag: e.target.value })}>
              {EMOTIONS.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
            </select>
            <div style={{ display: 'flex', gap: 8 }}>
              <button className="btn btn-primary" type="submit" style={{ flex: 1 }}>Ekle</button>
              <button className="btn btn-ghost" type="button" onClick={() => setShowForm(false)}>Vazgeç</button>
            </div>
          </form>
        ) : (
          <button className="btn btn-primary btn-full" onClick={() => setShowForm(true)}>
            + Varlık Ekle
          </button>
        )}

        {error && <p style={{ color: 'var(--red)', fontSize: 13 }}>{error}</p>}
      </div>
    </div>
  )
}
