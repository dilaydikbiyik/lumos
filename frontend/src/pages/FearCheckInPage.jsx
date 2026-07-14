import { useState } from 'react'
import LumosLogo from '../components/LumosLogo'
import { useNavigate } from 'react-router-dom'
import { UserButton } from '@clerk/clerk-react'
import api from '../utils/api'

const FEARS = [
  {
    id: 'param_eriyor',
    icon: '💧',
    label: 'Param erir / değerini kaybeder',
    sublabel: 'Enflasyon karşısında elimdekini koruyamam',
    color: 'rgba(91,142,240,0.14)',
    border: 'rgba(91,142,240,0.4)',
  },
  {
    id: 'kandirilirim',
    icon: '🎭',
    label: 'Kandırılırım / dolandırılırım',
    sublabel: 'Güvenilir olmayan platform veya tavsiyeye denk gelirim',
    color: 'rgba(245,81,95,0.12)',
    border: 'rgba(245,81,95,0.35)',
  },
  {
    id: 'anlamiyorum',
    icon: '🌫️',
    label: 'Hiçbir şey anlamıyorum',
    sublabel: 'Terimler ve grafikler aklımı karıştırıyor',
    color: 'rgba(124,111,247,0.12)',
    border: 'rgba(124,111,247,0.38)',
  },
  {
    id: 'batiririm',
    icon: '📉',
    label: 'Yanlış karar verip batırırım',
    sublabel: 'Kaybedemeyeceğim paralarımı risk altına sokarım',
    color: 'rgba(245,165,36,0.12)',
    border: 'rgba(245,165,36,0.4)',
  },
]

// Local copy of reassurance messages — matches backend exactly so we can show
// them instantly without waiting for the DB write (optimistic UX).
const REASSURANCE = {
  param_eriyor: 'Anlıyoruz — bu yüzden her portföyde enflasyona karşı reel getiriyi de göstereceğiz, sadece nominal sayıyı değil.',
  kandirilirim: 'Bu haklı bir endişe. Lumos sana hiçbir hisse/fon satmıyor, komisyon almıyor — sadece bilgi veriyor. Kararı hep sen verirsin.',
  anlamiyorum:  'Sorun değil, kimse doğuştan bilmiyor. Her terimi günlük dille açıklayacağız — anlamadığın hiçbir şeyi geçmeyeceğiz.',
  batiririm:    'Bu korku çoğu yeni başlayanda var. Küçük adımlarla, sanal pratikle başlayacağız — gerçek parayla asla acele etmeyeceksin.',
}

export default function FearCheckInPage() {
  const navigate = useNavigate()
  const [saving, setSaving] = useState(null)
  const [reassurance, setReassurance] = useState(null)
  const [hovered, setHovered] = useState(null)

  function choose(fearId) {
    setSaving(fearId)
    // Show reassurance immediately — no waiting for the backend.
    // Fire the save in the background; failure here is non-critical
    // (the fear tag is re-derivable and the reassurance is local).
    setReassurance(REASSURANCE[fearId])
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
              <img src="/favicon.svg" alt="" width={40} height={40} style={{ filter: 'drop-shadow(0 0 10px rgba(245,165,36,0.5))' }} />
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
            Adım 2 / 3
          </p>
          <h2 style={{ marginBottom: 8 }}>Yatırımda seni en çok ne korkutuyor?</h2>
          <p style={{ fontSize: 13, lineHeight: 1.6 }}>
            Bu korku bastırılacak bir şey değil — seni daha iyi anlamamız için bir ipucu.
            Seçtiğin korkuya özel bir yaklaşım geliştiririz.
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
                    {f.label}
                  </div>
                  <div style={{ fontSize: 12, color: 'var(--text-muted)', lineHeight: 1.5 }}>
                    {f.sublabel}
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
