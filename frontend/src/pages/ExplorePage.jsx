import { useEffect, useState, useCallback } from 'react'
import { UserButton, useAuth } from '@clerk/clerk-react'
import api, { extractErrorMessage, setAuthToken } from '../utils/api'
import IsikTut from '../components/IsikTut'

const fmt = n => new Intl.NumberFormat('tr-TR', { maximumFractionDigits: 0 }).format(n)

function RegionCard({ region }) {
  const realPositive = region.real_change_pct > 0
  return (
    <div className="card" style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
      <span style={{
        fontSize: 15, fontWeight: 700, width: 34, height: 34, borderRadius: '50%',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        background: realPositive ? 'rgba(74,222,128,0.15)' : 'rgba(248,113,113,0.12)',
        color: realPositive ? 'var(--green, #4ade80)' : 'var(--red)',
        flexShrink: 0,
      }}>{region.rank}</span>
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ fontWeight: 600, fontSize: 14 }}>{region.region}</div>
        <div style={{ fontSize: 12, opacity: 0.7 }}>{region.note}</div>
      </div>
      <div style={{ textAlign: 'right', flexShrink: 0 }}>
        <div style={{ fontSize: 13 }}>+{region.nominal_change_pct}%</div>
        <div style={{
          fontSize: 13, fontWeight: 700,
          color: realPositive ? 'var(--green, #4ade80)' : 'var(--red)',
        }}>
          reel {region.real_change_pct > 0 ? '+' : ''}{region.real_change_pct}%
        </div>
      </div>
    </div>
  )
}

function RentVsBuy() {
  const [form, setForm] = useState({ down_payment: '', monthly_rent: '', years: 10 })
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  async function run(e) {
    e.preventDefault()
    setError(null)
    try {
      const res = await api.post('/planning/rent-vs-buy', {
        down_payment: Number(form.down_payment),
        monthly_rent: Number(form.monthly_rent),
        years: Number(form.years),
      })
      setResult(res.data)
    } catch (err) {
      setError(extractErrorMessage(err, 'Hesaplanamadı'))
    }
  }

  return (
    <div className="card">
      <h3 style={{ marginBottom: 4 }}>🏠 Kirada mı otur, ev mi al?</h3>
      <p style={{ fontSize: 13, opacity: 0.8, marginBottom: 12 }}>
        İki senaryoyu dürüstçe yan yana koyarız — ev almak her zaman kazanç değildir.
      </p>
      <form onSubmit={run} style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
        <input className="input" type="number" placeholder="Peşinat / birikimin (TL)" required min="1"
               value={form.down_payment} onChange={e => setForm({ ...form, down_payment: e.target.value })} />
        <input className="input" type="number" placeholder="Şu anki aylık kiran (TL)" required min="1"
               value={form.monthly_rent} onChange={e => setForm({ ...form, monthly_rent: e.target.value })} />
        <select className="input" value={form.years} onChange={e => setForm({ ...form, years: e.target.value })}>
          {[5, 10, 20].map(y => <option key={y} value={y}>{y} yıllık projeksiyon</option>)}
        </select>
        <button className="btn btn-primary" type="submit">Karşılaştır</button>
      </form>

      {result && (
        <div style={{ marginTop: 14, display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
          <div style={{ padding: 12, borderRadius: 10, border: '1px solid var(--border)' }}>
            <div style={{ fontSize: 13, fontWeight: 700, marginBottom: 6 }}>🏠 Ev alırsan</div>
            <div style={{ fontSize: 12, opacity: 0.75 }}>Evin tahmini değeri</div>
            <div style={{ fontSize: 17, fontWeight: 700 }}>{fmt(result.buy.property_value)} TL</div>
            <div style={{ fontSize: 12, opacity: 0.75, marginTop: 6 }}>Kira ödemezsin</div>
          </div>
          <div style={{ padding: 12, borderRadius: 10, border: '1px solid var(--border)' }}>
            <div style={{ fontSize: 13, fontWeight: 700, marginBottom: 6 }}>📊 Kirada kalırsan</div>
            <div style={{ fontSize: 12, opacity: 0.75 }}>Portföyün + ödenen kira sonrası net</div>
            <div style={{ fontSize: 17, fontWeight: 700 }}>{fmt(result.rent.net_position)} TL</div>
            <div style={{ fontSize: 12, opacity: 0.75, marginTop: 6 }}>
              (Ödenen kira: {fmt(result.rent.total_rent_paid)} TL)
            </div>
          </div>
          <p style={{ gridColumn: '1 / -1', fontSize: 12, opacity: 0.65, lineHeight: 1.5 }}>
            Varsayımlar: konut yıllık %{result.assumptions.housing_annual_growth_pct},
            portföy yıllık %{result.assumptions.portfolio_annual_growth_pct} büyüme.
            Ev sahibi olma güvencesinin parasal olmayan değeri bu hesapta yok — o kararın duygusal
            tarafı da meşrudur.
          </p>
        </div>
      )}
      {error && <p style={{ color: 'var(--red)', fontSize: 13, marginTop: 10 }}>{error}</p>}
    </div>
  )
}

function ListingLinks() {
  const [form, setForm] = useState({ il: '', ilce: '', asset_type: 'arsa' })
  const [links, setLinks] = useState(null)
  const [error, setError] = useState(null)

  async function run(e) {
    e.preventDefault()
    setError(null)
    try {
      const res = await api.post('/planning/listing-links', form)
      setLinks(res.data.links)
    } catch (err) {
      setError(extractErrorMessage(err, 'Link üretilemedi'))
    }
  }

  return (
    <div className="card">
      <h3 style={{ marginBottom: 4 }}>🔗 İlanlara Git</h3>
      <p style={{ fontSize: 13, opacity: 0.8, marginBottom: 12 }}>
        Beğendiğin bölge için filtresi hazır ilan araması — satın almayı ilan sitesinde yaparsın,
        sonra buraya döner "Aldım" dersin.
      </p>
      <form onSubmit={run} style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
        <input className="input" placeholder="İl (örn: Ankara)" required style={{ flex: 2, minWidth: 120 }}
               value={form.il} onChange={e => setForm({ ...form, il: e.target.value })} />
        <input className="input" placeholder="İlçe (opsiyonel)" style={{ flex: 2, minWidth: 120 }}
               value={form.ilce} onChange={e => setForm({ ...form, ilce: e.target.value })} />
        <select className="input" style={{ flex: 1, minWidth: 90 }} value={form.asset_type}
                onChange={e => setForm({ ...form, asset_type: e.target.value })}>
          <option value="arsa">Arsa</option>
          <option value="daire">Daire</option>
        </select>
        <button className="btn btn-primary" type="submit" style={{ flexBasis: '100%' }}>Linkleri Getir</button>
      </form>
      {links && (
        <div style={{ display: 'flex', gap: 10, marginTop: 12 }}>
          {links.map(l => (
            <a key={l.site} href={l.url} target="_blank" rel="noopener noreferrer"
               className="btn btn-ghost" style={{ flex: 1, textAlign: 'center', textDecoration: 'none' }}>
              {l.site} →
            </a>
          ))}
        </div>
      )}
      {error && <p style={{ color: 'var(--red)', fontSize: 13, marginTop: 10 }}>{error}</p>}
    </div>
  )
}

export default function ExplorePage() {
  const { getToken } = useAuth()
  const [regions, setRegions] = useState(null)
  const [horizon, setHorizon] = useState(1)
  // Loading is derived: no data yet, or data belongs to a different horizon
  const loading = !regions || regions._horizon !== horizon

  const load = useCallback(async (years) => {
    try {
      setAuthToken(await getToken())
      const res = await api.get(`/planning/region-intelligence?horizon_years=${years}`)
      return res.data
    } catch {
      return { available: false, regions: [] }
    }
  }, [getToken])

  useEffect(() => {
    let cancelled = false
    async function run() {
      const data = await load(horizon)
      if (!cancelled) setRegions({ ...data, _horizon: horizon })
    }
    run()
    return () => { cancelled = true }
  }, [load, horizon])

  return (
    <div className="page">
      <header className="navbar">
        <span style={{ fontWeight: 700 }}><span className="gradient-text">Lumos</span></span>
        <UserButton afterSignOutUrl="/" />
      </header>

      <div className="page-content" style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
        <div>
          <h2>Emlak Keşfet</h2>
          <p style={{ fontSize: 13, marginTop: 4 }}>
            Bölgelerin gerçek (<IsikTut term="reel getiri">enflasyon sonrası</IsikTut>) değerlenmesi — TCMB verisiyle
          </p>
        </div>

        {/* Region intelligence */}
        <div className="card" style={{ padding: 0, background: 'none', border: 'none', boxShadow: 'none' }}>
          <div style={{ display: 'flex', gap: 8, marginBottom: 12 }}>
            {[1, 2, 3].map(y => (
              <button key={y}
                      className={`btn ${horizon === y ? 'btn-primary' : 'btn-ghost'}`}
                      style={{ flex: 1 }}
                      onClick={() => setHorizon(y)}>
                Son {y} yıl
              </button>
            ))}
          </div>

          {loading && (
            <div style={{ textAlign: 'center', padding: 24 }}>
              <span className="spinner" style={{ width: 28, height: 28 }} />
            </div>
          )}

          {!loading && regions?.available && (
            <>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                {regions.regions.map(r => <RegionCard key={r.code} region={r} />)}
              </div>
              <p style={{ fontSize: 12, opacity: 0.6, marginTop: 10, lineHeight: 1.5 }}>
                ⚠️ {regions.honesty_note} (Veri: {regions.data_through})
              </p>
            </>
          )}

          {!loading && !regions?.available && (
            <div className="card" style={{ textAlign: 'center', padding: 24 }}>
              <p style={{ fontSize: 14 }}>Bölge verisi şu an alınamıyor — birazdan tekrar dene.</p>
            </div>
          )}
        </div>

        <RentVsBuy />
        <ListingLinks />
      </div>
    </div>
  )
}
