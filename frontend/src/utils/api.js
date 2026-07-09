import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000',
})

/**
 * Clerk oturum token'ları ~1 dakikada süresi dolar. Token'ı bir kez alıp
 * saklamak "Signature has expired" hatası üretir. Çözüm: AuthBridge
 * (App.jsx) Clerk'in getToken'ını buraya kaydeder; interceptor HER istekte
 * taze token çeker — Clerk kendi içinde cache'leyip otomatik yenilediği
 * için maliyeti yoktur.
 */
let tokenGetter = null

export function registerTokenGetter(fn) {
  tokenGetter = fn
}

api.interceptors.request.use(async (config) => {
  if (tokenGetter) {
    try {
      const token = await tokenGetter()
      if (token) config.headers.Authorization = `Bearer ${token}`
    } catch {
      // token alınamazsa istek yine gitsin — backend 401 ile cevaplar
    }
  }
  return config
})

// Geriye dönük uyumluluk: eski sayfa-yükleme çağrıları zararsız hale geldi
// (interceptor her istekte bunun üzerine taze token yazar).
export function setAuthToken(token) {
  if (token) {
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`
  } else {
    delete api.defaults.headers.common['Authorization']
  }
}

/**
 * FastAPI error 'detail' is a string for our own HTTPExceptions, but
 * Pydantic validation errors (422) return an array of objects — render
 * either safely instead of letting React print "[object Object]".
 */
export function extractErrorMessage(err, fallback) {
  const detail = err?.response?.data?.detail
  if (!detail) return fallback
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) {
    return detail.map(d => d.msg || JSON.stringify(d)).join(', ')
  }
  return fallback
}

export default api
