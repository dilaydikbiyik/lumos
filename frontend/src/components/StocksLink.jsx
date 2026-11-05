import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'

/**
 * The way into the stock explorer, from where the question arises.
 *
 * On the portfolio page it sits under the funds, because "which companies
 * are in these?" is the question a reader has just after seeing fund names.
 * On the dashboard it sits with the market news. Both lead to the same
 * page, which describes companies and never recommends one.
 */
export default function StocksLink() {
  const { t } = useTranslation()
  const navigate = useNavigate()
  return (
    <button type="button" className="card" onClick={() => navigate('/stocks')}
            style={{
              width: '100%', textAlign: 'left', cursor: 'pointer', color: 'inherit',
              font: 'inherit', display: 'flex', justifyContent: 'space-between',
              alignItems: 'center', gap: 12, minHeight: 44,
            }}>
      <span>
        <strong style={{ fontSize: 14 }}>🔎 {t('stocks.cta')}</strong>
        <span style={{ display: 'block', fontSize: 12.5, opacity: 0.8, marginTop: 2 }}>
          {t('stocks.ctaSub')}
        </span>
      </span>
      <span aria-hidden="true" style={{ opacity: 0.6 }}>→</span>
    </button>
  )
}
