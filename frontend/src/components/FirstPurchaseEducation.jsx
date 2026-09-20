import { useTranslation } from 'react-i18next'

/**
 * The explainer for an asset type the reader has just bought for the FIRST
 * time.
 *
 * Timing is the whole point. An explainer offered before anyone has bought
 * anything is one more thing to read; the same words the moment money has
 * actually moved are the ones people want, because that is when "what have I
 * just done" is a live question rather than a hypothetical.
 *
 * Shown once per asset type, and only ever once — a card that reappears on
 * the second purchase is nagging, and the reader has already read it.
 */
export default function FirstPurchaseEducation({ assetType, onClose }) {
  const { t, i18n } = useTranslation()
  if (!assetType) return null

  // The category explainers already exist for every type the app can hold,
  // enforced by a conformance test, so there is nothing to invent here.
  const base = `explainer.byCategory.${assetType}`
  if (!i18n.exists(`${base}.what`)) return null

  return (
    <div className="card" style={{ border: '1px solid var(--firefly)' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', gap: 8 }}>
        <strong style={{ fontSize: '1rem' }}>
          🎉 {t('firstPurchase.title', {
            type: t(`holdings.types.${assetType}`, { defaultValue: assetType }),
          })}
        </strong>
        <button
          type="button"
          onClick={onClose}
          aria-label={t('common.close')}
          style={{
            background: 'none', border: 'none', color: 'var(--text-dim)',
            cursor: 'pointer', fontSize: 18, lineHeight: 1, padding: 4,
          }}
        >
          ✕
        </button>
      </div>

      <p style={{ fontSize: 13, opacity: 0.8, margin: '4px 0 10px' }}>
        {t('firstPurchase.subtitle')}
      </p>

      <dl style={{ margin: 0 }}>
        {['what', 'why', 'risk'].map(tab => (
          <div key={tab} style={{ marginBottom: 10 }}>
            <dt style={{ fontWeight: 600, fontSize: 12.5, color: 'var(--firefly)' }}>
              {t(`explainer.tabs.${tab}`, { defaultValue: tab })}
            </dt>
            <dd style={{ margin: '2px 0 0', fontSize: 12.5, lineHeight: 1.65, opacity: 0.9 }}>
              {t(`${base}.${tab}`)}
            </dd>
          </div>
        ))}
      </dl>
    </div>
  )
}
