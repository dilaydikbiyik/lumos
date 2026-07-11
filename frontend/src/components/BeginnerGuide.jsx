import { useState } from 'react'

/**
 * BeginnerGuide — the guided first-investment journey.
 * Turkey-specific, step-by-step brokerage walkthrough.
 * Static content — no LLM dependency, always available.
 */

const STEPS = [
  {
    id: 1,
    emoji: '🏦',
    title: 'Aracı Kurum Nedir?',
    body: 'Hisse senedi ve fon alıp satman için bir aracı kuruma ihtiyacın var. Banka hesabına benzer ama yatırım için. Türkiye\'de lisanslı kurumları SPK listesinden kontrol edebilirsin.',
    tip: '💡 Türk yatırımcılar için popüler seçenekler: İş Yatırım, Yapı Kredi Yatırım, Denizbank Yatırım.',
  },
  {
    id: 2,
    emoji: '📋',
    title: 'Hesap Nasıl Açılır?',
    body: '1. Seçtiğin kurumun web sitesine git.\n2. "Hesap Aç" butonuna tıkla.\n3. TC Kimlik No, e-posta, telefon gir.\n4. Video görüşmesiyle veya şubede kimlik doğrula.\n5. 1–3 iş günü içinde hesabın aktif olur.',
    tip: '💡 Çoğu kurum için mobil uygulama üzerinden uzaktan açılış mümkün — şubeye gitme zorunluluğu yok.',
  },
  {
    id: 3,
    emoji: '💳',
    title: 'Para Nasıl Yatırılır?',
    body: 'EFT veya havale ile kendi banka hesabından aracı kurum hesabına para gönderirsin. Genellikle aynı gün ya da 1 iş günü içinde görünür.',
    tip: '💡 Küçük başla — ilk deneme için 500–1000 TL yeterli. Hepsini tek seferde yatırmak zorunda değilsin.',
  },
  {
    id: 4,
    emoji: '🛒',
    title: 'İlk Emir Nasıl Verilir?',
    body: '1. Uygulamada "Emir Ver" veya "Al" bölümüne git.\n2. Almak istediğin varlığı ara (örn: "SPY" veya "XU100").\n3. Miktar gir (kaç lot / TL).\n4. "Piyasa Emri" seç — anlık fiyattan alınır.\n5. Onayla.',
    tip: '💡 Piyasa saatleri: BIST 10:00–18:00 TSİ. ABD hisseleri için Borsa İstanbul üzerinden kaldıraçsız erişim mümkün.',
  },
  {
    id: 5,
    emoji: '📊',
    title: 'Takip ve Sabır',
    body: 'Aldıktan sonra günlük fiyat değişimlerine bakma alışkanlığı edinme — bu kaygıyı artırır. Haftada bir bakman yeterli. Lumos zaten büyük değişimlerde seni bilgilendirir.',
    tip: '💡 Altın kural: Almayı düşündüğün parayı 5 yıl görmeyecekmişsin gibi davran. Kısa vadeli ihtiyaçların için kullanma.',
  },
]

export default function BeginnerGuide({ defaultExpanded = false }) {
  const [expanded, setExpanded] = useState(defaultExpanded)
  const [activeStep, setActiveStep] = useState(0)

  return (
    <div className="card" style={{ border: '1px solid var(--firefly-dim)' }}>
      {/* Header — tap to expand */}
      <button
        onClick={() => setExpanded(!expanded)}
        style={{
          width: '100%', background: 'none', border: 'none',
          cursor: 'pointer', padding: 0, textAlign: 'left',
          display: 'flex', alignItems: 'center', gap: 10,
        }}
      >
        <span style={{ fontSize: 20 }}>🎓</span>
        <div style={{ flex: 1 }}>
          <p style={{ fontSize: 13, fontWeight: 700, color: 'var(--text)' }}>
            İlk Yatırım Rehberi
          </p>
          <p style={{ fontSize: 11, color: 'var(--text-dim)', marginTop: 2 }}>
            Aracı kurum → Para yatır → İlk emir — adım adım Türkiye rehberi
          </p>
        </div>
        <span style={{
          fontSize: 11, color: 'var(--firefly)', fontWeight: 600,
          transform: expanded ? 'rotate(180deg)' : 'none',
          transition: 'transform 0.2s ease',
        }}>▼</span>
      </button>

      {expanded && (
        <div style={{ marginTop: 16 }}>
          {/* Step selector */}
          <div style={{ display: 'flex', gap: 6, marginBottom: 16, overflowX: 'auto', paddingBottom: 4 }}>
            {STEPS.map((s, i) => (
              <button
                key={s.id}
                onClick={() => setActiveStep(i)}
                style={{
                  flexShrink: 0, padding: '6px 12px', borderRadius: 20,
                  border: 'none', cursor: 'pointer', fontSize: 11, fontWeight: 600,
                  background: activeStep === i ? 'var(--firefly)' : 'var(--bg)',
                  color: activeStep === i ? '#000' : 'var(--text-dim)',
                  transition: 'all 0.2s ease',
                }}
              >
                {s.emoji} {s.id}
              </button>
            ))}
          </div>

          {/* Active step */}
          <div style={{
            padding: 16, borderRadius: 'var(--radius-xs)',
            background: 'var(--bg)', border: '1px solid var(--border)',
          }}>
            <p style={{ fontSize: 14, fontWeight: 700, marginBottom: 10 }}>
              {STEPS[activeStep].emoji} {STEPS[activeStep].title}
            </p>
            <p style={{
              fontSize: 13, color: 'var(--text-muted)',
              lineHeight: 1.7, whiteSpace: 'pre-line', marginBottom: 12,
            }}>
              {STEPS[activeStep].body}
            </p>
            <div style={{
              fontSize: 12, lineHeight: 1.6, padding: '8px 12px',
              background: 'var(--firefly-dim)', borderRadius: 'var(--radius-xs)',
              color: 'var(--text)',
            }}>
              {STEPS[activeStep].tip}
            </div>
          </div>

          {/* Next/back */}
          <div style={{ display: 'flex', gap: 8, marginTop: 12 }}>
            <button
              className="btn btn-ghost"
              style={{ flex: 1, fontSize: 12 }}
              disabled={activeStep === 0}
              onClick={() => setActiveStep(s => s - 1)}
            >
              ← Önceki
            </button>
            <button
              className="btn btn-ghost"
              style={{ flex: 1, fontSize: 12 }}
              disabled={activeStep === STEPS.length - 1}
              onClick={() => setActiveStep(s => s + 1)}
            >
              Sonraki →
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
