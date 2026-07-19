import { useState } from 'react'
import { useLocation } from 'react-router-dom'
import api from '../utils/api'
import Icon from '../components/Icon'

// Deliberately plain words: a beginner who is stuck won't self-classify as
// "UX issue" or "feature request", but will recognise "anlamadım".
const CATEGORIES = [
  { id: 'confusing', label: 'Anlamadım' },
  { id: 'bug',       label: 'Bir şey bozuk' },
  { id: 'idea',      label: 'Önerim var' },
  { id: 'other',     label: 'Başka' },
]

export default function FeedbackButton() {
  const { pathname } = useLocation()
  const [open, setOpen] = useState(false)
  const [category, setCategory] = useState(null)
  const [message, setMessage] = useState('')
  const [state, setState] = useState('idle')   // idle | sending | sent | error

  async function send() {
    if (!message.trim()) return
    setState('sending')
    try {
      await api.post('/feedback', { message, category, page: pathname })
      setState('sent')
      setTimeout(() => { setOpen(false); reset() }, 1600)
    } catch {
      setState('error')
    }
  }

  function reset() {
    setMessage(''); setCategory(null); setState('idle')
  }

  if (!open) {
    return (
      <button
        onClick={() => setOpen(true)}
        aria-label="Geri bildirim gönder"
        className="btn btn-ghost"
        style={{
          fontSize: 'var(--t-micro)', color: 'var(--text-dim)',
          display: 'flex', alignItems: 'center', gap: 6, margin: '0 auto',
        }}
      >
        <Icon name="chat" size={13} /> Buna dair bir şey söyle
      </button>
    )
  }

  return (
    <div style={{
      position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.6)',
      display: 'flex', alignItems: 'flex-end', justifyContent: 'center',
      zIndex: 1000, padding: 16,
    }}
      onClick={e => { if (e.target === e.currentTarget) { setOpen(false); reset() } }}
    >
      {/* Bottom sheet: most users are on a phone, and a thumb reaches the
          bottom of the screen far more easily than a centred dialog. */}
      <div className="card" style={{ maxWidth: 460, width: '100%', marginBottom: 'env(safe-area-inset-bottom)' }}>
        {state === 'sent' ? (
          <p style={{ fontSize: 14, textAlign: 'center', padding: '18px 0', lineHeight: 1.6 }}>
            Aldım, teşekkürler. Gerçekten okuyorum.
          </p>
        ) : (
          <>
            <h3 style={{ marginBottom: 4 }}>Ne oldu?</h3>
            <p style={{ fontSize: 'var(--t-small)', opacity: 0.8, marginBottom: 12, lineHeight: 1.6 }}>
              Anlamadığın, saçma bulduğun ya da bozuk olan her şeyi yaz. Kısa olabilir.
            </p>

            <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', marginBottom: 10 }}>
              {CATEGORIES.map(c => (
                <button
                  key={c.id}
                  onClick={() => setCategory(category === c.id ? null : c.id)}
                  className="btn btn-ghost"
                  style={{
                    fontSize: 'var(--t-micro)', padding: '5px 12px',
                    background: category === c.id ? 'var(--firefly-dim)' : 'transparent',
                    color: category === c.id ? 'var(--firefly)' : 'var(--text-dim)',
                  }}
                >
                  {c.label}
                </button>
              ))}
            </div>

            <textarea
              className="input"
              rows={4}
              autoFocus
              value={message}
              onChange={e => setMessage(e.target.value)}
              maxLength={2000}
              placeholder="Örn: risk skorunun nasıl çıktığını anlamadım"
              style={{ resize: 'vertical', width: '100%', fontFamily: 'inherit' }}
            />

            {state === 'error' && (
              <p style={{ color: 'var(--red)', fontSize: 13, marginTop: 8 }}>
                Gönderilemedi — tekrar deneyebilirsin.
              </p>
            )}

            <div style={{ display: 'flex', gap: 8, marginTop: 12 }}>
              <button className="btn btn-ghost" style={{ flex: 1 }}
                      onClick={() => { setOpen(false); reset() }}>
                Vazgeç
              </button>
              <button className="btn btn-primary" style={{ flex: 2 }}
                      onClick={send} disabled={state === 'sending' || !message.trim()}>
                {state === 'sending'
                  ? <span className="spinner" style={{ width: 18, height: 18 }} />
                  : 'Gönder'}
              </button>
            </div>
            <p style={{ fontSize: 'var(--t-micro)', color: 'var(--text-dim)', marginTop: 10, lineHeight: 1.5 }}>
              Hangi ekranda olduğun otomatik eklenir. Başka hiçbir şey toplanmaz.
            </p>
          </>
        )}
      </div>
    </div>
  )
}
