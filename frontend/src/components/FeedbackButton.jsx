import { useState } from 'react'
import { useLocation } from 'react-router-dom'
import api from '../utils/api'
import Icon from '../components/Icon'
import { useTranslation } from 'react-i18next'

// Deliberately plain words: a beginner who is stuck won't self-classify as
// "UX issue" or "feature request", but will recognise "anlamadım".
const CATEGORIES = [
  { id: 'confusing', label: 'feedback.catConfusing' },
  { id: 'bug',       label: 'feedback.catBug' },
  { id: 'idea',      label: 'feedback.catIdea' },
  { id: 'other',     label: 'feedback.catOther' },
]

export default function FeedbackButton() {
  const { t } = useTranslation()
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
        aria-label={t('feedback.openLabel')}
        className="btn btn-ghost"
        style={{
          fontSize: 'var(--t-micro)', color: 'var(--text-dim)',
          display: 'flex', alignItems: 'center', gap: 6, margin: '0 auto',
        }}
      >
        <Icon name="chat" size={13} /> {t('feedback.open')}
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
            {t('feedback.thanks')}
          </p>
        ) : (
          <>
            <h3 style={{ marginBottom: 4 }}>{t('feedback.title')}</h3>
            <p style={{ fontSize: 'var(--t-small)', opacity: 0.8, marginBottom: 12, lineHeight: 1.6 }}>
              {t('feedback.subtitle')}
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
                  {t(c.label)}
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
              placeholder={t('feedback.placeholder')}
              style={{ resize: 'vertical', width: '100%', fontFamily: 'inherit' }}
            />

            {state === 'error' && (
              <p style={{ color: 'var(--red)', fontSize: 13, marginTop: 8 }}>
                {t('feedback.error')}
              </p>
            )}

            <div style={{ display: 'flex', gap: 8, marginTop: 12 }}>
              <button className="btn btn-ghost" style={{ flex: 1 }}
                      onClick={() => { setOpen(false); reset() }}>
                {t('common.cancel')}
              </button>
              <button className="btn btn-primary" style={{ flex: 2 }}
                      onClick={send} disabled={state === 'sending' || !message.trim()}>
                {state === 'sending'
                  ? <span className="spinner" style={{ width: 18, height: 18 }} />
                  : t('common.send')}
              </button>
            </div>
            <p style={{ fontSize: 'var(--t-micro)', color: 'var(--text-dim)', marginTop: 10, lineHeight: 1.5 }}>
              {t('feedback.privacy')}
            </p>
          </>
        )}
      </div>
    </div>
  )
}
