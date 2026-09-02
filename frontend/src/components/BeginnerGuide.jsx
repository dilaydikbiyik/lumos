import { useState } from 'react'
import { useTranslation } from 'react-i18next'

/**
 * BeginnerGuide — the guided first-investment journey.
 * Turkey-specific, step-by-step brokerage walkthrough.
 * Static content — no LLM dependency, always available.
 */

const STEPS = [
  { id: 1, emoji: '🏦' },
  { id: 2, emoji: '📋' },
  { id: 3, emoji: '💳' },
  { id: 4, emoji: '🛒' },
  { id: 5, emoji: '📊' },
]

export default function BeginnerGuide({ defaultExpanded = false }) {
  const { t } = useTranslation()
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
            {t('guide.title')}
          </p>
          <p style={{ fontSize: 11, color: 'var(--text-dim)', marginTop: 2 }}>
            {t('guide.subtitle')}
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
              {STEPS[activeStep].emoji} {t(`guide.steps.${STEPS[activeStep].id}.title`)}
            </p>
            <p style={{
              fontSize: 13, color: 'var(--text-muted)',
              lineHeight: 1.7, whiteSpace: 'pre-line', marginBottom: 12,
            }}>
              {t(`guide.steps.${STEPS[activeStep].id}.body`)}
            </p>
            <div style={{
              fontSize: 12, lineHeight: 1.6, padding: '8px 12px',
              background: 'var(--firefly-dim)', borderRadius: 'var(--radius-xs)',
              color: 'var(--text)',
            }}>
              {t(`guide.steps.${STEPS[activeStep].id}.tip`)}
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
              {t('guide.prev')}
            </button>
            <button
              className="btn btn-ghost"
              style={{ flex: 1, fontSize: 12 }}
              disabled={activeStep === STEPS.length - 1}
              onClick={() => setActiveStep(s => s + 1)}
            >
              {t('guide.next')}
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
