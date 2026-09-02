import { useState, useRef, useEffect } from 'react'
import MessageBubble from './MessageBubble'
import useChat from '../hooks/useChat'
import { useTranslation } from 'react-i18next'

export default function ChatWindow({ onProfileComplete, onFirstMessage }) {
  const { t } = useTranslation()
  const { messages, isLoading, error, sendMessage, pendingProfile, confirmProfile,
          retryExtract, quizFinished } = useChat(onProfileComplete)
  const [input, setInput] = useState('')
  const [revealing, setRevealing] = useState(false)
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
        <MessageBubble role="assistant" content={t('quiz.intro')} />

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

      {/* Once the quiz is done the input bar gives way to an explicit hand-off:
          the user decides when they've finished reading the closing message. */}
      {pendingProfile ? (
        <div style={{ marginTop: 12, paddingTop: 12, borderTop: '1px solid var(--border)' }}>
          <button
            className="btn btn-primary btn-full"
            disabled={revealing}
            onClick={async () => { setRevealing(true); await confirmProfile() }}
          >
            {revealing
              ? <span className="spinner" style={{ width: 18, height: 18 }} />
              : t('quiz.reveal')}
          </button>
          <p style={{ fontSize: 'var(--t-micro)', color: 'var(--text-dim)', textAlign: 'center', marginTop: 8 }}>
            {t('quiz.noRush')}
          </p>
        </div>
      ) : quizFinished ? (
        /* Quiz done but the profile didn't come back — never a dead end:
           the answers are still held, so retrying costs the user nothing. */
        <div style={{ marginTop: 12, paddingTop: 12, borderTop: '1px solid var(--border)' }}>
          <button className="btn btn-primary btn-full" disabled={isLoading} onClick={retryExtract}>
            {isLoading
              ? <span className="spinner" style={{ width: 18, height: 18 }} />
              : t('common.tryAgain')}
          </button>
          <p style={{ fontSize: 'var(--t-micro)', color: 'var(--text-dim)', textAlign: 'center', marginTop: 8 }}>
            {t('quiz.answersKept')}
          </p>
        </div>
      ) : (
      <form
        onSubmit={handleSend}
        style={{ display: 'flex', gap: 8, marginTop: 12, paddingTop: 12, borderTop: '1px solid var(--border)' }}
      >
        <input
          ref={inputRef}
          className="input"
          value={input}
          onChange={e => setInput(e.target.value)}
          placeholder={t('quiz.inputPlaceholder')}
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
      )}
      <p style={{ fontSize: 10, color: 'var(--text-dim)', textAlign: 'center', marginTop: 8 }}>
        {t('common.eduFooter')}
      </p>
    </div>
  )
}
