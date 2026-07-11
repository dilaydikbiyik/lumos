import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useEffect } from 'react'
import { ClerkLoading, SignedIn, SignedOut, RedirectToSignIn, useAuth } from '@clerk/clerk-react'
import AppNav from './components/AppNav'
import PanicButton from './components/PanicButton'
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

/** Clerk token'ı her API isteğinde taze çekilsin diye interceptor'a kaydeder —
    "Signature has expired" hatasının kalıcı çözümü. */
function AuthBridge() {
  const { getToken } = useAuth()
  useEffect(() => {
    registerTokenGetter(getToken)
    return () => registerTokenGetter(null)
  }, [getToken])
  return null
}

/** Clerk yüklenirken ve yönlendirme sırasında görünür durum —
    korumalı linke oturumsuz gelen kullanıcı asla siyah ekran görmez. */
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

        {/* Her istekte taze Clerk token'ı (interceptor) */}
        <AuthBridge />

        {/* Aydınlanan Arayüz: cesaret skoru zemini geceden şafağa taşır */}
        <Illumination />

        {/* Responsive nav: mobilde alt bar, desktop'ta sol sidebar (CSS seçer) */}
        <AppNav />

        {/* Panik Düğmesi — kriz anı desteği (sadece giriş yapmışken) */}
        <SignedIn><PanicButton /></SignedIn>
      </BrowserRouter>
    </ErrorBoundary>
  )
}
