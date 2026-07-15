import { useState, useRef, useEffect } from 'react'
import MessageBubble from './MessageBubble'
import useChat from '../hooks/useChat'

const INTRO = "Merhaba! Ben Lumos.\n\nSana 9 kısa soru soracağım ve kişisel risk profilini oluşturacağım. Hazır mısın?\n\n**1️⃣ Başlayalım: Yatırıma ayırabileceğin bütçen nedir?** (Örn: 50.000 TL)"

export default function ChatWindow({ onProfileComplete, onFirstMessage }) {
  const { messages, isLoading, error, sendMessage } = useChat(onProfileComplete)
  const [input, setInput] = useState('')
  const bottomRef = useRef(null)
  const inputRef = useRef(null)
  const startedRef = useRef(false)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isLoading])

  async function handleSend(e) {
    e.preventDefault()
    if (!input.trim() || isLoading) return
    if (!startedRef.current) {
      // Lets the parent know the quiz is genuinely in progress (e.g. so a
      // late-arriving stored profile doesn't yank the user to the reveal).
      startedRef.current = true
      onFirstMessage?.()
    }
    const text = input
    setInput('')
    await sendMessage(text)
    // Keep keyboard open on mobile
    setTimeout(() => inputRef.current?.focus(), 100)
  }

  return (
    <div className="card" style={{ display: 'flex', flexDirection: 'column', height: 'calc(100dvh - 220px)', minHeight: 360 }}>
      {/* Messages */}
      <div style={{
        flex: 1, overflowY: 'auto',
        display: 'flex', flexDirection: 'column', gap: 10,
        paddingBottom: 8,
        /* smooth momentum scroll on iOS */
        WebkitOverflowScrolling: 'touch',
      }}>
        <div className="bubble-assistant" style={{ whiteSpace: 'pre-line' }}>{INTRO}</div>

        {messages.map((msg, i) => (
          <MessageBubble key={i} role={msg.role} content={msg.content} />
        ))}

        {isLoading && (
          <div className="bubble-assistant" style={{ display: 'flex', gap: 4, alignItems: 'center', padding: '14px 16px' }}>
            <span className="typing-dot" /><span className="typing-dot" /><span className="typing-dot" />
          </div>
        )}

        {error && <p style={{ color: 'var(--red)', fontSize: 13, alignSelf: 'center' }}>{error}</p>}
        <div ref={bottomRef} />
      </div>

      {/* Input bar */}
      <form
        onSubmit={handleSend}
        style={{ display: 'flex', gap: 8, marginTop: 12, paddingTop: 12, borderTop: '1px solid var(--border)' }}
      >
        <input
          ref={inputRef}
          className="input"
          value={input}
          onChange={e => setInput(e.target.value)}
          placeholder="Cevabını yaz…"
          disabled={isLoading}
          autoComplete="off"
          enterKeyHint="send"
        />
        <button
          className="btn btn-primary"
          type="submit"
          disabled={isLoading || !input.trim()}
          style={{ padding: '0 18px', flexShrink: 0 }}
          aria-label="Send"
        >
          {isLoading ? <span className="spinner" style={{ width: 18, height: 18 }} /> : '→'}
        </button>
      </form>
    </div>
  )
}
