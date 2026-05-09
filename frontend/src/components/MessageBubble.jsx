export default function MessageBubble({ role, content }) {
  const isUser = role === 'user'
  return (
    <div
      className={isUser ? 'bubble-user' : 'bubble-assistant'}
      style={{ whiteSpace: 'pre-line' }}
    >
      {content}
    </div>
  )
}
