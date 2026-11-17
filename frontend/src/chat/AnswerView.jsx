import { Pill } from '../ui.jsx'

// Shows the statements of an answer with a link to each cited source.
export function AnswerView({ result }) {
  const byId = Object.fromEntries(result.evidence.map((e) => [e.evidence_id, e]))
  const cites = (ids) =>
    ids.map((id) => {
      const e = byId[id]
      const extra = e.figure_number ? ` Figure ${e.figure_number}` : e.table_number ? ` Table ${e.table_number}` : ''
      return (
        <a key={id} className="cite" href={`#/evidence/${encodeURIComponent(id)}`}>
          {e.document_id} p{e.pdf_page}{extra}
        </a>
      )
    })
  if (result.status === 'no_answer') {
    return (
      <div className="card">
        <Pill status="no_answer" />
        <p>{result.answer}</p>
        {result.evidence_gaps.length > 0 && <p className="small muted">What is missing: {result.evidence_gaps.join(' ')}</p>}
      </div>
    )
  }
  return (
    <div className="card">
      <div className="row">
        <Pill status={result.status} />
        {result.degraded.length > 0 && <span className="pill ask">Reduced quality: {result.degraded.join(', ')}</span>}
      </div>
      {result.claims.map((c, i) => (
        <div key={i} className="claim">
          <p>{c.text}</p>
          <div>{cites(c.evidence_ids)}</div>
        </div>
      ))}
      {result.suggestions.length > 0 && (
        <div className="suggest stack">
          <h2>AI-generated suggestions</h2>
          <p className="small muted">Proposals by the assistant, not statements from the papers. Each is tied to the evidence that motivates it.</p>
          {result.suggestions.map((s, i) => (
            <div key={i} className="claim">
              <p>{s.text}</p>
              <div>{cites(s.evidence_ids)}</div>
            </div>
          ))}
        </div>
      )}
      {result.evidence_gaps.length > 0 && <p className="small muted">What is missing: {result.evidence_gaps.join(' ')}</p>}
      <p className="small muted">Models: {Object.values(result.models).join(' · ')}</p>
    </div>
  )
}
