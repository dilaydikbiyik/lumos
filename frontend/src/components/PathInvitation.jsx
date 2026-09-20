import { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '@clerk/clerk-react'
import api from '../utils/api'
import { readJSON, writeJSON, userKey } from '../utils/storage'

/**
 * A soft invitation to look at the other half of the app.
 *
 * Someone who picked "stocks only" on day one has Explore hidden and no
 * reason to know the real-estate side exists; someone who picked "real estate
 * only" never sees a portfolio. Both chose from a single onboarding card,
 * before using anything.
 *
 * Deliberately an invitation and not a prompt:
 *   - it appears only for a single-world path, never for hybrid or undecided
 *   - it is dismissible, and dismissal is remembered per user
 *   - dismissing it does NOT change the path; it just stops asking
 *   - it never appears again once dismissed, and never interrupts a flow
 *
 * The product rule from the start was that flows are chosen, never forced.
 * A card that keeps coming back after a "no" is a forced flow with extra
 * steps.
 */
const INVITE_FOR = {
  stocks: { to: '/explore', copy: 'toRealEstate' },
  real_estate: { to: '/recommend', copy: 'toStocks' },
}

export default function PathInvitation() {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const { userId } = useAuth()
  const storeKey = userKey('path-invite-dismissed', userId)
  const [path, setPath] = useState(null)
  const [justDismissed, setJustDismissed] = useState(false)
  // Read during render, against the CURRENT key. `userKey` returns null while
  // Clerk is still loading, so lazy initial state would read under the wrong
  // key once and never re-read — and the card would come back after every
  // "not now", which is the forced flow this is supposed not to be.
  const dismissed = justDismissed || readJSON(storeKey) === true

  useEffect(() => {
    let cancelled = false
    api.get('/users/me')
      .then(res => { if (!cancelled) setPath(res.data.investment_path) })
      .catch(() => { /* no invitation is the safe default */ })
    return () => { cancelled = true }
  }, [storeKey])

  const invite = INVITE_FOR[path]
  if (!invite || dismissed) return null

  function dismiss() {
    setJustDismissed(true)
    writeJSON(storeKey, true)
  }

  return (
    <div className="card" style={{ borderStyle: 'dashed' }}>
      <div style={{ display: 'flex', alignItems: 'flex-start', gap: 10 }}>
        <span style={{ fontSize: 20 }} aria-hidden="true">💡</span>
        <div style={{ flex: 1 }}>
          <strong style={{ fontSize: 14 }}>{t(`pathInvite.${invite.copy}.title`)}</strong>
          <p style={{ fontSize: 13, opacity: 0.85, margin: '4px 0 10px', lineHeight: 1.6 }}>
            {t(`pathInvite.${invite.copy}.body`)}
          </p>
          <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
            <button className="btn btn-ghost" onClick={() => navigate(invite.to)}>
              {t(`pathInvite.${invite.copy}.cta`)}
            </button>
            <button
              className="btn btn-ghost"
              style={{ opacity: 0.7 }}
              onClick={dismiss}
            >
              {t('pathInvite.notNow')}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
