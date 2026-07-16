import { CATEGORY_COLORS, COLORS } from '../utils/palette'

const CATEGORY_LABELS = {
  stocks: 'Hisse Senetleri', reit: 'Gayrimenkul (REIT)', fund: 'Yatırım Fonu',
  gold: 'Kıymetli Maden', bond: 'Tahvil / Sabit Getiri', cash: 'Nakit / Para Piyasası',
}

/** Quick glance card right under the pie — accented with the EXACT colour of
    the clicked slice, so the chart and the card read as one. */
export default function AssetCard({ allocation, index = 0, onClose }) {
  if (!allocation) return null
  const accent = CATEGORY_COLORS[allocation.category] || COLORS[index % COLORS.length]
  return (
    <div style={{
      marginTop: 16, padding: '16px', borderRadius: 10,
      background: 'var(--bg-input)', border: `1px solid ${accent}55`,
      position: 'relative',
    }}>
      <button
        onClick={onClose}
        aria-label="Kapat"
        style={{ position: 'absolute', top: 10, right: 10, background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', fontSize: 16 }}
      >✕</button>
      <p style={{ fontSize: 11, color: accent, fontWeight: 600, marginBottom: 4 }}>
        {CATEGORY_LABELS[allocation.category] || allocation.category}
      </p>
      <h3 style={{ marginBottom: 2 }}>{allocation.name}</h3>
      <p style={{ fontSize: 12, marginBottom: 12 }}>{allocation.ticker}</p>
      <div style={{ display: 'flex', gap: 16 }}>
        <div>
          <p style={{ fontSize: 11, color: 'var(--text-dim)' }}>Portföydeki payı</p>
          <p style={{ fontWeight: 700, fontSize: 22, color: accent }}>
            {(allocation.weight * 100).toFixed(1)}%
          </p>
        </div>
      </div>
    </div>
  )
}
