import { useEffect, useState, useCallback } from 'react'
import { UserButton, useAuth } from '@clerk/clerk-react'
import { parseTL } from '../utils/number'
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
          region_code: province.code, amount: parseTL(amount) || 1000000, years: 5,
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
            : `${fmt(parseTL(amount) || 1000000)} TL ile ${province.province}'de konut alsaydım?`}
        </button>
      )}
      {error && <p style={{ color: 'var(--red)', fontSize: 12 }}>{error}</p>}
      {band && !band.available && <p style={{ fontSize: 12, opacity: 0.75 }}>{band.reason}</p>}
      {band?.available && (
        <div style={{ fontSize: 13, lineHeight: 1.7 }}>
          <p style={{ fontSize: 12, color: 'var(--text-muted)', lineHeight: 1.6, marginBottom: 8 }}>
            TCMB&apos;nin {province.province} konut fiyat endeksine göre, geçmişteki
            <strong> tüm 5 yıllık dönemler</strong> tek tek hesaplandı. Bugün bu parayla
            konut alsaydın, o dönemlerin sonunda elindeki değer şu aralıkta olurdu:
          </p>
          <div>En kötü dönemlerden biri (%10&apos;luk dilim): <strong style={{ color: 'var(--red)' }}>{fmt(band.pessimistic.value)} TL</strong>
            {band.real_band && <span style={{ fontSize: 11, opacity: 0.7 }}> · reel {band.real_band.pessimistic_pct > 0 ? '+' : ''}{band.real_band.pessimistic_pct}%</span>}
          </div>
          <div>Tipik dönem (ortanca): <strong style={{ color: 'var(--firefly, #F5A524)' }}>{fmt(band.typical.value)} TL</strong>
            {band.real_band && <span style={{ fontSize: 11, opacity: 0.7 }}> · reel {band.real_band.typical_pct > 0 ? '+' : ''}{band.real_band.typical_pct}%</span>}
          </div>
          <div>En iyi dönemlerden biri (%90&apos;lık dilim): <strong style={{ color: 'var(--green, #3DD68C)' }}>{fmt(band.optimistic.value)} TL</strong>
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
          <p style={{ fontSize: 11, opacity: 0.6, marginTop: 6 }}>{band.honesty_note}</p>
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
  const [form, setForm] = useState({ down_payment: '', monthly_rent: '', home_price: '', income: '', years: 10 })
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)
  // Income lives on the user profile: prefilled when known, asked at most once
  const [savedIncome, setSavedIncome] = useState(null)

  useEffect(() => {
    let cancelled = false
    api.get('/users/me')
      .then(res => {
        if (cancelled) return
        if (res.data?.monthly_income > 0) {
          setSavedIncome(res.data.monthly_income)
          setForm(f => ({ ...f, income: String(res.data.monthly_income) }))
        }
      })
      .catch(() => {})
    return () => { cancelled = true }
  }, [])

  async function run(e) {
    e.preventDefault()
    setError(null)
    setLoading(true)
    try {
      const res = await api.post('/planning/rent-vs-buy', {
        down_payment: parseTL(form.down_payment),
        monthly_rent: parseTL(form.monthly_rent),
        years: Number(form.years),
        ...(form.home_price ? { home_price: parseTL(form.home_price) } : {}),
      })
      setResult(res.data)
      const income = parseTL(form.income)
      if (income > 0 && income !== savedIncome) {
        api.patch('/users/me/income', { monthly_income: income })
          .then(() => setSavedIncome(income)).catch(() => {})
      }
    } catch (err) {
      setError(extractErrorMessage(err, 'Hesaplanamadı'))
    } finally {
      setLoading(false)
    }
  }

  const buyWins = result?.verdict === 'buy'

  return (
    <div className="card">
      <h3 style={{ marginBottom: 4 }}>Kirada mı otur, ev mi al?</h3>
      <p style={{ fontSize: 13, opacity: 0.8, marginBottom: 12 }}>
        Aynı evi iki senaryoda karşılaştırırız: peşinat + kredi ile satın almak, ya da
        kirada kalıp farkı yatırmak. Ev almak her zaman kazanç değildir.
      </p>
      <form onSubmit={run} style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
        <input className="input" type="text" inputMode="numeric" placeholder="Peşinat / birikimin (TL)" required
               value={form.down_payment} onChange={e => setForm({ ...form, down_payment: e.target.value })} />
        <input className="input" type="text" inputMode="numeric" placeholder="Şu anki aylık kiran (TL)" required
               value={form.monthly_rent} onChange={e => setForm({ ...form, monthly_rent: e.target.value })} />
        <input className="input" type="text" inputMode="numeric" placeholder="Evin fiyatı (opsiyonel — boşsa kiradan tahmin edilir)"
               value={form.home_price} onChange={e => setForm({ ...form, home_price: e.target.value })} />
        {savedIncome == null && (
          <input className="input" type="text" inputMode="numeric" placeholder="Aylık net gelirin (opsiyonel — taksit gücünü kontrol eder)"
                 value={form.income} onChange={e => setForm({ ...form, income: e.target.value })} />
        )}
        <select className="input" value={form.years} onChange={e => setForm({ ...form, years: e.target.value })}>
          {[5, 10, 20].map(y => <option key={y} value={y}>{y} yıllık projeksiyon</option>)}
        </select>
        <button className="btn btn-primary" type="submit" disabled={loading}>
          {loading ? 'Hesaplanıyor…' : 'Karşılaştır'}
        </button>
      </form>

      {result && (
        <div style={{ marginTop: 14 }}>
          {/* Consistency line — the same home under both scenarios */}
          <div style={{ fontSize: 12, opacity: 0.8, marginBottom: 10, lineHeight: 1.5 }}>
            Karşılaştırılan ev: <strong>{fmt(result.home_price)} TL</strong>
            {result.home_price_estimated && ' (kiradan tahmin edildi)'} · aylık kredi taksiti
            ≈ <strong>{fmt(result.monthly_mortgage)} TL</strong>
          </div>

          {/* Affordability reality check — a comparison is meaningless if the
              installment doesn't fit the user's income */}
          {parseTL(form.income) > 0 && result.monthly_mortgage > 0 && (() => {
            const ratio = result.monthly_mortgage / parseTL(form.income)
            const pct = Math.round(ratio * 100)
            return (
              <div style={{
                fontSize: 12.5, lineHeight: 1.6, padding: '10px 12px', marginBottom: 10,
                borderRadius: 'var(--radius-xs)', border: '1px solid var(--border)',
                background: 'var(--bg-input)',
                color: ratio > 0.45 ? 'var(--red)' : 'var(--text-muted)',
              }}>
                {ratio > 0.45
                  ? `Taksit, gelirinin %${pct}'i — bankalar genelde gelirin ~%45'inin üzerindeki taksitlere kredi vermez. Bu ev bu peşinatla şu an gerçekçi olmayabilir; daha yüksek peşinat ya da daha uygun bir ev düşünebilirsin.`
                  : `Taksit, gelirinin %${pct}'i — genel kabul gören güvenli sınır ~%45'in altında, bu plan gelirine uygun görünüyor.`}
              </div>
            )
          })()}

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
            <div style={{
              padding: 12, borderRadius: 10,
              border: `1px solid ${buyWins ? 'var(--firefly)' : 'var(--border)'}`,
              background: buyWins ? 'var(--firefly-dim)' : 'transparent',
            }}>
              <div style={{ fontSize: 13, fontWeight: 700, marginBottom: 6 }}>
                🏠 Ev alırsan {buyWins && '✓'}
              </div>
              <div style={{ fontSize: 12, opacity: 0.75 }}>{result.years} yıl sonra net servetin</div>
              <div style={{ fontSize: 17, fontWeight: 700 }}>{fmt(result.buy.net_worth)} TL</div>
              <div style={{ fontSize: 11, opacity: 0.6, marginTop: 2 }}>
                bugünkü alım gücüyle ≈ {fmt(result.buy.net_worth_real)} TL
              </div>
              <div style={{ fontSize: 12, opacity: 0.7, marginTop: 6, lineHeight: 1.5 }}>
                Ev değeri {fmt(result.buy.home_value)} − kalan kredi {fmt(result.buy.remaining_loan)}
              </div>
            </div>
            <div style={{
              padding: 12, borderRadius: 10,
              border: `1px solid ${!buyWins ? 'var(--firefly)' : 'var(--border)'}`,
              background: !buyWins ? 'var(--firefly-dim)' : 'transparent',
            }}>
              <div style={{ fontSize: 13, fontWeight: 700, marginBottom: 6 }}>
                Kirada kalırsan {!buyWins && '✓'}
              </div>
              <div style={{ fontSize: 12, opacity: 0.75 }}>{result.years} yıl sonra net servetin</div>
              <div style={{ fontSize: 17, fontWeight: 700 }}>{fmt(result.rent.net_worth)} TL</div>
              <div style={{ fontSize: 11, opacity: 0.6, marginTop: 2 }}>
                bugünkü alım gücüyle ≈ {fmt(result.rent.net_worth_real)} TL
              </div>
              <div style={{ fontSize: 12, opacity: 0.7, marginTop: 6, lineHeight: 1.5 }}>
                Peşinat + fark yatırımda · ödenen kira {fmt(result.rent.total_rent_paid)} TL
              </div>
            </div>
          </div>

          <div style={{
            marginTop: 12, padding: '10px 14px', borderRadius: 'var(--radius-xs)',
            background: 'var(--bg-input)', fontSize: 13, lineHeight: 1.6,
          }}>
            {buyWins
              ? <>Bu varsayımlarla <strong>satın almak</strong> yaklaşık{' '}
                  <strong>{fmt(result.difference)} TL</strong> daha avantajlı görünüyor.</>
              : <>Bu varsayımlarla <strong>kirada kalıp yatırım yapmak</strong> yaklaşık{' '}
                  <strong>{fmt(result.difference)} TL</strong> daha avantajlı görünüyor.</>}
          </div>

          <p style={{ fontSize: 12, opacity: 0.6, lineHeight: 1.5, marginTop: 10 }}>
            Varsayımlar: konut +%{result.assumptions.housing_annual_growth_pct}/yıl,
            portföy +%{result.assumptions.portfolio_annual_growth_pct}/yıl,
            kredi %{result.assumptions.mortgage_annual_rate_pct}/yıl ({result.assumptions.mortgage_term_years} yıl vade),
            enflasyon %{result.assumptions.annual_inflation_pct}/yıl.
            Büyük TL rakamları çoğunlukla enflasyondan şişer; “bugünkü alım gücü” satırı gerçek
            değeri gösterir. Vergi, aidat, tapu ve bakım masrafları ile ev sahibi olmanın parasal
            olmayan değeri bu hesaba dahil değildir — o kararın duygusal tarafı da meşrudur.
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
  const [scenarioAmount, setScenarioAmount] = useState('1.000.000')
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
            type="text"
            inputMode="numeric"
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
                {provinces.honesty_note} (Veri: {provinces.data_through})
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
