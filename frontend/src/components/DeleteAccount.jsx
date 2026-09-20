import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { useAuth, useClerk } from '@clerk/clerk-react'
import { Link } from 'react-router-dom'
import api from '../utils/api'

/**
 * In-app account deletion.
 *
 * Apple rejects any app that can create an account but cannot delete one from
 * inside it, and "email us" does not count. Beyond the store rule, an app that
 * asks for someone's income, debts and holdings owes them a way out that does
 * not involve asking permission.
 *
 * Two deliberate frictions: the danger zone is collapsed, and the confirmation
 * is a typed word rather than a second button. Both exist because this cannot
 * be undone — there is no soft delete and no archived copy to restore from.
 */
export default function DeleteAccount() {
  const { t } = useTranslation()
  const { userId } = useAuth()
  const { signOut } = useClerk()
  const [open, setOpen] = useState(false)
  const [typed, setTyped] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState(null)

  const phrase = t('account.confirmWord')
  const armed = typed.trim().toLocaleUpperCase() === phrase.toLocaleUpperCase()

  async function remove() {
    setBusy(true)
    setError(null)
    try {
      const { data } = await api.delete('/users/me', {
        data: { confirm_user_id: userId },
      })
      // The server tells us whether the login went too. If it didn't, say so
      // on the way out rather than letting them discover it at next sign-in.
      if (!data?.identity_deleted) window.alert(data?.message || t('account.partial'))
      // Local caches are keyed per user, but a shared device should not keep
      // a departed account's numbers on screen for the next person.
      try { window.localStorage.clear() } catch { /* private mode */ }
      await signOut({ redirectUrl: '/' })
    } catch (e) {
      setError(e?.response?.data?.detail || t('account.failed'))
      setBusy(false)
    }
  }

  return (
    <div style={{
      marginTop: '2.5rem', padding: '1rem',
      border: '1px solid var(--border)', borderRadius: 12,
    }}>
      {!open ? (
        <button
          className="btn btn-ghost btn-full"
          style={{ color: 'var(--red, #f87171)' }}
          onClick={() => setOpen(true)}
        >
          {t('account.deleteTitle')}
        </button>
      ) : (
        <>
          <h3 style={{ margin: '0 0 0.5rem', fontSize: '1rem', color: 'var(--red, #f87171)' }}>
            {t('account.deleteTitle')}
          </h3>
          <p style={{ fontSize: 13, lineHeight: 1.65, opacity: 0.85, marginTop: 0 }}>
            {t('account.deleteBody')}
          </p>
          <p style={{ fontSize: 12, opacity: 0.7 }}>
            <Link to="/privacy">{t('legal.privacy.title')}</Link>
          </p>

          <label style={{ display: 'block', fontSize: 13, marginTop: '0.75rem' }}>
            {t('account.confirmPrompt', { word: phrase })}
            <input
              value={typed}
              onChange={e => setTyped(e.target.value)}
              aria-label={t('account.confirmPrompt', { word: phrase })}
              style={{ width: '100%', marginTop: 6 }}
              autoComplete="off"
            />
          </label>

          {error && (
            <p role="alert" style={{ color: 'var(--red, #f87171)', fontSize: 13 }}>{error}</p>
          )}

          <div style={{ display: 'flex', gap: 8, marginTop: '0.9rem' }}>
            <button
              className="btn btn-ghost"
              style={{ flex: 1 }}
              onClick={() => { setOpen(false); setTyped(''); setError(null) }}
              disabled={busy}
            >
              {t('common.cancel')}
            </button>
            <button
              className="btn btn-primary"
              style={{ flex: 1, background: 'var(--red, #f87171)', borderColor: 'var(--red, #f87171)' }}
              onClick={remove}
              disabled={!armed || busy}
            >
              {busy ? t('account.deleting') : t('account.deleteConfirm')}
            </button>
          </div>
        </>
      )}
    </div>
  )
}
