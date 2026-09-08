import { useEffect, useState, useCallback } from 'react'
import { UserButton, useAuth } from '@clerk/clerk-react'
import { parseTL } from '../utils/number'
import api, { extractErrorMessage, setAuthToken } from '../utils/api'
import LumosLogo from '../components/LumosLogo'
import IsikTut from '../components/IsikTut'
import useMarket from '../hooks/useMarket'
import { Trans, useTranslation } from 'react-i18next'

// EVERY amount on this page is TCMB TL/m² data — it stays pinned to
// TRY + tr-TR regardless of the user's market (pretending to convert
// currencies would be a lie). For non-TR markets the page shows an
// honest "integration on the way" state instead.
const fmt = n => new Intl.NumberFormat('tr-TR', { maximumFractionDigits: 0 }).format(n)

function ProvinceScenario({ province, amount }) {
  const { t } = useTranslation()
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
      setError(extractErrorMessage(err, t('explore.scenarioError')))
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
            : t('explore.whatIfBought', { amount: fmt(parseTL(amount) || 1000000), province: province.province })}
        </button>
      )}
      {error && <p style={{ color: 'var(--red)', fontSize: 12 }}>{error}</p>}
      {band && !band.available && <p style={{ fontSize: 12, opacity: 0.75 }}>{band.reason}</p>}
      {band?.available && (
        <div style={{ fontSize: 13, lineHeight: 1.7 }}>
          <p style={{ fontSize: 12, color: 'var(--text-muted)', lineHeight: 1.6, marginBottom: 8 }}>
            <Trans i18nKey="explore.bandIntro" values={{ province: province.province }}
                   components={[<strong key="a" />]} />
          </p>
          <div>{t('explore.worstBand')}: <strong style={{ color: 'var(--red)' }}>{fmt(band.pessimistic.value)} TL</strong>
            {band.real_band && <span style={{ fontSize: 11, opacity: 0.7 }}> · {t('explore.real')} {band.real_band.pessimistic_pct > 0 ? '+' : ''}{band.real_band.pessimistic_pct}%</span>}
          </div>
          <div>{t('explore.typicalBand')}: <strong style={{ color: 'var(--firefly, #F5A524)' }}>{fmt(band.typical.value)} TL</strong>
            {band.real_band && <span style={{ fontSize: 11, opacity: 0.7 }}> · {t('explore.real')} {band.real_band.typical_pct > 0 ? '+' : ''}{band.real_band.typical_pct}%</span>}
          </div>
          <div>{t('explore.bestBand')}: <strong style={{ color: 'var(--green, #3DD68C)' }}>{fmt(band.optimistic.value)} TL</strong>
            {band.real_band && <span style={{ fontSize: 11, opacity: 0.7 }}> · {t('explore.real')} {band.real_band.optimistic_pct > 0 ? '+' : ''}{band.real_band.optimistic_pct}%</span>}
          </div>
          {links && (
            <div style={{ marginTop: 10, padding: 10, borderRadius: 10, border: '1px dashed var(--border)' }}>
              <p style={{ fontSize: 12, opacity: 0.75, marginBottom: 8 }}>
                {t('explore.microLocation')}
              </p>
              <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', marginBottom: 8 }}
                   onClick={e => e.stopPropagation()}>
                <input className="input" placeholder={t('explore.districtPlaceholder')} value={ilce}
                       onChange={e => setIlce(e.target.value)}
                       style={{ flex: 1, minWidth: 100, fontSize: 13 }} />
                <input className="input" placeholder={t('explore.neighbourhoodPlaceholder')} value={detail}
                       onChange={e => setDetail(e.target.value)}
                       style={{ flex: 1, minWidth: 120, fontSize: 13 }} />
                <select className="input" value={assetType}
                        onChange={e => setAssetType(e.target.value)}
                        style={{ flex: 0.7, minWidth: 80, fontSize: 13 }}>
                  <option value="arsa">{t('explore.land')}</option>
                  <option value="daire">{t('explore.flat')}</option>
                </select>
                <button className="btn btn-ghost" style={{ fontSize: 12 }}
                        onClick={() => fetchLinks().catch(() => {})}>
                  {t('explore.refresh')}
                </button>
              </div>
              <div style={{ display: 'flex', gap: 8 }}>
                {links.map(l => (
                  <a key={l.site} href={l.url} target="_blank" rel="noopener noreferrer"
                     className="btn btn-ghost" style={{ flex: 1, textAlign: 'center', fontSize: 12, textDecoration: 'none' }}>
                    {t('explore.listingsAt', { site: l.site })}
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
  const { t } = useTranslation()
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
          {t('explore.real')} {province.real_change_pct > 0 ? '+' : ''}{province.real_change_pct}%
        </div>
      </div>
      {open && <div style={{ flexBasis: '100%' }}><ProvinceScenario province={province} amount={amount} /></div>}
    </div>
  )
}

function RentVsBuy() {
  const { t } = useTranslation()
  const [form, setForm] = useState({ down_payment: '', monthly_rent: '', home_price: '', income: '', years: 10, rate: '', term: '', cash_includes_costs: false })
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
        ...(form.rate ? { mortgage_annual_rate_pct: Number(String(form.rate).replace(',', '.')) } : {}),
        ...(form.term ? { mortgage_term_years: Number(form.term) } : {}),
        down_payment_includes_costs: form.cash_includes_costs,
      })
      setResult(res.data)
      const income = parseTL(form.income)
      if (income > 0 && income !== savedIncome) {
        api.patch('/users/me/income', { monthly_income: income })
          .then(() => setSavedIncome(income)).catch(() => {})
      }
    } catch (err) {
      setError(extractErrorMessage(err, t('goal.error')))
    } finally {
      setLoading(false)
    }
  }

  const buyWins = result?.verdict === 'buy'

  return (
    <div className="card">
      <h3 style={{ marginBottom: 4 }}>{t('rvb.title')}</h3>
      <p style={{ fontSize: 13, opacity: 0.8, marginBottom: 12 }}>
        {t('rvb.subtitle')}
      </p>
      <form onSubmit={run} style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
        <input className="input" type="text" inputMode="numeric"
               placeholder={form.cash_includes_costs ? t('rvb.cashPlaceholder') : t('rvb.downPaymentPlaceholder')}
               required
               value={form.down_payment} onChange={e => setForm({ ...form, down_payment: e.target.value })} />
        {/* Buyers think in "money I have", not "down payment net of fees".
            Closing costs are what blows up that budget, so let them say which
            number they typed and do the subtraction for them. */}
        <label style={{
          display: 'flex', gap: 8, alignItems: 'flex-start', cursor: 'pointer',
          fontSize: 12.5, color: 'var(--text-muted)', lineHeight: 1.5,
        }}>
          <input type="checkbox" checked={form.cash_includes_costs}
                 onChange={e => setForm({ ...form, cash_includes_costs: e.target.checked })}
                 style={{ marginTop: 2, accentColor: 'var(--accent)', width: 15, height: 15, flexShrink: 0 }} />
          {t('rvb.cashIncludesCosts')}
        </label>
        <input className="input" type="text" inputMode="numeric" placeholder={t('rvb.rentPlaceholder')} required
               value={form.monthly_rent} onChange={e => setForm({ ...form, monthly_rent: e.target.value })} />
        <input className="input" type="text" inputMode="numeric" placeholder={t('rvb.homePricePlaceholder')}
               value={form.home_price} onChange={e => setForm({ ...form, home_price: e.target.value })} />
        {savedIncome == null && (
          <input className="input" type="text" inputMode="numeric" placeholder={t('rvb.incomePlaceholder')}
                 value={form.income} onChange={e => setForm({ ...form, income: e.target.value })} />
        )}
        <select className="input" value={form.years} onChange={e => setForm({ ...form, years: e.target.value })}>
          {[5, 10, 20].map(y => <option key={y} value={y}>{t('rvb.projectionYears', { n: y })}</option>)}
        </select>
        {/* Bank offers vary a lot; left blank, the market average is used. */}
        <details>
          <summary style={{ fontSize: 12.5, color: 'var(--text-dim)', cursor: 'pointer' }}>
            {t('rvb.ownLoanTerms')}
          </summary>
          <div style={{ display: 'flex', gap: 8, marginTop: 8 }}>
            <input className="input" type="text" inputMode="decimal" style={{ flex: 1 }}
                   placeholder={t('rvb.ratePlaceholder')}
                   value={form.rate} onChange={e => setForm({ ...form, rate: e.target.value })} />
            <input className="input" type="text" inputMode="numeric" style={{ flex: 1 }}
                   placeholder={t('rvb.termPlaceholder')}
                   value={form.term} onChange={e => setForm({ ...form, term: e.target.value })} />
          </div>
          <p style={{ fontSize: 11, color: 'var(--text-dim)', marginTop: 6, lineHeight: 1.5 }}>
            {t('rvb.ownLoanHint')}
          </p>
        </details>
        <button className="btn btn-primary" type="submit" disabled={loading}>
          {loading ? t('common.calculating') : t('common.compare')}
        </button>
      </form>

      {result && (
        <div style={{ marginTop: 14 }}>
          {/* Consistency line — the same home under both scenarios */}
          <div style={{ fontSize: 12, opacity: 0.8, marginBottom: 10, lineHeight: 1.5 }}>
            <Trans i18nKey="rvb.comparedHome"
                   values={{ price: fmt(result.home_price), installment: fmt(result.monthly_mortgage) }}
                   components={[<strong key="a" />, <strong key="b" />]} />
            {result.home_price_estimated && ' ' + t('rvb.estimatedFromRent')}
            {/* The number people forget to budget for. */}
            {form.cash_includes_costs && result.buy.purchase_costs > 0 && (
              <><br />
              <span style={{ color: 'var(--text-muted)' }}>
                <Trans i18nKey="rvb.cashBreakdown"
                       values={{ cash: fmt(result.buy.cash_available),
                                 costs: fmt(result.buy.purchase_costs),
                                 applied: fmt(result.buy.down_payment_applied) }}
                       components={[<strong key="a" />, <strong key="b" />]} />
              </span></>
            )}
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
                  ? t('rvb.affordabilityTight', { pct })
                  : t('rvb.affordabilityOk', { pct })}
              </div>
            )
          })()}

          {/* What the loan itself costs. Beginners compare installments and
              miss that the interest can exceed the amount borrowed. */}
          {result.loan?.principal > 0 && (
            <div style={{
              fontSize: 12.5, lineHeight: 1.7, padding: '10px 12px', marginBottom: 10,
              borderRadius: 'var(--radius-xs)', border: '1px solid var(--border)',
              background: 'var(--bg-input)',
            }}>
              <Trans i18nKey="rvb.loanCost"
                     values={{
                       rate: result.assumptions.mortgage_annual_rate_pct,
                       term: result.assumptions.mortgage_term_years,
                       principal: fmt(result.loan.principal),
                       total: fmt(result.loan.total_over_full_term),
                       interest: fmt(result.loan.interest_over_full_term),
                       ratio: Math.round(result.loan.interest_over_full_term / result.loan.principal * 100),
                     }}
                     components={[<strong key="a" />, <br key="b" />, <strong key="c" />,
                                  <strong key="d" />, <br key="e" />, <strong key="f" />, <strong key="g" />]} />
              {result.loan.interest_over_full_term > result.loan.principal && (
                <> {t('rvb.payingTwice')}</>
              )}
              <div style={{ fontSize: 11, opacity: 0.65, marginTop: 4 }}>
                {t('rvb.fixedRateNote')}
              </div>
            </div>
          )}

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
            <div style={{
              padding: 12, borderRadius: 10,
              border: `1px solid ${buyWins ? 'var(--firefly)' : 'var(--border)'}`,
              background: buyWins ? 'var(--firefly-dim)' : 'transparent',
            }}>
              <div style={{ fontSize: 13, fontWeight: 700, marginBottom: 6 }}>
                🏠 {t('rvb.ifBuy')} {buyWins && '✓'}
              </div>
              <div style={{ fontSize: 12, opacity: 0.75 }}>{t('rvb.netWorthAfter', { years: result.years })}</div>
              <div style={{ fontSize: 17, fontWeight: 700 }}>{fmt(result.buy.net_worth)} TL</div>
              <div style={{ fontSize: 11, opacity: 0.6, marginTop: 2 }}>
                {t('rvb.inTodaysMoney', { amount: fmt(result.buy.net_worth_real) })}
              </div>
              <div style={{ fontSize: 12, opacity: 0.7, marginTop: 6, lineHeight: 1.5 }}>
                {t('rvb.equityLine', { value: fmt(result.buy.home_value), loan: fmt(result.buy.remaining_loan) })}
                {result.buy.purchase_costs > 0 && (
                  <><br />{t('rvb.costsLine', { costs: fmt(result.buy.purchase_costs), upkeep: fmt(result.buy.total_upkeep_paid) })}</>
                )}
              </div>
            </div>
            <div style={{
              padding: 12, borderRadius: 10,
              border: `1px solid ${!buyWins ? 'var(--firefly)' : 'var(--border)'}`,
              background: !buyWins ? 'var(--firefly-dim)' : 'transparent',
            }}>
              <div style={{ fontSize: 13, fontWeight: 700, marginBottom: 6 }}>
                {t('rvb.ifRent')} {!buyWins && '✓'}
              </div>
              <div style={{ fontSize: 12, opacity: 0.75 }}>{t('rvb.netWorthAfter', { years: result.years })}</div>
              <div style={{ fontSize: 17, fontWeight: 700 }}>{fmt(result.rent.net_worth)} TL</div>
              <div style={{ fontSize: 11, opacity: 0.6, marginTop: 2 }}>
                {t('rvb.inTodaysMoney', { amount: fmt(result.rent.net_worth_real) })}
              </div>
              <div style={{ fontSize: 12, opacity: 0.7, marginTop: 6, lineHeight: 1.5 }}>
                {t('rvb.rentLine', { rent: fmt(result.rent.total_rent_paid) })}
              </div>
            </div>
          </div>

          <div style={{
            marginTop: 12, padding: '10px 14px', borderRadius: 'var(--radius-xs)',
            background: 'var(--bg-input)', fontSize: 13, lineHeight: 1.6,
          }}>
            {buyWins
              ? <Trans i18nKey="rvb.verdictBuy" values={{ amount: fmt(result.difference) }}
                         components={[<strong key="a" />, <strong key="b" />]} />
              : <Trans i18nKey="rvb.verdictRent" values={{ amount: fmt(result.difference) }}
                         components={[<strong key="a" />, <strong key="b" />]} />}
          </div>

          <p style={{ fontSize: 12, opacity: 0.6, lineHeight: 1.5, marginTop: 10 }}>
            {t('rvb.assumptions', {
              housing: result.assumptions.housing_annual_growth_pct,
              portfolio: result.assumptions.portfolio_annual_growth_pct,
              rate: result.assumptions.mortgage_annual_rate_pct,
              term: result.assumptions.mortgage_term_years,
              inflation: result.assumptions.annual_inflation_pct,
              asOf: result.assumptions.inflation_as_of || '—',
              deed: result.assumptions.title_deed_fee_pct,
              agency: result.assumptions.agency_commission_pct,
              vat: result.assumptions.vat_pct,
              agencyVat: result.assumptions.agency_commission_with_vat_pct,
              upkeep: result.assumptions.annual_upkeep_pct,
            })}
          </p>
        </div>
      )}
      {error && <p style={{ color: 'var(--red)', fontSize: 13, marginTop: 10 }}>{error}</p>}
    </div>
  )
}

function ListingLinks() {
  const { t } = useTranslation()
  const { pack } = useMarket()
  // "İl / ilçe" is a Turkish administrative shape; every market gets the
  // portals from its own pack, so the labels have to generalise too.
  const isTR = pack.code === 'TR'
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
      setError(extractErrorMessage(err, t('explore.linkError')))
    }
  }

  return (
    <div className="card">
      <h3 style={{ marginBottom: 4 }}>{t('explore.listingsTitle')}</h3>
      <p style={{ fontSize: 13, opacity: 0.8, marginBottom: 12 }}>
        {t('explore.listingsBody')}
        {pack.listing_sites?.length > 0 && (
          <> {t('explore.listingsSites', { sites: pack.listing_sites.join(', ') })}</>
        )}
      </p>
      <form onSubmit={run} style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
        <input className="input" required style={{ flex: 2, minWidth: 120 }}
               placeholder={isTR ? t('explore.provincePlaceholder') : t('explore.cityPlaceholder')}
               value={form.il} onChange={e => setForm({ ...form, il: e.target.value })} />
        <input className="input" style={{ flex: 2, minWidth: 120 }}
               placeholder={isTR ? t('explore.districtOptional') : t('explore.areaOptional')}
               value={form.ilce} onChange={e => setForm({ ...form, ilce: e.target.value })} />
        <select className="input" style={{ flex: 1, minWidth: 90 }} value={form.asset_type}
                onChange={e => setForm({ ...form, asset_type: e.target.value })}>
          <option value="arsa">{t('explore.land')}</option>
          <option value="daire">{t('explore.flat')}</option>
        </select>
        <button className="btn btn-primary" type="submit" style={{ flexBasis: '100%' }}>{t('explore.fetchLinks')}</button>
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
  const { t } = useTranslation()
  const { getToken } = useAuth()
  const { pack } = useMarket()
  // A national house-price index and a province-by-province table are
  // different data products: Germany has the first (Eurostat) but not the
  // second, so this table is its own gate. The rent-vs-buy calculator and
  // the listing bridge below are market-aware and run everywhere.
  const hasProvinceTable = !!pack.regional_housing_breakdown
  const [provinces, setProvinces] = useState(null)
  const [horizon, setHorizon] = useState(3)
  const [scenarioAmount, setScenarioAmount] = useState('1.000.000')
  const [search, setSearch] = useState('')
  // Loading is derived: no data yet, or data belongs to a different horizon
  const loading = hasProvinceTable && (!provinces || provinces._horizon !== horizon)

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
    if (!hasProvinceTable) return
    let cancelled = false
    async function run() {
      const data = await load(horizon)
      if (!cancelled) setProvinces({ ...data, _horizon: horizon })
    }
    run()
    return () => { cancelled = true }
  }, [load, horizon, hasProvinceTable])

  const q = search.trim().toLocaleLowerCase('tr')
  const visible = provinces?.available
    ? (q
        ? provinces.provinces.filter(p => p.province.toLocaleLowerCase('tr').includes(q))
        : provinces.provinces.slice(0, 12))
    : []

  return (
    <div className="page">
      <header className="navbar">
        <LumosLogo />
        <UserButton afterSignOutUrl="/" />
      </header>

      <div className="page-content" style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
        <div>
          <h2>{t('explore.title')}</h2>
          <p style={{ fontSize: 13, marginTop: 4 }}>
            <Trans i18nKey="explore.subtitle"
                   components={[<IsikTut key="a" term="reel getiri" />]} />
          </p>
        </div>

        {/* Per-province price table — only where that data actually exists */}
        {hasProvinceTable ? (
          <>
          {/* Region intelligence */}
          <div className="card" style={{ padding: 0, background: 'none', border: 'none', boxShadow: 'none' }}>
            <div style={{ display: 'flex', gap: 8, marginBottom: 12 }}>
              {[1, 3, 5].map(y => (
                <button key={y}
                        className={`btn ${horizon === y ? 'btn-primary' : 'btn-ghost'}`}
                        style={{ flex: 1 }}
                        onClick={() => setHorizon(y)}>
                  {t('explore.lastYears', { n: y })}
                </button>
              ))}
            </div>

            <input
              className="input"
              placeholder={t('explore.searchPlaceholder')}
              value={search}
              onChange={e => setSearch(e.target.value)}
              style={{ marginBottom: 12 }}
              aria-label={t('explore.searchLabel')}
            />

            <input
              className="input"
              type="text"
              inputMode="numeric"
              placeholder={t('explore.amountPlaceholder')}
              value={scenarioAmount}
              onChange={e => setScenarioAmount(e.target.value)}
              style={{ marginBottom: 12 }}
              aria-label={t('explore.amountLabel')}
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
                      {t('explore.noResults', { search })}
                    </p>
                  )}
                </div>
                {!q && (
                  <p style={{ fontSize: 12, opacity: 0.55, marginTop: 8, textAlign: 'center' }}>
                    {t('explore.showingFirst')}
                  </p>
                )}
                <p style={{ fontSize: 12, opacity: 0.6, marginTop: 10, lineHeight: 1.5 }}>
                  {provinces.honesty_note} (Veri: {provinces.data_through})
                </p>
              </>
            )}

            {!loading && !provinces?.available && (
              <div className="card" style={{ textAlign: 'center', padding: 24 }}>
                <p style={{ fontSize: 14 }}>{t('explore.dataError')}</p>
              </div>
            )}
          </div>
          </>
        ) : (
          <div className="card">
            <div style={{ fontSize: 26, marginBottom: 8 }}>🌍</div>
            <p style={{ fontSize: 14, lineHeight: 1.7 }}>
              <Trans i18nKey="explore.noProvinceTable" values={{ market: pack.name }}
                     components={[<strong key="a" />]} />
            </p>
            <p style={{ fontSize: 12, opacity: 0.65, marginTop: 10, lineHeight: 1.6 }}>
              {pack.live_housing_index
                ? t('explore.nationalIndexOnly', { market: pack.name })
                : t('explore.noHousingIndex', { market: pack.name })}
            </p>
          </div>
        )}

        <RentVsBuy />
        <ListingLinks />
      </div>
    </div>
  )
}
