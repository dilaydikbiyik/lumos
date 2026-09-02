import useMarket from '../hooks/useMarket'
import { Trans, useTranslation } from 'react-i18next'

/**
 * "Pay this off first" — shown when the user carries credit-card or consumer
 * debt. Telling someone not to invest yet costs us the more engaging path,
 * which is exactly why it has to be here: no app with something to sell would
 * say it, and the arithmetic is not close.
 */
export default function DebtFirstCard({ check }) {
  const { t } = useTranslation()
  const { money } = useMarket()
  if (!check) return null

  return (
    <div className="card" style={{ borderColor: 'var(--red)' }}>
      <h3 style={{ marginBottom: 6 }}>{t('debt.title')}</h3>

      <p style={{ fontSize: 14, lineHeight: 1.75, marginBottom: 12 }}>
        <Trans
          i18nKey="debt.body"
          values={{ debt: money(check.debt), debtPct: check.debt_annual_pct, portPct: check.portfolio_annual_pct }}
          components={[<strong key="a" />, <strong key="b" />, <strong key="c" />]}
        />
      </p>

      {/* The comparison, side by side, on the same amount and the same year. */}
      <div style={{
        display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10, marginBottom: 12,
      }}>
        <div style={{
          padding: 12, borderRadius: 10,
          border: '1px solid var(--border)', background: 'var(--bg-input)',
        }}>
          <div style={{ fontSize: 12, opacity: 0.75, marginBottom: 4 }}>
            {t('debt.ifRepay', { amount: money(check.applied) })}
          </div>
          <div className="num-lead" style={{ color: 'var(--green, #3DD68C)' }}>
            +{money(check.interest_avoided)}
          </div>
          <div style={{ fontSize: 11, opacity: 0.65, marginTop: 2 }}>
            {t('debt.repayCaption')}
          </div>
        </div>
        <div style={{
          padding: 12, borderRadius: 10,
          border: '1px solid var(--border)', background: 'var(--bg-input)',
        }}>
          <div style={{ fontSize: 12, opacity: 0.75, marginBottom: 4 }}>
            {t('debt.ifInvest')}
          </div>
          <div className="num-lead">+{money(check.investment_gain)}</div>
          <div style={{ fontSize: 11, opacity: 0.65, marginTop: 2 }}>
            {t('debt.investCaption')}
          </div>
        </div>
      </div>

      <div style={{
        padding: '10px 14px', borderRadius: 'var(--radius-xs)',
        background: 'var(--firefly-dim)', fontSize: 13.5, lineHeight: 1.7,
      }}>
        <Trans
          i18nKey="debt.verdict"
          values={{ advantage: money(check.advantage) }}
          components={[<strong key="a" />]}
        />{' '}
        {check.covers_debt ? (
          <Trans
            i18nKey="debt.covers"
            values={{ leftover: money(check.leftover_after_repayment) }}
            components={[<strong key="a" />]}
          />
        ) : (
          t('debt.notCovered')
        )}
      </div>

      <p style={{ fontSize: 11, color: 'var(--text-dim)', marginTop: 10, lineHeight: 1.5 }}>
        {t('debt.assumption', {
          monthly: check.assumptions.card_monthly_rate_pct,
          annual: check.debt_annual_pct,
        })}
      </p>
    </div>
  )
}
