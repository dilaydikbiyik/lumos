import { useMemo, useState } from 'react'
import { useTranslation } from 'react-i18next'

/**
 * The whole glossary, in one place, searchable.
 *
 * The definitions already existed and were good. They were reachable from
 * four `IsikTut` tooltips in the entire app, while the word "inflation"
 * alone appears unlinked in twenty-three separate strings — so a beginner who
 * did not know a term had no way to look it up, which is the exact moment
 * this app is supposed to be useful.
 *
 * A list is deliberately chosen over inlining links into all seventy-eight
 * occurrences: that would mean rewriting seventy-eight translated strings in
 * three languages into `<Trans>` markers, and each rewrite is a chance to
 * break a sentence in a language nobody on the team reads back.
 *
 * Terms are keyed by stable Turkish ids — Türkiye was the first market — and
 * each entry carries the word as its own language writes it, so nothing here
 * assumes the reader's language matches the key.
 */
export default function Glossary({ onClose }) {
  const { t, i18n } = useTranslation()
  const [query, setQuery] = useState('')
  // Captured as a value. `i18n` is a stable object whose `language` is
  // mutated in place, so depending on the object alone would keep a memo
  // computed in the previous language after the reader switches.
  const lang = i18n.language

  const entries = useMemo(() => {
    // `t(..., returnObjects)` rather than `getResourceBundle`: the latter
    // reaches into how locales happen to be registered, returns nothing for a
    // bundle that has not lazily loaded yet, and skips the language fallback
    // chain entirely. `t` honours de -> en -> tr, so a term translated in only
    // one language still renders something the reader can use.
    const all = t('glossary', { returnObjects: true, defaultValue: {} })
    if (!all || typeof all !== 'object') return []
    return Object.entries(all)
      .map(([id, entry]) => ({ id, label: entry.label || id, text: entry.text || '' }))
      .filter(e => e.text)
      .sort((a, b) => a.label.localeCompare(b.label, lang))
  }, [t, lang])

  const shown = useMemo(() => {
    const q = query.trim().toLocaleLowerCase(lang)
    if (!q) return entries
    return entries.filter(e =>
      e.label.toLocaleLowerCase(lang).includes(q) ||
      e.text.toLocaleLowerCase(lang).includes(q))
  }, [entries, query, lang])

  return (
    <div className="card" style={{ marginTop: '1rem' }}>
      <div style={{
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        gap: 12, marginBottom: 4,
      }}>
        <h3 style={{ margin: 0, fontSize: '1rem' }}>
          💡 {t('glossaryPage.title')}
        </h3>
        {onClose && (
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
        )}
      </div>
      <p style={{ fontSize: 13, opacity: 0.8, marginTop: 0 }}>
        {t('glossaryPage.subtitle')}
      </p>

      <input
        value={query}
        onChange={e => setQuery(e.target.value)}
        placeholder={t('glossaryPage.search')}
        aria-label={t('glossaryPage.search')}
        style={{ width: '100%', marginBottom: 12 }}
      />

      {shown.length === 0 ? (
        <p style={{ fontSize: 13, opacity: 0.7 }}>
          {t('glossaryPage.noMatch', { query: query.trim() })}
        </p>
      ) : (
        <dl style={{ margin: 0 }}>
          {shown.map(entry => (
            <div key={entry.id} style={{
              paddingBottom: 10, marginBottom: 10,
              borderBottom: '1px solid var(--border)',
            }}>
              <dt style={{ fontWeight: 600, color: 'var(--firefly)' }}>{entry.label}</dt>
              <dd style={{ margin: '4px 0 0', fontSize: 13, lineHeight: 1.6, opacity: 0.9 }}>
                {entry.text}
              </dd>
            </div>
          ))}
        </dl>
      )}
    </div>
  )
}
