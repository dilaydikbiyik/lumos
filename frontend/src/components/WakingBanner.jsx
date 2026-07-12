import { useEffect, useState } from 'react'

/**
 * Honest cold-start banner. api.js retries requests while Render's free
 * instance wakes up and broadcasts 'lumos:waking' / 'lumos:awake' window
 * events — this banner turns that into a calm message instead of letting
 * the user stare at a spinner (or worse, an error).
 */
export default function WakingBanner() {
  const [waking, setWaking] = useState(false)

  useEffect(() => {
    const onWaking = () => setWaking(true)
    const onAwake = () => setWaking(false)
    window.addEventListener('lumos:waking', onWaking)
    window.addEventListener('lumos:awake', onAwake)
    return () => {
      window.removeEventListener('lumos:waking', onWaking)
      window.removeEventListener('lumos:awake', onAwake)
    }
  }, [])

  if (!waking) return null

  return (
    <div
      role="status"
      style={{
        position: 'fixed', top: 0, left: 0, right: 0, zIndex: 2000,
        display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8,
        padding: '9px 16px', fontSize: 13, fontWeight: 600,
        background: 'rgba(245,165,36,0.14)', color: 'var(--firefly, #F5A524)',
        borderBottom: '1px solid rgba(245,165,36,0.3)',
        backdropFilter: 'blur(12px)', WebkitBackdropFilter: 'blur(12px)',
      }}
    >
      <span className="light-loader" style={{ width: 14, height: 14, flexShrink: 0 }} />
      Sunucu uyandırılıyor — ilk istek ~30 sn sürebilir, isteğin otomatik tekrarlanacak 🪰
    </div>
  )
}
