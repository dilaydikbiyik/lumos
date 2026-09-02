import { useEffect, useState, useCallback } from 'react'
import FireflyMark from '../components/FireflyMark'
import Icon from '../components/Icon'
import { useNavigate } from 'react-router-dom'
import LumosLogo from '../components/LumosLogo'
import CurrencyExposure from '../components/CurrencyExposure'
import PortfolioValueChart from '../components/PortfolioValueChart'
import DriftCard from '../components/DriftCard'
import { UserButton, useAuth } from '@clerk/clerk-react'
import api, { extractErrorMessage, setAuthToken } from '../utils/api'
import useMarket from '../hooks/useMarket'
import { readJSON, writeJSON, userKey } from '../utils/storage'
import { Trans, useTranslation } from 'react-i18next'

const TYPE_KEYS = ['stock', 'fund', 'etf', 'real_estate', 'land', 'vehicle', 'gold', 'crypto', 'cash', 'other']
const OFF_EXCHANGE = ['real_estate', 'land', 'vehicle', 'cash', 'other']

const EMPTY_FORM = {
  asset_type: 'stock', name: '', ticker: '', quantity: '',
  purchase_amount: '', manual_current_value: '', note: '', emotion_tag: '',
}

// One-tap emotion tag — data source for the behaviour coach, fully optional.
// '' maps to the prompt label; the rest carry their own locale keys.
const EMOTION_VALUES = ['', 'plan', 'fomo', 'tuyo', 'panik']

export default function HoldingsPage() {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const { getToken, userId } = useAuth()
  const { money } = useMarket()
  const cacheKey = userKey('holdings', userId)
  // Hydrate instantly from the last snapshot so returning users never see a
  // blank/jank frame; the network refresh below replaces it in the background.
  const cached = readJSON(cacheKey)
  const [holdings, setHoldings] = useState(cached?.holdings ?? [])
  const [summary, setSummary] = useState(cached?.summary ?? null)
  const [health, setHealth] = useState(cached?.health ?? null)
  const [profile, setProfile] = useState(cached?.profile ?? null)
  const [form, setForm] = useState(EMPTY_FORM)
  // idle | loading | found | notfound — drives the symbol field's own feedback
  const [lookup, setLookup] = useState({ state: 'idle', data: null })
  const [showForm, setShowForm] = useState(false)
  const [error, setError] = useState(null)
  // "Empty portfolio" and "still fetching" must never look the same
  const [loaded, setLoaded] = useState(!!cached)

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
    writeJSON(cacheKey, {
      holdings: h.data, summary: s.data, health: hs.data, profile: p.data,
    })
  }, [getToken, cacheKey])

  useEffect(() => {
    let cancelled = false
    async function load() {
      try {
        await refresh()
      } catch {
        if (!cancelled) setError(t('holdings.loadError'))
      }
    }
    load()
    return () => { cancelled = true }
  }, [refresh])

  // Typing a symbol should not also mean typing its name and hunting for its
  // price. Looking it up fills both AND validates the symbol: one that fails
  // to resolve would otherwise be saved and silently never track live.
  async function lookupTicker() {
    const symbol = form.ticker.trim()
    if (!symbol || lookup.state === 'loading') return
    setLookup({ state: 'loading', data: null })
    try {
      const res = await api.get('/holdings/lookup', { params: { ticker: symbol } })
      setLookup({ state: 'found', data: res.data })
      setForm(f => ({
        ...f,
        ticker: res.data.ticker,
        // Never overwrite a name the user chose to write themselves — and
        // never invent one: the exchange sometimes returns a price with no
        // name, in which case the field stays theirs to fill.
        name: f.name.trim() || res.data.name || '',
      }))
    } catch {
      setLookup({ state: 'notfound', data: null })
    }
  }

  // Quantity × looked-up price — the number a user actually knows ("I bought
  // 10 shares") turned into the number the form needs.
  const lookedUpPrice = lookup.state === 'found' ? lookup.data.price : null
  const computedAmount = lookedUpPrice && Number(form.quantity) > 0
    ? lookedUpPrice * Number(form.quantity)
    : null

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
      // Quantity unlocks live tracking, so keep it when the user gave one.
      if (Number(form.quantity) > 0) body.quantity = Number(form.quantity)
      if (form.manual_current_value) body.manual_current_value = Number(form.manual_current_value)
      if (form.note) body.note = form.note
      if (form.emotion_tag) body.emotion_tag = form.emotion_tag
      await api.post('/holdings', body)
      setForm(EMPTY_FORM)
      setLookup({ state: 'idle', data: null })
      setShowForm(false)
      await refresh()
    } catch (err) {
      setError(extractErrorMessage(err, t('holdings.addError')))
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
          <h2>{t('holdings.title')}</h2>
          <p style={{ fontSize: 13, marginTop: 4 }}>{t('holdings.subtitle')}</p>
        </div>

        {/* Wealth summary */}
        {summary && (
          <div className="card" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
            <div>
              <div className="num-label">{t('holdings.totalValue')}</div>
              <div className="num-lead">{money(summary.total_current_value)}</div>
            </div>
            <div>
              <div className="num-label">{t('holdings.remainingBudget')}</div>
              <div className="num-lead" style={{ color: 'var(--green, #4ade80)' }}>
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
              <strong style={{ fontSize: 14 }}>{t('holdings.erosionTitle')}</strong>
            </div>
            <p style={{ fontSize: 'var(--t-small)', lineHeight: 1.6 }}>
              <Trans i18nKey="holdings.erosionBody"
                     values={{
                       idle: money(summary.cash_erosion.idle_cash ?? 0),
                       amount: money(summary.cash_erosion.erosion_amount),
                       pct: summary.cash_erosion.monthly_inflation_pct,
                     }}
                     components={[<strong key="a" />, <strong key="b" />]} />
            </p>
            {/* Where that number comes from — a figure the user never typed
                needs its own arithmetic shown, or it reads as invented. */}
            <div style={{
              marginTop: 8, paddingTop: 8, borderTop: '1px solid var(--border)',
              fontSize: 'var(--t-micro)', color: 'var(--text-muted)', lineHeight: 1.7,
            }}>
              <div><Trans i18nKey="holdings.erosionCash"
                     values={{ amount: money(summary.cash_erosion.cash_holdings ?? 0) }}
                     components={[<strong key="a" />]} /></div>
              <div><Trans i18nKey="holdings.erosionBudget"
                     values={{ amount: money(summary.cash_erosion.uninvested_budget ?? 0) }}
                     components={[<strong key="a" />]} /></div>
              <div style={{ marginTop: 2 }}>
                {t('holdings.erosionFormula', {
                  pct: summary.cash_erosion.monthly_inflation_pct,
                  amount: money(summary.cash_erosion.erosion_amount),
                })}
              </div>
            </div>
          </div>
        )}

        {/* Fener — health score */}
        {health && (
          <div className="card">
            <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 8 }}>
              <Icon name="bulb" size={22} glow />
              <strong>{t('holdings.healthTitle', { score: health.overall })}</strong>
            </div>
            <p style={{ fontSize: 11.5, color: 'var(--text-dim)', lineHeight: 1.5, marginBottom: 8 }}>
              {t('holdings.healthBody')}
            </p>
            {health.notes.map((n, i) => (
              <p key={i} style={{ fontSize: 13, lineHeight: 1.6, opacity: 0.85 }}>{n}</p>
            ))}
          </div>
        )}

        {/* Daily value of the real portfolio — the "what happened since I
            bought it" chart */}
        <PortfolioValueChart holdingsCount={holdings.length} />

        {/* Post-purchase advice: has the mix drifted from the target? */}
        <DriftCard holdingsCount={holdings.length} />

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
            {t('holdings.rebuildCta', { amount: money(summary.remaining_budget) })}
          </button>
        )}

        {/* Holdings list */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          {holdings.map(h => (
            <div key={h.id} className="card" style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
              <span style={{ fontSize: 14 }}>{t('holdings.types.' + h.asset_type, { defaultValue: h.asset_type })}</span>
              <div style={{ flex: 1 }}>
                <div style={{ fontWeight: 600, fontSize: 14 }}>{h.name}</div>
                <div style={{ fontSize: 12, opacity: 0.7 }}>
                  {t('holdings.purchase')}: {money(h.purchase_amount)}
                  {h.current_value != null && h.value_source !== 'purchase' && (
                    <> · {t('holdings.current')}: <strong style={{ color: 'var(--text)' }}>{money(h.current_value)}</strong>
                      {h.value_change_pct != null && (
                        <span style={{
                          marginLeft: 6, fontWeight: 700,
                          color: h.value_change_pct >= 0 ? 'var(--green, #3DD68C)' : 'var(--red)',
                        }}>
                          {h.value_change_pct >= 0 ? '▲' : '▼'} {Math.abs(h.value_change_pct)}%
                        </span>
                      )}
                      <span style={{ marginLeft: 6, fontSize: 10, opacity: 0.6 }}>
                        {h.value_source === 'live'
                          ? (h.purchase_date === new Date().toISOString().slice(0, 10)
                              // A 0% move on the day of purchase is correct, not a
                              // broken feed — say which it is instead of leaving doubt.
                              ? t('holdings.liveBoughtToday')
                              : t('holdings.live'))
                          : h.value_source === 'index' ? t('holdings.indexEstimate') : t('holdings.manual')}
                      </span>
                    </>
                  )}
                  {(h.current_value == null || h.value_source === 'purchase') && h.ticker && (
                    <span style={{ marginLeft: 6, fontSize: 10, opacity: 0.55 }}>
                      {t('holdings.liveHint')}
                    </span>
                  )}
                </div>
              </div>
              <button className="btn btn-ghost" onClick={() => remove(h.id)} aria-label={t('holdings.deleteLabel')} style={{ padding: '4px 10px' }}>✕</button>
            </div>
          ))}
          {!loaded && holdings.length === 0 && (
            <div className="card" style={{ textAlign: 'center', padding: '36px 24px' }}>
              <span className="spinner" style={{ width: 22, height: 22, display: 'inline-block' }} />
              <p style={{ fontSize: 13, color: 'var(--text-muted)', marginTop: 10 }}>
                {t('holdings.loading')}
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
                <FireflyMark size={46} />
                <p style={{ fontSize: 14, fontWeight: 600, marginBottom: 4 }}>
                  {t('holdings.emptyTitle')}
                </p>
                <p style={{ fontSize: 13, color: 'var(--text-muted)', lineHeight: 1.6 }}>
                  {t('holdings.emptyBody')}
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
              {TYPE_KEYS.map(v => <option key={v} value={v}>{t('holdings.types.' + v)}</option>)}
            </select>
            <input className="input" placeholder={t('holdings.namePlaceholder')} required
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
                  {t('holdings.vehicleTitle')}
                </p>
                <p style={{ color: 'var(--text-muted)', marginBottom: 6 }}>
                  {t('holdings.vehicleBody')}
                </p>
                <p style={{ color: 'var(--firefly)', fontWeight: 600 }}>
                  <Icon name="bulb" size={13} /> {t('holdings.vehicleTip')}
                </p>
              </div>
            )}
            {needsTicker && (
              <>
                <div style={{ display: 'flex', gap: 8 }}>
                  <input className="input" style={{ flex: 1 }} placeholder={t('holdings.tickerPlaceholder')} required
                         value={form.ticker}
                         onChange={e => { setForm({ ...form, ticker: e.target.value }); setLookup({ state: 'idle', data: null }) }}
                         onBlur={lookupTicker}
                         onKeyDown={e => { if (e.key === 'Enter') { e.preventDefault(); lookupTicker() } }} />
                  <button type="button" className="btn btn-ghost" onClick={lookupTicker}
                          disabled={!form.ticker.trim() || lookup.state === 'loading'}
                          style={{ flexShrink: 0 }}>
                    {lookup.state === 'loading'
                      ? <span className="spinner" style={{ width: 16, height: 16 }} />
                      : t('holdings.lookupCta')}
                  </button>
                </div>

                {/* What the symbol resolved to — proof it will track live, and
                    the price the quantity field multiplies against. */}
                {lookup.state === 'found' && (
                  <div style={{
                    padding: '10px 12px', borderRadius: 'var(--radius-xs)',
                    background: 'var(--firefly-dim)', fontSize: 12.5, lineHeight: 1.6,
                  }}>
                    <strong>{lookup.data.name || lookup.data.ticker}</strong>
                    <div style={{ color: 'var(--text-muted)', marginTop: 2 }}>
                      {t('holdings.lookupPrice', {
                        price: lookup.data.price,
                        currency: lookup.data.currency || '',
                      })}
                    </div>
                  </div>
                )}
                {lookup.state === 'notfound' && (
                  <p style={{ fontSize: 12.5, color: 'var(--red)', lineHeight: 1.6 }}>
                    {t('holdings.lookupNotFound')}
                  </p>
                )}

                <input className="input" type="number" step="any" min="0"
                       placeholder={t('holdings.quantityPlaceholder')}
                       value={form.quantity}
                       onChange={e => {
                         const quantity = e.target.value
                         // Filling the amount for them is the point; they can
                         // still overwrite it if they paid a different price.
                         const auto = lookedUpPrice && Number(quantity) > 0
                           ? String(Math.round(lookedUpPrice * Number(quantity) * 100) / 100)
                           : form.purchase_amount
                         setForm({ ...form, quantity, purchase_amount: auto })
                       }} />
              </>
            )}
            <input className="input" type="number" placeholder={t('holdings.amountPlaceholder')} required min="1"
                   value={form.purchase_amount} onChange={e => setForm({ ...form, purchase_amount: e.target.value })} />
            {computedAmount != null && (
              <p style={{ fontSize: 'var(--t-micro)', color: 'var(--text-dim)', marginTop: -4, lineHeight: 1.5 }}>
                {t('holdings.computedNote', {
                  quantity: form.quantity,
                  price: lookedUpPrice,
                  total: Math.round(computedAmount * 100) / 100,
                })}
              </p>
            )}
            <input className="input" type="number" placeholder={t('holdings.currentPlaceholder')} min="1"
                   value={form.manual_current_value} onChange={e => setForm({ ...form, manual_current_value: e.target.value })} />
            <select className="input" value={form.emotion_tag}
                    onChange={e => setForm({ ...form, emotion_tag: e.target.value })}>
              {EMOTION_VALUES.map(v => <option key={v} value={v}>{t(v ? 'holdings.emotions.' + v : 'holdings.emotions.prompt')}</option>)}
            </select>
            <div style={{ display: 'flex', gap: 8 }}>
              <button className="btn btn-primary" type="submit" style={{ flex: 1 }}>{t('holdings.add')}</button>
              <button className="btn btn-ghost" type="button" onClick={() => setShowForm(false)}>{t('common.cancel')}</button>
            </div>
          </form>
        ) : (
          <button className="btn btn-primary btn-full" onClick={() => setShowForm(true)}>
            {t('holdings.addCta')}
          </button>
        )}

        {error && <p style={{ color: 'var(--red)', fontSize: 13 }}>{error}</p>}
      </div>
    </div>
  )
}
