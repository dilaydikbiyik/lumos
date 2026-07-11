import { useState } from 'react'
import GLOSSARY from '../data/glossary'

/**
 * "Işık Tut" (hold a light) — firefly-themed jargon tooltip.
 *   <IsikTut term="volatilite" />            → renders the term itself
 *   <IsikTut term="etf">ETF sepeti</IsikTut> → custom display text
 * Tap/click opens a plain-language explanation bubble.
 */
export default function IsikTut({ term, children }) {
  const [open, setOpen] = useState(false)
  const explanation = GLOSSARY[term.toLowerCase()]

  if (!explanation) return children || term

  return (
    <span style={{ position: 'relative', display: 'inline-block' }}>
      <button
        type="button"
        onClick={() => setOpen(!open)}
        aria-expanded={open}
        style={{
          background: 'none', border: 'none', padding: 0, cursor: 'pointer',
          color: 'var(--firefly)', font: 'inherit', fontWeight: 500,
          borderBottom: '1px dashed var(--firefly-dim)',
          transition: 'all 0.2s ease',
        }}
      >
        {children || term}
        <span style={{
          fontSize: '0.75em', marginLeft: 2,
          filter: open ? 'drop-shadow(0 0 6px var(--firefly))' : 'none',
          transition: 'filter 0.3s ease',
        }}>💡</span>
      </button>

      {open && (
        <>
          {/* Tiny light-burst animation */}
          <span style={{
            position: 'absolute', bottom: '120%', left: '50%',
            width: 60, height: 60, borderRadius: '50%',
            background: 'radial-gradient(circle, rgba(245,165,36,0.3) 0%, transparent 70%)',
            transform: 'translate(-50%, 50%)',
            animation: 'pulse 1s ease-out forwards',
            pointerEvents: 'none',
          }} />

          {/* Explanation bubble */}
          <span
            role="tooltip"
            style={{
              position: 'absolute', bottom: '130%', left: '50%',
              transform: 'translateX(-50%)', zIndex: 30,
              width: 260, padding: '12px 14px', borderRadius: 'var(--radius-sm)',
              background: 'var(--bg-card)',
              border: '1px solid var(--firefly-dim)',
              boxShadow: '0 4px 24px rgba(0,0,0,0.4), 0 0 16px rgba(245,165,36,0.15)',
              fontSize: 13, lineHeight: 1.6, textAlign: 'left',
              display: 'block', color: 'var(--text)',
              animation: 'fade-in 0.2s ease',
            }}
          >
            {/* Title */}
            <span style={{
              display: 'flex', alignItems: 'center', gap: 6,
              marginBottom: 6, fontSize: 11, fontWeight: 700,
              color: 'var(--firefly)', textTransform: 'uppercase',
              letterSpacing: '0.05em',
            }}>
              💡 Işık Tut
            </span>

            {explanation}

            {/* Pointer (triangle) */}
            <span style={{
              position: 'absolute', bottom: -6, left: '50%',
              transform: 'translateX(-50%)',
              width: 0, height: 0,
              borderLeft: '6px solid transparent',
              borderRight: '6px solid transparent',
              borderTop: '6px solid var(--firefly-dim)',
            }} />
          </span>
        </>
      )}
    </span>
  )
}
