import { useTranslation } from 'react-i18next'
import { useNavigate } from 'react-router-dom'

/**
 * What a "real estate only" reader sees instead of a stock portfolio.
 *
 * The nav hides this page for them, but a bookmark, a deep link or the
 * dashboard invitation still lands here — and the page's whole job is to
 * generate a stock allocation. Doing that anyway would be the app overruling
 * the answer it asked for, which is the one thing the path feature exists to
 * prevent: flows are chosen, never forced.
 *
 * Not a wall either. It explains, points at the half they did choose, and
 * leaves a door open — because "no stock recommendation FORCED on you" is not
 * the same as "no stock recommendation available to you".
 */
export default function RealEstatePathNotice({ onShowAnyway }) {
  const { t } = useTranslation()
  const navigate = useNavigate()

  return (
    <div className="card" style={{ borderStyle: 'dashed' }}>
      <h3 style={{ margin: '0 0 6px', fontSize: '1rem' }}>
        🏘️ {t('realEstatePath.title')}
      </h3>
      <p style={{ fontSize: 13, lineHeight: 1.7, opacity: 0.85, marginTop: 0 }}>
        {t('realEstatePath.body')}
      </p>

      <button className="btn btn-primary btn-full" onClick={() => navigate('/explore')}>
        {t('realEstatePath.toExplore')}
      </button>
      <button
        className="btn btn-ghost btn-full"
        style={{ marginTop: 8 }}
        onClick={onShowAnyway}
      >
        {t('realEstatePath.showAnyway')}
      </button>
      <p style={{ fontSize: 12, opacity: 0.6, margin: '10px 0 0', textAlign: 'center' }}>
        {t('realEstatePath.changePath')}
      </p>
    </div>
  )
}
