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
  const { market, packs, setMarket } = useMarket()
  if (packs.length < 2) return null

  return (
    <HeaderSelect
      label={t('market.label')}
      value={market}
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
  )
}
