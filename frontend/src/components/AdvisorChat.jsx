import { useEffect, useRef, useState } from 'react'
import { SignedIn, useAuth } from '@clerk/clerk-react'
import MessageBubble from './MessageBubble'
import api, { extractErrorMessage, setAuthToken } from '../utils/api'

const GREETING = {
  role: 'assistant',
  content:
    'Merhaba, ben Lumos 🪰\n\nAklına takılan her şeyi sorabilirsin — "ETF nedir?", ' +
    '"altın neden portföyümde?", "risk skorum ne anlama geliyor?", "ya düşerse?" gibi. ' +
    'Jargon yok, baskı yok.',
}

const SUGGESTIONS = [
  'ETF nedir?',
  'Risk skorum ne anlama geliyor?',
  'Şimdi almak için doğru zaman mı?',
  'Piyasa düşerse ne yapmalıyım?',
]

/**
 * Always-available education advisor. A floating button on every signed-in
 * page opens a chat panel wired to POST /chat/advisor (free-form mode — NOT
 * the risk quiz). The backend injects the user's real profile as context.
 */
function AdvisorPanel({ onClose }) {
  const { getToken } = useAuth()
  const [messages, setMessages] = useState([GREETING])
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
      const history = next.filter(m => m !== GREETING)
      const res = await api.post('/chat/advisor', { messages: history })
      setMessages([...next, { role: 'assistant', content: res.data.reply }])
    } catch (err) {
      setError(extractErrorMessage(err, 'Şu an cevap veremedim — birazdan tekrar dene.'))
    } finally {
      setLoading(false)
      setTimeout(() => inputRef.current?.focus(), 100)
    }
  }

  return (
    <div
      style={{
        position: 'fixed', inset: 0, zIndex: 60,
        display: 'flex', alignItems: 'flex-end', justifyContent: 'flex-end',
        background: 'rgba(0,0,0,0.45)', backdropFilter: 'blur(4px)',
      }}
      onClick={onClose}
    >
      <div
        onClick={e => e.stopPropagation()}
        className="card"
        style={{
          margin: 14, width: 'min(420px, calc(100vw - 28px))',
          height: 'min(620px, calc(100dvh - 28px))',
          display: 'flex', flexDirection: 'column', padding: 0, overflow: 'hidden',
        }}
      >
        {/* Header */}
        <div style={{
          display: 'flex', alignItems: 'center', gap: 8, padding: '14px 16px',
          borderBottom: '1px solid var(--border)',
        }}>
          <span style={{ fontSize: 20 }}>🪰</span>
          <div style={{ flex: 1 }}>
            <div style={{ fontWeight: 700, fontSize: 15 }}>Lumos Danışman</div>
            <div style={{ fontSize: 11, color: 'var(--text-dim)' }}>Sorularını yanıtlar — tavsiye değil, eğitim</div>
          </div>
          <button onClick={onClose} aria-label="Kapat"
            style={{ background: 'none', border: 'none', color: 'var(--text-muted)', fontSize: 22, cursor: 'pointer' }}>
            ×
          </button>
        </div>

        {/* Messages */}
        <div style={{ flex: 1, overflowY: 'auto', padding: 14, display: 'flex', flexDirection: 'column', gap: 10 }}>
          {messages.map((m, i) => <MessageBubble key={i} role={m.role} content={m.content} />)}
          {loading && (
            <div className="bubble-assistant" style={{ opacity: 0.7 }}>
              <span className="light-loader" style={{ width: 14, height: 14, display: 'inline-block' }} /> yazıyor…
            </div>
          )}
          {error && <p style={{ color: 'var(--red)', fontSize: 13 }}>{error}</p>}
          {messages.length === 1 && !loading && (
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginTop: 4 }}>
              {SUGGESTIONS.map(s => (
                <button key={s} className="btn btn-ghost" style={{ fontSize: 12 }} onClick={() => send(s)}>
                  {s}
                </button>
              ))}
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        {/* Input */}
        <form onSubmit={e => { e.preventDefault(); send() }}
          style={{ display: 'flex', gap: 8, padding: 12, borderTop: '1px solid var(--border)' }}>
          <input ref={inputRef} className="input" style={{ flex: 1 }} placeholder="Bir şey sor…"
            value={input} onChange={e => setInput(e.target.value)} enterKeyHint="send" />
          <button className="btn btn-primary" type="submit" disabled={loading} aria-label="Gönder">→</button>
        </form>
      </div>
    </div>
  )
}

export default function AdvisorChat() {
  const [open, setOpen] = useState(false)
  return (
    <SignedIn>
      {!open && (
        <button
          onClick={() => setOpen(true)}
          aria-label="Danışmana sor"
          style={{
            // Stacked above the Panic button (right:14, bottom:76) so neither
            // collides with the desktop left sidebar.
            position: 'fixed', right: 14, bottom: 140, zIndex: 40,
            width: 52, height: 52, borderRadius: '50%', border: 'none', cursor: 'pointer',
            background: 'var(--firefly, #F5A524)', color: '#1a1205', fontSize: 24,
            boxShadow: '0 4px 16px rgba(245,165,36,0.45)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}
        >
          💬
        </button>
      )}
      {open && <AdvisorPanel onClose={() => setOpen(false)} />}
    </SignedIn>
  )
}
