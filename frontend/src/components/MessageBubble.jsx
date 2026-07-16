// Chat replies use a tiny markdown subset; only **bold** is rendered —
// anything richer stays literal rather than pulling in a parser.
function renderBold(text) {
  const parts = String(text).split(/\*\*(.+?)\*\*/g)
  return parts.map((part, i) => (i % 2 === 1 ? <strong key={i}>{part}</strong> : part))
}

export default function MessageBubble({ role, content }) {
  const isUser = role === 'user'
  return (
    <div
      className={isUser ? 'bubble-user' : 'bubble-assistant'}
      style={{ whiteSpace: 'pre-line' }}
    >
      {renderBold(content)}
    </div>
  )
}
