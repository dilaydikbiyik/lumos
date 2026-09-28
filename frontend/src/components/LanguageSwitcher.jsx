import { useTranslation } from 'react-i18next'
import { LANGUAGES, setLanguage } from '../i18n'
import HeaderSelect from './HeaderSelect'

/**
 * Language picker — deliberately separate from the market picker.
 *
 * These are two independent choices: an English reader may be investing in
 * Türkiye, and a Turkish reader may be looking at Germany. The language
 * decides the words; the market decides the rules, rates and instruments.
 * They share a styled control and nothing else.
 */
export default function LanguageSwitcher({ compact = false }) {
  const { t, i18n } = useTranslation()

  return (
    <HeaderSelect
      label={t('language.label')}
      value={i18n.language}
      onChange={setLanguage}
      ariaLabel={t('language.label')}
      compact={compact}
    >
      {LANGUAGES.map(l => (
        /* In a header there is room for "EN", not for "English" — the
           options still spell it out once the picker is open. */
        <option key={l.code} value={l.code}>
          {compact ? l.code.toUpperCase() : l.label}
        </option>
      ))}
    </HeaderSelect>
  )
}
