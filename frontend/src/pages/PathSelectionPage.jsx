import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { UserButton, useAuth } from '@clerk/clerk-react'
import api, { extractErrorMessage, setAuthToken } from '../utils/api'

const PATHS = [
  {
    id: 'stocks',
    icon: '🏦',
    title: 'Sadece Borsa',
    desc: 'Hisse, fon ve ETF dünyasına odaklan — emlak modülleri görünmez.',
  },
  {
    id: 'real_estate',
    icon: '🏘️',
    title: 'Sadece Emlak',
    desc: 'Arsa ve konut fırsatlarını öğrenerek keşfet — borsa önerisi dayatılmaz.',
  },
  {
    id: 'hybrid',
    icon: '⚖️',
    title: 'İkisi Birden',
    desc: 'Bütçeni iki dünya arasında dengeli böl — tam Lumos deneyimi.',
  },
  {
    id: 'undecided',
    icon: '🤷',
    title: 'Kararsızım',
    desc: 'Sorun değil! Profilini çıkaralım, sana en uygun yolu birlikte bulalım.',
  },
]

export default function PathSelectionPage() {
  const navigate = useNavigate()
  const { getToken } = useAuth()
  const [saving, setSaving] = useState(null)
  const [error, setError] = useState(null)

  async function choose(pathId) {
    setSaving(pathId)
    setError(null)
    try {
      setAuthToken(await getToken())
      await api.patch('/users/me/investment-path', { investment_path: pathId })
      navigate('/fear-check-in')
    } catch (err) {
      setError(extractErrorMessage(err, 'Seçim kaydedilemedi — tekrar dener misin?'))
      setSaving(null)
    }
  }

  return (
    <div className="page">
      <header className="navbar">
        <span style={{ fontWeight: 700 }}><span className="gradient-text">Lumos</span></span>
        <UserButton afterSignOutUrl="/" />
      </header>

      <div className="page-content" style={{ maxWidth: 560, margin: '0 auto' }}>
        <h2 style={{ marginBottom: 6 }}>Nasıl yatırım yapmak istersin?</h2>
        <p style={{ fontSize: 13, marginBottom: 20 }}>
          Yol her an değiştirilebilir — bu bir taahhüt değil, başlangıç noktası.
        </p>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          {PATHS.map(p => (
            <button
              key={p.id}
              className="card"
              onClick={() => choose(p.id)}
              disabled={saving !== null}
              style={{
                textAlign: 'left', cursor: 'pointer', display: 'flex',
                gap: 14, alignItems: 'center', border: '1px solid var(--border)',
                opacity: saving && saving !== p.id ? 0.5 : 1,
              }}
            >
              <span style={{ fontSize: 30 }}>{p.icon}</span>
              <span>
                <strong style={{ display: 'block', marginBottom: 2 }}>{p.title}</strong>
                <span style={{ fontSize: 13, color: 'var(--text-dim, #9aa)' }}>{p.desc}</span>
              </span>
              {saving === p.id && <span className="spinner" style={{ marginLeft: 'auto', width: 18, height: 18 }} />}
            </button>
          ))}
        </div>

        {error && <p style={{ color: 'var(--red)', fontSize: 13, marginTop: 12 }}>{error}</p>}
      </div>
    </div>
  )
}
