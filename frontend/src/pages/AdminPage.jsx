import { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { useNavigate } from 'react-router-dom'
import AppHeader from '../components/AppHeader'
import api from '../utils/api'
import useMarket from '../hooks/useMarket'

/**
 * Admin view — where the feedback people send actually gets read.
 *
 * The endpoint existed from the start and nothing rendered it, so every
 * message users sent went into a table nobody opened. The whole point of
 * making it one tap to say "I didn't understand this screen" is lost if the
 * reports are write-only.
 *
 * The route is hidden from non-admins, but that is convenience, not
 * security: /feedback and /admin/stats both check the role server-side.
 */

const CATEGORY_COLORS = {
  bug: 'var(--red)',
  confusing: 'var(--firefly)',
  idea: 'var(--accent, #7C5CFF)',
  other: 'var(--text-dim)',
}

function Stat({ label, value }) {
  return (
    <div style={{ flex: '1 1 120px' }}>
      <div className="num-label">{label}</div>
      <div style={{ fontSize: 22, fontWeight: 700 }}>{value ?? '—'}</div>
    </div>
  )
}

export default function AdminPage() {
  const { t, i18n } = useTranslation()
  const navigate = useNavigate()
  const { pack } = useMarket()
  const [stats, setStats] = useState(null)
  const [feedback, setFeedback] = useState(null)
  const [filter, setFilter] = useState('all')
  const [error, setError] = useState(null)

  useEffect(() => {
    let cancelled = false
    async function load() {
      try {
        const [s, f] = await Promise.all([
          api.get('/admin/stats'),
          api.get('/feedback'),
        ])
        if (cancelled) return
        setStats(s.data)
        setFeedback(f.data)
      } catch (err) {
        if (cancelled) return
        // 403 means "you are signed in but not an admin" — say that rather
        // than showing an empty page that looks broken.
        setError(err.response?.status === 403 ? 'forbidden' : 'failed')
      }
    }
    load()
    return () => { cancelled = true }
  }, [])

  const visible = feedback?.filter(f => filter === 'all' || f.category === filter) ?? []
  const counts = (feedback ?? []).reduce((acc, f) => {
    const key = f.category || 'other'
    acc[key] = (acc[key] || 0) + 1
    return acc
  }, {})

  function when(iso) {
    if (!iso) return ''
    try {
      return new Date(iso).toLocaleString(pack.locale || i18n.language, {
        dateStyle: 'medium', timeStyle: 'short',
      })
    } catch {
      return iso
    }
  }

  return (
    <div className="page">
      <AppHeader />
      <div className="page-content" style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
        <div>
          <h2>{t('admin.title')}</h2>
          <p style={{ fontSize: 13, marginTop: 4, color: 'var(--text-muted)' }}>
            {t('admin.subtitle')}
          </p>
        </div>

        {error && (
          <div className="card">
            <p style={{ fontSize: 14 }}>
              {error === 'forbidden' ? t('admin.forbidden') : t('admin.loadError')}
            </p>
            <button className="btn btn-ghost" style={{ marginTop: 12 }}
                    onClick={() => navigate('/dashboard')}>
              {t('admin.backToDashboard')}
            </button>
          </div>
        )}

        {!error && stats && (
          <div className="card" style={{ display: 'flex', gap: 16, flexWrap: 'wrap' }}>
            <Stat label={t('admin.totalUsers')} value={stats.total_users} />
            <Stat label={t('admin.profiledUsers')} value={stats.profiled_users} />
            <Stat label={t('admin.totalHoldings')} value={stats.total_holdings} />
            <Stat label={t('admin.messagesToday')} value={stats.ai_messages_today} />
          </div>
        )}

        {!error && feedback && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
              {['all', 'bug', 'confusing', 'idea', 'other'].map(key => (
                <button
                  key={key}
                  className={`btn ${filter === key ? 'btn-primary' : 'btn-ghost'}`}
                  style={{ fontSize: 12, padding: '6px 12px' }}
                  onClick={() => setFilter(key)}
                >
                  {t(`admin.filter.${key}`)}
                  {key !== 'all' && counts[key] ? ` (${counts[key]})` : ''}
                  {key === 'all' ? ` (${feedback.length})` : ''}
                </button>
              ))}
            </div>

            {visible.length === 0 && (
              <div className="card" style={{ textAlign: 'center', padding: 28 }}>
                <div style={{ fontSize: 26, marginBottom: 8 }}>📭</div>
                <p style={{ fontSize: 14 }}>{t('admin.noFeedback')}</p>
              </div>
            )}

            {visible.map(f => (
              <div key={f.id} className="card" style={{ padding: 16 }}>
                <div style={{
                  display: 'flex', alignItems: 'center', gap: 8,
                  marginBottom: 8, flexWrap: 'wrap',
                }}>
                  <span className="badge" style={{
                    color: CATEGORY_COLORS[f.category] || 'var(--text-dim)',
                    border: '1px solid var(--border)', background: 'var(--bg-input)',
                  }}>
                    {t(`admin.filter.${f.category || 'other'}`)}
                  </span>
                  {f.page && (
                    <code style={{ fontSize: 11, color: 'var(--text-dim)' }}>{f.page}</code>
                  )}
                  <span style={{ fontSize: 11, color: 'var(--text-dim)', marginLeft: 'auto' }}>
                    {when(f.created_at)}
                  </span>
                </div>
                <p style={{ fontSize: 14, lineHeight: 1.6, whiteSpace: 'pre-wrap' }}>
                  {f.message}
                </p>
              </div>
            ))}
          </div>
        )}

        {!error && !feedback && (
          <div style={{ textAlign: 'center', padding: 24 }}>
            <span className="spinner" style={{ width: 28, height: 28 }} />
          </div>
        )}
      </div>
    </div>
  )
}
