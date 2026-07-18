import { useEffect, useState } from 'react'
import Icon from '../components/Icon'
import { useLocation, useNavigate } from 'react-router-dom'
import { UserButton } from '@clerk/clerk-react'
import LumosLogo from '../components/LumosLogo'
import PortfolioChart from '../components/PortfolioChart'
import { sliceColor } from '../utils/palette'
import ReitCard from '../components/ReitCard'
import AssetExplainer from '../components/AssetExplainer'
import TimeMachine from '../components/TimeMachine'
import FutureScenarios from '../components/FutureScenarios'
import AllocationRationale from '../components/AllocationRationale'
import WhatIfAssistant from '../components/WhatIfAssistant'
import PracticeMode from '../components/PracticeMode'
import BoughtItBridge from '../components/BoughtItBridge'
import BeginnerGuide from '../components/BeginnerGuide'
import usePortfolio from '../hooks/usePortfolio'
import useMarket from '../hooks/useMarket'


/** One stage of the portfolio journey. Collapsed by default so the page opens
    as "here is your portfolio and why", not as a wall of thirteen cards. */
function Layer({ title, hint, open, onToggle, children }) {
  return (
    <section style={{ display: 'flex', flexDirection: 'column', gap: open ? 16 : 0 }}>
      <button
        onClick={onToggle}
        aria-expanded={open}
        style={{
          width: '100%', textAlign: 'left', cursor: 'pointer',
          background: open ? 'var(--bg-card-2)' : 'var(--bg-card)',
          border: '1px solid var(--border)', borderRadius: 'var(--radius-sm)',
          padding: '14px 16px', color: 'var(--text)',
          display: 'flex', alignItems: 'center', gap: 12,
        }}
      >
        <div style={{ flex: 1 }}>
          <div style={{ fontSize: 'var(--t-lead)', fontWeight: 700, marginBottom: 2 }}>{title}</div>
          <div style={{ fontSize: 'var(--t-micro)', color: 'var(--text-muted)', lineHeight: 1.5 }}>{hint}</div>
        </div>
        <span style={{
          color: 'var(--firefly)', fontSize: 18, flexShrink: 0,
          transform: open ? 'rotate(180deg)' : 'none', transition: 'transform 0.2s ease',
        }}>⌄</span>
      </button>
      {open && children}
    </section>
  )
}

export default function RecommendPage() {
  const { state: profileState } = useLocation()
  const navigate = useNavigate()
  const { money } = useMarket()
  const { portfolio, isLoading, error, recommend, loadProfile } = usePortfolio()
  const [selectedTicker, setSelectedTicker] = useState(null)
  const [layer, setLayer] = useState(null)   // 'test' | 'apply' | null

  useEffect(() => {
    if (profileState?.risk_score && profileState?.answers?.budget) {
      recommend(profileState.risk_score, profileState.answers.budget)
      return
    }
    // Opened directly (bottom nav, deep link, refresh): no router state —
    // fall back to the saved server profile before bouncing to the quiz.
    let cancelled = false
    ;(async () => {
      const saved = await loadProfile()
      if (cancelled) return
      if (saved?.risk_score != null && saved?.answers?.budget) {
        recommend(saved.risk_score, saved.answers.budget)
      } else if (saved === null && !portfolio) {
        // The server DEFINITIVELY has no profile and nothing is cached —
        // only then send the user to the quiz. A transient error (undefined)
        // must never throw someone with a cached portfolio back to step one.
        navigate('/profile')
      }
    })()
    return () => { cancelled = true }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [profileState?.risk_score, profileState?.answers?.budget])

  if (isLoading) return (
    <div className="page" style={{ alignItems: 'center', justifyContent: 'center', gap: 16 }}>
      <div className="light-loader" style={{ width: 24, height: 24 }} />
      <p style={{ fontSize: 14, color: 'var(--text-muted)' }}>Portföyün hazırlanıyor…</p>
    </div>
  )

  if (error) return (
    <div className="page" style={{ alignItems: 'center', justifyContent: 'center' }}>
      <p style={{ color: 'var(--red)' }}>{error}</p>
      <button className="btn btn-ghost" style={{ marginTop: 16 }} onClick={() => navigate('/profile')}>← Tekrar Dene</button>
    </div>
  )

  if (!portfolio) return null

  const selectedAlloc = portfolio.allocations?.find(a => a.ticker === selectedTicker)

  return (
    <div className="page">
      <header className="navbar">
        <LumosLogo />
        <UserButton afterSignOutUrl="/" />
      </header>

      <div className="page-content" style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
        {/* Header */}
        <div>
          <h2 style={{ marginBottom: 6 }}>
            <span className="gradient-text">Portföyün Hazır</span>
          </h2>
          <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
            <span className="badge badge-amber">Risk {portfolio.risk_score}/10</span>
            <span className="badge" style={{ background: 'var(--bg-input)', color: 'var(--text-muted)', border: '1px solid var(--border)' }}>
              {money(portfolio.budget ?? 0)} bütçe
            </span>
            {portfolio.includes_reits && <span className="badge badge-green">REIT dahil ✓</span>}
          </div>
        </div>

        {/* ── Layer 1: PORTFÖYÜN — what you got and why (always visible) ── */}
        <PortfolioChart allocations={portfolio.allocations} onSliceClick={setSelectedTicker} />

        {selectedAlloc && (
          <AssetExplainer
            allocation={selectedAlloc}
            color={sliceColor(selectedAlloc, portfolio.allocations.findIndex(a => a.ticker === selectedTicker))}
            onClose={() => setSelectedTicker(null)}
          />
        )}

        <AllocationRationale portfolio={portfolio} />

        {portfolio.plain_explanation && (
          <div className="card">
            <h3 style={{ marginBottom: 10, display: 'flex', alignItems: 'center', gap: 8 }}>
              <Icon name="bulb" size={18} />
              Neden Bu Portföy?
            </h3>
            <p style={{ fontSize: 'var(--t-small)', whiteSpace: 'pre-line', lineHeight: 1.7 }}>
              {portfolio.plain_explanation}
            </p>
          </div>
        )}

        {portfolio.includes_reits && <ReitCard explanation={portfolio.metadata?.reit_explanation} />}

        {/* ── Layer 2: SINA — test it against reality before risking money ── */}
        <Layer
          title="Bu portföyü sına"
          hint="Gerçek geçmiş verilerle dene: kötü günlerde ne olurdu, sen ne hissederdin?"
          open={layer === 'test'}
          onToggle={() => setLayer(layer === 'test' ? null : 'test')}
        >
          <PracticeMode allocations={portfolio.allocations} />
          <TimeMachine allocations={portfolio.allocations} budget={portfolio.budget} />
          <FutureScenarios allocations={portfolio.allocations} budget={portfolio.budget} />
          <WhatIfAssistant riskScore={portfolio.risk_score} budget={portfolio.budget} />
        </Layer>

        {/* "How do I actually buy this?" — reference material, fine to fold away */}
        <Layer
          title="Nasıl alırım?"
          hint="Aracı kurum hesabı açmaktan ilk emri vermeye kadar adım adım rehber."
          open={layer === 'howto'}
          onToggle={() => setLayer(layer === 'howto' ? null : 'howto')}
        >
          <BeginnerGuide />
        </Layer>

        {/* The execution bridge is the page's primary action once someone has
            bought — it must never sit behind a collapsed section. */}
        <BoughtItBridge allocations={portfolio.allocations} budget={portfolio.budget} />

        <div className="disclaimer">
          <Icon name="warning" size={13} /> Bu bilgiler yalnızca eğitim amaçlıdır. Geçmiş performans, gelecek sonuçların garantisi değildir. Yatırım kararlarınız için lisanslı bir finansal danışmana başvurun.
        </div>

        {/* Nothing is saved here — the portfolio is recomputed from the profile
            on demand. Calling it "Kaydet" implied an action that never happened. */}
        <button className="btn btn-ghost btn-full" onClick={() => navigate('/dashboard')}>
          Panele dön →
        </button>
      </div>
    </div>
  )
}
