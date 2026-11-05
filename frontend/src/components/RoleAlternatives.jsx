import { useTranslation } from 'react-i18next'
import { percent } from '../utils/format'

/**
 * The funds that could have played this role, beside the one that does.
 *
 * Asked for so the page teaches by showing choices rather than one answer.
 * Each row is measured on the same basis — five-year volatility and worst
 * fall, dividends included, and how long the fund has existed — so the
 * reader can see for themselves how small the difference between "the same
 * kind of fund" usually is (GLD and IAU move together to the decimal), and
 * where it is real (a 7–10 year Treasury fund falls harder than the whole
 * bond market when rates rise).
 *
 * Nothing is ranked or called better: the role's fund first, the others by
 * name, and the note says why the app holds only one of them.
 */
export default function RoleAlternatives({ role, ticker }) {
  const { t } = useTranslation()
  if (!role?.rows?.length || role.rows.length < 2) return null

  return (
    <details style={{ marginTop: 6 }}>
      <summary style={{ cursor: 'pointer', fontSize: 12, color: 'var(--text-dim)', minHeight: 24 }}>
        {t('rationale.alternativesTitle', { count: role.rows.length - 1 })}
      </summary>
      <p style={{ fontSize: 12, lineHeight: 1.6, margin: '6px 0 8px' }}>{role.note}</p>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
        {role.rows.map(r => (
          <div key={r.ticker} style={{
            padding: '8px 10px', borderRadius: 8, fontSize: 12, lineHeight: 1.55,
            background: r.ticker === ticker ? 'var(--firefly-dim)' : 'var(--bg-input)',
          }}>
            <strong>{r.name}</strong> <span style={{ opacity: 0.7 }}>({r.ticker})</span>
            {r.ticker === ticker && (
              <span style={{ marginLeft: 6, fontSize: 11, color: 'var(--firefly)' }}>
                · {t('rationale.inPortfolio')}
              </span>
            )}
            <div style={{ opacity: 0.8 }}>{r.holds}</div>
            {r.volatility_pct != null && (
              <div className="num" style={{ marginTop: 2, color: 'var(--text-dim)' }}>
                {t('rationale.altFacts', {
                  vol: percent(r.volatility_pct, { decimals: 1 }),
                  drop: percent(r.worst_drop_pct, { decimals: 1 }),
                  years: r.history_years,
                })}
              </div>
            )}
          </div>
        ))}
      </div>
      <p style={{ fontSize: 11, color: 'var(--text-dim)', margin: '6px 0 0', lineHeight: 1.5 }}>
        {t('rationale.altWindow', { years: role.window_years })}
      </p>
    </details>
  )
}
