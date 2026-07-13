import { useEffect, useState } from 'react'
import { useAuth } from '@clerk/clerk-react'
import api, { setAuthToken } from '../utils/api'

/**
 * Courage Score — the visible face of the vision. No black box: 5
 * transparent milestones, each something the user actually did.
 * The 60% threshold triggers the "ready for real investing" message.
 */
export default function ReadinessScore() {
  const { getToken, isSignedIn } = useAuth()
  const [data, setData] = useState(null)

  useEffect(() => {
    if (!isSignedIn) return
    let cancelled = false
    async function load() {
      try {
        setAuthToken(await getToken())
        const res = await api.get('/users/me/readiness')
        if (!cancelled) setData(res.data)
      } catch {
        // kozmetik — sessizce atla
      }
    }
    load()
    return () => { cancelled = true }
  }, [isSignedIn, getToken])

  if (!data) return null

  const { score, milestones, ready_for_real_investing } = data

  return (
    <div className="card" style={{
      border: ready_for_real_investing ? '1px solid rgba(61,214,140,0.3)' : '1px solid var(--firefly-dim)',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 10 }}>
        <div style={{
          width: 44, height: 44, borderRadius: '50%', flexShrink: 0,
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          background: `conic-gradient(var(--firefly, #F5A524) ${score * 3.6}deg, var(--bg-input) 0deg)`,
        }}>
          <div style={{
            width: 34, height: 34, borderRadius: '50%', background: 'var(--bg-card)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: 12, fontWeight: 700,
          }}>
            {score}
          </div>
        </div>
        <div>
          <strong style={{ fontSize: 14 }}>Cesaret Skoru</strong>
          <p style={{ fontSize: 12, opacity: 0.7, margin: 0 }}>
            {ready_for_real_investing
              ? 'Gerçek yatırıma hazırsın'
              : 'Her adım seni biraz daha hazırlıyor'}
          </p>
        </div>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
        {Object.entries(milestones).map(([label, done]) => (
          <div key={label} style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 13 }}>
            <span style={{
              width: 16, height: 16, borderRadius: '50%', flexShrink: 0,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              background: done ? 'var(--green, #3DD68C)' : 'var(--bg-input)',
              color: done ? '#0C0D14' : 'transparent',
              fontSize: 10, fontWeight: 700,
            }}>
              {done ? '✓' : ''}
            </span>
            <span style={{ opacity: done ? 1 : 0.55 }}>{label}</span>
          </div>
        ))}
      </div>
    </div>
  )
}
