import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
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
      <img src="/logo-icon.svg" alt="" width={40} height={40} className="firefly-mark" />
      <p style={{ marginTop: 14, fontSize: 13, color: 'var(--text-muted)' }}>
        Giriş sayfasına yönlendiriliyorsun…
      </p>
    </div>
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

        {/* Panic Button — crisis-moment support (signed-in only) */}
        <SignedIn><PanicButton /></SignedIn>

        {/* Advisor chat — always-available education Q&A (signed-in only) */}
        <AdvisorChat />

        </MarketProvider>
      </BrowserRouter>
    </ErrorBoundary>
  )
}
