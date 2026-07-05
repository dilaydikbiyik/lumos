import { useEffect, useState } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { SignedIn, useAuth } from '@clerk/clerk-react'
import api, { setAuthToken } from '../utils/api'

const NAV_ITEMS = [
  { path: '/explore',   icon: '🏘️', label: 'Keşfet'    },
  { path: '/profile',   icon: '💬', label: 'Chat'      },
  { path: '/recommend', icon: '📊', label: 'Portfolio' },
  { path: '/holdings',  icon: '💰', label: 'Varlıklar' },
  { path: '/dashboard', icon: '⚡', label: 'Dashboard' },
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
        {items.map(item => (
          <button
            key={item.path}
            className={`bottom-nav-item${pathname === item.path ? ' active' : ''}`}
            onClick={() => navigate(item.path)}
            aria-label={item.label}
          >
            <span style={{ fontSize: 20 }}>{item.icon}</span>
            <span>{item.label}</span>
          </button>
        ))}
      </nav>
    </SignedIn>
  )
}
