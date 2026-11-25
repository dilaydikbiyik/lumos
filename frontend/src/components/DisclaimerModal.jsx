import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import LanguageSwitcher from './LanguageSwitcher'

export default function DisclaimerModal({ onAccept }) {
  const { t } = useTranslation()
  const [checked, setChecked] = useState(false)

  return (
    <div style={{
      position: 'fixed', inset: 0,
      background: 'rgba(0,0,0,0.75)', backdropFilter: 'blur(6px)',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      zIndex: 1000, padding: 16, overflowY: 'auto',
    }}>
      {/* The card scrolls inside the viewport: on a small phone, or any
          phone held sideways, it was taller than the screen and the
          "Got it" button could not be reached, so the app could not be
          entered at all. */}
      <div className="card"
           style={{ maxWidth: 480, width: '100%', maxHeight: 'calc(100dvh - 32px)', overflowY: 'auto' }}
           role="dialog" aria-modal="true" aria-labelledby="disclaimer-title">
        {/* The modal covers the landing header, so the language picker
            lives here too: nobody should have to agree to a text they
            cannot switch into their own language. */}
        <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: 8 }}>
          <LanguageSwitcher compact />
        </div>
        <h2 id="disclaimer-title" style={{ marginBottom: 12, textAlign: 'center' }}>{t('disclaimerModal.title')}</h2>

        {/* Same legal boundary as before, stated in the other order: what the
            app does first, then its limits. Leading with "only" made the
            product sound like a lesser version of something else. */}
        <p style={{ fontSize: 14, marginBottom: 16, lineHeight: 1.7 }}>
          <strong style={{ color: 'var(--text)' }}>{t('disclaimerModal.does')}</strong>{' '}
          {t('disclaimerModal.doesBody')}<br /><br />
          <strong style={{ color: 'var(--text)' }}>{t('disclaimerModal.doesnt')}</strong>{' '}
          {t('disclaimerModal.doesntBody')}
        </p>

        <div className="disclaimer" style={{ marginBottom: 20 }}>
          {t('disclaimerModal.detail')}
        </div>

        <label style={{ display: 'flex', gap: 10, alignItems: 'flex-start', cursor: 'pointer', marginBottom: 20, fontSize: 14, color: 'var(--text-muted)' }}>
          <input
            type="checkbox"
            checked={checked}
            onChange={e => setChecked(e.target.checked)}
            style={{ marginTop: 2, accentColor: 'var(--accent)', width: 16, height: 16 }}
          />
          {t('disclaimerModal.checkbox')}
        </label>

        {/* The terms this text refers to must be readable before agreeing. */}
        <nav style={{
          display: 'flex', justifyContent: 'center', gap: '0.5rem',
          marginTop: -12, marginBottom: 8, fontSize: 12, flexWrap: 'wrap',
        }}>
          <Link to="/privacy" style={{
            color: 'var(--text-dim)', padding: '14px 12px',
            display: 'inline-flex', alignItems: 'center', minHeight: 44,
          }}>{t('legal.privacy.title')}</Link>
          <Link to="/terms" style={{
            color: 'var(--text-dim)', padding: '14px 12px',
            display: 'inline-flex', alignItems: 'center', minHeight: 44,
          }}>{t('legal.terms.title')}</Link>
        </nav>

        <button
          className="btn btn-primary"
          style={{ width: '100%', justifyContent: 'center' }}
          disabled={!checked}
          onClick={onAccept}
        >
          {t('disclaimerModal.accept')}
        </button>
      </div>
    </div>
  )
}
