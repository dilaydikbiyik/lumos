import { useState } from 'react'
import { useTranslation } from 'react-i18next'

export default function DisclaimerModal({ onAccept }) {
  const { t } = useTranslation()
  const [checked, setChecked] = useState(false)

  return (
    <div style={{
      position: 'fixed', inset: 0,
      background: 'rgba(0,0,0,0.75)', backdropFilter: 'blur(6px)',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      zIndex: 1000, padding: 16,
    }}>
      <div className="card" style={{ maxWidth: 480, width: '100%' }}>
        <div style={{ fontSize: 36, marginBottom: 16, textAlign: 'center' }}></div>
        <h2 style={{ marginBottom: 12, textAlign: 'center' }}>{t('disclaimerModal.title')}</h2>

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
