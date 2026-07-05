/**
 * HeadlineEducation — "Manşet dili eğitimi"
 * "BORSA ÇAKILDI manşetini gördüğünde gerçekte ne olur?" mikro-eğitim kartı.
 * Carousel formatında 4 senaryo, localStorage ile gösterilme takibi.
 */

const SCENARIOS = [
  {
    id: 'headline-crash',
    headline: '📰 "BORSA ÇAKILDI"',
    reality: 'BIST 100 büyük ihtimalle %2–4 düştü. Tarihsel olarak bu düşüşler 3–6 ayda telafi edilir. "Çakılmak" manşet için cazip, yatırımcı için norm.',
    action: '👉 Sakin kal. Bugün satmak, kaybı gerçeğe dönüştürür.',
  },
  {
    id: 'headline-crash-global',
    headline: '📰 "KRİZ GELİYOR"',
    reality: 'Kriz öngörüleri medyada sürekli var — çoğu gerçekleşmez. Gerçekleşen krizlerin %80\'i de 2–5 yılda portföyleri eski seviyeye getirdi.',
    action: '👉 Panikle değil, çeşitlendirmeyle hazırlan.',
  },
  {
    id: 'headline-gold',
    headline: '📰 "ALTIN REKORA KOŞTU"',
    reality: 'Altın yükselince genellikle belirsizlik var demektir. Bu, diğer varlıklarının değersizleştiği anlamına gelmez — her varlık farklı koşulda parlar.',
    action: '👉 Tek varlığa bağlı kalmak risklidir. Denge önemli.',
  },
  {
    id: 'headline-dolar',
    headline: '📰 "DOLAR PATLIYOR"',
    reality: 'TL değer kaybedince döviz bazlı varlıkların TL karşılığı yükselir. Portföyünde SPY veya GLD varsa bu manşet seni koruyabilir.',
    action: '👉 Kur riski için portföyde döviz bazlı varlık tut.',
  },
]

const STORAGE_KEY = 'lumos-seen-headlines'

function getSeenHeadlines() {
  try { return JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]') } catch { return [] }
}

import { useState } from 'react'

export default function HeadlineEducation() {
  const seen = getSeenHeadlines()
  const unseen = SCENARIOS.filter(s => !seen.includes(s.id))
  const [scenario] = useState(() => unseen[0] || null)
  const [dismissed, setDismissed] = useState(false)

  if (!scenario || dismissed) return null

  function dismiss() {
    const next = [...getSeenHeadlines(), scenario.id]
    localStorage.setItem(STORAGE_KEY, JSON.stringify(next))
    setDismissed(true)
  }

  return (
    <div className="card" style={{
      background: 'linear-gradient(135deg, var(--bg-card) 0%, rgba(248,113,113,0.03) 100%)',
      border: '1px solid rgba(248,113,113,0.15)',
      position: 'relative',
    }}>
      <button
        onClick={dismiss}
        style={{
          position: 'absolute', top: 10, right: 12,
          background: 'none', border: 'none', color: 'var(--text-dim)',
          cursor: 'pointer', fontSize: 16, padding: '2px 6px',
        }}
        aria-label="Kapat"
      >✕</button>

      <span style={{
        display: 'inline-block', fontSize: 10, fontWeight: 700,
        color: 'var(--red)', textTransform: 'uppercase', letterSpacing: '0.08em',
        marginBottom: 10,
      }}>
        🗞️ Manşet Oku, Paniklemeden Anla
      </span>

      <p style={{ fontSize: 18, fontWeight: 800, marginBottom: 10 }}>
        {scenario.headline}
      </p>

      <p style={{ fontSize: 13, color: 'var(--text-muted)', lineHeight: 1.65, marginBottom: 10 }}>
        {scenario.reality}
      </p>

      <p style={{
        fontSize: 13, fontWeight: 600, lineHeight: 1.5,
        padding: '8px 12px', borderRadius: 'var(--radius-xs)',
        background: 'var(--firefly-dim)', color: 'var(--firefly)',
      }}>
        {scenario.action}
      </p>

      {/* İlerleme */}
      <div style={{
        marginTop: 12, height: 3, background: 'var(--bg)',
        borderRadius: 2, overflow: 'hidden',
      }}>
        <div style={{
          width: `${(seen.length / SCENARIOS.length) * 100}%`,
          height: '100%', background: 'var(--red)',
          borderRadius: 2, transition: 'width 0.4s ease',
        }} />
      </div>
      <p style={{ fontSize: 10, color: 'var(--text-dim)', marginTop: 4 }}>
        {seen.length}/{SCENARIOS.length} manşet gerçeği öğrenildi
      </p>
    </div>
  )
}
