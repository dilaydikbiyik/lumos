import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { UserButton } from '@clerk/clerk-react'
import ChatWindow from '../components/ChatWindow'
import RiskGauge from '../components/RiskGauge'
import usePortfolio from '../hooks/usePortfolio'

export default function ProfilePage() {
  const navigate = useNavigate()
  const { saveProfile, isLoading } = usePortfolio()
  const [riskResult, setRiskResult] = useState(null)

  async function handleProfileComplete(answers) {
    const result = await saveProfile(answers)
    if (result) setRiskResult(result)
  }

  return (
    <div className="page">
      {/* Navbar */}
      <header className="navbar">
        <span style={{ fontWeight: 700 }}><span className="gradient-text">Lumos</span></span>
        <UserButton afterSignOutUrl="/" />
      </header>

      <div className="page-content">
        {!riskResult ? (
          <>
            <div style={{ marginBottom: 16 }}>
              <h2>Risk Profiling</h2>
              <p style={{ fontSize: 13, marginTop: 4 }}>Answer 7 questions to get your personalised portfolio</p>
            </div>
            <ChatWindow onProfileComplete={handleProfileComplete} />
          </>
        ) : (
          /* Score reveal — full page on mobile */
          <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            <h2>Your Risk Profile</h2>
            <RiskGauge score={riskResult.risk_score} label={riskResult.label} />
            <div className="card">
              <p style={{ fontSize: 14, lineHeight: 1.7 }}>{riskResult.summary}</p>
            </div>
            <button
              className="btn btn-primary btn-full"
              onClick={() => navigate('/recommend', { state: riskResult })}
            >
              See My Portfolio →
            </button>
            <button
              className="btn btn-ghost btn-full"
              onClick={() => setRiskResult(null)}
            >
              ← Redo Chat
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
