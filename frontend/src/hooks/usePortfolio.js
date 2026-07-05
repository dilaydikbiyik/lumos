import { useState, useCallback } from 'react'
import { useAuth } from '@clerk/clerk-react'
import api, { setAuthToken } from '../utils/api'

export default function usePortfolio() {
  const { getToken } = useAuth()
  const [portfolio, setPortfolio] = useState(null)
  const [profile, setProfile] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)

  async function ensureAuth() {
    const token = await getToken()
    setAuthToken(token)
  }

  // useCallback — DashboardPage'deki useEffect dependency'i için
  const loadProfile = useCallback(async () => {
    try {
      await ensureAuth()
      const res = await api.get('/profile')
      setProfile(res.data)
    } catch {
      setProfile(null)
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [getToken])

  async function recommend(riskScore, budget) {
    setIsLoading(true)
    setError(null)
    try {
      await ensureAuth()
      const res = await api.post('/recommend', {
        risk_score: riskScore,
        budget: budget,
      })
      setPortfolio(res.data)
      return res.data
    } catch (err) {
      setError(err.response?.data?.detail || 'Öneri alınamadı')
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
