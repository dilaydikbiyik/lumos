import { useTranslation } from 'react-i18next'
import { percent } from '../utils/format'

/**
 * What each asset is like to LIVE WITH, judged against the reader's own
 * answers.
 *
 * The backtest already measured all of this and returned it, and nothing
 * rendered it. "-42% over 18 months" is not information to a beginner; "this
 * goes deeper than the 20% you said you could sit through" is.
 *
 * The stagnation figure is given equal billing with the drawdown on purpose.
 * A crash is frightening and brief, and everybody warns you about it. Three
 * years of going nowhere looks like nothing on a chart and is what actually
 * makes people give up.
 */
const VERDICT_STYLE = {
  comfortable: { color: 'var(--green)', icon: '🙂' },
  demanding: { color: 'var(--firefly)', icon: '😐' },
  mismatch: { color: 'var(--red, #f87171)', icon: '⚠️' },
  unknown: { color: 'var(--text-dim)', icon: '·' },
}

export default function AssetCharacter({ perAsset }) {
  const { t } = useTranslation()
  const entries = Object.entries(perAsset || {})
  if (!entries.length) return null

  return (
    <div style={{ marginTop: 14 }}>
      <h4 style={{ margin: '0 0 2px', fontSize: 14 }}>{t('character.title')}</h4>
      <p style={{ fontSize: 12, opacity: 0.75, marginTop: 0 }}>{t('character.subtitle')}</p>

      {entries.map(([ticker, data]) => {
        const character = data.character || {}
        const style = VERDICT_STYLE[character.verdict] || VERDICT_STYLE.unknown
        return (
          <div key={ticker} style={{
            padding: '10px 12px', borderRadius: 10, marginBottom: 8,
            border: `1px solid ${style.color}`,
          }}>
            <div style={{ display: 'flex', alignItems: 'baseline', gap: 8 }}>
              <strong style={{ fontSize: 13 }}>{ticker}</strong>
              <span style={{ fontSize: 12, color: style.color }}>
                {style.icon} {t(`character.verdict.${character.verdict || 'unknown'}`)}
              </span>
            </div>

            <div style={{ fontSize: 11.5, opacity: 0.75, margin: '4px 0 6px' }}>
              {/* Both numbers, side by side — the flat stretch is the one
                  nobody quotes, so it does not get hidden behind the fall. */}
              {t('character.worstFall', { pct: percent(data.max_drawdown_pct) })}
              {data.longest_stagnation_months != null && (
                <> · {t('character.flatFor', { months: data.longest_stagnation_months })}</>
              )}
              {character.recovery_months != null
                ? <> · {t('character.backAfter', { months: character.recovery_months })}</>
                : <> · {t('character.neverBack')}</>}
            </div>

            <p style={{ fontSize: 12.5, lineHeight: 1.6, margin: 0 }}>{character.reason}</p>
          </div>
        )
      })}
    </div>
  )
}
