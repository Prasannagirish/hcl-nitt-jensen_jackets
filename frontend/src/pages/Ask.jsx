import { useEffect, useState } from 'react'
import ChatThread from '../chat/ChatThread.jsx'
import {
  activeChatId,
  askInChat,
  getChat,
  newChat,
  removeTurn,
  setActiveChat,
} from '../chat/chatStore.js'
import { go } from '../router.js'
import { Heading, Notice } from '../ui.jsx'
import '../chat/chat.css'

// The Compare page imports AnswerView from here, so it stays exported from this file.
export { AnswerView } from '../chat/AnswerView.jsx'

// A chat: several questions in one thread. At "/" it shows the active chat (or an empty one);
// at "/chat/<id>" it shows that chat. The first question moves the address to "/chat/<id>".
export default function Ask({ chatId }) {
  const [id, setId] = useState(chatId || activeChatId())
  const [chat, setChat] = useState(() => (id ? getChat(id) : null))

  useEffect(() => {
    const refresh = () => setChat(id ? getChat(id) : null)
    refresh()
    window.addEventListener('chats-changed', refresh)
    window.addEventListener('storage', refresh) // another tab changed this chat
    return () => {
      window.removeEventListener('chats-changed', refresh)
      window.removeEventListener('storage', refresh)
    }
  }, [id])

  // Citations are looked up in the active chat, so opening a chat makes it the active one.
  useEffect(() => {
    if (id) setActiveChat(id)
  }, [id])

  function send(question) {
    const target = id || newChat()
    setId(target)
    askInChat(target, question) // the answer is written into the store when it arrives
    if (!chatId) go(`/chat/${target}`)
  }

  function retry(turn) {
    removeTurn(id, turn.id)
    send(turn.question)
  }

  function startOver() {
    newChat()
    go('/')
    window.location.reload()
  }

  if (chatId && !chat) {
    return (
      <>
        <Heading eyebrow="Chat" lead="That chat is" bold="not available." />
        <Notice>It may have been deleted, or it belongs to another account.</Notice>
        <div><button className="primary" onClick={startOver}>Start a new chat</button></div>
      </>
    )
  }

  return (
    <div className="chat-page">
      <div className="chat-head">
        <Heading eyebrow="Chat" lead="Ask the papers," bold="get cited answers." />
      </div>
      <ChatThread turns={chat?.turns ?? []} onSend={send} onRetry={retry} />
    </div>
  )
}
