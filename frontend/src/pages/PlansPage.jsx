import { useCallback, useEffect, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { useAuth } from '@clerk/clerk-react'
import { useTranslation } from 'react-i18next'
import AppHeader from '../components/AppHeader'
import api, { extractErrorMessage } from '../utils/api'
import { isNativeApp } from '../utils/platform'
import {
  buyNative, configurePurchases, nativePackages, nativePurchasesAvailable, restoreNative,
} from '../utils/purchases'

const ORDER = ['free', 'plus', 'pro']

/**
 * Plans: what each one buys, and the way to buy it on this device.
 *
 * What a paid plan changes is the AI advisor only — a higher daily limit and
 * a stronger model. Recommendations, calculations and every figure are the
 * same for every reader, and the page says so before any price: selling
 * "better advice" would be exactly the regulated activity this app stays
 * out of.
 */
export default function PlansPage() {
  const { t, i18n } = useTranslation()
  const { userId } = useAuth()
  const [params] = useSearchParams()
  const [plans, setPlans] = useState(null)
  const [webCheckout, setWebCheckout] = useState(false)
  const [mine, setMine] = useState(null)
  // True when /billing/me failed and nothing was ever loaded: the page then
  // cannot tell a paying reader from a free one, so it offers no purchase.
  const [mineFailed, setMineFailed] = useState(false)
  const [packages, setPackages] = useState({})
  const [busy, setBusy] = useState(null)
  const [error, setError] = useState(null)
  const native = isNativeApp()
  const justPaid = params.get('paid') === '1'

  const loadMine = useCallback(() =>
    api.get('/billing/me')
      .then(res => { setMine(res.data); setMineFailed(false) })
      .catch(() => setMineFailed(true)), [])

  useEffect(() => {
    api.get('/billing/plans').then(res => {
      setPlans(res.data.plans)
      setWebCheckout(Boolean(res.data.web_checkout))
    }).catch(() => setError(t('plans.loadError')))
    loadMine()
  }, [loadMine, t])

  // Back from a checkout: the store's webhook may land a few seconds after
  // the reader does, so the plan is read again a few times.
  useEffect(() => {
    if (!justPaid) return
    let tries = 0
    const timer = setInterval(() => {
      tries += 1
      loadMine()
      if (tries >= 6) clearInterval(timer)
    }, 3000)
    return () => clearInterval(timer)
  }, [justPaid, loadMine])

  useEffect(() => {
    if (!nativePurchasesAvailable() || !userId) return
    configurePurchases(userId).then(nativePackages).then(setPackages)
      .catch(() => setError(t('plans.storeError')))
  }, [userId, t])

  async function buy(plan) {
    setBusy(plan)
    setError(null)
    try {
      if (native) {
        await buyNative(packages[plan])
        await loadMine()
      } else {
        const res = await api.post('/billing/checkout', { plan })
        window.location.assign(res.data.url)
        return
      }
    } catch (err) {
      // A cancelled App Store sheet is not an error worth showing.
      if (!err?.userCancelled) setError(extractErrorMessage(err, t('plans.buyError')))
    }
    setBusy(null)
  }

  async function restore() {
    setBusy('restore')
    try { await restoreNative(); await loadMine() } catch { setError(t('plans.storeError')) }
    setBusy(null)
  }

  const price = (p) => {
    if (native) return packages[p.plan]?.product?.priceString || null
    if (!p.price_monthly_usd) return t('plans.freePrice')
    return t('plans.perMonth', {
      price: new Intl.NumberFormat(i18n.language, { style: 'currency', currency: 'USD' })
        .format(p.price_monthly_usd),
    })
  }

  // Until the reader's plan is known, no plan is "current" and nothing can be
  // bought: assuming free would offer a paying reader a second subscription
  // (the server refuses a second web checkout with 409, but an App Store
  // purchase never reaches the server first).
  const current = mine ? (mine.plan || 'free') : null
  // Already paying in a store: a second purchase would be a second
  // subscription, charged alongside the first. A web subscriber changes plan
  // in the store's portal; an App Store subscriber changes it inside the App
  // Store (Apple treats that as an upgrade, not a new subscription), so only
  // that one may still buy here — and only in the app.
  const payingWeb = current !== 'free' && mine?.source === 'lemonsqueezy'
  const payingApple = current !== 'free' && mine?.source === 'revenuecat'
  const blocked = payingWeb || (payingApple && !native)
  const canBuy = (plan) => mine !== null && plan !== 'free' && !blocked
    && (native ? Boolean(packages[plan]) : webCheckout)

  return (
    <div className="page">
      <AppHeader />
      <div className="page-content" style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
        <div>
          <h2>{t('plans.title')}</h2>
          <p style={{ fontSize: 13, marginTop: 4 }}>{t('plans.sameAdvice')}</p>
        </div>

        {justPaid && <div className="card" role="status" style={{ fontSize: 13 }}>{t('plans.thanks')}</div>}
        {error && <p role="alert" style={{ fontSize: 13, color: 'var(--red)' }}>{error}</p>}
        {!plans && !error && <div className="spinner" style={{ margin: '24px auto' }} />}
        {mineFailed && !mine && (
          <div className="card" role="alert" style={{ fontSize: 13 }}>
            <p style={{ margin: '0 0 10px' }}>{t('plans.mineError')}</p>
            <button type="button" className="btn btn-ghost btn-full" onClick={loadMine}>
              {t('common.tryAgain')}
            </button>
          </div>
        )}

        {(plans || []).slice().sort((a, b) => ORDER.indexOf(a.plan) - ORDER.indexOf(b.plan)).map(p => (
          <div key={p.plan} className="card" style={{
            borderColor: current === p.plan ? 'var(--firefly)' : undefined,
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', gap: 8 }}>
              <strong style={{ fontSize: 16 }}>{t(`plans.${p.plan}.label`)}</strong>
              {price(p) && <span className="num" style={{ fontWeight: 700 }}>{price(p)}</span>}
            </div>
            <p style={{ fontSize: 13, margin: '6px 0 4px' }}>{t(`plans.${p.plan}.pitch`)}</p>
            <p style={{ fontSize: 12, color: 'var(--text-dim)', margin: 0 }}>
              {t('plans.quota', { count: p.daily_quota })}
            </p>
            {current === p.plan ? (
              <p style={{ fontSize: 12.5, marginTop: 10, fontWeight: 600 }}>
                {t('plans.current')}
                {mine?.ends_at && ` · ${t('plans.endsAt', { date: new Date(mine.ends_at).toLocaleDateString(i18n.language) })}`}
              </p>
            ) : canBuy(p.plan) && (
              <button type="button" className="btn btn-primary btn-full" style={{ marginTop: 10, minHeight: 44 }}
                      disabled={busy !== null} onClick={() => buy(p.plan)}>
                {busy === p.plan ? <span className="spinner" style={{ width: 16, height: 16 }} /> : t('plans.choose')}
              </button>
            )}
          </div>
        ))}

        {current !== 'free' && mine?.source === 'lemonsqueezy' && mine?.portal_url && !native && (
          <a className="btn btn-ghost" href={mine.portal_url} target="_blank" rel="noopener noreferrer"
             style={{ textAlign: 'center' }}>{t('plans.manageWeb')}</a>
        )}
        {payingWeb && native && (
          <p style={{ fontSize: 12.5, color: 'var(--text-dim)' }}>{t('plans.manageWebFromApp')}</p>
        )}
        {current !== 'free' && mine?.source === 'revenuecat' && (
          <p style={{ fontSize: 12.5, color: 'var(--text-dim)' }}>{t('plans.manageApple')}</p>
        )}
        {nativePurchasesAvailable() && (
          <button type="button" className="btn btn-ghost" disabled={busy !== null} onClick={restore}
                  style={{ minHeight: 44 }}>
            {t('plans.restore')}
          </button>
        )}
        {!native && !webCheckout && plans && (
          <p style={{ fontSize: 12.5, color: 'var(--text-dim)' }}>{t('plans.soon')}</p>
        )}

        <p style={{ fontSize: 11.5, color: 'var(--text-dim)', lineHeight: 1.6 }}>
          {t(native ? 'plans.renewalApple' : 'plans.renewalWeb')}{' '}
          <Link to="/terms">{t('plans.terms')}</Link> · <Link to="/privacy">{t('plans.privacy')}</Link>
        </p>
      </div>
    </div>
  )
}
