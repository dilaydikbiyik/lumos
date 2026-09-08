import { useEffect, useCallback } from 'react'
import FireflyMark from '../components/FireflyMark'
import Icon from '../components/Icon'
import { useNavigate } from 'react-router-dom'
import { UserButton, useAuth } from '@clerk/clerk-react'
import LumosLogo from '../components/LumosLogo'
import PortfolioChart from '../components/PortfolioChart'
import PortfolioComparison from '../components/PortfolioComparison'
import NewsDigest from '../components/NewsDigest'
import GoalPlanner from '../components/GoalPlanner'
import DailyTip from '../components/DailyTip'
import HeadlineEducation from '../components/HeadlineEducation'
import ReadinessScore from '../components/ReadinessScore'
import usePortfolio from '../hooks/usePortfolio'
import useMarket from '../hooks/useMarket'
import api, { setAuthToken } from '../utils/api'
import { useState } from 'react'
import { Trans, useTranslation } from 'react-i18next'

/** Progressive UI: minimal view for new users, deepens via "Show More" */
function ProgressiveDetails({ holdingsSummary, portfolio }) {
  const { t } = useTranslation()
  const [expanded, setExpanded] = useState(false)
  // No holdings → hide the details section
  const hasData = holdingsSummary?.total_current_value > 0 || portfolio
  if (!hasData) return null
  return (
    <>
      {!expanded ? (
        <button
          onClick={() => setExpanded(true)}
          className="btn btn-ghost"
          style={{ width: '100%', fontSize: 13, border: '1px dashed var(--border)' }}
        >
          <Icon name="chart" size={14} /> {t('dashboard.showDetails')}
        </button>
      ) : (
        <>
          <PortfolioComparison />
          <GoalPlanner />
          <button
            onClick={() => setExpanded(false)}
            className="btn btn-ghost"
            style={{ width: '100%', fontSize: 12, color: 'var(--text-dim)' }}
          >
            {t('dashboard.collapse')}
          </button>
        </>
      )}
    </>
  )
}


export default function DashboardPage() {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const { getToken } = useAuth()
  const { fmt, money, unit } = useMarket()
  const { portfolio, profile, isLoading, loadProfile, recommend } = usePortfolio()

  // Holdings summary — for the dashboard card
  const [holdingsSummary, setHoldingsSummary] = useState(null)

  const loadSummary = useCallback(async () => {
    try {
      setAuthToken(await getToken())
      const res = await api.get('/holdings/summary')
      setHoldingsSummary(res.data)
    } catch {
      // summary is not critical
    }
  }, [getToken])

  /* eslint-disable react-hooks/set-state-in-effect */
  useEffect(() => {
    loadProfile()
    loadSummary()
  }, [loadProfile, loadSummary])
  /* eslint-enable react-hooks/set-state-in-effect */

  async function handleRerun() {
    if (profile) {
      await recommend(profile.risk_score, profile.budget || 100_000)
    }
  }

  if (isLoading) return (
    <div className="page" style={{ alignItems: 'center', justifyContent: 'center' }}>
      <div className="light-loader" style={{ width: 20, height: 20 }} />
      <p style={{ marginTop: 16, fontSize: 13, color: 'var(--text-muted)' }}>{t('common.loading')}</p>
    </div>
  )

  return (
    <div className="page">
      <header className="navbar">
        <LumosLogo />
        <UserButton afterSignOutUrl="/" />
      </header>

      <div className="page-content" style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>

        {/* ── Greeting header ── */}
        <div>
          <h2 style={{ marginBottom: 4 }}>
            <span className="gradient-text">{t('dashboard.title')}</span>
          </h2>
          <p style={{ fontSize: 13 }}>{t('dashboard.subtitle')}</p>
        </div>

        {/* ── Courage Score — the visible face of the vision ── */}
        <ReadinessScore />

        {/* ── Daily tip ──
            Held back until the wealth summary has arrived. It renders with no
            network of its own, so showing it first left the dashboard as a
            lone tip card for seconds — a tester read that as stray metadata.
            A tip is secondary content; it should never be the whole page. */}
        {holdingsSummary && <DailyTip />}

        {/* ── Summary card ── */}
        {holdingsSummary && (
          <div className="card" style={{
            background: 'linear-gradient(135deg, var(--bg-card) 0%, var(--bg-card-2) 100%)',
            border: '1px solid rgba(245,165,36,0.2)',
            boxShadow: '0 4px 24px rgba(245,165,36,0.08)',
          }}>
            <p style={{ fontSize: 11, letterSpacing: '0.1em', textTransform: 'uppercase', color: 'var(--firefly)', fontWeight: 700, marginBottom: 14 }}>
              {t('dashboard.wealthSummary')}
            </p>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
              <div>
                <div className="num-label">{t('holdings.totalValue')}</div>
                <div className="num-hero" style={{ color: 'var(--firefly)' }}>
                  {fmt(holdingsSummary.total_current_value)} <span style={{ fontSize: 13, fontWeight: 500 }}>{unit}</span>
                </div>
                {holdingsSummary.total_purchase_amount > 0 && (
                  <div style={{ fontSize: 11, color: 'var(--text-dim)', marginTop: 3 }}>
                    {t('holdings.purchase')}: {money(holdingsSummary.total_purchase_amount)}
                  </div>
                )}
              </div>
              <div>
                <div className="num-label">{t('holdings.remainingBudget')}</div>
                <div className="num-hero" style={{
                  color: holdingsSummary.remaining_budget > 0 ? 'var(--green)' : 'var(--text-muted)',
                }}>
                  {holdingsSummary.remaining_budget != null
                    ? <>{fmt(holdingsSummary.remaining_budget)} <span style={{ fontSize: 13, fontWeight: 500 }}>{unit}</span></>
                    : '—'
                  }
                </div>
                {holdingsSummary.cash_erosion && holdingsSummary.remaining_budget > 0 && (
                  <div style={{ fontSize: 11, color: 'var(--red)', marginTop: 3 }}>
                    ↓ {t('dashboard.erodingPerMonth', { amount: money(holdingsSummary.cash_erosion.erosion_amount) })}
                  </div>
                )}
              </div>
            </div>

            {/* Monthly plan tracker — for users whose quiz answer was "regularly, every month" */}
            {holdingsSummary.monthly_contribution > 0 && (
              <div style={{
                marginTop: 14, padding: '10px 12px', borderRadius: 'var(--radius-xs)',
                background: 'var(--bg-input)', border: '1px solid var(--border)',
                fontSize: 12.5, lineHeight: 1.6,
              }}>
                {(() => {
                  const plan = holdingsSummary.monthly_contribution
                  const done = holdingsSummary.invested_this_month || 0
                  const left = Math.max(plan - done, 0)
                  return done >= plan
                    ? <Trans i18nKey="dashboard.planDone"
                             values={{ plan: money(plan), done: money(done) }}
                             components={[<strong key="a" />, <strong key="b" />]} />
                    : <Trans i18nKey="dashboard.planRemaining"
                             values={{ plan: money(plan), done: money(done), left: money(left) }}
                             components={[<strong key="a" />, <strong key="b" />, <strong key="c" />]} />
                })()}
              </div>
            )}

            {/* Per-type allocation mini bar */}
            {holdingsSummary.by_type && Object.keys(holdingsSummary.by_type).length > 0 && (
              <div style={{ marginTop: 16 }}>
                <div style={{ display: 'flex', gap: 4, height: 6, borderRadius: 6, overflow: 'hidden', marginBottom: 8 }}>
                  {Object.entries(holdingsSummary.by_type).map(([type, val], i) => {
                    const colors = ['#F5A524', '#7A4A93', '#1FB2A6', '#E8663F', '#9C5A34']
                    const pct = holdingsSummary.total_current_value > 0
                      ? (Number(val) / holdingsSummary.total_current_value) * 100
                      : 0
                    return (
                      <div key={type} style={{
                        width: `${pct}%`, background: colors[i % colors.length],
                        borderRadius: 3, minWidth: pct > 0 ? 4 : 0,
                        transition: 'width 0.6s ease',
                      }} title={`${type}: ${Math.round(pct)}%`} />
                    )
                  })}
                </div>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px 12px' }}>
                  {Object.entries(holdingsSummary.by_type).map(([type, val], i) => {
                    const colors = ['#F5A524', '#7A4A93', '#1FB2A6', '#E8663F', '#9C5A34']
                    const pct = holdingsSummary.total_current_value > 0
                      ? Math.round((Number(val) / holdingsSummary.total_current_value) * 100)
                      : 0
                    return (
                      <span key={type} style={{ fontSize: 11, color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: 4 }}>
                        <span style={{ width: 7, height: 7, borderRadius: '50%', background: colors[i % colors.length], display: 'inline-block' }} />
                        {t('holdings.types.' + type, { defaultValue: type })} %{pct}
                      </span>
                    )
                  })}
                </div>
              </div>
            )}

            <button
              className="btn btn-ghost"
              style={{ width: '100%', marginTop: 14, fontSize: 13 }}
              onClick={() => navigate('/holdings')}
            >
              {t('dashboard.manageAssets')}
            </button>
          </div>
        )}

        {/* ── News digest ── */}
        <NewsDigest />

        {/* ── Headline-language education ── */}
        <HeadlineEducation />

        {/* ── Progressive details toggle ── */}
        <ProgressiveDetails holdingsSummary={holdingsSummary} portfolio={portfolio} />

        {/* ── Risk profile / portfolio ── */}
        {!profile ? (
          <div className="card" style={{ textAlign: 'center', padding: '40px 24px', position: 'relative', overflow: 'hidden' }}>
            {/* Firefly glow effect */}
            <div style={{
              position: 'absolute', top: '50%', left: '50%',
              width: 120, height: 120, borderRadius: '50%',
              background: 'radial-gradient(circle, rgba(245,165,36,0.12) 0%, transparent 70%)',
              transform: 'translate(-50%, -50%)',
              animation: 'pulse 3s ease-in-out infinite',
            }} />
            <div style={{ position: 'relative', zIndex: 1 }}>
              <FireflyMark size={48} style={{ display: 'block', margin: '0 auto 12px', filter: 'drop-shadow(0 0 12px rgba(245,165,36,0.4))' }} />
              <p style={{ fontSize: 15, fontWeight: 600, marginBottom: 6 }}>{t('dashboard.journeyTitle')}</p>
              <p style={{ fontSize: 13, color: 'var(--text-muted)', marginBottom: 20 }}>
                {t('dashboard.journeyBody')}
              </p>
              <button className="btn btn-primary btn-full" onClick={() => navigate('/profile')}>
                {t('dashboard.journeyCta')}
              </button>
            </div>
          </div>
        ) : (
          <>
            {/* Profile card */}
            <div className="card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
                <div>
                  <h3>{t('dashboard.riskProfile')}</h3>
                  <p style={{ fontSize: 12, marginTop: 2 }}>{profile.label}</p>
                </div>
                <span className="badge badge-amber">{profile.risk_score}/10</span>
              </div>
              <div style={{ display: 'flex', gap: 10 }}>
                <button className="btn btn-ghost" style={{ flex: 1, fontSize: 13 }} onClick={handleRerun}>
                  {t('dashboard.refresh')}
                </button>
                <button className="btn btn-ghost" style={{ flex: 1, fontSize: 13 }} onClick={() => navigate('/profile')}>
                  {t('dashboard.editProfile')}
                </button>
              </div>
            </div>

            {/* Portfolio snapshot */}
            {portfolio ? (
              <PortfolioChart allocations={portfolio.allocations} />
            ) : (
              <div className="card" style={{ textAlign: 'center', padding: '32px 24px' }}>
                <FireflyMark size={40} style={{ display: 'block', margin: '0 auto 10px', filter: 'drop-shadow(0 0 8px rgba(245,165,36,0.3))' }} />
                <p style={{ fontSize: 14, marginBottom: 6 }}>{t('dashboard.profileReadyTitle')}</p>
                <p style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 18 }}>{t('dashboard.profileReadyBody')}</p>
                <button className="btn btn-primary" onClick={handleRerun}>
                  {t('dashboard.buildPortfolio')}
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  )
}
