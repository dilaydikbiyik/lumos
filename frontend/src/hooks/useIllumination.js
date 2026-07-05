import { useEffect } from 'react'
import { useAuth } from '@clerk/clerk-react'
import api, { setAuthToken } from '../utils/api'

/**
 * Aydınlanan Arayüz — imza özellik: kullanıcının hazırlık (cesaret) skoru
 * arttıkça uygulamanın zemini geceden şafağa yürür. Öğrenmenin ödülü
 * ekranın kendisinde hissedilir.
 *
 * skor 0-24  -> gece (varsayılan)
 * skor 25-49 -> alacakaranlık
 * skor 50-79 -> şafak öncesi
 * skor 80+   -> şafak
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
        // aydınlatma kozmetik — hata durumunda gece temasında kal
      }
    }
    illuminate()
    return () => { cancelled = true }
  }, [isSignedIn, getToken])
}
