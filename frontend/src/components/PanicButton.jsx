import { useEffect, useState } from 'react'
import useScrollDirection from '../hooks/useScrollDirection'
import Icon from './Icon'
import { useAuth } from '@clerk/clerk-react'
import api, { setAuthToken } from '../utils/api'

/**
 * Panic Button — press it when a market drop makes you want to sell everything.
 * Purpose is behavioural, not decorative: a deliberate pause before an
 * irreversible decision. Panic-selling into a fall is the single most common
 * and most expensive mistake retail investors make.
 *
 * 3 stages: a short forced pause → profile-based facts → an honest
 * "the decision is yours" close. No dark patterns: we never block selling.
 */
export default function PanicButton() {
  const { getToken } = useAuth()
  const tucked = useScrollDirection()
  const [open, setOpen] = useState(false)
  const [stage, setStage] = useState('pause')     // pause | coach | done
  const [coach, setCoach] = useState(null)
  const [closing, setClosing] = useState(null)
  const [secondsLeft, setSecondsLeft] = useState(10)

  // Pause stage: a 10-second countdown before the facts appear. The wait is
  // the point — it breaks the reflex to act instantly. Skippable.
  // All state transitions live in the timeout callback (never synchronously
  // in the effect body — react-hooks/set-state-in-effect).
  useEffect(() => {
    if (!open || stage !== 'pause') return
    const t = setTimeout(() => {
      if (secondsLeft <= 1) setStage('coach')
      else setSecondsLeft(secondsLeft - 1)
    }, 1000)
    return () => clearTimeout(t)
  }, [open, stage, secondsLeft])

  async function press() {
    setOpen(true)
    setStage('pause')
    setSecondsLeft(10)
    setClosing(null)
    try {
      setAuthToken(await getToken())
      const res = await api.post('/coach/panic', {})
      setCoach(res.data)
    } catch {
      setCoach({
        message: 'Acele bir karar vermek zorunda değilsin. Bir düşüş, ancak sattığında kesinleşir.',
        facts: ['Bu ekranı kapatıp hiçbir şey yapmamak da geçerli bir karardır.'],
      })
    }
  }

  async function resolve(choice) {
    try {
      const res = await api.post('/coach/panic', { resolution: choice })
      setClosing(res.data.message)
    } catch {
      setClosing('Karar senin. Acele etmene gerek yok — rakamlar yerinde duruyor.')
    }
    setStage('done')
  }

  return (
    <>
      {/* Floating panic button — left side, above the bottom nav */}
      <button
        onClick={press}
        aria-label="Panik anı desteği"
        className={`fab fab-panic ${tucked ? "fab-tucked" : ""}`}
        style={{
          background: 'var(--bg-card)', border: '1px solid var(--firefly-dim)',
          boxShadow: '0 4px 18px rgba(245,165,36,0.18)',
        }}
      >
        <Icon name="lifebuoy" size={24} />
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
          {stage === 'pause' && (
            <>
              <div style={{
                fontSize: 44, fontWeight: 700, fontVariantNumeric: 'tabular-nums',
                color: 'var(--firefly)',
              }}>
                {secondsLeft}
              </div>
              <p style={{ fontSize: 17, fontWeight: 600, marginTop: 18 }}>
                Karar vermeden önce dur
              </p>
              <p style={{ fontSize: 14, opacity: 0.75, marginTop: 8, maxWidth: 360, lineHeight: 1.6 }}>
                Düşüşte acele satış, yatırımcıların en sık yaptığı ve en pahalıya mal olan hatadır.
                Birkaç saniye sonra elindeki gerçek rakamları göstereceğim.
              </p>
              <button className="btn btn-ghost" style={{ marginTop: 24, fontSize: 13 }}
                      onClick={() => setStage('coach')}>
                Rakamları şimdi göster →
              </button>
            </>
          )}

          {stage === 'coach' && coach && (
            <div style={{ maxWidth: 460 }}>
              <p style={{
                fontSize: 12, fontWeight: 700, letterSpacing: '0.08em',
                textTransform: 'uppercase', color: 'var(--firefly)', marginBottom: 14,
              }}>
                Senin durumun
              </p>
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
                  Planıma sadık kalıyorum
                </button>
                <button className="btn btn-ghost btn-full" onClick={() => resolve('still_worried')}>
                  Hâlâ endişeliyim
                </button>
              </div>
            </div>
          )}

          {stage === 'done' && (
            <div style={{ maxWidth: 420 }}>
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
