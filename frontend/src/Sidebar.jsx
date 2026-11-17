import { ago, clearChats, removeChat, useChats } from './chats.js'
import { activeChatId, deleteChat, hasPending, listChats, newChat } from './chat/chatStore.js'
import { go } from './router.js'

// Recent conversations for the signed-in reader, newest first. Ask threads come from the chat
// store; Compare runs are kept in chats.js.
function collect(compares) {
  const asks = listChats().map((c) => ({
    key: `ask-${c.id}`,
    kind: 'ask',
    id: c.id,
    title: c.title,
    at: c.updatedAt,
    href: `#/chat/${c.id}`,
    pending: hasPending(c.id),
    detail: c.turnCount > 1 ? `Ask · ${c.turnCount} questions` : 'Ask',
  }))
  const runs = compares
    .filter((c) => c.kind === 'compare')
    .map((c) => ({ key: `compare-${c.id}`, kind: 'compare', id: c.id, title: c.title, at: c.at, href: `#/compare/${c.id}`, detail: 'Compare' }))
  return [...asks, ...runs].sort((a, b) => b.at - a.at)
}

export default function Sidebar({ login, path }) {
  const compares = useChats(login) // also re-renders this list whenever any chat changes
  const items = collect(compares)
  const routeId = path.startsWith('/chat/') || path.startsWith('/compare/') ? path.split('/')[2] : null
  // At "/" the Ask page shows the active thread.
  const currentAsk = path.startsWith('/chat/') ? routeId : path === '/' ? activeChatId() : null
  const isActive = (item) => (item.kind === 'ask' ? item.id === currentAsk : path.startsWith('/compare/') && item.id === routeId)

  function startNew() {
    newChat()
    go('/')
  }

  function remove(item) {
    const wasActive = isActive(item)
    if (item.kind === 'ask') deleteChat(item.id)
    else removeChat(login, item.id)
    if (wasActive) go(item.kind === 'compare' ? '/compare' : '/')
  }

  function clearAll() {
    if (!window.confirm('Remove all recent chats from this browser?')) return
    items.forEach((i) => (i.kind === 'ask' ? deleteChat(i.id) : null))
    clearChats(login)
    if (routeId) go('/')
  }

  return (
    <aside className="sidebar" aria-label="Recent chats">
      <div className="sidebar-head">
        <h2>Recent chats</h2>
        {items.length > 0 && (
          <button className="textbtn" onClick={clearAll}>
            Clear all
          </button>
        )}
      </div>
      <button className="newchat" onClick={startNew}>
        + New chat
      </button>
      {items.length === 0 ? (
        <p className="sidebar-empty">Questions you ask and papers you compare will appear here.</p>
      ) : (
        <ul className="chatlist">
          {items.map((item) => (
            <li key={item.key} className={`chat-item ${isActive(item) ? 'active' : ''}`}>
              <a href={item.href} aria-current={isActive(item) ? 'page' : undefined}>
                <span className="chat-title">{item.title}</span>
                <span className="chat-meta">
                  {item.pending ? (
                    <>
                      <span className="dot" aria-hidden="true" /> Answering…
                    </>
                  ) : (
                    <>
                      {item.detail} · {ago(item.at)}
                    </>
                  )}
                </span>
              </a>
              <button className="chat-del" onClick={() => remove(item)} aria-label={`Remove chat: ${item.title}`} title="Remove">
                ×
              </button>
            </li>
          ))}
        </ul>
      )}
    </aside>
  )
}
