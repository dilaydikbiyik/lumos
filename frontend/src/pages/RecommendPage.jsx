import { useEffect, useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { UserButton } from '@clerk/clerk-react'
import PortfolioChart from '../components/PortfolioChart'
import PerformanceChart from '../components/PerformanceChart'
import ReitCard from '../components/ReitCard'
import TimeMachine from '../components/TimeMachine'
import PracticeMode from '../components/PracticeMode'
import BoughtItBridge from '../components/BoughtItBridge'
import usePortfolio from '../hooks/usePortfolio'

export default function RecommendPage() {
  const { state: profileState } = useLocation()
  const navigate = useNavigate()
  const { portfolio, isLoading, error, recommend } = usePortfolio()
  const [selectedTicker, setSelectedTicker] = useState(null)

  useEffect(() => {
    if (profileState?.risk_score && profileState?.answers?.budget) {
      recommend(profileState.risk_score, profileState.answers.budget)
    } else {
      navigate('/profile')
    }
  }, [])

  if (isLoading) return (
    <div className="page" style={{ alignItems: 'center', justifyContent: 'center' }}>
      <span className="spinner" style={{ width: 40, height: 40 }} />
      <p style={{ marginTop: 16, fontSize: 14 }}>Building your portfolio…</p>
    </div>
  )

  if (error) return (
    <div className="page" style={{ alignItems: 'center', justifyContent: 'center' }}>
      <p style={{ color: 'var(--red)' }}>{error}</p>
      <button className="btn btn-ghost" style={{ marginTop: 16 }} onClick={() => navigate('/profile')}>← Try Again</button>
    </div>
  )

  if (!portfolio) return null

  return (
    <div className="page">
      <header className="navbar">
        <span style={{ fontWeight: 700 }}><span className="gradient-text">Lumos</span></span>
        <UserButton afterSignOutUrl="/" />
      </header>

      <div className="page-content" style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
        {/* Summary strip */}
        <div>
          <h2 style={{ marginBottom: 6 }}>Your Portfolio</h2>
          <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
            <span className="badge badge-accent">Risk {portfolio.risk_score}/10</span>
            <span className="badge" style={{ background: 'var(--bg-input)', color: 'var(--text-muted)', border: '1px solid var(--border)' }}>
              {portfolio.budget?.toLocaleString()} TRY
            </span>
            {portfolio.includes_reits && <span className="badge badge-green">REIT ✓</span>}
          </div>
        </div>

        {/* Charts — stack on mobile, side-by-side on tablet+ */}
        <PortfolioChart allocations={portfolio.allocations} onSliceClick={setSelectedTicker} />
        <PerformanceChart tickers={portfolio.allocations?.map(a => a.ticker)} selected={selectedTicker} />

        {/* Sanal portföy — try before real money */}
        <PracticeMode allocations={portfolio.allocations} />

        {/* Zaman Makinesi — honest historical simulation */}
        <TimeMachine allocations={portfolio.allocations} budget={portfolio.budget} />

        {/* REIT card */}
        {portfolio.includes_reits && <ReitCard explanation={portfolio.metadata?.reit_explanation} />}

        {/* Explanation */}
        {portfolio.plain_explanation && (
          <div className="card">
            <h3 style={{ marginBottom: 10 }}>Why this portfolio?</h3>
            <p style={{ fontSize: 14, whiteSpace: 'pre-line' }}>{portfolio.plain_explanation}</p>
          </div>
        )}

        <div className="disclaimer">
          ⚠️ Educational purposes only. Past performance does not guarantee future results. Consult a licensed financial advisor.
        </div>

        {/* "Aldım" köprüsü — no-execution modelinin son halkası */}
        <BoughtItBridge allocations={portfolio.allocations} budget={portfolio.budget} />

        <button className="btn btn-ghost btn-full" onClick={() => navigate('/dashboard')}>
          Save & View Dashboard →
        </button>
      </div>
    </div>
  )
}
