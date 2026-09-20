import { useTranslation } from 'react-i18next'
import { Link, useLocation } from 'react-router-dom'
import LanguageSwitcher from '../components/LanguageSwitcher'
import LumosLogo from '../components/LumosLogo'

/**
 * Privacy policy and terms of use.
 *
 * Deliberately PUBLIC — no ProtectedRoute. Both stores check these URLs from
 * a signed-out crawler during review, and a policy you have to log in to read
 * is not a published policy. It is also the page someone reaches for when
 * they are deciding whether to sign up at all.
 *
 * The copy lives in the locale files rather than here, because a privacy
 * policy a Turkish reader cannot read is not a disclosure to them.
 */
export default function LegalPage({ doc }) {
  const { t } = useTranslation()
  const { pathname } = useLocation()
  const key = doc || (pathname.includes('terms') ? 'terms' : 'privacy')
  const sections = t(`legal.${key}.sections`, { returnObjects: true })
  const other = key === 'privacy' ? 'terms' : 'privacy'

  return (
    <div style={{ maxWidth: 760, margin: '0 auto', padding: '1.5rem 1rem 5rem' }}>
      <header style={{
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        gap: '1rem', flexWrap: 'wrap', marginBottom: '2rem',
      }}>
        <Link to="/" style={{ textDecoration: 'none' }}><LumosLogo /></Link>
        <LanguageSwitcher />
      </header>

      <h1 style={{ marginBottom: '0.35rem' }}>{t(`legal.${key}.title`)}</h1>
      <p style={{ opacity: 0.7, fontSize: '0.9rem', marginTop: 0 }}>
        {t('legal.updated', { date: t('legal.updatedDate') })}
      </p>

      {Array.isArray(sections) && sections.map((section, i) => (
        <section key={i} style={{ marginTop: '1.75rem' }}>
          <h2 style={{ fontSize: '1.1rem', marginBottom: '0.5rem' }}>{section.h}</h2>
          <p style={{ lineHeight: 1.7, margin: 0, whiteSpace: 'pre-line' }}>{section.p}</p>
        </section>
      ))}

      <p style={{ marginTop: '2.5rem', fontSize: '0.9rem', opacity: 0.85 }}>
        {t('legal.contact')}
      </p>

      <nav style={{ marginTop: '2rem', display: 'flex', gap: '1.25rem', flexWrap: 'wrap' }}>
        <Link to={`/${other}`}>{t(`legal.${other}.title`)}</Link>
        <Link to="/">{t('legal.backHome')}</Link>
      </nav>
    </div>
  )
}
