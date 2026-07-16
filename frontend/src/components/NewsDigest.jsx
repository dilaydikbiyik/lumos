import { useEffect, useState } from 'react'
import Icon from './Icon'
import { useAuth } from '@clerk/clerk-react'
import api, { setAuthToken } from '../utils/api'

/**
 * "What happened today?" — at most 3 calm, beginner-friendly news items.
 * Silent on failure: with no news the card simply never appears.
 */
export default function NewsDigest() {
  const { getToken } = useAuth()
  const [items, setItems] = useState(null)
  const [expanded, setExpanded] = useState(null)

  useEffect(() => {
    let cancelled = false
    async function load() {
      try {
        setAuthToken(await getToken())
        const res = await api.get('/news/digest')
        if (!cancelled) setItems(res.data.items)
      } catch {
        if (!cancelled) setItems([])
      }
    }
    load()
    return () => { cancelled = true }
  }, [getToken])

  if (items === null || items.length === 0) return null

  return (
    <div className="card" style={{
      background: 'var(--bg-card)',
      border: '1px solid var(--border)',
      overflow: 'hidden',
    }}>
      {/* Header */}
      <div style={{
        display: 'flex', alignItems: 'center', gap: 8,
        marginBottom: 14,
      }}>
        <span style={{
          fontSize: 18,
          filter: 'drop-shadow(0 0 6px rgba(245,165,36,0.4))',
        }}><Icon name="news" size={18} glow /></span>
        <h3 style={{ fontSize: 14, fontWeight: 700, color: 'var(--text)' }}>
          Bugün Ne Oldu?
        </h3>
        <span style={{
          fontSize: 10, color: 'var(--firefly)', background: 'var(--firefly-dim)',
          padding: '2px 8px', borderRadius: 20, fontWeight: 600,
          marginLeft: 'auto',
        }}>
          {items.length} haber
        </span>
      </div>

      {/* Haber listesi */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 0 }}>
        {items.map((item, i) => {
          const isExpanded = expanded === i
          return (
            <button
              key={i}
              onClick={() => setExpanded(isExpanded ? null : i)}
              style={{
                textAlign: 'left',
                cursor: 'pointer',
                padding: '12px 0',
                borderTop: i > 0 ? '1px solid var(--border)' : 'none',
                background: 'none', border: 'none',
                color: 'var(--text)',
                transition: 'all 0.2s ease',
                width: '100%',
              }}
            >
              {/* Title row */}
              <div style={{
                display: 'flex', alignItems: 'flex-start', gap: 10,
              }}>
                {/* Accent dot */}
                <span style={{
                  width: 6, height: 6, borderRadius: '50%',
                  background: 'var(--firefly)',
                  marginTop: 6, flexShrink: 0,
                  boxShadow: '0 0 8px rgba(245,165,36,0.4)',
                }} />
                <div style={{ flex: 1 }}>
                  <p style={{
                    fontSize: 13.5, fontWeight: 600, lineHeight: 1.45,
                    color: 'var(--text)',
                    marginBottom: isExpanded ? 8 : 0,
                    transition: 'margin 0.2s ease',
                  }}>
                    {item.headline}
                  </p>

                  {/* Expanded detail */}
                  {isExpanded && (
                    <div style={{
                      animation: 'fade-in 0.2s ease',
                    }}>
                      {/* Why it matters */}
                      <p style={{
                        fontSize: 12.5, color: 'var(--text-muted)', lineHeight: 1.6,
                        marginBottom: 8, paddingLeft: 0,
                      }}>
                        {item.why_it_matters}
                      </p>

                      {/* Calming note */}
                      <div style={{
                        fontSize: 12, color: 'var(--firefly)',
                        background: 'var(--firefly-dim)',
                        padding: '8px 12px', borderRadius: 'var(--radius-xs)',
                        lineHeight: 1.55,
                        display: 'flex', alignItems: 'flex-start', gap: 6,
                      }}>
                        <span style={{ flexShrink: 0, fontSize: 14 }}>💡</span>
                        <span style={{ fontStyle: 'italic' }}>{item.calmness_note}</span>
                      </div>
                    </div>
                  )}
                </div>

                {/* Expand chevron */}
                <span style={{
                  fontSize: 12, color: 'var(--text-dim)',
                  transition: 'transform 0.2s ease',
                  transform: isExpanded ? 'rotate(180deg)' : 'rotate(0)',
                  flexShrink: 0, marginTop: 4,
                }}>
                  ▼
                </span>
              </div>
            </button>
          )
        })}
      </div>
    </div>
  )
}
