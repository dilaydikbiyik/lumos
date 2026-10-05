/**
 * A titled band of a page.
 *
 * Every page was one flat column of equal-weight cards: no headers, no
 * grouping, almost nothing collapsed. A card carrying the page's whole
 * purpose looked exactly like a card carrying a side note, so a reader had
 * to read everything to find out what mattered. That is what "piled up"
 * means — not the volume, the absence of ranking.
 *
 * So a section says what the cards under it are FOR. Explore has three
 * answers in one column — where prices are, whether to buy, and what to do
 * about one specific listing — and nothing was telling them apart.
 *
 * `collapsible` exists for the bands that are support rather than subject.
 * They stay one tap away rather than unrolled, which is what the purchase
 * checklist already did and the only part of the app that read calmly.
 */
import { useState } from 'react'

export default function Section({
  title, subtitle, children, collapsible = false, defaultOpen = true, count,
}) {
  const [open, setOpen] = useState(defaultOpen)
  const body = (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>{children}</div>
  )

  return (
    <section style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
      {collapsible ? (
        <button
          type="button"
          onClick={() => setOpen(!open)}
          aria-expanded={open}
          style={{
            display: 'flex', alignItems: 'baseline', gap: 8, width: '100%',
            background: 'none', border: 'none', padding: 0, cursor: 'pointer',
            color: 'inherit', font: 'inherit', textAlign: 'left',
          }}
        >
          <Heading title={title} subtitle={subtitle} count={count} />
          <span aria-hidden="true" style={{ marginLeft: 'auto', opacity: 0.6, fontSize: 12 }}>
            {open ? '▲' : '▼'}
          </span>
        </button>
      ) : (
        <Heading title={title} subtitle={subtitle} count={count} />
      )}
      {open && body}
    </section>
  )
}

function Heading({ title, subtitle, count }) {
  return (
    <div>
      <h3 style={{
        margin: 0, fontSize: 12, fontWeight: 700, letterSpacing: '0.09em',
        textTransform: 'uppercase', color: 'var(--firefly)',
      }}>
        {title}{count != null && <span style={{ opacity: 0.6 }}> · {count}</span>}
      </h3>
      {subtitle && (
        <p style={{ fontSize: 12.5, opacity: 0.7, margin: '3px 0 0', lineHeight: 1.5 }}>
          {subtitle}
        </p>
      )}
    </div>
  )
}
