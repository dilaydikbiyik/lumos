import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { SignedIn, SignedOut, RedirectToSignIn } from '@clerk/clerk-react'
import BottomNav from './components/BottomNav'
import ErrorBoundary from './utils/errorBoundary'
import useIllumination from './hooks/useIllumination'
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

function ProtectedRoute({ children }) {
  return (
    <>
      <SignedIn>{children}</SignedIn>
      <SignedOut><RedirectToSignIn /></SignedOut>
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

        {/* Aydınlanan Arayüz: cesaret skoru zemini geceden şafağa taşır */}
        <Illumination />

        {/* Mobile bottom nav — hidden on desktop via CSS */}
        <BottomNav />
      </BrowserRouter>
    </ErrorBoundary>
  )
}
