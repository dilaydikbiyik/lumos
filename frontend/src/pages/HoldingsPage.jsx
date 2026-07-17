import { useEffect, useState, useCallback } from 'react'
import Icon from '../components/Icon'
import { useNavigate } from 'react-router-dom'
import LumosLogo from '../components/LumosLogo'
import CurrencyExposure from '../components/CurrencyExposure'
import PortfolioValueChart from '../components/PortfolioValueChart'
import { UserButton, useAuth } from '@clerk/clerk-react'
import api, { extractErrorMessage, setAuthToken } from '../utils/api'
import useMarket from '../hooks/useMarket'

const TYPE_LABELS = {
  stock: 'Hisse', fund: 'Fon', etf: 'ETF',
  real_estate: 'Konut', land: 'Arsa', vehicle: 'Araç',
  gold: 'Altın', crypto: 'Kripto', cash: 'Nakit', other: 'Diğer',
}
const OFF_EXCHANGE = ['real_estate', 'land', 'vehicle', 'cash', 'other']

const EMPTY_FORM = {
  asset_type: 'stock', name: '', ticker: '',
  purchase_amount: '', manual_current_value: '', note: '', emotion_tag: '',
}

// One-tap emotion tag — data source for the behaviour coach, fully optional
const EMOTIONS = [
  { value: '', label: 'Bu kararı ne verdirdi? (ops.)' },
  { value: 'plan', label: 'Planımın parçası' },
  { value: 'fomo', label: 'Kaçırma korkusu (FOMO)' },
  { value: 'tuyo', label: 'Tüyo / tavsiye' },
  { value: 'panik', label: 'Panik / acele' },
]

export default function HoldingsPage() {
  const navigate = useNavigate()
  const { getToken } = useAuth()
  const { money } = useMarket()
  const [holdings, setHoldings] = useState([])
  const [summary, setSummary] = useState(null)
  const [health, setHealth] = useState(null)
  const [profile, setProfile] = useState(null)
  const [form, setForm] = useState(EMPTY_FORM)
  const [showForm, setShowForm] = useState(false)
  const [error, setError] = useState(null)
  // "Empty portfolio" and "still fetching" must never look the same
  const [loaded, setLoaded] = useState(false)

  const refresh = useCallback(async () => {
    setAuthToken(await getToken())
    const [h, s, hs, p] = await Promise.all([
      api.get('/holdings'), api.get('/holdings/summary'), api.get('/holdings/health'),
      api.get('/profile').catch(() => ({ data: null })),
    ])
    setHoldings(h.data)
    setSummary(s.data)
    setHealth(hs.data)
    setProfile(p.data)
    setLoaded(true)
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
  const isVehicle = form.asset_type === 'vehicle'

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
              <div style={{ fontSize: 22, fontWeight: 700 }}>{money(summary.total_current_value)}</div>
            </div>
            <div>
              <div style={{ fontSize: 12, opacity: 0.7 }}>Kalan Bütçe</div>
              <div style={{ fontSize: 22, fontWeight: 700, color: 'var(--green, #4ade80)' }}>
                {summary.remaining_budget != null ? money(summary.remaining_budget) : '—'}
              </div>
            </div>
          </div>
        )}

        {/* Param eriyor mu? — idle cash real erosion */}
        {summary?.cash_erosion && (
          <div className="card" style={{ borderColor: 'var(--red)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
              <Icon name="droplet" size={18} color="var(--red)" />
              <strong style={{ fontSize: 14 }}>Param eriyor mu?</strong>
            </div>
            <p style={{ fontSize: 13, lineHeight: 1.6 }}>
              Kasada bekleyen {money(summary.cash_erosion.idle_cash ?? (summary.remaining_budget || 0))}'nin
              (nakit varlıkların + yatırılmamış bütçen) bu ay enflasyon nedeniyle
              gerçek değeri ~{money(summary.cash_erosion.erosion_amount)} azaldı
              (aylık enflasyon %{summary.cash_erosion.monthly_inflation_pct}).
            </p>
          </div>
        )}

        {/* Fener — health score */}
        {health && (
          <div className="card">
            <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 8 }}>
              <Icon name="bulb" size={22} glow />
              <strong>Fener Skoru: {health.overall}/100</strong>
            </div>
            <p style={{ fontSize: 11.5, color: 'var(--text-dim)', lineHeight: 1.5, marginBottom: 8 }}>
              Fener, portföyünün sağlığını tek bakışta gösterir: varlıkların ne kadar
              çeşitli ve gerektiğinde ne kadar kolay nakde çevrilebilir olduğuna bakar.
            </p>
            {health.notes.map((n, i) => (
              <p key={i} style={{ fontSize: 13, lineHeight: 1.6, opacity: 0.85 }}>{n}</p>
            ))}
          </div>
        )}

        {/* Daily value of the real portfolio — the "what happened since I
            bought it" chart */}
        <PortfolioValueChart holdingsCount={holdings.length} />

        {/* Currency exposure — TL vs FX */}
        <CurrencyExposure holdings={holdings} />

        {/* Rebuild the portfolio with the remaining budget */}
        {profile?.risk_score != null && summary?.remaining_budget > 0 && (
          <button
            className="btn btn-primary btn-full"
            onClick={() => navigate('/recommend', {
              state: {
                risk_score: profile.risk_score,
                answers: { budget: summary.remaining_budget },
              },
            })}
          >
            ↻ Kalan {money(summary.remaining_budget)} ile portföyümü güncelle
          </button>
        )}

        {/* Holdings list */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          {holdings.map(h => (
            <div key={h.id} className="card" style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
              <span style={{ fontSize: 14 }}>{TYPE_LABELS[h.asset_type] || h.asset_type}</span>
              <div style={{ flex: 1 }}>
                <div style={{ fontWeight: 600, fontSize: 14 }}>{h.name}</div>
                <div style={{ fontSize: 12, opacity: 0.7 }}>
                  Alış: {money(h.purchase_amount)}
                  {h.current_value != null && h.value_source !== 'purchase' && (
                    <> · Güncel: <strong style={{ color: 'var(--text)' }}>{money(h.current_value)}</strong>
                      {h.value_change_pct != null && (
                        <span style={{
                          marginLeft: 6, fontWeight: 700,
                          color: h.value_change_pct >= 0 ? 'var(--green, #3DD68C)' : 'var(--red)',
                        }}>
                          {h.value_change_pct >= 0 ? '▲' : '▼'} {Math.abs(h.value_change_pct)}%
                        </span>
                      )}
                      <span style={{ marginLeft: 6, fontSize: 10, opacity: 0.6 }}>
                        {h.value_source === 'live' ? '● canlı' : h.value_source === 'index' ? 'endeks tahmini' : 'manuel'}
                      </span>
                    </>
                  )}
                  {(h.current_value == null || h.value_source === 'purchase') && h.ticker && (
                    <span style={{ marginLeft: 6, fontSize: 10, opacity: 0.55 }}>
                      (canlı takip için adet veya alış tarihi ekle)
                    </span>
                  )}
                </div>
              </div>
              <button className="btn btn-ghost" onClick={() => remove(h.id)} aria-label="Sil" style={{ padding: '4px 10px' }}>✕</button>
            </div>
          ))}
          {!loaded && holdings.length === 0 && (
            <div className="card" style={{ textAlign: 'center', padding: '36px 24px' }}>
              <span className="spinner" style={{ width: 22, height: 22, display: 'inline-block' }} />
              <p style={{ fontSize: 13, color: 'var(--text-muted)', marginTop: 10 }}>
                Varlıkların yükleniyor…
              </p>
            </div>
          )}
          {loaded && holdings.length === 0 && (
            <div className="card" style={{
              textAlign: 'center', padding: '36px 24px',
              position: 'relative', overflow: 'hidden',
            }}>
              {/* Background glow */}
              <div style={{
                position: 'absolute', top: '40%', left: '50%',
                width: 140, height: 140, borderRadius: '50%',
                background: 'radial-gradient(circle, rgba(245,165,36,0.10) 0%, transparent 70%)',
                transform: 'translate(-50%, -50%)',
                animation: 'pulse 3s ease-in-out infinite',
              }} />
              <div style={{ position: 'relative', zIndex: 1 }}>
                <img src="/favicon.svg" alt="" width={46} height={46} style={{
                  display: 'block', margin: '0 auto 10px',
                  filter: 'drop-shadow(0 0 12px rgba(245,165,36,0.35))',
                }} />
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
            {/* 🚗 Vehicle warning — "is your car wealth or an expense?" */}
            {isVehicle && (
              <div style={{
                padding: '12px 14px', borderRadius: 'var(--radius-xs)',
                background: 'rgba(248,113,113,0.06)',
                border: '1px solid rgba(248,113,113,0.2)',
                fontSize: 12, lineHeight: 1.65,
              }}>
                <p style={{ fontWeight: 700, marginBottom: 6, color: 'var(--text)' }}>
                  🚗 Araban serveti mi, gideri mi?
                </p>
                <p style={{ color: 'var(--text-muted)', marginBottom: 6 }}>
                  Araç servet resmine dahil edilebilir — ama dikkatli ol: her yıl %10–20 değer kaybeder (amortisman),
                  üstüne kasko + MTV + bakım gelir. Lumos asla araç almayı yatırım olarak önermez.
                </p>
                <p style={{ color: 'var(--firefly)', fontWeight: 600 }}>
                  <Icon name="bulb" size={13} /> Bunu eklemek istiyorsan güncel piyasa değerini "Güncel tahmini değer"e yaz.
                </p>
              </div>
            )}
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
