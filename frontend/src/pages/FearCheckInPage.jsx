import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { UserButton, useAuth } from '@clerk/clerk-react'
import api, { extractErrorMessage, setAuthToken } from '../utils/api'

const FEARS = [
  { id: 'param_eriyor', icon: '💧', label: 'Param erir / değerini kaybeder' },
  { id: 'kandirilirim', icon: '🎭', label: 'Kandırılırım / dolandırılırım' },
  { id: 'anlamiyorum', icon: '🌫️', label: 'Hiçbir şey anlamıyorum' },
  { id: 'batiririm', icon: '📉', label: 'Yanlış karar verip batırırım' },
]

export default function FearCheckInPage() {
  const navigate = useNavigate()
  const { getToken } = useAuth()
  const [saving, setSaving] = useState(null)
  const [reassurance, setReassurance] = useState(null)
  const [error, setError] = useState(null)

  async function choose(fearId) {
    setSaving(fearId)
    setError(null)
    try {
      setAuthToken(await getToken())
      const res = await api.patch('/users/me/fear-check-in', { primary_fear: fearId })
      setReassurance(res.data.reassurance)
    } catch (err) {
      setError(extractErrorMessage(err, 'Kaydedilemedi — tekrar dener misin?'))
      setSaving(null)
    }
  }

  if (reassurance) {
    return (
      <div className="page">
        <header className="navbar">
          <span style={{ fontWeight: 700 }}><span className="gradient-text">Lumos</span></span>
          <UserButton afterSignOutUrl="/" />
        </header>
        <div className="page-content" style={{ maxWidth: 480, margin: '0 auto', textAlign: 'center' }}>
          <div style={{ fontSize: 32, marginBottom: 12 }}>💛</div>
          <p style={{ fontSize: 15, lineHeight: 1.7, marginBottom: 24 }}>{reassurance}</p>
          <button className="btn btn-primary btn-full" onClick={() => navigate('/profile')}>
            Devam Et →
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="page">
      <header className="navbar">
        <span style={{ fontWeight: 700 }}><span className="gradient-text">Lumos</span></span>
        <UserButton afterSignOutUrl="/" />
      </header>

      <div className="page-content" style={{ maxWidth: 480, margin: '0 auto' }}>
        <h2 style={{ marginBottom: 6 }}>Yatırımda seni en çok ne korkutuyor?</h2>
        <p style={{ fontSize: 13, marginBottom: 20 }}>
          Bu korku bastırılacak bir şey değil — seni daha iyi anlamamız için bir ipucu.
        </p>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
          {FEARS.map(f => (
            <button
              key={f.id}
              className="card"
              onClick={() => choose(f.id)}
              disabled={saving !== null}
              style={{
                textAlign: 'left', cursor: 'pointer', display: 'flex',
                gap: 12, alignItems: 'center', border: '1px solid var(--border)',
                opacity: saving && saving !== f.id ? 0.5 : 1,
              }}
            >
              <span style={{ fontSize: 22 }}>{f.icon}</span>
              <span style={{ fontSize: 14 }}>{f.label}</span>
              {saving === f.id && <span className="spinner" style={{ marginLeft: 'auto', width: 16, height: 16 }} />}
            </button>
          ))}
        </div>

        {error && <p style={{ color: 'var(--red)', fontSize: 13, marginTop: 12 }}>{error}</p>}
      </div>
    </div>
  )
}
