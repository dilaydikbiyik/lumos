import { useCallback, useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import api, { extractErrorMessage } from '../utils/api'

/**
 * Who can do what — the half of RBAC that has to live in the app.
 *
 * Granting access by pasting Clerk ids into a server environment variable and
 * redeploying works exactly once, for the first admin. Everything after that
 * belongs here.
 *
 * The role table comes from the server rather than being hard-coded, so a role
 * added in backend/auth/permissions.py shows up with its real permissions
 * instead of a stale copy of them.
 */
export default function UserAccessPanel({ canWriteRoles }) {
  const { t } = useTranslation()
  const [roles, setRoles] = useState(null)
  const [users, setUsers] = useState(null)
  const [query, setQuery] = useState('')
  const [busy, setBusy] = useState(null)
  const [error, setError] = useState(null)

  const load = useCallback(async (q = '') => {
    const [r, u] = await Promise.all([
      api.get('/admin/roles'),
      api.get('/admin/users', { params: q ? { q } : {} }),
    ])
    setRoles(r.data)
    setUsers(u.data)
  }, [])

  useEffect(() => {
    let cancelled = false
    async function run() {
      try {
        await load()
      } catch {
        if (!cancelled) setError(t('admin.loadError'))
      }
    }
    run()
    return () => { cancelled = true }
  }, [load, t])

  async function search(e) {
    e.preventDefault()
    setError(null)
    try {
      await load(query)
    } catch (err) {
      setError(extractErrorMessage(err, t('admin.loadError')))
    }
  }

  async function changeRole(clerkId, role) {
    setBusy(clerkId)
    setError(null)
    try {
      await api.patch(`/admin/users/${encodeURIComponent(clerkId)}/role`, { role })
      await load(query)
    } catch (err) {
      // The server refuses self-demotion and last-admin demotion with a
      // readable reason; showing it beats a silent no-op.
      setError(extractErrorMessage(err, t('admin.roleChangeFailed')))
    } finally {
      setBusy(null)
    }
  }

  return (
    <div className="card">
      <h3 style={{ marginBottom: 4 }}>{t('admin.accessTitle')}</h3>
      <p style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 12, lineHeight: 1.6 }}>
        {t('admin.accessBody')}
      </p>

      <form onSubmit={search} style={{ display: 'flex', gap: 8, marginBottom: 12 }}>
        <input
          className="input"
          style={{ flex: 1 }}
          placeholder={t('admin.searchUsers')}
          aria-label={t('admin.searchUsers')}
          value={query}
          onChange={e => setQuery(e.target.value)}
        />
        <button className="btn btn-ghost" type="submit">{t('admin.search')}</button>
      </form>

      {roles && (
        <details style={{ marginBottom: 12 }}>
          <summary style={{ cursor: 'pointer', fontSize: 12, color: 'var(--text-dim)' }}>
            {t('admin.whatRolesMean')}
          </summary>
          <div style={{ marginTop: 8, display: 'flex', flexDirection: 'column', gap: 6 }}>
            {roles.roles.map(r => (
              <div key={r.name} style={{ fontSize: 12, lineHeight: 1.6 }}>
                <strong>{t(`admin.role.${r.name}`, { defaultValue: r.name })}</strong>
                {' — '}
                <span style={{ color: 'var(--text-muted)' }}>
                  {r.permissions.length
                    ? r.permissions.join(', ')
                    : t('admin.noPermissions')}
                </span>
              </div>
            ))}
          </div>
        </details>
      )}

      {error && (
        <p style={{ color: 'var(--red)', fontSize: 13, marginBottom: 10 }}>{error}</p>
      )}

      {!users && !error && (
        <div style={{ textAlign: 'center', padding: 16 }}>
          <span className="spinner" style={{ width: 22, height: 22 }} />
        </div>
      )}

      {users && users.length === 0 && (
        <p style={{ fontSize: 13, opacity: 0.7 }}>{t('admin.noUsers')}</p>
      )}

      {users && users.map(u => (
        <div key={u.clerk_user_id} style={{
          display: 'flex', alignItems: 'center', gap: 10, flexWrap: 'wrap',
          padding: '10px 0', borderTop: '1px solid var(--border)',
        }}>
          <div style={{ flex: 1, minWidth: 160 }}>
            <div style={{ fontSize: 13, fontWeight: 600 }}>
              {u.email || t('admin.noEmail')}
            </div>
            <code style={{ fontSize: 10, color: 'var(--text-dim)', wordBreak: 'break-all' }}>
              {u.clerk_user_id}
            </code>
          </div>

          <span className="badge" style={{
            background: 'var(--bg-input)', border: '1px solid var(--border)',
            color: 'var(--text-muted)', fontSize: 11,
          }}>
            {u.plan} · {u.market}
          </span>

          {canWriteRoles && roles ? (
            <select
              className="input"
              style={{ width: 'auto', fontSize: 12, padding: '6px 8px' }}
              value={u.role}
              disabled={busy === u.clerk_user_id}
              aria-label={t('admin.changeRoleFor', { user: u.email || u.clerk_user_id })}
              onChange={e => changeRole(u.clerk_user_id, e.target.value)}
            >
              {roles.assignable.map(role => (
                <option key={role} value={role}>
                  {t(`admin.role.${role}`, { defaultValue: role })}
                </option>
              ))}
            </select>
          ) : (
            <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>
              {t(`admin.role.${u.role}`, { defaultValue: u.role })}
            </span>
          )}
        </div>
      ))}
    </div>
  )
}
