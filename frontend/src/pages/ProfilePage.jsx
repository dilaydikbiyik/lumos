import { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { UserButton, useAuth } from '@clerk/clerk-react'
import LumosLogo from '../components/LumosLogo'
import ChatWindow from '../components/ChatWindow'
import RiskGauge from '../components/RiskGauge'
import usePortfolio from '../hooks/usePortfolio'
import useMarket from '../hooks/useMarket'

// Risk score → user-friendly label and colour
const RISK_META = {
  low:    { color: 'var(--green)',   label: 'Muhafazakâr'  },
  medium: { color: 'var(--firefly)', label: 'Dengeli'      },
  high:   { color: 'var(--accent)',  label: 'Atılgan'      },
}

function getRiskMeta(score) {
  if (score <= 3) return RISK_META.low
  if (score <= 6) return RISK_META.medium
  return RISK_META.high
}

function readCachedProfile(key) {
  if (!key) return null
  try {
    return JSON.parse(localStorage.getItem(key) || 'null')
  } catch {
    return null
  }
}

export default function ProfilePage() {
  const navigate = useNavigate()
  const { userId } = useAuth()
  const { saveProfile, loadProfile } = usePortfolio()
  const { money } = useMarket()

  // NOTHING here blocks on the network: a returning user sees their cached
  // result instantly, a new user sees the quiz instantly (its intro is a
  // local constant). The server copy refreshes in the background.
  const cacheKey = userId ? `lumos-profile-${userId}` : null
  const [displayProfile, setDisplayProfile] = useState(() => readCachedProfile(cacheKey))
  const [retaking, setRetaking] = useState(false)   // user chose to redo
  const quizStartedRef = useRef(false)              // guards against late swaps

  useEffect(() => {
    let cancelled = false
    loadProfile().then(result => {
      if (cancelled) return
      if (result?.risk_score != null) {
        // Fresh server copy — adopt it unless the user is mid-quiz
        if (!quizStartedRef.current) setDisplayProfile(result)
        if (cacheKey) localStorage.setItem(cacheKey, JSON.stringify(result))
      } else if (result === null) {
        // Server DEFINITIVELY has no profile — drop any stale cache
        if (cacheKey) localStorage.removeItem(cacheKey)
        if (!quizStartedRef.current) setDisplayProfile(null)
      }
      // undefined = transient error (cold start etc.) — keep what we have
    })
    return () => { cancelled = true }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  async function handleProfileComplete(answers) {
    const result = await saveProfile(answers)
    if (result) {
      setRetaking(false)
      quizStartedRef.current = false
      setDisplayProfile(result)
      if (cacheKey) localStorage.setItem(cacheKey, JSON.stringify(result))
    }
  }

  // Show result if we have a saved profile AND the user hasn't asked to redo
  const showResult = !retaking && displayProfile?.risk_score != null

  return (
    <div className="page">
      <header className="navbar">
        <LumosLogo />
        <UserButton afterSignOutUrl="/" />
      </header>

      <div className="page-content">
        {!showResult ? (
          <>
            {/* Header — jargon-free copy */}
            <div style={{ marginBottom: 16 }}>
              <p style={{
                fontSize: 12, letterSpacing: '0.12em', textTransform: 'uppercase',
                color: 'var(--firefly)', fontWeight: 700, marginBottom: 8,
              }}>
                Adım 3 / 3
              </p>
              <h2>Seni Tanıyalım</h2>
              <p style={{ fontSize: 13, marginTop: 6 }}>
                9 kısa soru — yapay zeka profilini çıkaracak, portföyünü buna göre kişiselleştirecek.
              </p>
            </div>
            <ChatWindow
              onProfileComplete={handleProfileComplete}
              onFirstMessage={() => { quizStartedRef.current = true }}
            />
          </>
        ) : (
          /* Score reveal — full-page result */
          <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            {/* Header */}
            <div style={{ textAlign: 'center', padding: '12px 0' }}>
              <img src="/favicon.svg" alt="" width={44} height={44} style={{ display: 'block', margin: '0 auto 10px', filter: 'drop-shadow(0 0 12px rgba(245,165,36,0.4))' }} />
              <h2>Risk Profilin Hazır</h2>
              <p style={{ fontSize: 13, marginTop: 6 }}>
                Cevapların analiz edildi — sana özel portföy hesaplanıyor.
              </p>
            </div>

            <RiskGauge score={displayProfile.risk_score} label={displayProfile.label} />

            {/* Summary card */}
            <div className="card" style={{
              borderColor: getRiskMeta(displayProfile.risk_score).color + '44',
              background: 'var(--bg-card)',
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 10 }}>
                <span style={{
                  fontSize: 12, fontWeight: 700, letterSpacing: '0.08em',
                  color: getRiskMeta(displayProfile.risk_score).color,
                  textTransform: 'uppercase',
                }}>
                  {getRiskMeta(displayProfile.risk_score).label} Profil
                </span>
                <span className="badge badge-amber">{displayProfile.risk_score}/10</span>
              </div>
              <p style={{ fontSize: 14, lineHeight: 1.75, color: 'var(--text)' }}>
                {displayProfile.summary}
              </p>
              {displayProfile.answers?.budget && (() => {
                const dropPct = Math.round(10 + displayProfile.risk_score * 3.8)
                const worst = displayProfile.answers.budget * (1 - dropPct / 100)
                return (
                  <div style={{
                    marginTop: 12, padding: '10px 14px',
                    background: 'var(--firefly-dim)', borderRadius: 'var(--radius-xs)',
                    fontSize: 13, lineHeight: 1.6, color: 'var(--text)',
                  }}>
                    💡 Senin bütçen <strong>{money(displayProfile.answers.budget)}</strong>.
                    Bu risk seviyesinde, sert bir düşüşte portföyün geçici olarak
                    yaklaşık <strong>%{dropPct}</strong> gerileyip{' '}
                    <strong>{money(worst)}</strong>&apos;ye inebilir.
                    Bu, bu profil için normal bir dalgalanma aralığı — satmadığın sürece
                    zarar kesinleşmez.
                  </div>
                )
              })()}
            </div>

            {/* Score breakdown */}
            {displayProfile.factors?.length > 0 && (
              <div className="card">
                <h3 style={{ marginBottom: 4, fontSize: 15 }}>🧮 Bu skor nereden geldi?</h3>
                <p style={{ fontSize: 12, opacity: 0.7, marginBottom: 12 }}>
                  Kara kutu yok — her puanın kaynağı ve gerekçesi:
                </p>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                  {displayProfile.factors.map((f, i) => (
                    <div key={i} style={{ display: 'flex', gap: 10, alignItems: 'flex-start' }}>
                      <span style={{
                        minWidth: 52, textAlign: 'center', padding: '3px 6px',
                        borderRadius: 8, fontSize: 12, fontWeight: 700,
                        background: f.contribution >= 0 ? 'rgba(61,214,140,0.14)' : 'rgba(248,113,113,0.12)',
                        color: f.contribution >= 0 ? 'var(--green, #3DD68C)' : 'var(--red)',
                      }}>
                        {f.contribution >= 0 ? '+' : ''}{f.contribution}
                      </span>
                      <div style={{ fontSize: 13, lineHeight: 1.5 }}>
                        <strong>{f.factor}:</strong> {f.answer}
                        <div style={{ fontSize: 12, opacity: 0.65 }}>{f.explanation}</div>
                      </div>
                    </div>
                  ))}
                </div>
                <p style={{ fontSize: 12, opacity: 0.6, marginTop: 12, borderTop: '1px solid var(--border)', paddingTop: 8 }}>
                  Toplam ≈ <strong>{displayProfile.risk_score}/10</strong> (katkıların toplamı, 1-10 aralığına sabitlenir)
                </p>
              </div>
            )}

            <button
              className="btn btn-primary btn-full"
              onClick={() => navigate('/recommend', { state: displayProfile })}
            >
              Portföyümü Gör
            </button>
            <button
              className="btn btn-ghost btn-full"
              onClick={() => setRetaking(true)}
            >
              ← Risk Analizini Güncelle
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
