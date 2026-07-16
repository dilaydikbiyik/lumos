import { useState, useCallback } from 'react'
import { useAuth } from '@clerk/clerk-react'
import api, { setAuthToken } from '../utils/api'

// The recommendation is deterministic for a given (risk, budget) — cache it
// per user so revisiting the portfolio page renders instantly instead of
// showing a "hazırlanıyor" screen; a background refresh keeps it current.
export function readCachedPortfolio(userId) {
  try {
    const raw = localStorage.getItem(`lumos-portfolio-${userId}`)
    return raw ? JSON.parse(raw) : null
  } catch {
    return null
  }
}

function cachePortfolio(userId, data) {
  try {
    localStorage.setItem(`lumos-portfolio-${userId}`, JSON.stringify(data))
  } catch { /* storage full/blocked — cache is best-effort */ }
}

export default function usePortfolio() {
  const { getToken, userId } = useAuth()
  const [portfolio, setPortfolio] = useState(() => readCachedPortfolio(userId))
  const [profile, setProfile] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)

  async function ensureAuth() {
    const token = await getToken()
    setAuthToken(token)
  }

  // useCallback — needed as a useEffect dependency in DashboardPage.
  // Return contract: profile object = saved profile exists; null = server
  // DEFINITIVELY says there is none; undefined = transient error (network,
  // cold start) — callers must not treat an error as "no profile".
  const loadProfile = useCallback(async () => {
    try {
      await ensureAuth()
      const res = await api.get('/profile')
      setProfile(res.data)
      return res.data ?? null
    } catch {
      return undefined
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [getToken])

  async function recommend(riskScore, budget) {
    // Instant render from cache; the fresh copy replaces it silently below.
    const cached = readCachedPortfolio(userId)
    const hasCache = cached && cached.risk_score === riskScore && cached.budget === budget
    if (hasCache) setPortfolio(cached)
    setIsLoading(!hasCache)
    setError(null)
    try {
      await ensureAuth()
      const res = await api.post('/recommend', {
        risk_score: riskScore,
        budget: budget,
      })
      // Identical refresh must not re-render the page (it restarts the pie
      // animation and re-mounts every card — visible jank on phones).
      if (!hasCache || JSON.stringify(res.data) !== JSON.stringify(cached)) {
        setPortfolio(res.data)
        cachePortfolio(userId, res.data)
      }
      return res.data
    } catch (err) {
      // With a cached portfolio on screen, a transient refresh failure is
      // not worth an error banner.
      if (!hasCache) setError(err.response?.data?.detail || 'Öneri alınamadı')
    } finally {
      setIsLoading(false)
    }
  }

  async function saveProfile(answers) {
    setIsLoading(true)
    setError(null)
    try {
      await ensureAuth()
      const res = await api.post('/profile', answers)
      setProfile(res.data)
      return res.data
    } catch (err) {
      setError(err.response?.data?.detail || 'Profil kaydedilemedi')
    } finally {
      setIsLoading(false)
    }
  }

  return { portfolio, profile, isLoading, error, loadProfile, recommend, saveProfile }
}
