import { useEffect, useState } from 'react'
import { useAuth } from '@clerk/clerk-react'
import api, { setAuthToken } from '../utils/api'

/**
 * "Bugün Ne Oldu?" — at most 3 calm, beginner-framed news items.
 * Silent on failure: news is a nice-to-have, never a blocking error.
 */
export default function NewsDigest() {
  const { getToken } = useAuth()
  const [items, setItems] = useState(null)

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
    <div className="card">
      <h3 style={{ marginBottom: 10 }}>📰 Bugün Ne Oldu?</h3>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
        {items.map((item, i) => (
          <div key={i} style={{ paddingBottom: i < items.length - 1 ? 12 : 0, borderBottom: i < items.length - 1 ? '1px solid var(--border)' : 'none' }}>
            <p style={{ fontSize: 14, fontWeight: 600, marginBottom: 4 }}>{item.headline}</p>
            <p style={{ fontSize: 13, opacity: 0.8, marginBottom: 4 }}>{item.why_it_matters}</p>
            <p style={{ fontSize: 12, opacity: 0.6, fontStyle: 'italic' }}>{item.calmness_note}</p>
          </div>
        ))}
      </div>
    </div>
  )
}
