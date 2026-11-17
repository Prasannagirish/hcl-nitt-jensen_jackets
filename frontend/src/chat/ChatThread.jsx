import { useEffect, useRef, useState } from 'react'
import { AnswerView } from './AnswerView.jsx'
import { Notice } from '../ui.jsx'
import './chat.css'

const LIMIT = 1000
const EXAMPLES = [
  'What speed-up does ENGINE achieve over LOREN?',
  'How does MeltKV reduce the memory used by the KV cache?',
  'What limitations do the authors of the Less is Safer paper acknowledge?',
]

function Pending() {
  return (
    <div className="chat-pending" role="status">
      <span className="chat-dots" aria-hidden="true"><span /><span /><span /></span>
      Searching the papers. This can take up to 30 seconds.
    </div>
  )
}

function Turn({ turn, onRetry }) {
  return (
    <div className="chat-turn">
      <p className="chat-q">{turn.question}</p>
      <div className="chat-a">
        {turn.status === 'pending' && <Pending />}
        {turn.status === 'done' && <AnswerView result={turn.answer} />}
        {turn.status === 'error' && (
          <div className="stack">
            <Notice error>{turn.error}</Notice>
            <div><button className="secondary" onClick={() => onRetry(turn)}>Try again</button></div>
          </div>
        )}
      </div>
    </div>
  )
}

// The thread of questions and answers, and the box to ask the next question.
export default function ChatThread({ turns, onSend, onRetry }) {
  const [text, setText] = useState('')
  const endRef = useRef(null)
  const busy = turns.some((t) => t.status === 'pending')
  const last = turns[turns.length - 1]

  // Keep the newest question and answer in view.
  useEffect(() => {
    const calm = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches
    endRef.current?.scrollIntoView({ behavior: calm ? 'auto' : 'smooth', block: 'end' })
  }, [turns.length, last?.status])

  function send(question) {
    const asked = question.trim()
    if (!asked || busy) return
    setText('')
    onSend(asked)
  }

  function onKeyDown(event) {
    // Enter sends, Shift+Enter adds a line. Do nothing while an input method is composing text.
    if (event.key === 'Enter' && !event.shiftKey && !event.nativeEvent.isComposing) {
      event.preventDefault()
      send(text)
    }
  }

  return (
    <>
      <div className="chat-thread" role="log" aria-live="polite" aria-label="Conversation">
        {turns.length === 0 && (
          <div className="chat-empty card">
            <h2>Ask a question about the papers</h2>
            <p className="muted">Every answer cites the paper, page and figure it comes from. Try one of these:</p>
            <div className="chat-chips">
              {EXAMPLES.map((q) => (
                <button key={q} type="button" className="chat-chip" onClick={() => send(q)}>{q}</button>
              ))}
            </div>
          </div>
        )}
        {turns.map((turn) => <Turn key={turn.id} turn={turn} onRetry={onRetry} />)}
        <div ref={endRef} />
      </div>
      <form className="chat-composer" onSubmit={(e) => { e.preventDefault(); send(text) }}>
        <label htmlFor="chat-input" className="small muted">
          {turns.length ? 'Ask another question' : 'Your question'}
        </label>
        <div className="chat-row">
          <textarea
            id="chat-input"
            value={text}
            maxLength={LIMIT}
            onChange={(e) => setText(e.target.value)}
            onKeyDown={onKeyDown}
            placeholder="Type your question and press Enter"
          />
          <button className="primary" type="submit" disabled={busy || !text.trim()}>
            {busy ? 'Waiting…' : 'Ask'}
          </button>
        </div>
        <div className="chat-hint small muted">
          <span>Each question is answered on its own from the papers. Earlier questions in this chat are not used as context.</span>
          <span>{text.length > LIMIT - 100 ? `${text.length} / ${LIMIT}` : 'Shift+Enter for a new line'}</span>
        </div>
      </form>
    </>
  )
}
