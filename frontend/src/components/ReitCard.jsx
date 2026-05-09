export default function ReitCard({ explanation }) {
  return (
    <div className="card" style={{ borderColor: 'var(--accent-2)', marginBottom: 4 }}>
      <div style={{ display: 'flex', gap: 12, alignItems: 'flex-start' }}>
        <span style={{ fontSize: 28 }}>🏢</span>
        <div>
          <div style={{ display: 'flex', gap: 8, alignItems: 'center', marginBottom: 6 }}>
            <h3>Real Estate Exposure via REITs</h3>
            <span className="badge badge-accent">Included</span>
          </div>
          <p style={{ fontSize: 13, marginBottom: explanation ? 10 : 0 }}>
            Your budget is below the threshold for direct real estate investment.
            Lumos has included <strong>VNQ</strong> and <strong>SCHH</strong> — US REIT ETFs —
            to give you real estate exposure without buying property.
          </p>
          {explanation && (
            <p style={{ fontSize: 13, color: 'var(--text)', fontStyle: 'italic', borderLeft: '3px solid var(--accent-2)', paddingLeft: 12 }}>
              {explanation}
            </p>
          )}
        </div>
      </div>
    </div>
  )
}
