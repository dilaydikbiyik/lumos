import { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { isIosSafari, isStandaloneDisplay } from '../utils/install'

/**
 * The one piece missing from a free route to people's phones.
 *
 * Push notifications are the behavioural coach's only real carrier: "the
 * market dropped, here is what you said you would do" is worthless an hour
 * later, and this app's whole purpose is reaching somebody in the minute
 * they are frightened. The service worker has had a push handler all along
 * (public/sw.js), the manifest is complete, and the icons are in place — so
 * on paper this app can already do it without a cent of store fees.
 *
 * It could not, in practice, for one reason: push on iOS works ONLY for a
 * web app that has been added to the home screen, and iOS never offers to
 * add one. No prompt, no banner, nothing. A reader had to already know to
 * tap Share and scroll to "Add to Home Screen" — so there was not even a
 * place to ASK for notification permission. The carrier reached nobody.
 *
 * The two platforms need opposite things, which is why this is one
 * component with two branches rather than two components:
 *
 *   Android/Chrome gives a real event. `beforeinstallprompt` fires, we keep
 *   it, and a button calls prompt(). The OS draws the dialog.
 *
 *   iOS gives nothing. There is no event to wait for and no API to call, so
 *   the only honest thing is to describe the gesture — and ONLY in Safari,
 *   because Chrome and Firefox on iOS run on WebKit and cannot install at
 *   all. Telling a Chrome-on-iOS reader to tap Share would send them
 *   looking for a menu item that is not there.
 *
 * It renders nothing at all when the app is already installed, which is the
 * common case for anyone who has done this once.
 */

const DISMISSED_KEY = 'lumos-install-hint-dismissed'

export default function InstallHint() {
  const { t } = useTranslation()
  const [prompt, setPrompt] = useState(null)
  const [dismissed, setDismissed] = useState(() => {
    try {
      return window.localStorage.getItem(DISMISSED_KEY) === '1'
    } catch {
      // Private browsing throws on access. A reader who cannot be remembered
      // should still see the hint rather than nothing.
      return false
    }
  })

  useEffect(() => {
    const onPrompt = event => {
      // Keep the event instead of letting Chrome show its own mini-infobar,
      // so the invitation sits in the page where the reason for it is.
      event.preventDefault()
      setPrompt(event)
    }
    window.addEventListener('beforeinstallprompt', onPrompt)
    return () => window.removeEventListener('beforeinstallprompt', onPrompt)
  }, [])

  const close = () => {
    setDismissed(true)
    try {
      window.localStorage.setItem(DISMISSED_KEY, '1')
    } catch { /* unremembered is better than broken */ }
  }

  const install = async () => {
    if (!prompt) return
    try {
      await prompt.prompt()
      // The event is single-use whatever the reader chose. Dropping it is
      // what hides the card: a second tap on a spent prompt does nothing,
      // which would look broken.
      setPrompt(null)
      close()
    } catch { /* a dismissed OS dialog is not an error */ }
  }

  if (dismissed || isStandaloneDisplay(window.matchMedia, window.navigator)) return null

  const android = Boolean(prompt)
  const ios = !android && isIosSafari(window.navigator)
  if (!android && !ios) return null

  return (
    <div className="card" style={{ borderColor: 'var(--firefly-dim)' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', gap: 8 }}>
        <strong style={{ fontSize: '0.95rem' }}>📲 {t('install.title')}</strong>
        <button
          type="button"
          onClick={close}
          aria-label={t('install.dismiss')}
          style={{
            background: 'none', border: 'none', cursor: 'pointer',
            color: 'var(--text-dim)', font: 'inherit', padding: 0, lineHeight: 1,
          }}
        >
          ✕
        </button>
      </div>

      <p style={{ fontSize: 12.5, lineHeight: 1.65, margin: '6px 0 0', opacity: 0.88 }}>
        {t('install.why')}
      </p>

      {android && (
        <button type="button" className="btn btn-primary" onClick={install}
                style={{ marginTop: 12, width: '100%' }}>
          {t('install.action')}
        </button>
      )}

      {ios && (
        // No button, because there is no API. An ordered list of the two
        // taps, in the order the reader will make them.
        <ol style={{ margin: '10px 0 0', paddingLeft: 20, fontSize: 12.5, lineHeight: 1.7 }}>
          <li>{t('install.iosShare')}</li>
          <li>{t('install.iosAdd')}</li>
        </ol>
      )}
    </div>
  )
}
