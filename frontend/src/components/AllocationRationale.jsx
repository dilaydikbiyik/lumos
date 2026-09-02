import useMarket from '../hooks/useMarket'
import { Trans, useTranslation } from 'react-i18next'

/**
 * "Why this allocation?" — the engine's deterministic rationale.
 * No black box: the formula, each asset's role/weight reasoning and
 * every DROPPED asset (with its reason) are visible — no silent pruning.
 */
export default function AllocationRationale({ portfolio }) {
  const { t } = useTranslation()
  const { money } = useMarket()
  const logic = portfolio?.metadata?.allocation_logic
  if (!portfolio?.allocations?.length) return null

  return (
    <div className="card">
      <h3 style={{ marginBottom: 4, fontSize: 15 }}>{t('rationale.title')}</h3>
      <p style={{ fontSize: 12, opacity: 0.7, marginBottom: 12 }}>
        {t('rationale.subtitle')}
      </p>

      {logic && (
        <div style={{
          padding: '12px 14px', borderRadius: 10, marginBottom: 12,
          background: 'var(--bg-input)', fontSize: 'var(--t-small)', lineHeight: 1.65,
        }}>
          <p style={{ marginBottom: 10 }}>
            <Trans i18nKey="rationale.intro" values={{ score: portfolio.risk_score }}
                   components={[<strong key="a" />]} />
          </p>

          <div style={{ display: 'flex', gap: 10, marginBottom: 10 }}>
            <span style={{
              flexShrink: 0, width: 22, height: 22, borderRadius: '50%',
              background: 'var(--firefly-dim)', color: 'var(--firefly)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontSize: 'var(--t-micro)', fontWeight: 700,
            }}>1</span>
            <div>
              <Trans i18nKey="rationale.step1" values={{ pct: logic.defensive_target_pct }}
                     components={[<strong key="a" />, <br key="b" />, <strong key="c" />]} />
            </div>
          </div>

          <div style={{ display: 'flex', gap: 10 }}>
            <span style={{
              flexShrink: 0, width: 22, height: 22, borderRadius: '50%',
              background: 'var(--firefly-dim)', color: 'var(--firefly)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontSize: 'var(--t-micro)', fontWeight: 700,
            }}>2</span>
            <div>
              <Trans i18nKey="rationale.step2" values={{ pct: logic.growth_target_pct }}
                     components={[<strong key="a" />, <br key="b" />]} />{' '}
              {portfolio.risk_score <= 3.5
                ? t('rationale.lowBand')
                : portfolio.risk_score >= 7
                  ? t('rationale.highBand')
                  : t('rationale.midBand')}
            </div>
          </div>

          {/* The exact formula stays one tap away: plain language for everyone,
              full transparency for anyone who wants to check the arithmetic. */}
          {logic.formula && (
            <details style={{ marginTop: 10 }}>
              <summary style={{
                cursor: 'pointer', fontSize: 'var(--t-micro)', color: 'var(--text-dim)',
              }}>
                {t('rationale.showFormula')}
              </summary>
              <div style={{
                marginTop: 6, fontSize: 'var(--t-micro)', color: 'var(--text-muted)',
                lineHeight: 1.6, fontFamily: 'ui-monospace, SFMono-Regular, monospace',
              }}>
                {logic.formula}
                <div style={{ marginTop: 4 }}>{t('rationale.alphaNote', { alpha: logic.alpha })}</div>
              </div>
            </details>
          )}
        </div>
      )}

      <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
        {portfolio.allocations.map(a => (
          <div key={a.ticker} style={{ display: 'flex', gap: 10, alignItems: 'flex-start' }}>
            <span style={{
              minWidth: 52, textAlign: 'center', padding: '3px 6px',
              borderRadius: 8, fontSize: 12, fontWeight: 700,
              background: 'var(--firefly-dim)', color: 'var(--firefly, #F5A524)',
            }}>
              %{Math.round(a.weight * 100)}
            </span>
            <div style={{ fontSize: 13, lineHeight: 1.5 }}>
              <strong>{a.name}</strong>
              <div style={{ fontSize: 12, opacity: 0.7 }}>{a.explanation}</div>
            </div>
          </div>
        ))}
      </div>

      {logic?.dropped?.length > 0 && (
        <div style={{ marginTop: 14, paddingTop: 10, borderTop: '1px dashed var(--border)' }}>
          <p style={{ fontSize: 12, fontWeight: 700, marginBottom: 6, opacity: 0.8 }}>
            {t('rationale.droppedTitle', { count: portfolio.allocations.length })}
          </p>
          {logic.dropped.map((d, i) => (
            <p key={i} style={{ fontSize: 12, opacity: 0.65, lineHeight: 1.55 }}>
              • <strong>{d.ticker}</strong> {t('rationale.wouldBe', { pct: d.weight_pct })}: {d.reason}
            </p>
          ))}
        </div>
      )}

      <p style={{ fontSize: 'var(--t-micro)', color: 'var(--text-dim)', marginTop: 10, lineHeight: 1.6 }}>
        {t('rationale.footer', {
          budget: money(portfolio.budget),
          cap: logic?.position_cap ?? '—',
          minPct: logic?.min_weight_pct ?? 8,
        })}
      </p>
    </div>
  )
}
