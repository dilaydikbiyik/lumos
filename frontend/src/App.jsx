import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom'
import { useEffect } from 'react'
import { ClerkLoading, SignedIn, SignedOut, RedirectToSignIn, useAuth } from '@clerk/clerk-react'
import AppNav from './components/AppNav'
import PanicButton from './components/PanicButton'
import AdvisorChat from './components/AdvisorChat'
import { MarketProvider } from './contexts/MarketContext'
import ErrorBoundary from './utils/errorBoundary'
import useIllumination from './hooks/useIllumination'
import { registerTokenGetter } from './utils/api'
import OnboardingPage from './pages/OnboardingPage'
import PathSelectionPage from './pages/PathSelectionPage'
import FearCheckInPage from './pages/FearCheckInPage'
import ProfilePage from './pages/ProfilePage'
import HoldingsPage from './pages/HoldingsPage'
import ExplorePage from './pages/ExplorePage'
import RecommendPage from './pages/RecommendPage'
import DashboardPage from './pages/DashboardPage'

function Illumination() {
  useIllumination()
  return null
}

/** React Router keeps the window scroll position across navigations; on
    mobile that makes every new page open "shifted up" mid-content. */
function ScrollToTop() {
  const { pathname } = useLocation()
  useEffect(() => {
    window.scrollTo(0, 0)
  }, [pathname])
  return null
}

/** Registers Clerk's getToken with the axios interceptor so every API
    request carries a fresh token — permanent fix for "Signature has expired". */
function AuthBridge() {
  const { getToken } = useAuth()
  useEffect(() => {
    registerTokenGetter(getToken)
    return () => registerTokenGetter(null)
  }, [getToken])
  return null
}

/** Visible state while Clerk loads and during the sign-in redirect —
    a signed-out visitor on a protected link never sees a black screen. */
function AuthPending() {
  return (
    <div className="page" style={{ alignItems: 'center', justifyContent: 'center', minHeight: '100dvh' }}>
      <img src="/favicon.svg" alt="" width={40} height={40} className="firefly-mark" />
      <p style={{ marginTop: 14, fontSize: 13, color: 'var(--text-muted)' }}>
        Giriş sayfasına yönlendiriliyorsun…
      </p>
    </div>
  )
}

/** Panic + advisor floating buttons. Hidden on /profile: the quiz screen is
    itself a chat, and on small screens the FABs sat on top of its input. */
function FloatingHelpers() {
  const { pathname } = useLocation()
  if (pathname === '/profile') return null
  return (
    <>
      <SignedIn><PanicButton /></SignedIn>
      <AdvisorChat />
    </>
  )
}

function ProtectedRoute({ children }) {
  return (
    <>
      <ClerkLoading><AuthPending /></ClerkLoading>
      <SignedIn>{children}</SignedIn>
      <SignedOut>
        <RedirectToSignIn />
        <AuthPending />
      </SignedOut>
    </>
  )
}

export default function App() {
  return (
    <ErrorBoundary>
      <BrowserRouter>
        {/* Fresh Clerk token per request (interceptor) — must be registered
            BEFORE MarketProvider's fetch */}
        <AuthBridge />
        <ScrollToTop />

        <MarketProvider>
        <Routes>
          <Route path="/"          element={<OnboardingPage />} />
          <Route path="/path"      element={<ProtectedRoute><PathSelectionPage /></ProtectedRoute>} />
          <Route path="/fear-check-in" element={<ProtectedRoute><FearCheckInPage /></ProtectedRoute>} />
          <Route path="/profile"   element={<ProtectedRoute><ProfilePage /></ProtectedRoute>} />
          <Route path="/holdings"  element={<ProtectedRoute><HoldingsPage /></ProtectedRoute>} />
          <Route path="/explore"   element={<ProtectedRoute><ExplorePage /></ProtectedRoute>} />
          <Route path="/recommend" element={<ProtectedRoute><RecommendPage /></ProtectedRoute>} />
          <Route path="/dashboard" element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
          <Route path="*"          element={<Navigate to="/" replace />} />
        </Routes>

        {/* Illuminating UI: the courage score moves the background from night to dawn */}
        <Illumination />

        {/* Responsive nav: bottom bar on mobile, left sidebar on desktop (CSS decides) */}
        <AppNav />

        {/* Floating helpers — hidden on the quiz page, where the user is
            already chatting with Lumos and the FABs cover the input row */}
        <FloatingHelpers />

        </MarketProvider>
      </BrowserRouter>
    </ErrorBoundary>
  )
}
