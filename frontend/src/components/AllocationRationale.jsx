const fmt = n => new Intl.NumberFormat('tr-TR', { maximumFractionDigits: 0 }).format(n)

/**
 * "Neden bu dağılım?" — motorun deterministik gerekçeleri.
 * Kara kutu yok: formül, her varlığın rolü/ağırlık gerekçesi ve
 * ELENEN varlıklar nedenleriyle görünür (sessiz eleme yapılmaz).
 */
export default function AllocationRationale({ portfolio }) {
  const logic = portfolio?.metadata?.allocation_logic
  if (!portfolio?.allocations?.length) return null

  return (
    <div className="card">
      <h3 style={{ marginBottom: 4, fontSize: 15 }}>🧮 Neden bu dağılım?</h3>
      <p style={{ fontSize: 12, opacity: 0.7, marginBottom: 12 }}>
        Bu oranlar yapay zekanın değil, deterministik bir formülün çıktısı — her adımı burada:
      </p>

      {logic?.formula && (
        <div style={{
          padding: '8px 12px', borderRadius: 10, marginBottom: 12,
          background: 'var(--bg-input)', fontSize: 12, lineHeight: 1.6,
        }}>
          <strong>Formül:</strong> {logic.formula}
          <div style={{ opacity: 0.7 }}>Senin α değerin: {logic.alpha} (risk skorun ÷ 10)</div>
        </div>
      )}

      <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
        {portfolio.allocations.map(a => (
          <div key={a.ticker} style={{ display: 'flex', gap: 10, alignItems: 'flex-start' }}>
            <span style={{
              minWidth: 52, textAlign: 'center', padding: '3px 6px',
              borderRadius: 8, fontSize: 12, fontWeight: 700,
              background: 'var(--firefly-dim)', color: 'var(--firefly, #F5A524)',
            }}>
              %{Math.round(a.weight * 100)}
            </span>
            <div style={{ fontSize: 13, lineHeight: 1.5 }}>
              <strong>{a.name}</strong>
              <div style={{ fontSize: 12, opacity: 0.7 }}>{a.explanation}</div>
            </div>
          </div>
        ))}
      </div>

      {logic?.dropped?.length > 0 && (
        <div style={{ marginTop: 14, paddingTop: 10, borderTop: '1px dashed var(--border)' }}>
          <p style={{ fontSize: 12, fontWeight: 700, marginBottom: 6, opacity: 0.8 }}>
            Neden {portfolio.allocations.length} pozisyon? Şunlar bilinçli olarak elendi:
          </p>
          {logic.dropped.map((d, i) => (
            <p key={i} style={{ fontSize: 12, opacity: 0.65, lineHeight: 1.55 }}>
              • <strong>{d.ticker}</strong> (%{d.weight_pct} olurdu): {d.reason}
            </p>
          ))}
        </div>
      )}

      <p style={{ fontSize: 11, opacity: 0.55, marginTop: 10 }}>
        Bütçen: {fmt(portfolio.budget)} TL · Azami pozisyon: {logic?.position_cap ?? '—'} ·
        Kırıntı eşiği: %{logic?.min_weight_pct ?? 8}
      </p>
    </div>
  )
}
