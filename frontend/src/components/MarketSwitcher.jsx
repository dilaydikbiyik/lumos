import useMarket from '../hooks/useMarket'
import { useTranslation } from 'react-i18next'

const FLAGS = { TR: '🇹🇷', US: '🇺🇸', DE: '🇩🇪' }

/**
 * Market selector — currency, number format and data sources follow the
 * selected pack. Markets without live data are HONESTLY labelled; they
 * are selectable, but TR-data pages show an "integration on the way"
 * state instead of masquerading foreign data.
 */
export default function MarketSwitcher({ compact = false }) {
  const { t } = useTranslation()
  const { market, packs, setMarket } = useMarket()
  if (packs.length < 2) return null

  return (
    <label style={{
      display: 'flex', alignItems: 'center', gap: 8,
      fontSize: compact ? 12 : 13, color: 'var(--text-dim)',
    }}>
      {!compact && <span style={{ fontWeight: 600 }}>{t('market.label')}</span>}
      <select
        value={market}
        onChange={e => setMarket(e.target.value)}
        aria-label={t('market.select')}
        style={{
          background: 'var(--bg-input, rgba(255,255,255,0.05))',
          color: 'var(--text)', border: '1px solid var(--border)',
          borderRadius: 'var(--radius-xs, 8px)', padding: '7px 10px',
          fontFamily: 'var(--font)', fontSize: 13, cursor: 'pointer',
          width: compact ? 'auto' : '100%',
        }}
      >
        {packs.map(p => (
          <option key={p.code} value={p.code}>
            {FLAGS[p.code] ?? '🌍'} {p.name} ({p.currency})
            {p.live_housing_index ? '' : ' — ' + t('market.limitedData')}
          </option>
        ))}
      </select>
    </label>
  )
}
