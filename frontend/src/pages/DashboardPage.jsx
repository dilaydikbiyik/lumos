import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { UserButton } from '@clerk/clerk-react'
import PortfolioChart from '../components/PortfolioChart'
import usePortfolio from '../hooks/usePortfolio'

export default function DashboardPage() {
  const navigate = useNavigate()
  const { portfolio, profile, isLoading, loadProfile, recommend } = usePortfolio()

  useEffect(() => { loadProfile() }, [])

  async function handleRerun() {
    if (profile) {
      await recommend(profile.risk_score, profile.budget || 100_000)
    }
  }

  if (isLoading) return (
    <div className="page" style={{ alignItems: 'center', justifyContent: 'center' }}>
      <span className="spinner" style={{ width: 40, height: 40 }} />
    </div>
  )

  return (
    <div className="page">
      <header className="navbar">
        <span style={{ fontWeight: 700 }}><span className="gradient-text">Lumos</span></span>
        <UserButton afterSignOutUrl="/" />
      </header>

      <div className="page-content" style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
        <h2>Dashboard</h2>

        {!profile ? (
          <div className="card" style={{ textAlign: 'center', padding: 40 }}>
            <p style={{ marginBottom: 20, fontSize: 15 }}>No profile saved yet.</p>
            <button className="btn btn-primary btn-full" onClick={() => navigate('/profile')}>
              Start Risk Assessment →
            </button>
          </div>
        ) : (
          <>
            {/* Profile card */}
            <div className="card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
                <h3>Risk Profile</h3>
                <span className="badge badge-accent">{profile.risk_score}/10</span>
              </div>
              <p style={{ fontSize: 13, marginBottom: 16 }}>{profile.label}</p>
              <div style={{ display: 'flex', gap: 10 }}>
                <button className="btn btn-ghost" style={{ flex: 1 }} onClick={handleRerun}>
                  ↻ Re-run
                </button>
                <button className="btn btn-ghost" style={{ flex: 1 }} onClick={() => navigate('/profile')}>
                  ✏️ Re-profile
                </button>
              </div>
            </div>

            {/* Portfolio snapshot */}
            {portfolio ? (
              <PortfolioChart allocations={portfolio.allocations} />
            ) : (
              <div className="card" style={{ textAlign: 'center', padding: 32 }}>
                <p style={{ marginBottom: 16, fontSize: 14 }}>No portfolio generated yet.</p>
                <button className="btn btn-primary" onClick={handleRerun}>
                  Generate Portfolio
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  )
}
