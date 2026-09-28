import { Component } from 'react'
import i18n from 'i18next'
import api from './api'

/**
 * The screen a reader sees when the app breaks, and the only place a crash
 * gets recorded.
 *
 * Two things were wrong with the previous version. It logged to the console
 * and nowhere else, so a crash in somebody's browser left no trace at all —
 * the backend has had Sentry wired for a while, the frontend never did, and
 * "set SENTRY_DSN on Vercel" would have been a no-op that looked like
 * coverage. And the fallback was hardcoded English on hardcoded light colours,
 * so a Turkish or German reader met a screen in the wrong language and the
 * wrong theme at the exact moment they most needed to trust the thing.
 *
 * Reported THROUGH the backend rather than by adding a Sentry SDK here: the
 * bundle is already large, the backend is already instrumented, and a crash
 * report then goes to an origin this app controls rather than to a third
 * party straight from the reader's browser.
 *
 * Translations are read from `i18n` directly rather than through a hook,
 * because a class component cannot use one — and this component has to work
 * when everything around it has already failed, so it also survives i18n
 * itself being the thing that broke.
 */
const FALLBACK = {
  tr: { title: 'Bir şeyler ters gitti', home: 'Ana sayfaya dön' },
  en: { title: 'Something went wrong', home: 'Go home' },
  de: { title: 'Etwas ist schiefgelaufen', home: 'Zur Startseite' },
}

export default class ErrorBoundary extends Component {
  constructor(props) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error }
  }

  componentDidCatch(error, info) {
    console.error('ErrorBoundary caught:', error, info)
    // Never let reporting a crash cause one: the reader is already looking
    // at a broken screen, and a throw in here would replace it with the
    // browser's own blank page.
    try {
      api.post('/client-errors', {
        message: String(error?.message || error).slice(0, 500),
        stack: String(error?.stack || '').slice(0, 4000),
        // Path only. The query string can carry identifiers, and a crash
        // report does not need them to be actionable.
        path: window.location?.pathname || '',
        component: String(info?.componentStack || '').trim().split('\n')[0] || '',
      }).catch(() => {})
    } catch { /* offline, blocked, or the API module itself is the casualty */ }
  }

  render() {
    if (!this.state.hasError) return this.props.children

    const lang = (i18n?.language || 'en').split('-')[0]
    const copy = FALLBACK[lang] || FALLBACK.en

    return (
      <div style={{
        display: 'flex', flexDirection: 'column', alignItems: 'center',
        justifyContent: 'center', minHeight: '100vh', gap: 16, padding: 24,
        textAlign: 'center',
        // The app's own tokens, with literals behind them: if the stylesheet
        // is what failed, this screen still has to be readable.
        fontFamily: 'var(--font, Inter, sans-serif)',
        background: 'var(--bg, #0A0B12)',
        color: 'var(--text, #E8EAF2)',
      }}>
        <h2 style={{ margin: 0, fontSize: '1.15rem' }}>{copy.title}</h2>
        {/* The raw message, small and dim. It is rarely meaningful to a
            reader, but it is what they can quote when they tell us. */}
        <p style={{ color: 'var(--text-dim, #8A90A6)', fontSize: 13, margin: 0, maxWidth: 420 }}>
          {this.state.error?.message}
        </p>
        <button
          onClick={() => { window.location.href = '/' }}
          style={{
            padding: '10px 24px', borderRadius: 10, cursor: 'pointer',
            background: 'var(--firefly, #F5A524)', color: '#0A0B12',
            border: 'none', font: 'inherit', fontWeight: 600,
          }}
        >
          {copy.home}
        </button>
      </div>
    )
  }
}
