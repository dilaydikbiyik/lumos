import { useTranslation } from 'react-i18next'
import { LANGUAGES, setLanguage } from '../i18n'

/**
 * Language picker — deliberately separate from the market picker.
 *
 * These are two independent choices: an English reader may be investing in
 * Türkiye, and a Turkish reader may be looking at Germany. The language
 * decides the words; the market decides the rules, rates and instruments.
 */
export default function LanguageSwitcher({ compact = false }) {
  const { t, i18n } = useTranslation()

  return (
    <label style={{
      display: 'flex', alignItems: 'center', gap: 8,
      fontSize: compact ? 12 : 13, color: 'var(--text-dim)',
    }}>
      {!compact && <span style={{ fontWeight: 600 }}>{t('language.label')}</span>}
      <select
        value={i18n.language}
        onChange={e => setLanguage(e.target.value)}
        aria-label={t('language.label')}
        style={{
          background: 'var(--bg-input, rgba(255,255,255,0.05))',
          color: 'var(--text)', border: '1px solid var(--border)',
          borderRadius: 'var(--radius-xs, 8px)', padding: '7px 10px',
          fontFamily: 'var(--font)', fontSize: 13, cursor: 'pointer',
          width: compact ? 'auto' : '100%',
        }}
      >
        {LANGUAGES.map(l => (
          <option key={l.code} value={l.code}>{l.label}</option>
        ))}
      </select>
    </label>
  )
}
