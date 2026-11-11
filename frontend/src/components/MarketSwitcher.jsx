import useMarket from '../hooks/useMarket'
import { useTranslation } from 'react-i18next'
import HeaderSelect from './HeaderSelect'

const FLAGS = { TR: '🇹🇷', US: '🇺🇸', DE: '🇩🇪' }

/**
 * Market selector — currency, number format and data sources follow the
 * selected pack. Markets without live data are HONESTLY labelled; they
 * are selectable, but TR-data pages show an "integration on the way"
 * state instead of masquerading foreign data.
 */
export default function MarketSwitcher({ compact = false }) {
  const { t } = useTranslation()
  const { market, packs, setMarket, pendingMarket, marketError } = useMarket()
  if (packs.length < 2) return null

  return (
    <>
    <HeaderSelect
      label={t('market.label')}
      value={pendingMarket ?? market}
      onChange={setMarket}
      ariaLabel={t('market.select')}
      compact={compact}
    >
      {packs.map(p => (
        <option key={p.code} value={p.code}>
          {FLAGS[p.code] ?? '🌍'}{compact ? ` ${p.code}` : ` ${p.name} (${p.currency})`}
          {!compact && !p.live_housing_index ? ' — ' + t('market.limitedData') : ''}
        </option>
      ))}
    </HeaderSelect>
    {marketError && (
      <span role="alert" style={{
        position: 'fixed', left: 16, right: 16, bottom: 88, zIndex: 50,
        padding: '10px 12px', borderRadius: 10, fontSize: 12.5, lineHeight: 1.5,
        background: 'var(--bg-card, #16182a)', border: '1px solid var(--red)', color: 'var(--text)',
      }}>
        {marketError === true ? t('market.switchFailed') : marketError}
      </span>
    )}
    </>
  )
}
