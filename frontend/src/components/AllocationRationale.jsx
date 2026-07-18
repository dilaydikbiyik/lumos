import useMarket from '../hooks/useMarket'

/**
 * "Why this allocation?" — the engine's deterministic rationale.
 * No black box: the formula, each asset's role/weight reasoning and
 * every DROPPED asset (with its reason) are visible — no silent pruning.
 */
export default function AllocationRationale({ portfolio }) {
  const { money } = useMarket()
  const logic = portfolio?.metadata?.allocation_logic
  if (!portfolio?.allocations?.length) return null

  return (
    <div className="card">
      <h3 style={{ marginBottom: 4, fontSize: 15 }}>Neden bu dağılım?</h3>
      <p style={{ fontSize: 12, opacity: 0.7, marginBottom: 12 }}>
        Bu oranlar yapay zekanın değil, deterministik bir formülün çıktısı — her adımı burada:
      </p>

      {logic && (
        <div style={{
          padding: '12px 14px', borderRadius: 10, marginBottom: 12,
          background: 'var(--bg-input)', fontSize: 'var(--t-small)', lineHeight: 1.65,
        }}>
          <p style={{ marginBottom: 10 }}>
            Risk skorun <strong>{portfolio.risk_score}/10</strong>. Dağılım iki adımda çıkıyor:
          </p>

          <div style={{ display: 'flex', gap: 10, marginBottom: 10 }}>
            <span style={{
              flexShrink: 0, width: 22, height: 22, borderRadius: '50%',
              background: 'var(--firefly-dim)', color: 'var(--firefly)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontSize: 'var(--t-micro)', fontWeight: 700,
            }}>1</span>
            <div>
              <strong>Ne kadarı güvenli tarafta dursun?</strong><br />
              Risk skoru yükseldikçe nakit ve tahvilin payı azalır. Seninkiyle
              güvenli taraf <strong>%{logic.defensive_target_pct}</strong> oldu — bu kısım
              sert düşüşlerde portföyünün sarsıntısını yumuşatır.
            </div>
          </div>

          <div style={{ display: 'flex', gap: 10 }}>
            <span style={{
              flexShrink: 0, width: 22, height: 22, borderRadius: '50%',
              background: 'var(--firefly-dim)', color: 'var(--firefly)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontSize: 'var(--t-micro)', fontWeight: 700,
            }}>2</span>
            <div>
              <strong>Kalan %{logic.growth_target_pct} nasıl paylaşıldı?</strong><br />
              Büyüme tarafındaki varlıklar oynaklıklarına (fiyatın ne kadar inip
              çıktığına) göre tartıldı. Düşük risk skorunda sakin varlıklar ağır
              basar, yüksek skorda hareketli olanlar.{' '}
              {portfolio.risk_score <= 3.5
                ? 'Senin skorun düşük tarafta, ağırlık sakin varlıklarda.'
                : portfolio.risk_score >= 7
                  ? 'Senin skorun yüksek tarafta, ağırlık hareketli varlıklarda.'
                  : 'Sen ortadasın, ikisi dengeli karıştırıldı.'}
            </div>
          </div>

          {/* The exact formula stays one tap away: plain language for everyone,
              full transparency for anyone who wants to check the arithmetic. */}
          {logic.formula && (
            <details style={{ marginTop: 10 }}>
              <summary style={{
                cursor: 'pointer', fontSize: 'var(--t-micro)', color: 'var(--text-dim)',
              }}>
                Formülün kendisini göster
              </summary>
              <div style={{
                marginTop: 6, fontSize: 'var(--t-micro)', color: 'var(--text-muted)',
                lineHeight: 1.6, fontFamily: 'ui-monospace, SFMono-Regular, monospace',
              }}>
                {logic.formula}
                <div style={{ marginTop: 4 }}>α = {logic.alpha} (risk skorun ÷ 10)</div>
              </div>
            </details>
          )}
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

      <p style={{ fontSize: 'var(--t-micro)', color: 'var(--text-dim)', marginTop: 10, lineHeight: 1.6 }}>
        Bütçen {money(portfolio.budget)} · en fazla {logic?.position_cap ?? '—'} varlığa bölündü ·
        payı %{logic?.min_weight_pct ?? 8}&apos;in altında kalanlar elendi (çok küçük paylar
        takibi zorlaştırır, getiriye katkısı ise ihmal edilebilir)
      </p>
    </div>
  )
}
