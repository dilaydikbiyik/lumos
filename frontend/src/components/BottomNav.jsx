import { useNavigate, useLocation } from 'react-router-dom'
import { SignedIn } from '@clerk/clerk-react'

const NAV_ITEMS = [
  { path: '/',          icon: '🏠', label: 'Home'      },
  { path: '/profile',   icon: '💬', label: 'Chat'      },
  { path: '/recommend', icon: '📊', label: 'Portfolio' },
  { path: '/dashboard', icon: '⚡', label: 'Dashboard' },
]

export default function BottomNav() {
  const navigate = useNavigate()
  const { pathname } = useLocation()

  return (
    <SignedIn>
      <nav className="bottom-nav">
        {NAV_ITEMS.map(item => (
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
