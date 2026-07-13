const CATEGORY_LABELS = {
  stocks: 'Equities', reit: 'Real Estate', fund: 'Investment Fund',
  gold: 'Commodity', bond: 'Bonds / Fixed Income', cash: 'Cash / Money Market',
}

export default function AssetCard({ allocation, onClose }) {
  if (!allocation) return null
  return (
    <div style={{
      marginTop: 16, padding: '16px', borderRadius: 10,
      background: 'var(--bg-input)', border: '1px solid var(--border-light)',
      position: 'relative',
    }}>
      <button
        onClick={onClose}
        style={{ position: 'absolute', top: 10, right: 10, background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', fontSize: 16 }}
      >✕</button>
      <p style={{ fontSize: 11, color: 'var(--accent)', fontWeight: 600, marginBottom: 4 }}>
        {CATEGORY_LABELS[allocation.category] || allocation.category}
      </p>
      <h3 style={{ marginBottom: 2 }}>{allocation.name}</h3>
      <p style={{ fontSize: 12, marginBottom: 12 }}>{allocation.ticker}</p>
      <div style={{ display: 'flex', gap: 16 }}>
        <div>
          <p style={{ fontSize: 11, color: 'var(--text-dim)' }}>Allocation</p>
          <p style={{ fontWeight: 700, fontSize: 22, color: 'var(--accent)' }}>
            {(allocation.weight * 100).toFixed(1)}%
          </p>
        </div>
      </div>
    </div>
  )
}
