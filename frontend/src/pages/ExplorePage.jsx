import { useEffect, useState, useCallback } from 'react'
import { UserButton, useAuth } from '@clerk/clerk-react'
import api, { extractErrorMessage, setAuthToken } from '../utils/api'
import LumosLogo from '../components/LumosLogo'
import IsikTut from '../components/IsikTut'
import useMarket from '../hooks/useMarket'

// EVERY amount on this page is TCMB TL/m² data — it stays pinned to
// TRY + tr-TR regardless of the user's market (pretending to convert
// currencies would be a lie). For non-TR markets the page shows an
// honest "integration on the way" state instead.
const fmt = n => new Intl.NumberFormat('tr-TR', { maximumFractionDigits: 0 }).format(n)

function ProvinceScenario({ province, amount }) {
  const [band, setBand] = useState(null)
  const [links, setLinks] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [ilce, setIlce] = useState('')
  const [detail, setDetail] = useState('')
  const [assetType, setAssetType] = useState('daire')

  async function fetchLinks() {
    const res = await api.post('/planning/listing-links', {
      il: province.province, ilce, asset_type: assetType, detail,
    })
    setLinks(res.data.links)
  }

  async function run() {
    setLoading(true)
    setError(null)
    try {
      const [b] = await Promise.all([
        api.post('/planning/projection/province', {
          region_code: province.code, amount: Number(amount) || 1000000, years: 5,
        }),
        fetchLinks(),
      ])
      setBand(b.data)
    } catch (err) {
      setError(extractErrorMessage(err, 'Senaryo hesaplanamadı'))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ paddingTop: 10, marginTop: 10, borderTop: '1px solid var(--border)' }}>
      {!band && (
        <button className="btn btn-ghost" style={{ width: '100%' }} onClick={run} disabled={loading}>
          {loading
            ? <span className="spinner" style={{ width: 16, height: 16 }} />
            : `${fmt(Number(amount) || 1000000)} TL ${province.province}'de 5 yılda ne olurdu?`}
        </button>
      )}
      {error && <p style={{ color: 'var(--red)', fontSize: 12 }}>{error}</p>}
      {band && !band.available && <p style={{ fontSize: 12, opacity: 0.75 }}>{band.reason}</p>}
      {band?.available && (
        <div style={{ fontSize: 13, lineHeight: 1.7 }}>
          <div>Kötü dönem: <strong style={{ color: 'var(--red)' }}>{fmt(band.pessimistic.value)} TL</strong>
            {band.real_band && <span style={{ fontSize: 11, opacity: 0.7 }}> · reel {band.real_band.pessimistic_pct > 0 ? '+' : ''}{band.real_band.pessimistic_pct}%</span>}
          </div>
          <div>Tipik dönem: <strong style={{ color: 'var(--firefly, #F5A524)' }}>{fmt(band.typical.value)} TL</strong>
            {band.real_band && <span style={{ fontSize: 11, opacity: 0.7 }}> · reel {band.real_band.typical_pct > 0 ? '+' : ''}{band.real_band.typical_pct}%</span>}
          </div>
          <div>İyi dönem: <strong style={{ color: 'var(--green, #3DD68C)' }}>{fmt(band.optimistic.value)} TL</strong>
            {band.real_band && <span style={{ fontSize: 11, opacity: 0.7 }}> · reel {band.real_band.optimistic_pct > 0 ? '+' : ''}{band.real_band.optimistic_pct}%</span>}
          </div>
          {links && (
            <div style={{ marginTop: 10, padding: 10, borderRadius: 10, border: '1px dashed var(--border)' }}>
              <p style={{ fontSize: 12, opacity: 0.75, marginBottom: 8 }}>
                📍 İlçe/köy düzeyinde resmi fiyat verisi yayınlanmıyor — mikro konum
                için seni doğrudan ilanlara götürüyoruz:
              </p>
              <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', marginBottom: 8 }}
                   onClick={e => e.stopPropagation()}>
                <input className="input" placeholder="İlçe (örn: Keşan)" value={ilce}
                       onChange={e => setIlce(e.target.value)}
                       style={{ flex: 1, minWidth: 100, fontSize: 13 }} />
                <input className="input" placeholder="Köy/mahalle (örn: Çeribaşı)" value={detail}
                       onChange={e => setDetail(e.target.value)}
                       style={{ flex: 1, minWidth: 120, fontSize: 13 }} />
                <select className="input" value={assetType}
                        onChange={e => setAssetType(e.target.value)}
                        style={{ flex: 0.7, minWidth: 80, fontSize: 13 }}>
                  <option value="arsa">Arsa</option>
                  <option value="daire">Daire</option>
                </select>
                <button className="btn btn-ghost" style={{ fontSize: 12 }}
                        onClick={() => fetchLinks().catch(() => {})}>
                  Yenile
                </button>
              </div>
              <div style={{ display: 'flex', gap: 8 }}>
                {links.map(l => (
                  <a key={l.site} href={l.url} target="_blank" rel="noopener noreferrer"
                     className="btn btn-ghost" style={{ flex: 1, textAlign: 'center', fontSize: 12, textDecoration: 'none' }}>
                    {l.site}'de ilanlar →
                  </a>
                ))}
              </div>
            </div>
          )}
          <p style={{ fontSize: 11, opacity: 0.6, marginTop: 6 }}>⚠️ {band.honesty_note}</p>
        </div>
      )}
    </div>
  )
}

function ProvinceCard({ province, amount }) {
  const realPositive = (province.real_change_pct ?? 0) > 0
  const [open, setOpen] = useState(false)
  return (
    <div className="card" onClick={() => setOpen(true)}
         style={{ display: 'flex', alignItems: 'center', gap: 12, flexWrap: 'wrap', cursor: 'pointer' }}>
      <span style={{
        fontSize: 13, fontWeight: 700, width: 34, height: 34, borderRadius: '50%',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        background: realPositive ? 'rgba(74,222,128,0.15)' : 'rgba(248,113,113,0.12)',
        color: realPositive ? 'var(--green, #4ade80)' : 'var(--red)',
        flexShrink: 0,
      }}>{province.rank}</span>
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ fontWeight: 600, fontSize: 14 }}>{province.province}</div>
        <div style={{ fontSize: 12, opacity: 0.7 }}>{fmt(province.price_per_m2)} TL/m²</div>
      </div>
      <div style={{ textAlign: 'right', flexShrink: 0 }}>
        <div style={{ fontSize: 13 }}>+{province.nominal_change_pct}%</div>
        <div style={{
          fontSize: 13, fontWeight: 700,
          color: realPositive ? 'var(--green, #4ade80)' : 'var(--red)',
        }}>
          reel {province.real_change_pct > 0 ? '+' : ''}{province.real_change_pct}%
        </div>
      </div>
      {open && <div style={{ flexBasis: '100%' }}><ProvinceScenario province={province} amount={amount} /></div>}
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
  const { pack } = useMarket()
  const [provinces, setProvinces] = useState(null)
  const [horizon, setHorizon] = useState(3)
  const [scenarioAmount, setScenarioAmount] = useState('1000000')
  const [search, setSearch] = useState('')
  // Loading is derived: no data yet, or data belongs to a different horizon
  const loading = !provinces || provinces._horizon !== horizon

  const load = useCallback(async (years) => {
    try {
      setAuthToken(await getToken())
      const res = await api.get(`/planning/province-intelligence?horizon_years=${years}`)
      return res.data
    } catch {
      return { available: false, provinces: [] }
    }
  }, [getToken])

  useEffect(() => {
    let cancelled = false
    async function run() {
      const data = await load(horizon)
      if (!cancelled) setProvinces({ ...data, _horizon: horizon })
    }
    run()
    return () => { cancelled = true }
  }, [load, horizon])

  const q = search.trim().toLocaleLowerCase('tr')
  const visible = provinces?.available
    ? (q
        ? provinces.provinces.filter(p => p.province.toLocaleLowerCase('tr').includes(q))
        : provinces.provinces.slice(0, 12))
    : []

  // Honesty gate: this whole page is TCMB (TR) data. For non-TR markets
  // we say so plainly instead of dressing TL data up as dollars/euros.
  if (!pack.live_housing_index) {
    return (
      <div className="page">
        <header className="navbar">
          <LumosLogo />
          <UserButton afterSignOutUrl="/" />
        </header>
        <div className="page-content">
          <h2>Emlak Keşfet</h2>
          <div className="card" style={{ marginTop: 16, textAlign: 'center', padding: 28 }}>
            <div style={{ fontSize: 32, marginBottom: 10 }}>🌍</div>
            <p style={{ fontSize: 14, lineHeight: 1.7 }}>
              <strong>{pack.name}</strong> pazarı için canlı konut verisi entegrasyonu yolda.
              Bu sayfa şu an yalnızca Türkiye (TCMB) verisiyle çalışıyor — sana
              başka bir ülkenin verisini "buymuş gibi" göstermeyiz.
            </p>
            <p style={{ fontSize: 12, opacity: 0.65, marginTop: 10 }}>
              Pazarı sol menüden 🇹🇷 Türkiye'ye alarak il il m² fiyatlarını görebilirsin.
            </p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="page">
      <header className="navbar">
        <LumosLogo />
        <UserButton afterSignOutUrl="/" />
      </header>

      <div className="page-content" style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
        <div>
          <h2>Emlak Keşfet</h2>
          <p style={{ fontSize: 13, marginTop: 4 }}>
            İl il konut m² fiyatları ve gerçek (<IsikTut term="reel getiri">enflasyon sonrası</IsikTut>) değerlenme — TCMB verisiyle
          </p>
        </div>

        {/* Region intelligence */}
        <div className="card" style={{ padding: 0, background: 'none', border: 'none', boxShadow: 'none' }}>
          <div style={{ display: 'flex', gap: 8, marginBottom: 12 }}>
            {[1, 3, 5].map(y => (
              <button key={y}
                      className={`btn ${horizon === y ? 'btn-primary' : 'btn-ghost'}`}
                      style={{ flex: 1 }}
                      onClick={() => setHorizon(y)}>
                Son {y} yıl
              </button>
            ))}
          </div>

          <input
            className="input"
            placeholder="İl ara (örn: Muğla, Eskişehir...)"
            value={search}
            onChange={e => setSearch(e.target.value)}
            style={{ marginBottom: 12 }}
            aria-label="İl ara"
          />

          <input
            className="input"
            type="number"
            min="1"
            placeholder="Senaryo tutarı (TL)"
            value={scenarioAmount}
            onChange={e => setScenarioAmount(e.target.value)}
            style={{ marginBottom: 12 }}
            aria-label="Senaryo tutarı"
          />

          {loading && (
            <div style={{ textAlign: 'center', padding: 24 }}>
              <span className="spinner" style={{ width: 28, height: 28 }} />
            </div>
          )}

          {!loading && provinces?.available && (
            <>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                {visible.map(p => <ProvinceCard key={p.code} province={p} amount={scenarioAmount} />)}
                {visible.length === 0 && (
                  <p style={{ fontSize: 13, opacity: 0.7, textAlign: 'center', padding: 12 }}>
                    "{search}" bulunamadı — 81 ilin tamamında arayabilirsin.
                  </p>
                )}
              </div>
              {!q && (
                <p style={{ fontSize: 12, opacity: 0.55, marginTop: 8, textAlign: 'center' }}>
                  İlk 12 il gösteriliyor — diğer iller için yukarıdan ara.
                </p>
              )}
              <p style={{ fontSize: 12, opacity: 0.6, marginTop: 10, lineHeight: 1.5 }}>
                ⚠️ {provinces.honesty_note} (Veri: {provinces.data_through})
              </p>
            </>
          )}

          {!loading && !provinces?.available && (
            <div className="card" style={{ textAlign: 'center', padding: 24 }}>
              <p style={{ fontSize: 14 }}>İl verisi şu an alınamıyor — birazdan tekrar dene.</p>
            </div>
          )}
        </div>

        <RentVsBuy />
        <ListingLinks />
      </div>
    </div>
  )
}
