import { useEffect, useMemo, useState } from 'react'
import { useTranslation } from 'react-i18next'
import AppHeader from '../components/AppHeader'
import Disclaimer from '../components/Disclaimer'
import api from '../utils/api'
import { percent } from '../utils/format'

/**
 * The stock explorer: as broad as a brokerage's list, built to teach.
 *
 * Asked for because the portfolio page only ever names funds, and a reader
 * who has heard of THYAO, Apple or SAP wants to see them. The page lists the
 * largest companies on their market's exchange — and is built so that it
 * cannot become a recommendation, because that is the line the legal review
 * is about:
 *
 *  - the list is the same for every reader on a market; the endpoint never
 *    sees the profile;
 *  - it is sorted by NAME, so it is never a leaderboard of last year's
 *    winners;
 *  - nothing says buy, suits or fits.
 *
 * What each row teaches is the measured comparison a beginner most needs
 * before picking a single company: over the same five years, how far did it
 * fall at its worst, and how far did the whole index fall? The headline
 * counts how many in the current view fell harder — on live data, 25 of 25
 * in Türkiye. That number is the argument for the funds on the portfolio
 * page, made by the reader's own scrolling rather than by the app's say-so.
 */
export default function StocksPage() {
  const { t, i18n } = useTranslation()
  const [data, setData] = useState(null)
  const [error, setError] = useState(false)
  const [query, setQuery] = useState('')
  const [sector, setSector] = useState('')
  const [open, setOpen] = useState(null)

  useEffect(() => {
    let cancelled = false
    api.get('/stocks/explore')
      .then(res => { if (!cancelled) setData(res.data) })
      .catch(() => { if (!cancelled) setError(true) })
    return () => { cancelled = true }
  }, [])

  const stocks = useMemo(() => data?.stocks || [], [data])
  const sectors = useMemo(() => [...new Set(stocks.map(s => s.sector))].sort(), [stocks])
  const shown = useMemo(() => {
    const q = query.trim().toLocaleLowerCase()
    // Sorted again here, in the reader's own alphabet. The API sorts by name
    // with a plain casefold, which puts Şişecam and Türk Hava Yolları after
    // "Z" — alphabetical in Unicode, not in Turkish.
    const collator = new Intl.Collator(i18n.language)
    return stocks
      .filter(s => (!sector || s.sector === sector)
        && (!q || s.name.toLocaleLowerCase().includes(q) || s.ticker.toLocaleLowerCase().includes(q)))
      .sort((a, b) => collator.compare(a.name, b.name))
  }, [stocks, query, sector, i18n.language])

  const index = data?.index
  const harder = index ? shown.filter(s => s.worst_drop_pct < index.worst_drop_pct).length : 0

  return (
    <div className="page">
      <AppHeader />
      <div className="page-content" style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
        <div>
          <h2>{t('stocks.title')}</h2>
          <p style={{ fontSize: 13, marginTop: 4 }}>{t('stocks.subtitle')}</p>
        </div>

        {/* Said before the list, not under it: this is the page's terms. */}
        <div className="card" style={{ borderColor: 'var(--firefly-dim)', fontSize: 12.5, lineHeight: 1.6 }}>
          <strong>{t('stocks.notAdviceTitle')}</strong>
          <p style={{ margin: '4px 0 0' }}>{t('stocks.notAdvice')}</p>
          {data?.as_of && (
            <p style={{ margin: '6px 0 0', color: 'var(--text-dim)' }}>
              {t('stocks.asOf', { date: data.as_of, years: data.window_years })}
              {' '}
              {t(data.dividends_included ? 'stocks.basisTotal' : 'stocks.basisPrice')}
            </p>
          )}
        </div>

        {error && <p style={{ fontSize: 13, color: 'var(--text-dim)' }}>{t('stocks.error')}</p>}
        {!data && !error && <div className="spinner" style={{ margin: '24px auto' }} />}
        {data && !data.available && <p style={{ fontSize: 13 }}>{t('stocks.unavailable')}</p>}

        {index && shown.length > 0 && (
          <div className="card">
            <strong style={{ fontSize: 15 }}>
              {t('stocks.lessonHeadline', { harder, total: shown.length })}
            </strong>
            <p style={{ fontSize: 12.5, lineHeight: 1.6, margin: '6px 0 0' }}>
              {t('stocks.indexLine', {
                index: index.name || index.ticker,
                drop: percent(index.worst_drop_pct),
                real: index.real_change_pct == null ? '—' : percent(index.real_change_pct),
              })}
            </p>
          </div>
        )}

        {stocks.length > 0 && (
          <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
            <input className="input" style={{ flex: '1 1 180px' }} value={query}
                   placeholder={t('stocks.search')} aria-label={t('stocks.search')}
                   onChange={e => setQuery(e.target.value)} />
            <select className="input" style={{ flex: '0 1 200px' }} value={sector}
                    aria-label={t('stocks.sectorFilter')}
                    onChange={e => setSector(e.target.value)}>
              <option value="">{t('stocks.allSectors')}</option>
              {sectors.map(s => <option key={s} value={s}>{t(`stocks.sector.${s}`)}</option>)}
            </select>
          </div>
        )}

        {stocks.length > 0 && shown.length === 0 && (
          <p style={{ fontSize: 13, color: 'var(--text-dim)' }}>{t('stocks.empty')}</p>
        )}

        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          {shown.map(s => {
            const expanded = open === s.ticker
            const fellHarder = index && s.worst_drop_pct < index.worst_drop_pct
            return (
              <div key={s.ticker} className="card" style={{ padding: 0 }}>
                <button type="button" onClick={() => setOpen(expanded ? null : s.ticker)}
                        aria-expanded={expanded}
                        style={{
                          width: '100%', background: 'none', border: 'none', cursor: 'pointer',
                          color: 'inherit', font: 'inherit', textAlign: 'left', padding: '12px 14px',
                          display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                          gap: 12, minHeight: 44,
                        }}>
                  <span style={{ minWidth: 0 }}>
                    <strong style={{ fontSize: 14 }}>{s.name}</strong>
                    <span style={{ display: 'block', fontSize: 11.5, color: 'var(--text-dim)' }}>
                      {s.ticker} · {t(`stocks.sector.${s.sector}`)}
                    </span>
                  </span>
                  <span style={{ textAlign: 'right', flexShrink: 0 }}>
                    <span className="num" style={{ fontSize: 13, fontWeight: 700,
                      color: fellHarder ? 'var(--red)' : 'inherit' }}>
                      {percent(s.worst_drop_pct)}
                    </span>
                    <span style={{ display: 'block', fontSize: 10.5, color: 'var(--text-dim)' }}>
                      {t('stocks.worstDrop')}
                    </span>
                  </span>
                </button>
                {expanded && (
                  <div style={{ padding: '0 14px 14px', fontSize: 12.5, lineHeight: 1.65 }}>
                    <p style={{ margin: 0 }}>
                      {t(fellHarder ? 'stocks.lessonHarder' : 'stocks.lessonCalmer', {
                        drop: percent(s.worst_drop_pct),
                        index: percent(index?.worst_drop_pct),
                      })}
                    </p>
                    <p style={{ margin: '6px 0 0' }}>
                      {t('stocks.swing', { times: s.swing_vs_index })}
                    </p>
                    <p style={{ margin: '6px 0 0', color: 'var(--text-dim)' }}>
                      {s.real_change_pct == null
                        ? t('stocks.nominalOnly', { change: percent(s.change_pct) })
                        : t('stocks.realReturn', { real: percent(s.real_change_pct), nominal: percent(s.change_pct) })}
                    </p>
                  </div>
                )}
              </div>
            )
          })}
        </div>

        <Disclaimer />
      </div>
    </div>
  )
}
