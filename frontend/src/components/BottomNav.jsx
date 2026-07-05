import { useEffect, useState } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { SignedIn, useAuth } from '@clerk/clerk-react'
import api, { setAuthToken } from '../utils/api'

/* ── Inline SVG ikonları — hafif, emoji yerine crisp ── */
const icons = {
  explore: (active) => (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke={active ? 'var(--firefly)' : 'var(--text-dim)'} strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="10" />
      <polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76" fill={active ? 'var(--firefly-dim)' : 'none'} />
    </svg>
  ),
  chat: (active) => (
    <svg width="22" height="22" viewBox="0 0 24 24" fill={active ? 'var(--firefly-dim)' : 'none'} stroke={active ? 'var(--firefly)' : 'var(--text-dim)'} strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
    </svg>
  ),
  portfolio: (active) => (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke={active ? 'var(--firefly)' : 'var(--text-dim)'} strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <path d="M18 20V10" /><path d="M12 20V4" /><path d="M6 20v-6" />
    </svg>
  ),
  holdings: (active) => (
    <svg width="22" height="22" viewBox="0 0 24 24" fill={active ? 'var(--firefly-dim)' : 'none'} stroke={active ? 'var(--firefly)' : 'var(--text-dim)'} strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <rect x="2" y="7" width="20" height="14" rx="2" ry="2" />
      <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16" />
    </svg>
  ),
  dashboard: (active) => (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke={active ? 'var(--firefly)' : 'var(--text-dim)'} strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z" fill={active ? 'var(--firefly-dim)' : 'none'} />
    </svg>
  ),
}

const NAV_ITEMS = [
  { path: '/explore',   icon: 'explore',   label: 'Keşfet'    },
  { path: '/profile',   icon: 'chat',      label: 'Profil'    },
  { path: '/recommend', icon: 'portfolio', label: 'Portföy'   },
  { path: '/holdings',  icon: 'holdings',  label: 'Varlıklar' },
  { path: '/dashboard', icon: 'dashboard', label: 'Panel'     },
]

export default function BottomNav() {
  const navigate = useNavigate()
  const { pathname } = useLocation()
  const { getToken, isSignedIn } = useAuth()
  const [investmentPath, setInvestmentPath] = useState(null)

  // Akış 0 sözü: seçilen yola göre modüller uyarlanır — dayatma yok
  useEffect(() => {
    if (!isSignedIn) return
    let cancelled = false
    async function load() {
      try {
        setAuthToken(await getToken())
        const res = await api.get('/users/me')
        if (!cancelled) setInvestmentPath(res.data.investment_path)
      } catch {
        // nav için kritik değil — varsayılan: her şeyi göster
      }
    }
    load()
    return () => { cancelled = true }
  }, [isSignedIn, getToken, pathname])

  const items = NAV_ITEMS.filter(item => {
    if (item.path === '/explore' && investmentPath === 'stocks') return false
    if (item.path === '/recommend' && investmentPath === 'real_estate') return false
    return true
  })

  return (
    <SignedIn>
      <nav className="bottom-nav">
        {items.map(item => {
          const active = pathname === item.path
          return (
            <button
              key={item.path}
              className={`bottom-nav-item${active ? ' active' : ''}`}
              onClick={() => navigate(item.path)}
              aria-label={item.label}
            >
              {icons[item.icon](active)}
              <span>{item.label}</span>
            </button>
          )
        })}
      </nav>
    </SignedIn>
  )
}
