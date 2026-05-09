import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { SignInButton, SignedIn, SignedOut, UserButton } from '@clerk/clerk-react'
import DisclaimerModal from '../components/DisclaimerModal'

export default function OnboardingPage() {
  const navigate = useNavigate()
  const [showDisclaimer, setShowDisclaimer] = useState(true)

  return (
    <div className="page">
      {/* Navbar */}
      <header className="navbar">
        <span style={{ fontSize: 18, fontWeight: 700 }}>
          <span className="gradient-text">Lumos</span>
        </span>
        <SignedIn><UserButton afterSignOutUrl="/" /></SignedIn>
      </header>

      <div className="page-content" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', flex: 1 }}>
        {/* Hero */}
        <div style={{ textAlign: 'center', padding: '32px 0 40px' }}>
          <div style={{ fontSize: 52, marginBottom: 20 }}>✦</div>
          <h1 style={{ marginBottom: 14 }}>
            Your <span className="gradient-text">smart</span><br />investment guide
          </h1>
          <p style={{ fontSize: 15, marginBottom: 32 }}>
            Lumos builds a personalised, volatility-weighted portfolio in minutes — powered by Claude AI.
          </p>

          <SignedOut>
            <SignInButton mode="modal">
              <button className="btn btn-primary btn-full" style={{ maxWidth: 320, margin: '0 auto', fontSize: 16 }}>
                Get Started →
              </button>
            </SignInButton>
          </SignedOut>

          <SignedIn>
            <button
              className="btn btn-primary btn-full"
              style={{ maxWidth: 320, margin: '0 auto', fontSize: 16 }}
              onClick={() => navigate('/profile')}
            >
              Continue to Chat →
            </button>
          </SignedIn>
        </div>

        {/* Feature cards — stack vertically on mobile */}
        <div className="grid-3" style={{ marginBottom: 24 }}>
          {[
            { icon: '🎯', title: 'Risk Profiling', desc: '5-question AI chat' },
            { icon: '📊', title: 'Smart Portfolio', desc: 'Volatility-weighted' },
            { icon: '🏠', title: 'Real Estate', desc: 'REIT ETFs included' },
          ].map(f => (
            <div key={f.title} className="card" style={{ textAlign: 'center', padding: '16px 12px' }}>
              <div style={{ fontSize: 26, marginBottom: 6 }}>{f.icon}</div>
              <h3 style={{ fontSize: 13, marginBottom: 2 }}>{f.title}</h3>
              <p style={{ fontSize: 12 }}>{f.desc}</p>
            </div>
          ))}
        </div>

        <div className="disclaimer">
          ⚠️ <strong>Educational purposes only.</strong> Not investment advice. Consult a licensed financial advisor.
        </div>
      </div>

      {showDisclaimer && <DisclaimerModal onAccept={() => setShowDisclaimer(false)} />}
    </div>
  )
}
