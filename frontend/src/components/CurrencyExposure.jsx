import { useTranslation } from 'react-i18next'
import useMarket from '../hooks/useMarket'

/**
 * TL / FX exposure & currency-risk indicator.
 * Groups holdings by their currency and shows an educational
 * message about exchange-rate risk.
 */

// Known ticker → currency mapping
const TICKER_CURRENCY = {
  'XU100.IS': 'TRY', 'THYAO.IS': 'TRY', 'GARAN.IS': 'TRY',
  'ASELS.IS': 'TRY', 'BIMAS.IS': 'TRY', 'EREGL.IS': 'TRY',
  'SPY': 'USD', 'QQQ': 'USD', 'GLD': 'USD',
  'VNQ': 'USD', 'SCHH': 'USD', 'VOO': 'USD', 'VTI': 'USD',
  'AAPL': 'USD', 'MSFT': 'USD', 'GOOGL': 'USD', 'AMZN': 'USD',
}

// Default currency by asset type
const TYPE_CURRENCY = {
  real_estate: 'TRY', land: 'TRY', vehicle: 'TRY',
  cash: 'TRY', gold: 'USD', crypto: 'USD',
}

function getCurrency(holding) {
  if (holding.ticker && TICKER_CURRENCY[holding.ticker]) {
    return TICKER_CURRENCY[holding.ticker]
  }
  if (holding.ticker?.endsWith('.IS')) return 'TRY'
  if (TYPE_CURRENCY[holding.asset_type]) return TYPE_CURRENCY[holding.asset_type]
  return 'USD' // foreign stock/ETF default
}

export default function CurrencyExposure({ holdings }) {
  const { t } = useTranslation()
  // Holding amounts are recorded in TL (TR-market component) — TRY is pinned
  const { money } = useMarket()
  if (!holdings || holdings.length === 0) return null

  let tryTotal = 0
  let usdTotal = 0

  holdings.forEach(h => {
    const value = h.manual_current_value || h.purchase_amount || 0
    const currency = getCurrency(h)
    if (currency === 'TRY') {
      tryTotal += value
    } else {
      usdTotal += value
    }
  })

  const total = tryTotal + usdTotal
  if (total === 0) return null

  const tryPct = Math.round((tryTotal / total) * 100)
  const usdPct = 100 - tryPct

  // Currency-risk message
  let riskLevel, riskMessage, riskColor
  if (tryPct >= 80) {
    riskLevel = t('fx.high'); riskMessage = t('fx.highMsg'); riskColor = 'var(--red)'
  } else if (tryPct >= 50) {
    riskLevel = t('fx.mid'); riskMessage = t('fx.midMsg'); riskColor = 'var(--firefly)'
  } else {
    riskLevel = t('fx.low'); riskMessage = t('fx.lowMsg'); riskColor = 'var(--green)'
  }

  return (
    <div className="card">
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 14 }}>
        <span style={{ fontSize: 18 }}>💱</span>
        <div style={{ flex: 1 }}>
          <h3 style={{ fontSize: 14, fontWeight: 700 }}>{t('fx.title')}</h3>
          <p style={{ fontSize: 11, color: 'var(--text-dim)', marginTop: 1 }}>{t('fx.subtitle')}</p>
        </div>
        <span style={{
          fontSize: 11, fontWeight: 600, padding: '3px 10px',
          borderRadius: 20, color: riskColor,
          background: `${riskColor}18`,
        }}>
          {t('fx.riskLabel')}: {riskLevel}
        </span>
      </div>

      {/* Dual bar */}
      <div style={{
        display: 'flex', height: 10, borderRadius: 6, overflow: 'hidden',
        marginBottom: 10, background: 'var(--bg)',
      }}>
        <div style={{
          width: `${tryPct}%`, background: 'var(--firefly)',
          transition: 'width 0.6s ease', minWidth: tryPct > 0 ? 4 : 0,
        }} />
        <div style={{
          width: `${usdPct}%`, background: 'var(--accent-2)',
          transition: 'width 0.6s ease', minWidth: usdPct > 0 ? 4 : 0,
        }} />
      </div>

      {/* Legend */}
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 12 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <span style={{
            width: 8, height: 8, borderRadius: '50%',
            background: 'var(--firefly)', display: 'inline-block',
          }} />
          <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>
            {t('fx.tryLegend', { pct: tryPct })} · {money(tryTotal, 'TRY')}
          </span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <span style={{
            width: 8, height: 8, borderRadius: '50%',
            background: 'var(--accent-2)', display: 'inline-block',
          }} />
          <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>
            {t('fx.fxLegend', { pct: usdPct })} · {money(usdTotal, 'TRY')}
          </span>
        </div>
      </div>

      {/* Currency-risk message */}
      <p style={{ fontSize: 12, color: 'var(--text-muted)', lineHeight: 1.6 }}>
        {riskMessage}
      </p>
    </div>
  )
}
