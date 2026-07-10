import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { UserButton } from '@clerk/clerk-react'
import LumosLogo from '../components/LumosLogo'
import ChatWindow from '../components/ChatWindow'
import RiskGauge from '../components/RiskGauge'
import usePortfolio from '../hooks/usePortfolio'

// Risk skoru → kullanıcı dostu etiket ve renk
const RISK_META = {
  low:    { emoji: '🌿', color: 'var(--green)',   label: 'Muhafazakâr'  },
  medium: { emoji: '⚖️', color: 'var(--firefly)', label: 'Dengeli'      },
  high:   { emoji: '🚀', color: 'var(--accent)',  label: 'Atılgan'      },
}

function getRiskMeta(score) {
  if (score <= 3) return RISK_META.low
  if (score <= 6) return RISK_META.medium
  return RISK_META.high
}

export default function ProfilePage() {
  const navigate = useNavigate()
  const { saveProfile } = usePortfolio()
  const [riskResult, setRiskResult] = useState(null)

  async function handleProfileComplete(answers) {
    const result = await saveProfile(answers)
    if (result) setRiskResult(result)
  }

  return (
    <div className="page">
      <header className="navbar">
        <LumosLogo />
        <UserButton afterSignOutUrl="/" />
      </header>

      <div className="page-content">
        {!riskResult ? (
          <>
            {/* Başlık — jargonsuz Türkçe */}
            <div style={{ marginBottom: 16 }}>
              <p style={{
                fontSize: 12, letterSpacing: '0.12em', textTransform: 'uppercase',
                color: 'var(--firefly)', fontWeight: 700, marginBottom: 8,
              }}>
                Adım 3 / 3
              </p>
              <h2>Seni Tanıyalım 👋</h2>
              <p style={{ fontSize: 13, marginTop: 6 }}>
                9 kısa soru — yapay zeka profilini çıkaracak, portföyünü buna göre kişiselleştirecek.
              </p>
            </div>
            <ChatWindow onProfileComplete={handleProfileComplete} />
          </>
        ) : (
          /* Skor gösterimi — tam sayfa akış */
          <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            {/* Başarı başlığı */}
            <div style={{ textAlign: 'center', padding: '12px 0' }}>
              <div style={{ fontSize: 40, marginBottom: 10 }}>
                {getRiskMeta(riskResult.risk_score).emoji}
              </div>
              <h2>Risk Profilin Hazır</h2>
              <p style={{ fontSize: 13, marginTop: 6 }}>
                Cevapların analiz edildi — sana özel portföy hesaplanıyor.
              </p>
            </div>

            <RiskGauge score={riskResult.risk_score} label={riskResult.label} />

            {/* Özet kart */}
            <div className="card" style={{
              borderColor: getRiskMeta(riskResult.risk_score).color + '44',
              background: 'var(--bg-card)',
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 10 }}>
                <span style={{
                  fontSize: 12, fontWeight: 700, letterSpacing: '0.08em',
                  color: getRiskMeta(riskResult.risk_score).color,
                  textTransform: 'uppercase',
                }}>
                  {getRiskMeta(riskResult.risk_score).label} Profil
                </span>
                <span className="badge badge-amber">{riskResult.risk_score}/10</span>
              </div>
              <p style={{ fontSize: 14, lineHeight: 1.75, color: 'var(--text)' }}>
                {riskResult.summary}
              </p>
              {/* Somutlaştırılmış risk mesajı — kendi bütçesiyle göster */}
              {riskResult.answers?.budget && (
                <div style={{
                  marginTop: 12, padding: '10px 14px',
                  background: 'var(--firefly-dim)', borderRadius: 'var(--radius-xs)',
                  fontSize: 13, lineHeight: 1.6, color: 'var(--text)',
                }}>
                  💡 Senin bütçen <strong>
                    {Number(riskResult.answers.budget).toLocaleString('tr-TR')} TL
                  </strong>. En kötü senaryoda portföyün geçici olarak{' '}
                  <strong>
                    {Math.round(riskResult.answers.budget * 0.8).toLocaleString('tr-TR')} TL
                  </strong>'ye düşebilir.
                  Bu normal bir dalgalanma — satmadığın sürece zarar kesinleşmez.
                </div>
              )}
            </div>

            {/* Skor dökümü — kara kutu yok: her puanın kaynağı */}
            {riskResult.factors?.length > 0 && (
              <div className="card">
                <h3 style={{ marginBottom: 4, fontSize: 15 }}>🧮 Bu skor nereden geldi?</h3>
                <p style={{ fontSize: 12, opacity: 0.7, marginBottom: 12 }}>
                  Kara kutu yok — her puanın kaynağı ve gerekçesi:
                </p>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                  {riskResult.factors.map((f, i) => (
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
                  Toplam ≈ <strong>{riskResult.risk_score}/10</strong> (katkıların toplamı, 1-10 aralığına sabitlenir)
                </p>
              </div>
            )}

            <button
              className="btn btn-primary btn-full"
              onClick={() => navigate('/recommend', { state: riskResult })}
            >
              Portföyümü Gör ✨
            </button>
            <button
              className="btn btn-ghost btn-full"
              onClick={() => setRiskResult(null)}
            >
              ← Sohbeti Yenile
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
