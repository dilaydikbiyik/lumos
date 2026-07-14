import { useState } from 'react'
import LumosLogo from '../components/LumosLogo'
import { useNavigate } from 'react-router-dom'
import { UserButton } from '@clerk/clerk-react'
import api from '../utils/api'

const PATHS = [
  {
    id: 'stocks',
    icon: '🏦',
    title: 'Sadece Borsa',
    desc: 'Hisse, fon ve ETF dünyasına odaklan — emlak modülleri görünmez.',
    color: 'rgba(91,142,240,0.15)',
    border: 'rgba(91,142,240,0.35)',
  },
  {
    id: 'real_estate',
    icon: '🏘️',
    title: 'Sadece Emlak',
    desc: 'Arsa ve konut fırsatlarını öğrenerek keşfet — borsa önerisi dayatılmaz.',
    color: 'rgba(61,214,140,0.12)',
    border: 'rgba(61,214,140,0.32)',
  },
  {
    id: 'hybrid',
    icon: '⚖️',
    title: 'İkisi Birden',
    desc: 'Bütçeni iki dünya arasında dengeli böl — tam Lumos deneyimi.',
    color: 'rgba(245,165,36,0.12)',
    border: 'rgba(245,165,36,0.4)',
  },
  {
    id: 'undecided',
    icon: '🤷',
    title: 'Kararsızım',
    desc: 'Sorun değil! Profilini çıkaralım, birlikte en uygun yolu bulalım.',
    color: 'rgba(124,111,247,0.12)',
    border: 'rgba(124,111,247,0.32)',
  },
]

export default function PathSelectionPage() {
  const navigate = useNavigate()
  const [saving, setSaving] = useState(null)
  const [error, setError] = useState(null)
  const [hovered, setHovered] = useState(null)

  function choose(pathId) {
    setSaving(pathId)
    setError(null)
    // Move on instantly — the save is not worth blocking the UI on (a cold-
    // started backend can take 30-60s). Fire it in the background; the token
    // interceptor attaches auth, and a failure here is non-critical (the path
    // is re-selectable and re-derived on the next screen's load).
    api.patch('/users/me/investment-path', { investment_path: pathId }).catch(() => {})
    navigate('/fear-check-in')
  }

  return (
    <div className="page">
      <header className="navbar">
        <LumosLogo />
        <UserButton afterSignOutUrl="/" />
      </header>

      <div className="page-content" style={{ maxWidth: 560, margin: '0 auto' }}>
        {/* Header */}
        <div style={{ marginBottom: 28 }}>
          <p style={{
            fontSize: 12, letterSpacing: '0.12em', textTransform: 'uppercase',
            color: 'var(--firefly)', fontWeight: 700, marginBottom: 8,
          }}>
            Adım 1 / 3
          </p>
          <h2 style={{ marginBottom: 8 }}>Nasıl yatırım yapmak istersin?</h2>
          <p style={{ fontSize: 13 }}>
            Yol her an değiştirilebilir — bu bir taahhüt değil, başlangıç noktası.
          </p>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          {PATHS.map((p) => {
            const isHovered = hovered === p.id
            const isSaving = saving === p.id
            const isDimmed = saving !== null && saving !== p.id

            return (
              <button
                key={p.id}
                onClick={() => choose(p.id)}
                disabled={saving !== null}
                onMouseEnter={() => setHovered(p.id)}
                onMouseLeave={() => setHovered(null)}
                style={{
                  color: 'var(--text)',
                  textAlign: 'left',
                  cursor: saving !== null ? 'default' : 'pointer',
                  display: 'flex',
                  gap: 16,
                  alignItems: 'center',
                  padding: '18px 20px',
                  borderRadius: 'var(--radius)',
                  border: `1.5px solid ${isHovered || isSaving ? p.border : 'var(--border)'}`,
                  background: isHovered || isSaving ? p.color : 'var(--bg-card)',
                  opacity: isDimmed ? 0.4 : 1,
                  transition: 'all 0.2s ease',
                  transform: isHovered && !saving ? 'translateX(4px)' : 'translateX(0)',
                  boxShadow: isHovered && !saving
                    ? `0 4px 24px ${p.color}`
                    : '0 2px 12px rgba(0,0,0,0.3)',
                  position: 'relative',
                  overflow: 'hidden',
                }}
              >
                {/* Icon — grows slightly on hover */}
                <span style={{
                  fontSize: 32,
                  flexShrink: 0,
                  transition: 'transform 0.2s ease',
                  transform: isHovered ? 'scale(1.12)' : 'scale(1)',
                  filter: isHovered ? 'drop-shadow(0 0 6px rgba(245,165,36,0.4))' : 'none',
                }}>
                  {p.icon}
                </span>

                <div style={{ flex: 1 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 3 }}>
                    <strong style={{ fontSize: 15 }}>{p.title}</strong>
                  </div>
                  <span style={{ fontSize: 13, color: 'var(--text-muted)', lineHeight: 1.5 }}>
                    {p.desc}
                  </span>
                </div>

                {/* Ok veya spinner */}
                <span style={{
                  fontSize: 18,
                  color: isHovered ? p.border : 'var(--text-dim)',
                  transition: 'all 0.2s',
                  transform: isHovered ? 'translateX(3px)' : 'translateX(0)',
                  flexShrink: 0,
                }}>
                  {isSaving
                    ? <span className="spinner" style={{ width: 18, height: 18 }} />
                    : '→'
                  }
                </span>
              </button>
            )
          })}
        </div>

        {error && (
          <p style={{ color: 'var(--red)', fontSize: 13, marginTop: 16, textAlign: 'center' }}>
            {error}
          </p>
        )}
      </div>
    </div>
  )
}
