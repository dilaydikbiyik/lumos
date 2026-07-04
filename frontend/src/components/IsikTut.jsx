import { useState } from 'react'
import GLOSSARY from '../data/glossary'

/**
 * "Işık Tut" — jargon tooltip. Wrap any finance term:
 *   <IsikTut term="volatilite" />            → shows the term itself
 *   <IsikTut term="etf">ETF sepeti</IsikTut> → custom display text
 * Tap toggles a plain-language explanation bubble.
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
          color: 'inherit', font: 'inherit',
          borderBottom: '1px dashed var(--accent, #8b8bf5)',
        }}
      >
        {children || term} <span style={{ fontSize: '0.8em' }}>✨</span>
      </button>

      {open && (
        <span
          role="tooltip"
          style={{
            position: 'absolute', bottom: '130%', left: '50%',
            transform: 'translateX(-50%)', zIndex: 30,
            width: 230, padding: '10px 12px', borderRadius: 10,
            background: 'var(--card-bg, #181a26)',
            border: '1px solid var(--accent, #8b8bf5)',
            boxShadow: '0 0 18px rgba(139,139,245,0.25)',
            fontSize: 13, lineHeight: 1.5, textAlign: 'left',
            display: 'block',
          }}
        >
          {explanation}
        </span>
      )}
    </span>
  )
}
