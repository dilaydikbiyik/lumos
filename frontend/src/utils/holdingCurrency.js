// Which currency an asset's VALUE follows. Listings follow their exchange;
// cash and physical things follow the currency they were recorded in.
const LOCAL_TYPES = new Set(['real_estate', 'land', 'vehicle', 'cash'])
// Listing suffix → currency. A hand-maintained ticker list went stale the
// moment the app gained a second market; the exchange suffix does not.
const SUFFIX_CURRENCY = { '.IS': 'TRY', '.DE': 'EUR', '.F': 'EUR', '.PA': 'EUR', '.L': 'GBP' }

export function getCurrency(holding, homeCurrency) {
  const ticker = (holding.ticker || '').toUpperCase()
  for (const [suffix, ccy] of Object.entries(SUFFIX_CURRENCY)) {
    if (ticker.endsWith(suffix)) return ccy
  }
  // Cash, property and vehicles hold the currency they were recorded in: dollar
  // cash is foreign money, not lira. Legacy rows without a currency are home.
  if (LOCAL_TYPES.has(holding.asset_type)) return (holding.currency || homeCurrency).toUpperCase()
  if (holding.asset_type === 'gold' || holding.asset_type === 'crypto') return 'USD'
  return ticker ? 'USD' : homeCurrency   // unsuffixed listings are US
}
