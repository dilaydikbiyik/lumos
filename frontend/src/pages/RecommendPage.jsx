import { useEffect, useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { UserButton } from '@clerk/clerk-react'
import LumosLogo from '../components/LumosLogo'
import PortfolioChart from '../components/PortfolioChart'
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

export default function RecommendPage() {
  const { state: profileState } = useLocation()
  const navigate = useNavigate()
  const { money } = useMarket()
  const { portfolio, isLoading, error, recommend } = usePortfolio()
  const [selectedTicker, setSelectedTicker] = useState(null)

  useEffect(() => {
    if (profileState?.risk_score && profileState?.answers?.budget) {
      recommend(profileState.risk_score, profileState.answers.budget)
    } else {
      navigate('/profile')
    }
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

        {/* Allocation chart — clicking a slice opens AssetExplainer */}
        <PortfolioChart allocations={portfolio.allocations} onSliceClick={setSelectedTicker} />

        {/* Why this allocation? — deterministic formula + dropped assets */}
        <AllocationRationale portfolio={portfolio} />

        {/* Asset explainer — what/why/risk for the selected asset */}
        {selectedAlloc && (
          <AssetExplainer
            allocation={selectedAlloc}
            onClose={() => setSelectedTicker(null)}
          />
        )}

        {/* Practice portfolio — try it without risking real money */}
        <PracticeMode allocations={portfolio.allocations} />

        {/* Time Machine — honest historical simulation */}
        <TimeMachine allocations={portfolio.allocations} budget={portfolio.budget} />

        {/* Future Scenarios — not a forecast: historical window distribution */}
        <FutureScenarios allocations={portfolio.allocations} budget={portfolio.budget} />

        {/* What if? — tool-use: the AI calls the real engine, never invents math */}
        <WhatIfAssistant riskScore={portfolio.risk_score} budget={portfolio.budget} />

        {/* REIT card */}
        {portfolio.includes_reits && <ReitCard explanation={portfolio.metadata?.reit_explanation} />}

        {/* Portfolio explanation */}
        {portfolio.plain_explanation && (
          <div className="card">
            <h3 style={{ marginBottom: 10, display: 'flex', alignItems: 'center', gap: 8 }}>
              <span style={{ fontSize: 18 }}>💡</span>
              Neden Bu Portföy?
            </h3>
            <p style={{ fontSize: 14, whiteSpace: 'pre-line', lineHeight: 1.7 }}>{portfolio.plain_explanation}</p>
          </div>
        )}

        {/* Legal disclaimer */}
        <div className="disclaimer">
          ⚠️ Bu bilgiler yalnızca eğitim amaçlıdır. Geçmiş performans, gelecek sonuçların garantisi değildir. Yatırım kararlarınız için lisanslı bir finansal danışmana başvurun.
        </div>

        {/* "Take the first step" guide — broker walkthrough */}
        <BeginnerGuide />

        {/* "I bought it" bridge — the last link of the no-execution model */}
        <BoughtItBridge allocations={portfolio.allocations} budget={portfolio.budget} />

        <button className="btn btn-ghost btn-full" onClick={() => navigate('/dashboard')}>
          Kaydet ve Panele Git →
        </button>
      </div>
    </div>
  )
}
