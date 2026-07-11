import { useEffect, useState } from 'react'
import { useAuth } from '@clerk/clerk-react'
import api, { setAuthToken } from '../utils/api'

/**
 * Panic Button 🫨 — a real button to press when the market gets scary.
 * No finance app has one; the crisis-moment form of the "fear = data" vision.
 *
 * 3 stages: breathing exercise → profile-based coach message + honest
 * facts → a "the decision is yours" close. No dark patterns: we never
 * block selling.
 */
export default function PanicButton() {
  const { getToken } = useAuth()
  const [open, setOpen] = useState(false)
  const [stage, setStage] = useState('breathe')     // breathe | coach | done
  const [coach, setCoach] = useState(null)
  const [closing, setClosing] = useState(null)
  const [breathCount, setBreathCount] = useState(0)

  // Breathing stage: 3 breaths (~4.5s each), then move to the coach stage.
  // All setStates live in the timeout callback — never synchronous in the
  // effect body.
  useEffect(() => {
    if (!open || stage !== 'breathe') return
    const t = setTimeout(() => {
      if (breathCount + 1 >= 3) setStage('coach')
      else setBreathCount(breathCount + 1)
    }, 4500)
    return () => clearTimeout(t)
  }, [open, stage, breathCount])

  async function press() {
    setOpen(true)
    setStage('breathe')
    setBreathCount(0)
    setClosing(null)
    try {
      setAuthToken(await getToken())
      const res = await api.post('/coach/panic', {})
      setCoach(res.data)
    } catch {
      setCoach({
        message: 'Derin bir nefes al. Şu an hiçbir şey yapmak zorunda değilsin.',
        facts: ['Bu ekranı kapattıktan sonra hiçbir şey yapmaman da tamamen geçerli bir karardır.'],
      })
    }
  }

  async function resolve(choice) {
    try {
      const res = await api.post('/coach/panic', { resolution: choice })
      setClosing(res.data.message)
    } catch {
      setClosing('Yanındayız. Acele bir karar vermek zorunda değilsin.')
    }
    setStage('done')
  }

  return (
    <>
      {/* Floating panic button — above the bottom nav */}
      <button
        onClick={press}
        aria-label="Panik anı desteği"
        style={{
          position: 'fixed', right: 14, bottom: 76, zIndex: 40,
          width: 52, height: 52, borderRadius: '50%',
          background: 'var(--bg-card)', border: '1px solid var(--firefly-dim)',
          boxShadow: '0 4px 18px rgba(245,165,36,0.18)',
          fontSize: 22, cursor: 'pointer',
        }}
      >
        🫨
      </button>

      {open && (
        <div
          role="dialog"
          aria-modal="true"
          style={{
            position: 'fixed', inset: 0, zIndex: 50,
            background: 'rgba(6,7,12,0.94)', backdropFilter: 'blur(6px)',
            display: 'flex', flexDirection: 'column', alignItems: 'center',
            justifyContent: 'center', padding: 24, textAlign: 'center',
          }}
        >
          {stage === 'breathe' && (
            <>
              <div className="panic-breath" aria-hidden="true" />
              <p style={{ fontSize: 17, fontWeight: 600, marginTop: 28 }}>
                Önce birlikte nefes alalım
              </p>
              <p style={{ fontSize: 14, opacity: 0.75, marginTop: 6 }}>
                Halka büyürken al, küçülürken ver · {3 - breathCount} nefes kaldı
              </p>
              <button className="btn btn-ghost" style={{ marginTop: 24, fontSize: 13 }}
                      onClick={() => setStage('coach')}>
                Atla →
              </button>
            </>
          )}

          {stage === 'coach' && coach && (
            <div style={{ maxWidth: 460 }}>
              <div style={{ fontSize: 30, marginBottom: 14 }}>🕯️</div>
              <p style={{ fontSize: 15, lineHeight: 1.7, marginBottom: 18 }}>{coach.message}</p>
              <div style={{ textAlign: 'left', display: 'flex', flexDirection: 'column', gap: 10, marginBottom: 22 }}>
                {coach.facts?.map((f, i) => (
                  <div key={i} style={{ display: 'flex', gap: 8, fontSize: 13, opacity: 0.85 }}>
                    <span style={{ color: 'var(--firefly)' }}>•</span>
                    <span>{f}</span>
                  </div>
                ))}
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                <button className="btn btn-primary btn-full" onClick={() => resolve('held')}>
                  Sakinleştim — planımdayım
                </button>
                <button className="btn btn-ghost btn-full" onClick={() => resolve('still_worried')}>
                  Hâlâ endişeliyim
                </button>
              </div>
            </div>
          )}

          {stage === 'done' && (
            <div style={{ maxWidth: 420 }}>
              <div style={{ fontSize: 30, marginBottom: 14 }}>🪰✨</div>
              <p style={{ fontSize: 15, lineHeight: 1.7, marginBottom: 22 }}>{closing}</p>
              <button className="btn btn-primary" onClick={() => setOpen(false)}>
                Kapat
              </button>
            </div>
          )}
        </div>
      )}
    </>
  )
}
