import { sliceColor } from '../utils/palette'
import { useTranslation } from 'react-i18next'
import { percentFromWeight } from '../utils/format'



/** Quick glance card right under the pie — accented with the EXACT colour of
    the clicked slice, so the chart and the card read as one. */
export default function AssetCard({ allocation, index = 0, color = null, onClose }) {
  const { t } = useTranslation()
  if (!allocation) return null
  // The caller knows the sibling shading; fall back only when it doesn't.
  const accent = color || sliceColor(allocation, index)
  // Sibling shades arrive as hsl(), so alpha can't be appended as hex digits.
  const border = `color-mix(in srgb, ${accent} 33%, transparent)`
  // Several category colours (REIT purple, cash brown) fall under 4.5:1 on this
  // background, so the slice colour marks the card (border, dot) but text stays
  // in readable tokens.
  const share = percentFromWeight(allocation.weight, { decimals: 1 }) || '—'
  return (
    <div style={{
      marginTop: 16, padding: '16px', borderRadius: 10,
      background: 'var(--bg-input)', border: `1px solid ${border}`,
      position: 'relative',
    }}>
      <button
        type="button"
        onClick={onClose}
        aria-label={t('common.close')}
        style={{
          position: 'absolute', top: 0, right: 0,
          width: 'var(--touch-target)', height: 'var(--touch-target)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          background: 'none', border: 'none', borderRadius: 10,
          color: 'var(--text-muted)', cursor: 'pointer', fontSize: 16,
        }}
      >✕</button>
      <div style={{ paddingRight: 'calc(var(--touch-target) - 8px)' }}>
        <p style={{
          fontSize: 'var(--t-small)', color: 'var(--text-muted)', fontWeight: 600, marginBottom: 4,
          display: 'flex', alignItems: 'center', gap: 6,
        }}>
          <span aria-hidden="true" style={{ width: 10, height: 10, borderRadius: '50%', background: accent, flexShrink: 0 }} />
          {t('categories.' + allocation.category, { defaultValue: allocation.category })}
        </p>
        <h3 style={{ fontSize: 'var(--t-lead)', marginBottom: 2 }}>{allocation.name || '—'}</h3>
        <p style={{ fontSize: 'var(--t-small)', marginBottom: 12 }}>{allocation.ticker}</p>
      </div>
      <div style={{ display: 'flex', gap: 16 }}>
        <div>
          <p style={{ fontSize: 'var(--t-small)', color: 'var(--text-muted)' }}>{t('bridge.shareLabel')}</p>
          <p style={{ fontWeight: 700, fontSize: 22, color: 'var(--text)' }}>{share}</p>
        </div>
      </div>
    </div>
  )
}
