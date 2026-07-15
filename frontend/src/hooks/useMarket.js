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
  pack: { code: 'TR', currency: 'TRY', locale: 'tr-TR', live_inflation: true, live_housing_index: true },
  packs: [],
  fmt: (n) => new Intl.NumberFormat('tr-TR', { maximumFractionDigits: 0 }).format(n),
  money: (n) => `${new Intl.NumberFormat('tr-TR', { maximumFractionDigits: 0 }).format(Math.round(n))} TL`,
  unit: 'TL',
  setMarket: () => {},
}

export default function useMarket() {
  return useContext(MarketContext) ?? FALLBACK_MARKET
}
