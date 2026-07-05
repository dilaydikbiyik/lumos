import { useState } from 'react'

/**
 * "Bugün Öğrendin" — her oturumda tek kavram, 15 saniyelik okuma.
 * Kullanıcı kapatınca localStorage'da kayıt tutulur, aynı kartı tekrar görmez.
 */

const TIPS = [
  { id: 'etf', emoji: '🧺', title: 'ETF Aslında Bir Sepettir', body: 'Tek alımda onlarca hisseye birden ortak olursun. Tek tek seçme derdi yok — hazır paketlenmiş yatırım.' },
  { id: 'diversification', emoji: '🥚', title: 'Yumurtaları Tek Sepete Koyma', body: 'Farklı varlıklara dağıtınca tek bir kötü gün her şeyini götürmez. Buna çeşitlendirme denir.' },
  { id: 'inflation', emoji: '📉', title: 'Enflasyon Paranı Eritir', body: '%50 enflasyonda yastık altındaki 100 TL, bir yıl sonra 67 TL gibi davranır. Yatırım yapmamak da bir risk.' },
  { id: 'dividend', emoji: '💰', title: 'Temettü = Kira Gibi', body: 'Şirketin kârından sana düşen pay. Hisseni tuttuğun sürece düzenli gelir getirir — mülk kiralamak gibi.' },
  { id: 'reel-return', emoji: '📊', title: 'Reel Getiri Gerçek Kazanç', body: '%45 kazandın ama enflasyon %60 ise gerçekte kaybettin. Her zaman enflasyondan arındırılmış getiriye bak.' },
  { id: 'liquidity', emoji: '💧', title: 'Likidite Hayat Kurtarır', body: 'Hisse dakikalar içinde nakde döner, arsa aylar sürebilir. Acil paraya ihtiyacın olabilir — bunu unutma.' },
  { id: 'drawdown', emoji: '🎢', title: 'Düşüşler Normal', body: 'Piyasalar her yıl ortalama %10-15 düşüş yaşar. Bu panik değil, doğal döngü. Satmadığın sürece zarar etmedin.' },
  { id: 'gold', emoji: '🥇', title: 'Altın Sigorta Gibi', body: 'Kriz dönemlerinde hisse düşerken altın genelde yükselir. Portföyünün "koruma kalkanı" olarak düşün.' },
  { id: 'patience', emoji: '⏳', title: 'Sabır En İyi Strateji', body: 'S&P 500 tarihinde hiçbir 10 yıllık dönemde zarar ettirmemiştir. Zaman, en güçlü yatırım aracın.' },
  { id: 'reit', emoji: '🏢', title: 'Ev Almadan Emlakçı Ol', body: 'REIT ETF\'leri ile küçük tutarlarla gayrimenkul geliri elde edebilirsin. Mülk almadan emlak yatırımcısı olmanın yolu.' },
  { id: 'fomo', emoji: '🔥', title: 'FOMO Düşmanın', body: '"Herkes alıyor, ben de alayım" en tehlikeli yatırım cümlesidir. Her yükselişte alsan, genelde tepeyi yakalar düşersin.' },
  { id: 'cost-avg', emoji: '📅', title: 'Düzenli Yatırım Kur Riskini Azaltır', body: 'Her ay aynı tutarı yatırmak, bazı ay ucuza bazı ay pahalıya almana sebep olur. Sonuç: ortalamanın altında maliyet.' },
]

const STORAGE_KEY = 'lumos-learned-tips'

function getSeenTips() {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]')
  } catch {
    return []
  }
}

function markSeen(tipId) {
  const seen = getSeenTips()
  if (!seen.includes(tipId)) {
    seen.push(tipId)
    localStorage.setItem(STORAGE_KEY, JSON.stringify(seen))
  }
}

export default function DailyTip() {
  const seen = getSeenTips()
  const unseen = TIPS.filter(t => !seen.includes(t.id))
  const [tip] = useState(() => unseen[0] || null)
  const [dismissed, setDismissed] = useState(false)

  if (!tip || dismissed) return null

  const progress = getSeenTips().length
  const total = TIPS.length

  return (
    <div className="card" style={{
      background: 'linear-gradient(135deg, var(--bg-card) 0%, rgba(245,165,36,0.04) 100%)',
      border: '1px solid var(--firefly-dim)',
      position: 'relative', overflow: 'hidden',
    }}>
      {/* Kapat */}
      <button
        onClick={() => { markSeen(tip.id); setDismissed(true) }}
        style={{
          position: 'absolute', top: 10, right: 12,
          background: 'none', border: 'none', color: 'var(--text-dim)',
          cursor: 'pointer', fontSize: 16, padding: '2px 6px',
        }}
        aria-label="Kapat"
      >
        ✕
      </button>

      {/* Başlık */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 10 }}>
        <span style={{
          fontSize: 11, fontWeight: 700, color: 'var(--firefly)',
          textTransform: 'uppercase', letterSpacing: '0.08em',
        }}>
          💡 Bugün Öğrendin
        </span>
        <span style={{
          fontSize: 10, color: 'var(--text-dim)', marginLeft: 'auto',
        }}>
          {progress}/{total}
        </span>
      </div>

      {/* İçerik */}
      <div style={{ display: 'flex', gap: 12, alignItems: 'flex-start' }}>
        <span style={{
          fontSize: 28, flexShrink: 0,
          filter: 'drop-shadow(0 0 6px rgba(245,165,36,0.3))',
        }}>{tip.emoji}</span>
        <div>
          <p style={{ fontSize: 14, fontWeight: 700, marginBottom: 4 }}>{tip.title}</p>
          <p style={{ fontSize: 13, color: 'var(--text-muted)', lineHeight: 1.65 }}>{tip.body}</p>
        </div>
      </div>

      {/* İlerleme çubuğu */}
      <div style={{
        marginTop: 12, height: 3, background: 'var(--bg)',
        borderRadius: 2, overflow: 'hidden',
      }}>
        <div style={{
          width: `${(progress / total) * 100}%`,
          height: '100%', background: 'var(--firefly)',
          borderRadius: 2, transition: 'width 0.4s ease',
        }} />
      </div>
    </div>
  )
}
