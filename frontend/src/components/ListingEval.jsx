import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { useNavigate } from 'react-router-dom'
import api, { extractErrorMessage } from '../utils/api'
import useMarket from '../hooks/useMarket'

/**
 * "Is this listing a fair price?"
 *
 * Paste what the listing says; get the asking price per m² against what the
 * area actually trades at, plus the questions to ask before anyone signs.
 *
 * It refuses in markets whose area data is an INDEX rather than a price
 * level, and the refusal is shown as prominently as a verdict would be. That
 * is the honest outcome, not a failure to display: a made-up number here
 * costs somebody a fair property or an unfair price.
 *
 * The caveat sits WITH the verdict rather than under it. A province average
 * against one specific flat is the weakness of the whole comparison, and the
 * reader has to hold both facts at the same time.
 */
const VERDICT_COLOR = {
  below: 'var(--firefly)',
  fair: 'var(--green)',
  above: 'var(--firefly)',
  well_above: 'var(--red, #f87171)',
}

export default function ListingEval({ areas = [] }) {
  const { t } = useTranslation()
  const { money } = useMarket()
  const navigate = useNavigate()
  const [form, setForm] = useState({ area_code: '', size_m2: '', asking_price: '' })
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const digits = (value) => Number(String(value).replace(/[^\d]/g, ''))

  async function run(e) {
    e.preventDefault()
    const size = digits(form.size_m2)
    const price = digits(form.asking_price)
    if (!form.area_code || !size || !price || loading) return
    setLoading(true)
    setError(null)
    setResult(null)
    try {
      const { data } = await api.post('/planning/listing-eval', {
        area_code: form.area_code, size_m2: size, asking_price: price,
      })
      setResult(data)
    } catch (err) {
      setError(extractErrorMessage(err))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="card">
      <h3 style={{ margin: '0 0 4px', fontSize: '1rem' }}>🔎 {t('listingEval.title')}</h3>
      <p style={{ fontSize: 13, opacity: 0.8, marginTop: 0 }}>{t('listingEval.subtitle')}</p>

      <form onSubmit={run} style={{ display: 'grid', gap: 8, marginTop: 10 }}>
        <select
          value={form.area_code}
          onChange={e => setForm({ ...form, area_code: e.target.value })}
          aria-label={t('listingEval.pickArea')}
        >
          <option value="">{t('listingEval.pickArea')}</option>
          {areas.map(a => <option key={a.code} value={a.code}>{a.name}</option>)}
        </select>
        <input
          value={form.size_m2}
          onChange={e => setForm({ ...form, size_m2: e.target.value })}
          inputMode="numeric"
          placeholder={t('listingEval.sizePlaceholder')}
          aria-label={t('listingEval.sizePlaceholder')}
        />
        <input
          value={form.asking_price}
          onChange={e => setForm({ ...form, asking_price: e.target.value })}
          inputMode="numeric"
          placeholder={t('listingEval.pricePlaceholder')}
          aria-label={t('listingEval.pricePlaceholder')}
        />
        <button className="btn btn-primary btn-full" type="submit" disabled={loading}>
          {loading ? <span className="spinner" style={{ width: 18, height: 18 }} /> : t('listingEval.run')}
        </button>
      </form>

      {error && (
        <p role="alert" style={{ color: 'var(--red, #f87171)', fontSize: 13, marginTop: 10 }}>{error}</p>
      )}

      {result && !result.available && (
        <p style={{ fontSize: 12.5, lineHeight: 1.7, marginTop: 12, opacity: 0.85 }}>
          {result.reason}
        </p>
      )}

      {result?.available && (
        <div style={{ marginTop: 14 }}>
          <div style={{
            padding: '10px 12px', borderRadius: 10,
            border: `1px solid ${VERDICT_COLOR[result.verdict] || 'var(--border)'}`,
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', gap: 8 }}>
              <span style={{ fontSize: 12, opacity: 0.75 }}>{t('listingEval.thisListing')}</span>
              <strong style={{ fontSize: 13 }}>{money(result.listing_per_m2)}/m²</strong>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', gap: 8, marginTop: 2 }}>
              <span style={{ fontSize: 12, opacity: 0.75 }}>
                {t('listingEval.areaAverage', { area: result.area })}
              </span>
              <strong style={{ fontSize: 13 }}>{money(result.area_per_m2)}/m²</strong>
            </div>
            <p style={{
              fontSize: 13, lineHeight: 1.65, margin: '8px 0 0',
              color: VERDICT_COLOR[result.verdict],
            }}>
              {result.verdict_text}
            </p>
          </div>

          <p style={{ fontSize: 11.5, opacity: 0.7, lineHeight: 1.6, marginTop: 8 }}>
            {result.caveat}
          </p>

          {/* Closing the loop: if they go through with it, the details they
              just typed should not have to be typed again. */}
          <button
            className="btn btn-ghost btn-full"
            style={{ marginTop: 10 }}
            onClick={() => navigate('/holdings', {
              state: {
                prefillHolding: {
                  asset_type: 'real_estate',
                  name: `${result.area} · ${digits(form.size_m2)} m²`,
                  purchase_amount: String(digits(form.asking_price)),
                },
              },
            })}
          >
            {t('listingEval.boughtIt')}
          </button>

          <h4 style={{ fontSize: 13, margin: '14px 0 4px' }}>{t('listingEval.askThese')}</h4>
          <ul style={{ margin: 0, paddingLeft: 18, fontSize: 12.5, lineHeight: 1.7 }}>
            {result.questions.map((q, i) => <li key={i} style={{ marginBottom: 5 }}>{q}</li>)}
          </ul>
        </div>
      )}
    </div>
  )
}
