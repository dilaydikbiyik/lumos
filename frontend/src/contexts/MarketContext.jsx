import { createContext, useCallback, useEffect, useMemo, useState } from 'react'
import { useAuth } from '@clerk/clerk-react'
import api from '../utils/api'
import { readJSON, writeJSON } from '../utils/storage'

/**
 * Frontend side of the Market Pack architecture — currency, number
 * formatting and data availability come from one place; components can
 * never hardcode a country.
 *
 * REALISM RULE: data carries its own currency. TCMB TL/m² figures are
 * never displayed as if converted to dollars when the user switches to
 * the US market — they stay pinned via money(n, 'TRY'). Pages built on
 * TR-only data show an honest "integration on the way" state when the
 * pack's live_* flags are false.
 */

// The shape every consumer may read. Carrying every field matters as much as
// carrying the right values: a missing `example_district` rendered the literal
// string "undefined" inside a placeholder.
const TR_FALLBACK = {
  code: 'TR', name: 'Türkiye', currency: 'TRY', currency_symbol: '₺',
  locale: 'tr-TR', live_inflation: true, live_housing_index: true,
  regional_housing_breakdown: true, area_kind: 'province',
  example_district: '', example_locality: '',
  example_ticker: '', example_asset_name: '',
}

// What the backend last told us. The first paint happens before /users/markets
// answers, and before this cache existed that paint was always Türkiye — so a
// US reader watched their dollars render as lira for a moment on every load,
// and saw them stay that way whenever the backend was unreachable.
const CACHE_KEY = 'lumos-market-cache'

function cached() {
  const value = readJSON(CACHE_KEY)
  if (!value?.packs?.length || !value?.market) return null
  return value
}

const MarketContext = createContext(null)

export function MarketProvider({ children }) {
  const { isSignedIn } = useAuth()
  const remembered = cached()
  const [packs, setPacks] = useState(remembered?.packs ?? [TR_FALLBACK])
  const [marketCode, setMarketCode] = useState(remembered?.market ?? 'TR')

  useEffect(() => {
    if (!isSignedIn) return
    let cancelled = false
    async function load() {
      try {
        const [marketsRes, meRes] = await Promise.all([
          api.get('/users/markets'),
          api.get('/users/me'),
        ])
        if (cancelled) return
        const fetched = marketsRes.data?.markets
        const chosen = meRes.data?.market
        if (fetched?.length) setPacks(fetched)
        if (chosen) setMarketCode(chosen)
        if (fetched?.length && chosen) {
          writeJSON(CACHE_KEY, { packs: fetched, market: chosen })
        }
      } catch {
        // Keep whatever we already have — formatting must never break, and
        // the remembered market is a better guess than Türkiye for everyone
        // who is not in it.
      }
    }
    load()
    return () => { cancelled = true }
  }, [isSignedIn])

  const setMarket = useCallback(async (code) => {
    const prev = marketCode
    setMarketCode(code) // optimistic — the UI responds instantly
    try {
      await api.patch('/users/me/market', { market: code })
      writeJSON(CACHE_KEY, { packs, market: code })
    } catch {
      setMarketCode(prev) // save failed — don't stay in a lying state
    }
  }, [marketCode, packs])

  const value = useMemo(() => {
    const pack = packs.find(p => p.code === marketCode) ?? TR_FALLBACK
    const nf = new Intl.NumberFormat(pack.locale, { maximumFractionDigits: 0 })

    /** Number: 100000 → "100.000" (tr-TR) / "100,000" (en-US) */
    const fmt = (n) => nf.format(n)

    /**
     * Money: defaults to the market currency; TL-denominated components
     * pin 'TRY'. Turkish convention is preserved ("100.000 TL"); other
     * currencies follow Intl rules ("$1,234").
     */
    const money = (n, currency = pack.currency) => {
      if (currency === 'TRY') return `${nf.format(Math.round(n))} TL`
      return new Intl.NumberFormat(pack.locale, {
        style: 'currency', currency, maximumFractionDigits: 0,
      }).format(n)
    }

    /** Unit label for "big number + small unit" layouts */
    const unit = pack.currency === 'TRY' ? 'TL' : (pack.currency_symbol || pack.currency)

    return { market: pack.code, pack, packs, fmt, money, unit, setMarket }
  }, [packs, marketCode, setMarket])

  return <MarketContext.Provider value={value}>{children}</MarketContext.Provider>
}

export default MarketContext
