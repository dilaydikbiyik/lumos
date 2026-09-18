import { useContext } from 'react'
import MarketContext from '../contexts/MarketContext'

/**
 * Market formatters: { market, pack, packs, fmt, money, unit, setMarket }
 *   fmt(n)              → "100.000"                (market locale)
 *   money(n)            → "100.000 TL" / "$1,234"  (market currency)
 *   money(n, 'TRY')     → pinned for TL-denominated data — stays correct
 *                         even when the user switches markets
 * Outside the provider (tests / isolated renders) TR defaults apply.
 */
export const FALLBACK_MARKET = {
  market: 'TR',
  // Every field a consumer may read. An absent `example_district` rendered
  // the literal string "undefined" inside a placeholder.
  pack: {
    code: 'TR', name: 'Türkiye', currency: 'TRY', currency_symbol: '₺',
    locale: 'tr-TR', live_inflation: true, live_housing_index: true,
    regional_housing_breakdown: true, area_kind: 'province',
    example_district: '', example_locality: '',
    example_ticker: '', example_asset_name: '',
  },
  packs: [],
  fmt: (n) => new Intl.NumberFormat('tr-TR', { maximumFractionDigits: 0 }).format(n),
  money: (n) => `${new Intl.NumberFormat('tr-TR', { maximumFractionDigits: 0 }).format(Math.round(n))} TL`,
  unit: 'TL',
  setMarket: () => {},
}

export default function useMarket() {
  return useContext(MarketContext) ?? FALLBACK_MARKET
}
