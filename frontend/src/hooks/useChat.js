import { useState, useRef, useEffect } from 'react'
import { useAuth } from '@clerk/clerk-react'
import api, { setAuthToken } from '../utils/api'

export default function useChat() {
  const { getToken } = useAuth()
  const [messages, setMessages] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)
  const abortRef = useRef(null)

  // Attach Clerk token before every API call
  async function ensureAuth() {
    const token = await getToken()
    setAuthToken(token)
  }

  async function sendMessage(text) {
    if (!text.trim()) return

    const userMsg = { role: 'user', content: text }
    const next = [...messages, userMsg]
    setMessages(next)
    setIsLoading(true)
    setError(null)

    try {
      await ensureAuth()
      const res = await api.post('/chat', { messages: next })
      const assistantMsg = { role: 'assistant', content: res.data.reply }
      setMessages([...next, assistantMsg])
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to send message')
    } finally {
      setIsLoading(false)
    }
  }

  function clearChat() {
    setMessages([])
    setError(null)
  }

  return { messages, isLoading, error, sendMessage, clearChat }
}
