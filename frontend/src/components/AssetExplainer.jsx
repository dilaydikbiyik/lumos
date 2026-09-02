import { useState } from 'react'
import { useTranslation } from 'react-i18next'

/**
 * "What is it / why is it in your portfolio / what's the risk" card for
 * every portfolio item. Static dictionary based — no LLM call, zero cost.
 *
 * The educational copy lives in the locale files (explainer.byTicker.* /
 * explainer.byCategory.*); only language-independent presentation stays here.
 * Ticker dots are folded to underscores because "." nests i18next keys.
 */

const ASSET_META = {
  'XU100.IS': { icon: '🇹🇷', color: 'var(--red)' },
  'SPY':      { icon: '🇺🇸', color: 'var(--accent-2)' },
  'QQQ':      { icon: '💻', color: '#9B59B6' },
  'GLD':      { icon: '🥇', color: 'var(--firefly)' },
  'VNQ':      { icon: '🏢', color: 'var(--accent-2)' },
  'SCHH':     { icon: '🏠', color: 'var(--green)' },
}

const CATEGORY_META = {
  stocks: { icon: '📈', color: 'var(--accent)' },
  gold:   { icon: '🥇', color: 'var(--firefly)' },
  fund:   { icon: '🧺', color: 'var(--accent)' },
}

export default function AssetExplainer({ allocation, onClose, color }) {
  const { t, i18n } = useTranslation()
  const [activeTab, setActiveTab] = useState('what')

  const tickerKey = (allocation.ticker || '').replace(/\./g, '_')
  const hasTickerCopy = i18n.exists(`explainer.byTicker.${tickerKey}.what`)
  const category = CATEGORY_META[allocation.category] ? allocation.category : 'stocks'
  const base = hasTickerCopy
    ? `explainer.byTicker.${tickerKey}`
    : `explainer.byCategory.${category}`
  const meta = (hasTickerCopy && ASSET_META[allocation.ticker]) || CATEGORY_META[category]

  // The pie slice's colour wins — the card must match what was clicked
  const accent = color || meta.color

  const tabs = [
    { key: 'what', label: t('explainer.tabs.what'), icon: '📖' },
    { key: 'why',  label: t('explainer.tabs.why'),  icon: '🎯' },
    { key: 'risk', label: t('explainer.tabs.risk'), icon: '⚡' },
  ]

  return (
    <div className="card" style={{
      border: `1px solid ${accent}22`,
      background: `linear-gradient(135deg, var(--bg-card) 0%, ${accent}08 100%)`,
      animation: 'fade-in 0.3s ease',
      position: 'relative',
    }}>
      <button
        onClick={onClose}
        style={{
          position: 'absolute', top: 12, right: 12,
          background: 'none', border: 'none', color: 'var(--text-dim)',
          cursor: 'pointer', fontSize: 18, padding: '4px 8px',
        }}
        aria-label={t('common.close')}
      >
        ✕
      </button>

      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 14 }}>
        <span style={{
          fontSize: 28,
          filter: `drop-shadow(0 0 8px ${accent}40)`,
        }}>{meta.icon}</span>
        <div>
          <h3 style={{ fontSize: 15, fontWeight: 700 }}>
            {allocation.name}
          </h3>
          <div style={{ fontSize: 12, color: 'var(--text-dim)', display: 'flex', gap: 8, marginTop: 2 }}>
            <span>{allocation.ticker}</span>
            <span>·</span>
            <span>{t(`${base}.type`)}</span>
            <span>·</span>
            <span style={{ color: accent, fontWeight: 600 }}>
              %{(allocation.weight * 100).toFixed(0)}
            </span>
          </div>
        </div>
      </div>

      {/* Tab selector */}
      <div style={{
        display: 'flex', gap: 4, marginBottom: 14,
        background: 'var(--bg)', borderRadius: 'var(--radius-xs)',
        padding: 3,
      }}>
        {tabs.map(tab => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            style={{
              flex: 1, padding: '8px 4px',
              background: activeTab === tab.key ? 'var(--bg-card-2)' : 'transparent',
              border: activeTab === tab.key ? `1px solid ${accent}33` : '1px solid transparent',
              borderRadius: 'var(--radius-xs)',
              color: activeTab === tab.key ? 'var(--text)' : 'var(--text-dim)',
              fontSize: 12, fontWeight: activeTab === tab.key ? 600 : 400,
              cursor: 'pointer', transition: 'all 0.2s ease',
              display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 4,
            }}
          >
            <span style={{ fontSize: 13 }}>{tab.icon}</span>
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab content */}
      <p style={{
        fontSize: 13.5, lineHeight: 1.7, color: 'var(--text)',
        animation: 'fade-in 0.2s ease',
      }}>
        {t(`${base}.${activeTab}`)}
      </p>
    </div>
  )
}
