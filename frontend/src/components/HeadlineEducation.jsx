/**
 * HeadlineEducation — headline-language training.
 * Micro-education card: "what actually happens when you see a MARKET
 * CRASHES headline?". 4 scenarios in a carousel, views tracked in
 * localStorage.
 */

const SCENARIOS = [
  { id: 'headline-crash' },
  { id: 'headline-crash-global' },
  { id: 'headline-gold' },
  { id: 'headline-dolar' },
]

const STORAGE_KEY = 'lumos-seen-headlines'

function getSeenHeadlines() {
  try { return JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]') } catch { return [] }
}

import { useState } from 'react'
import Icon from './Icon'
import { useTranslation } from 'react-i18next'

function markHeadlineSeen(id) {
  const seen = getSeenHeadlines()
  if (!seen.includes(id)) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify([...seen, id]))
  }
}

export default function HeadlineEducation() {
  const { t } = useTranslation()
  // Tap the card to mark the current headline learned and move to the next —
  // a mini-carousel over the 4 scenarios.
  const [idx, setIdx] = useState(() => {
    const seen = getSeenHeadlines()
    const firstUnseen = SCENARIOS.findIndex(s => !seen.includes(s.id))
    return firstUnseen === -1 ? 0 : firstUnseen
  })
  const [dismissed, setDismissed] = useState(false)
  const [, forceRender] = useState(0)

  const scenario = SCENARIOS[idx]
  if (!scenario || dismissed) return null

  const seen = getSeenHeadlines()

  function advance() {
    markHeadlineSeen(scenario.id)
    setIdx((idx + 1) % SCENARIOS.length)
    forceRender(n => n + 1)
  }

  function dismiss(e) {
    e.stopPropagation()
    markHeadlineSeen(scenario.id)
    setDismissed(true)
  }

  return (
    <div
      className="card"
      onClick={advance}
      role="button"
      aria-label={t('headlines.nextLabel')}
      style={{
        background: 'linear-gradient(135deg, var(--bg-card) 0%, rgba(248,113,113,0.03) 100%)',
        border: '1px solid rgba(248,113,113,0.15)',
        position: 'relative', cursor: 'pointer',
      }}
    >
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
        <Icon name="news" size={12} color="var(--red)" /> {t('headlines.title')}
      </span>

      <p style={{ fontSize: 18, fontWeight: 800, marginBottom: 10 }}>
        {t('headlines.' + scenario.id + '.headline')}
      </p>

      <p style={{ fontSize: 13, color: 'var(--text-muted)', lineHeight: 1.65, marginBottom: 10 }}>
        {t('headlines.' + scenario.id + '.reality')}
      </p>

      <p style={{
        fontSize: 13, fontWeight: 600, lineHeight: 1.5,
        padding: '8px 12px', borderRadius: 'var(--radius-xs)',
        background: 'var(--firefly-dim)', color: 'var(--firefly)',
      }}>
        {t('headlines.' + scenario.id + '.action')}
      </p>

      {/* Progress */}
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
        {t('headlines.progress', { seen: seen.length, total: SCENARIOS.length })}
      </p>
    </div>
  )
}
