import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { SignedIn, SignedOut, RedirectToSignIn } from '@clerk/clerk-react'
import BottomNav from './components/BottomNav'
import ErrorBoundary from './utils/errorBoundary'
import OnboardingPage from './pages/OnboardingPage'
import ProfilePage from './pages/ProfilePage'
import RecommendPage from './pages/RecommendPage'
import DashboardPage from './pages/DashboardPage'

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
          <Route path="/profile"   element={<ProtectedRoute><ProfilePage /></ProtectedRoute>} />
          <Route path="/recommend" element={<ProtectedRoute><RecommendPage /></ProtectedRoute>} />
          <Route path="/dashboard" element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
          <Route path="*"          element={<Navigate to="/" replace />} />
        </Routes>

        {/* Mobile bottom nav — hidden on desktop via CSS */}
        <BottomNav />
      </BrowserRouter>
    </ErrorBoundary>
  )
}
