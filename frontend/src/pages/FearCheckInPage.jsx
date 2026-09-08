import { useState } from 'react'
import FireflyMark from '../components/FireflyMark'
import LumosLogo from '../components/LumosLogo'
import { useNavigate } from 'react-router-dom'
import { UserButton } from '@clerk/clerk-react'
import api from '../utils/api'
import { useTranslation } from 'react-i18next'

const FEARS = [
  { id: 'param_eriyor', icon: '💧', color: 'rgba(91,142,240,0.14)',  border: 'rgba(91,142,240,0.4)'  },
  { id: 'kandirilirim', icon: '🎭', color: 'rgba(245,81,95,0.12)',   border: 'rgba(245,81,95,0.35)'  },
  { id: 'anlamiyorum',  icon: '🌫️', color: 'rgba(124,111,247,0.12)', border: 'rgba(124,111,247,0.38)' },
  { id: 'batiririm',    icon: '📉', color: 'rgba(245,165,36,0.12)',  border: 'rgba(245,165,36,0.4)'  },
]

// Local copy of reassurance messages — matches backend exactly so we can show
// them instantly without waiting for the DB write (optimistic UX).
// Reassurance copy lives in the locale files, keyed by the same fear id the
// backend stores — so the stored answer survives a language switch.

export default function FearCheckInPage() {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const [saving, setSaving] = useState(null)
  const [reassurance, setReassurance] = useState(null)
  const [hovered, setHovered] = useState(null)

  function choose(fearId) {
    setSaving(fearId)
    // Show reassurance immediately — no waiting for the backend.
    // Fire the save in the background; failure here is non-critical
    // (the fear tag is re-derivable and the reassurance is local).
    setReassurance(t('fear.reassurance.' + fearId))
    api.patch('/users/me/fear-check-in', { primary_fear: fearId }).catch(() => {})
  }

  /* ── Reassurance screen ── */
  if (reassurance) {
    return (
      <div className="page">
        <header className="navbar">
          <LumosLogo />
          <UserButton afterSignOutUrl="/" />
        </header>
        <div className="page-content" style={{
          maxWidth: 480, margin: '0 auto',
          display: 'flex', flexDirection: 'column', alignItems: 'center',
          justifyContent: 'center', flex: 1, textAlign: 'center', gap: 20,
        }}>
          {/* Light-ring animation */}
          <div style={{ position: 'relative', marginBottom: 8 }}>
            <div style={{
              width: 80, height: 80, borderRadius: '50%',
              background: 'radial-gradient(circle, rgba(245,165,36,0.25) 0%, rgba(245,165,36,0.05) 70%, transparent 100%)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              boxShadow: '0 0 32px rgba(245,165,36,0.2)',
              animation: 'light-pulse 2s ease-in-out infinite',
            }}>
              <FireflyMark size={40} style={{ filter: 'drop-shadow(0 0 10px rgba(245,165,36,0.5))' }} />
            </div>
          </div>

          <div className="card" style={{ textAlign: 'left', maxWidth: 400 }}>
            <p style={{ fontSize: 15, lineHeight: 1.75, color: 'var(--text)' }}>
              {reassurance}
            </p>
          </div>

          <button
            className="btn btn-primary btn-full"
            style={{ maxWidth: 340 }}
            onClick={() => navigate('/profile')}
          >
            Harika, devam edelim →
          </button>
        </div>
      </div>
    )
  }

  /* ── Fear selection screen ── */
  return (
    <div className="page">
      <header className="navbar">
        <LumosLogo />
        <UserButton afterSignOutUrl="/" />
      </header>

      <div className="page-content" style={{ maxWidth: 480, margin: '0 auto' }}>
        {/* Header */}
        <div style={{ marginBottom: 28 }}>
          <p style={{
            fontSize: 12, letterSpacing: '0.12em', textTransform: 'uppercase',
            color: 'var(--firefly)', fontWeight: 700, marginBottom: 8,
          }}>
            {t('fear.step')}
          </p>
          <h2 style={{ marginBottom: 8 }}>{t('fear.title')}</h2>
          <p style={{ fontSize: 13, lineHeight: 1.6 }}>
            {t('fear.subtitle')}
          </p>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
          {FEARS.map((f) => {
            const isHovered = hovered === f.id
            const isSaving = saving === f.id
            const isDimmed = saving !== null && saving !== f.id

            return (
              <button
                key={f.id}
                onClick={() => choose(f.id)}
                disabled={saving !== null}
                onMouseEnter={() => setHovered(f.id)}
                onMouseLeave={() => setHovered(null)}
                style={{
                  textAlign: 'left',
                  cursor: saving !== null ? 'default' : 'pointer',
                  display: 'flex',
                  gap: 14,
                  alignItems: 'flex-start',
                  padding: '16px 18px',
                  borderRadius: 'var(--radius)',
                  border: `1.5px solid ${isHovered || isSaving ? f.border : 'var(--border)'}`,
                  background: isHovered || isSaving ? f.color : 'var(--bg-card)',
                  opacity: isDimmed ? 0.35 : 1,
                  transition: 'all 0.2s ease',
                  boxShadow: isHovered && !saving
                    ? `0 4px 20px ${f.color}`
                    : '0 2px 10px rgba(0,0,0,0.25)',
                  transform: isHovered && !saving ? 'scale(1.01)' : 'scale(1)',
                }}
              >
                <span style={{
                  fontSize: 26,
                  flexShrink: 0,
                  marginTop: 1,
                  transition: 'transform 0.2s',
                  transform: isHovered ? 'scale(1.1)' : 'scale(1)',
                }}>
                  {f.icon}
                </span>

                <div style={{ flex: 1 }}>
                  <div style={{ fontWeight: 600, fontSize: 14, marginBottom: 3, color: 'var(--text)' }}>
                    {t('fear.options.' + f.id + '.label')}
                  </div>
                  <div style={{ fontSize: 12, color: 'var(--text-muted)', lineHeight: 1.5 }}>
                    {t('fear.options.' + f.id + '.sublabel')}
                  </div>
                </div>

                {isSaving && (
                  <span className="spinner" style={{ marginLeft: 'auto', width: 18, height: 18, flexShrink: 0 }} />
                )}
              </button>
            )
          })}
        </div>

      </div>
    </div>
  )
}
