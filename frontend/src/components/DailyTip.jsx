import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import Icon from './Icon'

/**
 * Daily tip — one concept per session, a 15-second read.
 * Dismissals are stored in localStorage so the same card never returns.
 */

const TIPS = [
  { id: 'etf', emoji: '🧺' },
  { id: 'diversification', emoji: '🥚' },
  { id: 'inflation', emoji: '📉' },
  { id: 'dividend', emoji: '💰' },
  { id: 'reel-return', emoji: '📊' },
  { id: 'liquidity', emoji: '💧' },
  { id: 'drawdown', emoji: '🎢' },
  { id: 'gold', emoji: '🥇' },
  { id: 'patience', emoji: '⏳' },
  { id: 'reit', emoji: '🏢' },
  { id: 'fomo', emoji: '🔥' },
  { id: 'cost-avg', emoji: '📅' },
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
  const { t } = useTranslation()
  // Start at the first unseen tip; tapping the card (or "Sonraki") marks it
  // learned and advances — the card is a mini-carousel, not a one-shot.
  const [idx, setIdx] = useState(() => {
    const seen = getSeenTips()
    const firstUnseen = TIPS.findIndex(t => !seen.includes(t.id))
    return firstUnseen === -1 ? 0 : firstUnseen
  })
  const [dismissed, setDismissed] = useState(false)
  const [, forceRender] = useState(0)

  const tip = TIPS[idx]
  if (!tip || dismissed) return null

  const progress = getSeenTips().length
  const total = TIPS.length

  function advance() {
    markSeen(tip.id)
    setIdx((idx + 1) % TIPS.length)
    forceRender(n => n + 1) // progress counter reads localStorage
  }

  return (
    <div
      className="card"
      onClick={advance}
      role="button"
      aria-label={t('dailyTip.nextLabel')}
      style={{
        background: 'linear-gradient(135deg, var(--bg-card) 0%, rgba(245,165,36,0.04) 100%)',
        border: '1px solid var(--firefly-dim)',
        position: 'relative', overflow: 'hidden', cursor: 'pointer',
      }}
    >
      {/* Kapat */}
      <button
        onClick={(e) => { e.stopPropagation(); markSeen(tip.id); setDismissed(true) }}
        style={{
          position: 'absolute', top: 10, right: 12,
          background: 'none', border: 'none', color: 'var(--text-dim)',
          cursor: 'pointer', fontSize: 16, padding: '2px 6px',
        }}
        aria-label={t('common.close')}
      >
        ✕
      </button>

      {/* Header — right padding keeps the counter clear of the absolutely
          positioned close button, which used to sit on top of it. */}
      <div style={{
        display: 'flex', alignItems: 'center', gap: 8,
        marginBottom: 10, paddingRight: 28,
      }}>
        <span style={{
          fontSize: 11, fontWeight: 700, color: 'var(--firefly)',
          textTransform: 'uppercase', letterSpacing: '0.08em',
        }}>
          <Icon name="bulb" size={13} /> {t('dailyTip.label')}
        </span>
        <span style={{
          fontSize: 10, color: 'var(--text-dim)', marginLeft: 'auto',
          flexShrink: 0,
        }}>
          {progress}/{total}
        </span>
      </div>

      {/* Content */}
      <div style={{ display: 'flex', gap: 12, alignItems: 'flex-start' }}>
        <span style={{
          fontSize: 28, flexShrink: 0,
          filter: 'drop-shadow(0 0 6px rgba(245,165,36,0.3))',
        }}>{tip.emoji}</span>
        <div>
          <p style={{ fontSize: 14, fontWeight: 700, marginBottom: 4 }}>{t(`dailyTip.tips.${tip.id}.title`)}</p>
          <p style={{ fontSize: 13, color: 'var(--text-muted)', lineHeight: 1.65 }}>{t(`dailyTip.tips.${tip.id}.body`)}</p>
        </div>
      </div>

      {/* Progress bar */}
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
      <p style={{ fontSize: 10, color: 'var(--text-dim)', marginTop: 6 }}>
        {t('dailyTip.next')}
      </p>
    </div>
  )
}
