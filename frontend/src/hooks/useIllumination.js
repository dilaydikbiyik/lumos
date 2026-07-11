import { useEffect } from 'react'
import { useAuth } from '@clerk/clerk-react'
import api, { setAuthToken } from '../utils/api'

/**
 * Illuminating UI — signature feature: as the user's readiness (courage)
 * score grows, the app background walks from night to dawn. The reward
 * for learning is felt on the screen itself.
 *
 * score 0-24  -> night (default)
 * score 25-49 -> dusk
 * score 50-79 -> pre-dawn
 * score 80+   -> dawn
 */
export default function useIllumination() {
  const { getToken, isSignedIn } = useAuth()

  useEffect(() => {
    if (!isSignedIn) return
    let cancelled = false

    async function illuminate() {
      try {
        setAuthToken(await getToken())
        const res = await api.get('/users/me/readiness')
        if (cancelled) return
        const score = res.data.score ?? 0
        const stage = score >= 80 ? 3 : score >= 50 ? 2 : score >= 25 ? 1 : 0
        document.body.classList.remove('illumination-1', 'illumination-2', 'illumination-3')
        if (stage > 0) document.body.classList.add(`illumination-${stage}`)
      } catch {
        // illumination is cosmetic — stay on the night theme on failure
      }
    }
    illuminate()
    return () => { cancelled = true }
  }, [isSignedIn, getToken])
}
