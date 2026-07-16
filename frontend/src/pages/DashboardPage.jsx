import { useEffect, useCallback } from 'react'
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

/** Progressive UI: minimal view for new users, deepens via "Show More" */
function ProgressiveDetails({ holdingsSummary, portfolio }) {
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
          <Icon name="chart" size={14} /> Detayları Göster (karşılaştırma & hedef)
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
            ↑ Küçült
          </button>
        </>
      )}
    </>
  )
}

export default function DashboardPage() {
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
      <p style={{ marginTop: 16, fontSize: 13, color: 'var(--text-muted)' }}>Yükleniyor…</p>
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
            <span className="gradient-text">Kontrol Paneli</span>
          </h2>
          <p style={{ fontSize: 13 }}>Tüm servetin, tek bakışta.</p>
        </div>

        {/* ── Courage Score — the visible face of the vision ── */}
        <ReadinessScore />

        {/* ── Daily tip ── */}
        <DailyTip />

        {/* ── Summary card ── */}
        {holdingsSummary && (
          <div className="card" style={{
            background: 'linear-gradient(135deg, var(--bg-card) 0%, var(--bg-card-2) 100%)',
            border: '1px solid rgba(245,165,36,0.2)',
            boxShadow: '0 4px 24px rgba(245,165,36,0.08)',
          }}>
            <p style={{ fontSize: 11, letterSpacing: '0.1em', textTransform: 'uppercase', color: 'var(--firefly)', fontWeight: 700, marginBottom: 14 }}>
              Servet Özeti
            </p>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
              <div>
                <div style={{ fontSize: 11, color: 'var(--text-dim)', marginBottom: 4 }}>Toplam Değer</div>
                <div style={{ fontSize: 24, fontWeight: 800, color: 'var(--firefly)' }}>
                  {fmt(holdingsSummary.total_current_value)} <span style={{ fontSize: 13, fontWeight: 500 }}>{unit}</span>
                </div>
                {holdingsSummary.total_purchase_amount > 0 && (
                  <div style={{ fontSize: 11, color: 'var(--text-dim)', marginTop: 3 }}>
                    Alış: {money(holdingsSummary.total_purchase_amount)}
                  </div>
                )}
              </div>
              <div>
                <div style={{ fontSize: 11, color: 'var(--text-dim)', marginBottom: 4 }}>Kalan Bütçe</div>
                <div style={{
                  fontSize: 24, fontWeight: 800,
                  color: holdingsSummary.remaining_budget > 0 ? 'var(--green)' : 'var(--text-muted)',
                }}>
                  {holdingsSummary.remaining_budget != null
                    ? <>{fmt(holdingsSummary.remaining_budget)} <span style={{ fontSize: 13, fontWeight: 500 }}>{unit}</span></>
                    : '—'
                  }
                </div>
                {holdingsSummary.cash_erosion && (
                  <div style={{ fontSize: 11, color: 'var(--red)', marginTop: 3 }}>
                    ↓ {money(holdingsSummary.cash_erosion.erosion_amount)}/ay eriyor
                  </div>
                )}
              </div>
            </div>

            {/* Per-type allocation mini bar */}
            {holdingsSummary.by_type && Object.keys(holdingsSummary.by_type).length > 0 && (
              <div style={{ marginTop: 16 }}>
                <div style={{ display: 'flex', gap: 4, height: 6, borderRadius: 6, overflow: 'hidden', marginBottom: 8 }}>
                  {Object.entries(holdingsSummary.by_type).map(([type, val], i) => {
                    const colors = ['#F5A524', '#7A4A93', '#1FB2A6', '#E8663F', '#9C5A34']
                    const pct = holdingsSummary.total_current_value > 0
                      ? (val.current_value / holdingsSummary.total_current_value) * 100
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
                      ? Math.round((val.current_value / holdingsSummary.total_current_value) * 100)
                      : 0
                    return (
                      <span key={type} style={{ fontSize: 11, color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: 4 }}>
                        <span style={{ width: 7, height: 7, borderRadius: '50%', background: colors[i % colors.length], display: 'inline-block' }} />
                        {type} %{pct}
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
              Varlıklarımı Yönet →
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
              <img src="/favicon.svg" alt="" width={48} height={48} style={{ display: 'block', margin: '0 auto 12px', filter: 'drop-shadow(0 0 12px rgba(245,165,36,0.4))' }} />
              <p style={{ fontSize: 15, fontWeight: 600, marginBottom: 6 }}>Yolculuğun burada başlıyor</p>
              <p style={{ fontSize: 13, color: 'var(--text-muted)', marginBottom: 20 }}>
                Seni tanıyalım, korkularını dinleyelim ve sana özel bir portföy oluşturalım.
              </p>
              <button className="btn btn-primary btn-full" onClick={() => navigate('/profile')}>
                Seni Tanıyalım →
              </button>
            </div>
          </div>
        ) : (
          <>
            {/* Profile card */}
            <div className="card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
                <div>
                  <h3>Risk Profilin</h3>
                  <p style={{ fontSize: 12, marginTop: 2 }}>{profile.label}</p>
                </div>
                <span className="badge badge-amber">{profile.risk_score}/10</span>
              </div>
              <div style={{ display: 'flex', gap: 10 }}>
                <button className="btn btn-ghost" style={{ flex: 1, fontSize: 13 }} onClick={handleRerun}>
                  ↻ Yenile
                </button>
                <button className="btn btn-ghost" style={{ flex: 1, fontSize: 13 }} onClick={() => navigate('/profile')}>
                  ✏️ Profili Güncelle
                </button>
              </div>
            </div>

            {/* Portfolio snapshot */}
            {portfolio ? (
              <PortfolioChart allocations={portfolio.allocations} />
            ) : (
              <div className="card" style={{ textAlign: 'center', padding: '32px 24px' }}>
                <img src="/favicon.svg" alt="" width={40} height={40} style={{ display: 'block', margin: '0 auto 10px', filter: 'drop-shadow(0 0 8px rgba(245,165,36,0.3))' }} />
                <p style={{ fontSize: 14, marginBottom: 6 }}>Profilin hazır, sıra portföyde!</p>
                <p style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 18 }}>Senin risk profiline uygun bir portföy oluşturalım.</p>
                <button className="btn btn-primary" onClick={handleRerun}>
                  Portföyümü Oluştur
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  )
}
