import { useEffect, useRef, useState } from 'react'
import { ApiError, getJson, postJson } from '../api.js'
import { saveAnswer } from '../store.js'
import { addChat, getChat } from '../chats.js'
import { go } from '../router.js'
import { Heading, Notice } from '../ui.jsx'
import { AnswerView } from './Ask.jsx'

export default function Compare({ login, chatId }) {
  const saved = chatId ? getChat(login, chatId) : null
  const [papers, setPapers] = useState([])
  const [chosen, setChosen] = useState(saved?.document_ids ?? [])
  const [question, setQuestion] = useState(saved?.question ?? '')
  const [result, setResult] = useState(saved?.result ?? null)
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const mounted = useRef(true)

  useEffect(() => {
    mounted.current = true
    return () => {
      mounted.current = false
    }
  }, [])

  // Citations open from the last answer held in the session, so a reopened chat becomes the last answer.
  useEffect(() => {
    if (saved) saveAnswer(saved.result)
  }, [saved?.id])

  useEffect(() => {
    getJson('/papers').then(setPapers).catch((e) => setError(e.message))
  }, [])

  const toggle = (id) => setChosen((c) => (c.includes(id) ? c.filter((x) => x !== id) : [...c, id]))

  async function submit(event) {
    event.preventDefault()
    setBusy(true)
    setError('')
    setResult(null)
    try {
      const answer = await postJson('/compare', { document_ids: chosen, question })
      saveAnswer(answer)
      const titles = papers.filter((p) => chosen.includes(p.document_id)).map((p) => p.title.split(':')[0])
      const id = addChat(login, {
        kind: 'compare',
        title: question.trim() || `Compare ${titles.join(' vs ')}`,
        question: question.trim(),
        document_ids: chosen,
        result: answer,
      })
      if (mounted.current) go(`/compare/${id}`)
      else setResult(answer)
    } catch (e) {
      if (mounted.current) setError(e instanceof ApiError ? e.message : 'The comparison failed.')
    } finally {
      if (mounted.current) setBusy(false)
    }
  }

  return (
    <>
      <Heading eyebrow="Compare" lead="Put papers" bold="side by side." />
      <form className="card panel" onSubmit={submit}>
        <fieldset className="choices-set">
          <legend>Choose two or more papers</legend>
          <div className="choices">
            {papers.map((p) => (
              <label key={p.document_id} className="choice">
                <input type="checkbox" checked={chosen.includes(p.document_id)} onChange={() => toggle(p.document_id)} />
                <span>
                  {p.title}
                  <span className="mono">{p.document_id}</span>
                </span>
              </label>
            ))}
          </div>
        </fieldset>
        <label htmlFor="cq">Question (optional)</label>
        <textarea id="cq" maxLength={1000} value={question} onChange={(e) => setQuestion(e.target.value)} placeholder="Leave empty to compare objectives, methods, data, metrics, results and limitations." />
        <div className="row">
          <button className="primary" type="submit" disabled={busy || chosen.length < 2}>{busy ? 'Comparing…' : 'Compare'}</button>
          <span className="muted small">{chosen.length < 2 ? 'Choose at least two papers.' : `${chosen.length} papers selected.`}</span>
        </div>
      </form>
      <Notice error>{error}</Notice>
      {result && (
        <>
          <h2>What each paper says</h2>
          <div className="card table-card">
          <table>
            <thead><tr><th>Paper</th><th>Statements</th></tr></thead>
            <tbody>
              {result.comparison_rows.map((row) => (
                <tr key={row.document_id}>
                  <td><b>{row.title}</b><div className="mono">{row.document_id}</div></td>
                  <td>
                    {row.statements.map((s, i) => (s === 'NOT REPORTED' ? <p key={i}><span className="pill stop">NOT REPORTED</span></p> : <p key={i}>{s}</p>))}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          </div>
          <AnswerView result={result} />
        </>
      )}
    </>
  )
}
