import { useState } from 'react'

/**
 * Her portföy kalemi için "nedir / neden portföyünde / riski ne" açıklama kartı.
 * Statik sözlük tabanlı — LLM çağrısı yok, sıfır maliyet.
 */

const ASSET_INFO = {
  'XU100.IS': {
    type: 'Hisse Endeksi',
    icon: '🇹🇷',
    color: 'var(--red)',
    what: 'BIST 100, Türkiye\'nin en büyük 100 şirketinin hisselerinden oluşan bir endeks. THY, Aselsan, BİM gibi dev şirketler bu sepetin içinde.',
    why: 'Türk ekonomisi büyüdükçe bu şirketlerin değeri de büyür. Kendi ülkende yatırım yapmanın en kolay yolu.',
    risk: 'Kısa vadede %20-30 düşüşler olabilir. Ama uzun vadede (5+ yıl) Türkiye borsası tarihsel olarak enflasyonun üstünde getiri sağlamıştır.',
  },
  'SPY': {
    type: 'Amerikan Hisse ETF',
    icon: '🇺🇸',
    color: 'var(--accent-2)',
    what: 'S&P 500 — dünyanın en büyük 500 Amerikan şirketinin sepeti. Apple, Google, Amazon, Tesla hepsi içinde.',
    why: 'Dolar bazlı kazanç sağlar + ABD piyasası tarihsel olarak en istikrarlı büyüyen piyasa. TL eriyor derdine karşı bir kalkan.',
    risk: 'Dolar düşerse TL değerin azalır. Ama 10 yılda S&P 500, hiçbir 10 yıllık dönemde zarar ettirmemiştir.',
  },
  'QQQ': {
    type: 'Teknoloji ETF',
    icon: '💻',
    color: '#9B59B6',
    what: 'Nasdaq 100 — dünya teknoloji devlerinin sepeti. Apple, Microsoft, NVIDIA, Meta gibi şirketler.',
    why: 'Teknoloji sektörü uzun vadede en hızlı büyüyen sektör. Dolar bazlı, yüksek büyüme potansiyeli.',
    risk: 'Teknoloji hisseleri daha çok dalgalanır. 2022\'de %33 düşüp 2023\'te %55 çıktı — kalp dayanıklılığı gerektirir.',
  },
  'GLD': {
    type: 'Altın ETF',
    icon: '🥇',
    color: 'var(--firefly)',
    what: 'Fiziksel altının borsa hissesi versiyonu. Gram altın almak yerine, dolar bazlı altın fiyatına ortak olursun.',
    why: 'Altın, kriz dönemlerinde "güvenli liman" görevi görür. Hisse düşerken altın genelde yükselir — portföyünü dengeye getirir.',
    risk: 'Altın uzun vadede hisse kadar hızlı büyümez. Ama paranı koruma gücü çok yüksektir.',
  },
  'VNQ': {
    type: 'Gayrimenkul ETF (REIT)',
    icon: '🏢',
    color: 'var(--accent-2)',
    what: 'Vanguard REIT ETF — ABD\'deki ticari binalar, alışveriş merkezleri ve konutlara yatırım yapan bir emlak sepeti.',
    why: 'Daire almaya bütçen yetmese bile, küçük tutarlarla gayrimenkul geliri elde edebilirsin. Kira gibi düzenli temettü öder.',
    risk: 'Faiz oranları yükseldiğinde gayrimenkul fiyatları baskılanabilir. Fiziksel emlak gibi "dokunulabilir" değil.',
  },
  'SCHH': {
    type: 'ABD Konut REIT ETF',
    icon: '🏠',
    color: 'var(--green)',
    what: 'Schwab US REIT ETF — konut ağırlıklı Amerikan gayrimenkul sepeti.',
    why: 'VNQ\'ya benzer ama daha konut ağırlıklı. İki REIT\'le riski dağıtırsın — hepsi tek sepette olmaz.',
    risk: 'REIT ETF\'leri hisse gibi dalgalanır. Ama gerçek mülk alıp satma derdi yok, anında nakde çevirebilirsin.',
  },
}

// Bilinmeyen ticker'lar için genel açıklama
const DEFAULT_INFO = {
  stocks: {
    type: 'Hisse / Hisse ETF',
    icon: '📈',
    color: 'var(--accent)',
    what: 'Bir şirketin veya şirket sepetinin sahiplik payı. Şirket büyüdükçe, senin payın da değerlenir.',
    why: 'Uzun vadede en yüksek getiriyi sağlayan varlık sınıfı — enflasyonun çok üstünde büyüme potansiyeli.',
    risk: 'Kısa vadede sert düşüşler olabilir. Ama zamanla toparlanma tarihsel olarak istisnasız gerçekleşmiştir.',
  },
  gold: {
    type: 'Altın',
    icon: '🥇',
    color: 'var(--firefly)',
    what: 'Binlerce yıldır değerini koruyan kıymetli maden. "Kriz sigortası" olarak bilinir.',
    why: 'Hisse düşerken altın genelde yükselir. Portföyünün dengeyi korumasını sağlar.',
    risk: 'Uzun vadede hisseler kadar kazandırmaz, ama paranın erimesini engeller.',
  },
  fund: {
    type: 'Yatırım Fonu',
    icon: '🧺',
    color: 'var(--accent)',
    what: 'Profesyonellerin senin adına yönettiği ortak yatırım havuzu. TEFAS üzerinden alınıp satılır.',
    why: 'Tek tek hisse seçmek zorunda kalmazsın. Uzmanlar senin için en iyi karışımı yönetir.',
    risk: 'Fon yönetim ücreti kesilir. Ve fonun performansı, yöneticinin kararlarına bağlıdır.',
  },
}

function getAssetInfo(allocation) {
  if (ASSET_INFO[allocation.ticker]) return ASSET_INFO[allocation.ticker]
  // Fallback: kategori bazlı genel açıklama
  const category = allocation.category || 'stocks'
  return DEFAULT_INFO[category] || DEFAULT_INFO.stocks
}

export default function AssetExplainer({ allocation, onClose }) {
  const [activeTab, setActiveTab] = useState('what')
  const info = getAssetInfo(allocation)

  const tabs = [
    { key: 'what', label: 'Bu Nedir?', icon: '📖' },
    { key: 'why',  label: 'Neden Var?', icon: '🎯' },
    { key: 'risk', label: 'Riski Ne?', icon: '⚡' },
  ]

  return (
    <div className="card" style={{
      border: `1px solid ${info.color}22`,
      background: `linear-gradient(135deg, var(--bg-card) 0%, ${info.color}08 100%)`,
      animation: 'fade-in 0.3s ease',
      position: 'relative',
    }}>
      {/* Kapat butonu */}
      <button
        onClick={onClose}
        style={{
          position: 'absolute', top: 12, right: 12,
          background: 'none', border: 'none', color: 'var(--text-dim)',
          cursor: 'pointer', fontSize: 18, padding: '4px 8px',
        }}
        aria-label="Kapat"
      >
        ✕
      </button>

      {/* Başlık */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 14 }}>
        <span style={{
          fontSize: 28,
          filter: `drop-shadow(0 0 8px ${info.color}40)`,
        }}>{info.icon}</span>
        <div>
          <h3 style={{ fontSize: 15, fontWeight: 700 }}>
            {allocation.name}
          </h3>
          <div style={{ fontSize: 12, color: 'var(--text-dim)', display: 'flex', gap: 8, marginTop: 2 }}>
            <span>{allocation.ticker}</span>
            <span>·</span>
            <span>{info.type}</span>
            <span>·</span>
            <span style={{ color: info.color, fontWeight: 600 }}>
              %{(allocation.weight * 100).toFixed(0)}
            </span>
          </div>
        </div>
      </div>

      {/* Tab seçici */}
      <div style={{
        display: 'flex', gap: 4, marginBottom: 14,
        background: 'var(--bg)', borderRadius: 'var(--radius-xs)',
        padding: 3,
      }}>
        {tabs.map(tab => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            style={{
              flex: 1, padding: '8px 4px',
              background: activeTab === tab.key ? 'var(--bg-card-2)' : 'transparent',
              border: activeTab === tab.key ? `1px solid ${info.color}33` : '1px solid transparent',
              borderRadius: 'var(--radius-xs)',
              color: activeTab === tab.key ? 'var(--text)' : 'var(--text-dim)',
              fontSize: 12, fontWeight: activeTab === tab.key ? 600 : 400,
              cursor: 'pointer', transition: 'all 0.2s ease',
              display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 4,
            }}
          >
            <span style={{ fontSize: 13 }}>{tab.icon}</span>
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab içeriği */}
      <p style={{
        fontSize: 13.5, lineHeight: 1.7, color: 'var(--text)',
        animation: 'fade-in 0.2s ease',
      }}>
        {info[activeTab]}
      </p>
    </div>
  )
}
