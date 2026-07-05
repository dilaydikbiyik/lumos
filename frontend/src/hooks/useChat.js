import { useState } from 'react'
import { useAuth } from '@clerk/clerk-react'
import api, { extractErrorMessage, setAuthToken } from '../utils/api'

const COMPLETE_MARKER = '[PROFILE_COMPLETE]'

export default function useChat(onProfileComplete) {
  const { getToken } = useAuth()
  const [messages, setMessages] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)

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
      const rawReply = res.data.reply
      const isComplete = rawReply.includes(COMPLETE_MARKER)
      // Marker is an internal signal — never show it to the user
      const displayReply = rawReply.replace(COMPLETE_MARKER, '').trimEnd()

      const assistantMsg = { role: 'assistant', content: displayReply }
      const full = [...next, assistantMsg]
      setMessages(full)

      if (isComplete && onProfileComplete) {
        // Extract structured answers from the finished conversation
        const extracted = await api.post('/chat/extract-profile', { messages: full })
        await onProfileComplete(extracted.data)
      }
    } catch (err) {
      setError(extractErrorMessage(err, 'Mesaj gönderilemedi — tekrar dene'))
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
