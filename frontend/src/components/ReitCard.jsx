export default function ReitCard({ explanation }) {
  return (
    <div className="card" style={{
      borderColor: 'rgba(91,142,240,0.3)',
      background: 'linear-gradient(135deg, var(--bg-card) 0%, rgba(91,142,240,0.06) 100%)',
    }}>
      <div style={{ display: 'flex', gap: 12, alignItems: 'flex-start' }}>
        <span style={{
          fontSize: 28,
          filter: 'drop-shadow(0 0 8px rgba(91,142,240,0.3))',
        }}>🏢</span>
        <div>
          <div style={{ display: 'flex', gap: 8, alignItems: 'center', marginBottom: 8 }}>
            <h3 style={{ fontSize: 15 }}>Gayrimenkul Yatırımı: REIT ETF</h3>
            <span className="badge badge-accent" style={{ fontSize: 11 }}>Dahil</span>
          </div>
          <p style={{ fontSize: 13, lineHeight: 1.65, color: 'var(--text-muted)', marginBottom: explanation ? 12 : 0 }}>
            Bütçen doğrudan emlak almaya yetmediğinde, <strong style={{ color: 'var(--text)' }}>REIT ETF'leri</strong> ile 
            gayrimenkul piyasasına yatırım yapabilirsin. Bunlar hisse gibi alınıp satılan, 
            içinde onlarca ticari bina ve konut barındıran sepetlerdir — mülk almadan emlak getirisine ortak olursun.
          </p>
          <div style={{ fontSize: 12, color: 'var(--text-dim)', marginBottom: explanation ? 12 : 0 }}>
            📊 <strong>VNQ</strong> (Vanguard REIT) · <strong>SCHH</strong> (Schwab US REIT)
          </div>
          {explanation && (
            <div style={{
              fontSize: 13, color: 'var(--text)', lineHeight: 1.65,
              borderLeft: '3px solid var(--accent-2)', paddingLeft: 12,
              background: 'rgba(91,142,240,0.06)', padding: '10px 12px',
              borderRadius: '0 var(--radius-xs) var(--radius-xs) 0',
            }}>
              {explanation}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
