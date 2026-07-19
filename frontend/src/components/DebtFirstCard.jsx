import useMarket from '../hooks/useMarket'

/**
 * "Pay this off first" — shown when the user carries credit-card or consumer
 * debt. Telling someone not to invest yet costs us the more engaging path,
 * which is exactly why it has to be here: no app with something to sell would
 * say it, and the arithmetic is not close.
 */
export default function DebtFirstCard({ check }) {
  const { money } = useMarket()
  if (!check) return null

  return (
    <div className="card" style={{ borderColor: 'var(--red)' }}>
      <h3 style={{ marginBottom: 6 }}>Önce şunu konuşalım</h3>

      <p style={{ fontSize: 14, lineHeight: 1.75, marginBottom: 12 }}>
        <strong>{money(check.debt)}</strong> kredi kartı / ihtiyaç kredisi borcun var.
        Bu borç yılda yaklaşık <strong>%{check.debt_annual_pct}</strong> faizle büyüyor.
        Senin risk profiline uygun bir portföyün uzun vadeli beklentisi ise yılda
        yaklaşık <strong>%{check.portfolio_annual_pct}</strong> — ve bu bir beklenti,
        garanti değil.
      </p>

      {/* The comparison, side by side, on the same amount and the same year. */}
      <div style={{
        display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10, marginBottom: 12,
      }}>
        <div style={{
          padding: 12, borderRadius: 10,
          border: '1px solid var(--border)', background: 'var(--bg-input)',
        }}>
          <div style={{ fontSize: 12, opacity: 0.75, marginBottom: 4 }}>
            {money(check.applied)} ile borcu kapatırsan
          </div>
          <div className="num-lead" style={{ color: 'var(--green, #3DD68C)' }}>
            +{money(check.interest_avoided)}
          </div>
          <div style={{ fontSize: 11, opacity: 0.65, marginTop: 2 }}>
            bir yılda ödemediğin faiz — kesin
          </div>
        </div>
        <div style={{
          padding: 12, borderRadius: 10,
          border: '1px solid var(--border)', background: 'var(--bg-input)',
        }}>
          <div style={{ fontSize: 12, opacity: 0.75, marginBottom: 4 }}>
            Aynı parayı yatırırsan
          </div>
          <div className="num-lead">+{money(check.investment_gain)}</div>
          <div style={{ fontSize: 11, opacity: 0.65, marginTop: 2 }}>
            bir yılda beklenen getiri — garanti değil
          </div>
        </div>
      </div>

      <div style={{
        padding: '10px 14px', borderRadius: 'var(--radius-xs)',
        background: 'var(--firefly-dim)', fontSize: 13.5, lineHeight: 1.7,
      }}>
        Borcu kapatmak, bu yıl için <strong>{money(check.advantage)}</strong> daha
        iyi — üstelik risk almadan.{' '}
        {check.covers_debt ? (
          <>Bütçen borcu kapatmaya yetiyor; kalan{' '}
          <strong>{money(check.leftover_after_repayment)}</strong> ile yatırıma
          gönül rahatlığıyla başlayabilirsin.</>
        ) : (
          <>Önce borcu bitir, sonra buraya dön. Portföyün seni bekliyor olacak.</>
        )}
      </div>

      <p style={{ fontSize: 11, color: 'var(--text-dim)', marginTop: 10, lineHeight: 1.5 }}>
        Hesapta kart faizi aylık %{check.assumptions.card_monthly_rate_pct} varsayıldı
        (yıllık bileşik %{check.debt_annual_pct}). Bu bir planlama varsayımıdır, güncel
        resmî oran değil — TCMB dönemsel olarak günceller. Kendi ekstrendeki orana bak;
        rakam değişir, yön değişmez. Aşağıdaki portföyü yine de
        inceleyebilirsin — hazır olduğunda burada.
      </p>
    </div>
  )
}
