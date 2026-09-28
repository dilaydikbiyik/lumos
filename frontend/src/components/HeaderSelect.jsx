/**
 * The styled `<select>` used by the header pickers.
 *
 * Extracted because the market and language switchers had carried the same
 * label-and-select shell as two copies — including, verbatim, the comment
 * explaining a padding fix. A fix applied twice by copy is a fix that will be
 * applied once next time, and the second copy silently keeps the bug.
 *
 * It owns PRESENTATION only. What the options are, what they say and what
 * choosing one does stay with each picker, because the market and the
 * language are independent choices and sharing a widget must not become
 * sharing a decision — `independence.test.js` exists to keep that true.
 */
export default function HeaderSelect({
  label, value, onChange, ariaLabel, compact = false, children,
}) {
  return (
    <label style={{
      display: 'flex', alignItems: 'center', gap: 8,
      fontSize: compact ? 12 : 13, color: 'var(--text-dim)',
    }}>
      {!compact && label && <span style={{ fontWeight: 600 }}>{label}</span>}
      <select
        value={value}
        onChange={e => onChange(e.target.value)}
        aria-label={ariaLabel}
        style={{
          background: 'var(--bg-input, rgba(255,255,255,0.05))',
          color: 'var(--text)', border: '1px solid var(--border)',
          borderRadius: 'var(--radius-xs, 8px)',
          // `compact` used to change only the label, so the control itself
          // stayed full size and ate a third of a 375px header.
          padding: compact ? '4px 6px' : '7px 10px',
          fontFamily: 'var(--font)', fontSize: compact ? 12 : 13,
          cursor: 'pointer',
          width: compact ? 'auto' : '100%',
        }}
      >
        {children}
      </select>
    </label>
  )
}
