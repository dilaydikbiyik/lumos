import { useEffect, useRef, useState } from 'react'
import FireflyMark from './FireflyMark'
import useScrollDirection from '../hooks/useScrollDirection'
import Icon from './Icon'
import { SignedIn, useAuth } from '@clerk/clerk-react'
import MessageBubble from './MessageBubble'
import api, { extractErrorMessage, setAuthToken } from '../utils/api'
import { useTranslation } from 'react-i18next'

// Example prompts — shown only as starting points; the input is always free-form.
const SUGGESTION_KEYS = ['sug1', 'sug2', 'sug3', 'sug4', 'sug5', 'sug6']

/**
 * Always-available education advisor. A floating button on every signed-in
 * page opens a chat panel wired to POST /chat/advisor (free-form mode — NOT
 * the risk quiz). The backend injects the user's real profile as context.
 */
function AdvisorPanel({ onClose }) {
  const { t } = useTranslation()
  const { getToken } = useAuth()
  // The greeting is UI chrome, not conversation — flagged so it is never
  // sent to the backend and re-renders in the newly selected language.
  const [messages, setMessages] = useState([{ role: 'assistant', greeting: true }])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const bottomRef = useRef(null)
  const inputRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  async function send(text) {
    const trimmed = (text ?? input).trim()
    if (!trimmed || loading) return
    setInput('')
    setError(null)
    const next = [...messages, { role: 'user', content: trimmed }]
    setMessages(next)
    setLoading(true)
    try {
      setAuthToken(await getToken())
      // Send only the real turns (drop the local greeting) to the backend
      const history = next.filter(m => !m.greeting)
      const res = await api.post('/chat/advisor', { messages: history })
      setMessages([...next, { role: 'assistant', content: res.data.reply }])
    } catch (err) {
      setError(extractErrorMessage(err, t('advisor.error')))
    } finally {
      setLoading(false)
      setTimeout(() => inputRef.current?.focus(), 100)
    }
  }

  return (
    <div className="advisor-overlay" onClick={onClose}>
      <div onClick={e => e.stopPropagation()} className="card advisor-panel">
        {/* Header */}
        <div style={{
          display: 'flex', alignItems: 'center', gap: 8, padding: '14px 16px',
          borderBottom: '1px solid var(--border)',
        }}>
          <FireflyMark size={22} />
          <div style={{ flex: 1 }}>
            <div style={{ fontWeight: 700, fontSize: 15 }}>{t('advisor.title')}</div>
            <div style={{ fontSize: 11, color: 'var(--text-dim)' }}>{t('advisor.subtitle')}</div>
          </div>
          <button onClick={onClose} aria-label={t('common.close')}
            style={{ background: 'none', border: 'none', color: 'var(--text-muted)', fontSize: 22, cursor: 'pointer' }}>
            ×
          </button>
        </div>

        {/* Messages */}
        <div style={{ flex: 1, overflowY: 'auto', padding: 14, display: 'flex', flexDirection: 'column', gap: 10 }}>
          {messages.map((m, i) => <MessageBubble key={i} role={m.role} content={m.greeting ? t('advisor.greeting') : m.content} />)}
          {loading && (
            <div className="bubble-assistant" style={{ opacity: 0.7 }}>
              <span className="light-loader" style={{ width: 14, height: 14, display: 'inline-block' }} /> {t('advisor.typing')}
            </div>
          )}
          {error && <p style={{ color: 'var(--red)', fontSize: 13 }}>{error}</p>}
          {messages.length === 1 && !loading && (
            <div style={{ marginTop: 4 }}>
              <div style={{ fontSize: 11, color: 'var(--text-dim)', marginBottom: 6 }}>
                {t('advisor.suggestionsLabel')}
              </div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                {SUGGESTION_KEYS.map(k => (
                  <button key={k} className="btn btn-ghost" style={{ fontSize: 12 }} onClick={() => send(t('advisor.' + k))}>
                    {t('advisor.' + k)}
                  </button>
                ))}
              </div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        {/* Input */}
        <form onSubmit={e => { e.preventDefault(); send() }}
          className="advisor-input-row">
          <input ref={inputRef} className="input" style={{ flex: 1 }} placeholder={t('advisor.placeholder')}
            value={input} onChange={e => setInput(e.target.value)} enterKeyHint="send" />
          <button className="btn btn-primary" type="submit" disabled={loading} aria-label={t('common.send')}>→</button>
        </form>
        <p style={{ fontSize: 10, color: 'var(--text-dim)', textAlign: 'center', padding: '0 12px 10px' }}>
          {t('common.eduFooter')}
        </p>
      </div>
    </div>
  )
}

export default function AdvisorChat() {
  const { t } = useTranslation()
  const [open, setOpen] = useState(false)
  const tucked = useScrollDirection()
  return (
    <SignedIn>
      {!open && (
        <button
          onClick={() => setOpen(true)}
          aria-label={t('advisor.openLabel')}
          className={`fab fab-advisor ${tucked ? "fab-tucked" : ""}`}
          style={{
            border: 'none',
            background: 'var(--firefly, #F5A524)', color: '#1a1205', fontSize: 24,
            boxShadow: '0 4px 16px rgba(245,165,36,0.45)',
          }}
        >
          <Icon name="chat" size={24} color="#1a1205" />
        </button>
      )}
      {open && <AdvisorPanel onClose={() => setOpen(false)} />}
    </SignedIn>
  )
}
