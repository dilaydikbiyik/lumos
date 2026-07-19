import { useEffect, useState } from 'react'
import { useAuth } from '@clerk/clerk-react'
import api, { extractErrorMessage, setAuthToken } from '../utils/api'
import { readJSON, writeJSON, removeKey, userKey } from '../utils/storage'

const COMPLETE_MARKER = '[PROFILE_COMPLETE]'

export default function useChat(onProfileComplete) {
  const { getToken, userId } = useAuth()
  // Answering nine questions is real work. Keep the transcript so switching
  // tabs (or an accidental back gesture on mobile) doesn't throw it away.
  const draftKey = userKey('quiz-draft', userId)
  const [messages, setMessages] = useState(() => readJSON(draftKey) || [])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)
  // The finished profile waits here instead of being handed over immediately:
  // the closing message is the last thing the advisor says, and swapping the
  // page out from under it means the user never gets to read it.
  const [pendingProfile, setPendingProfile] = useState(null)
  // Transcript of a finished quiz, kept so extraction can be retried.
  const [finishedAt, setFinishedAt] = useState(null)

  useEffect(() => {
    if (messages.length) writeJSON(draftKey, messages)
  }, [messages, draftKey])

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
        // The quiz is over — remember the transcript so extraction can be
        // retried on its own. Without this, a failed extraction is a dead end:
        // there is no next message for "try again" to resend.
        setFinishedAt(full)
        await extract(full)
      }
    } catch (err) {
      setError(extractErrorMessage(err, 'Mesaj gönderilemedi — tekrar dene'))
    } finally {
      setIsLoading(false)
    }
  }

  // Turn the finished transcript into structured answers. Separate from
  // sendMessage so it can be retried without another chat round trip.
  async function extract(transcript) {
    setError(null)
    try {
      const res = await api.post('/chat/extract-profile', { messages: transcript })
      setPendingProfile(res.data)
    } catch (err) {
      setError(extractErrorMessage(err, 'Cevapların özetlenemedi — tekrar deneyebilirsin.'))
    }
  }

  // Retry after a failed extraction; the answers are still on screen.
  async function retryExtract() {
    if (!finishedAt) return
    setIsLoading(true)
    await extract(finishedAt)
    setIsLoading(false)
  }

  // Hand the finished profile to the parent — driven by the user, not the clock.
  async function confirmProfile() {
    if (!pendingProfile) return
    setError(null)
    // onProfileComplete persists the profile; if that fails the caller keeps
    // the user on the chat, so say so instead of appearing to do nothing.
    const ok = await onProfileComplete(pendingProfile)
    if (ok === false) {
      setError('Profilin kaydedilemedi — tekrar deneyebilirsin, cevapların duruyor.')
      return
    }
    removeKey(draftKey)   // saved for good; the draft has served its purpose
  }

  function clearChat() {
    setMessages([])
    setError(null)
    setPendingProfile(null)
    setFinishedAt(null)
    removeKey(draftKey)
  }

  return {
    messages, isLoading, error, sendMessage, clearChat,
    pendingProfile, confirmProfile, retryExtract, quizFinished: !!finishedAt,
  }
}
