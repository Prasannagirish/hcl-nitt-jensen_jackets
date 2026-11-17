import { Pill } from '../ui.jsx'

// Shows the statements of an answer with a link to each cited source.
export function AnswerView({ result }) {
  if (result.status === 'no_answer') {
    return (
      <div className="card">
        <Pill status="no_answer" />
        <p>{result.answer}</p>
        {result.evidence_gaps.length > 0 && <p className="small muted">What is missing: {result.evidence_gaps.join(' ')}</p>}
      </div>
    )
  }
  const evidenceById = new Map(result.evidence.map((source) => [source.evidence_id, source]))
  const statements = [...result.claims, ...result.suggestions]
  const sourceIds = [...new Set(statements.flatMap((statement) => statement.evidence_ids))]
    .filter((id) => evidenceById.has(id))
  const numbers = new Map(sourceIds.map((id, index) => [id, index + 1]))
  const sourceHref = (id) => `#/evidence/${encodeURIComponent(id)}`

  function references(ids) {
    return [...new Set(ids)].filter((id) => numbers.has(id)).map((id) => (
      <sup key={id}>
        <a className="citation-ref" href={sourceHref(id)} aria-label={`Source ${numbers.get(id)}`}>
          [{numbers.get(id)}]
        </a>
      </sup>
    ))
  }

  return (
    <div className="card">
      <div className="row">
        <Pill status={result.status} />
        {result.degraded.length > 0 && <span className="pill ask">Reduced quality: {result.degraded.join(', ')}</span>}
      </div>
      {result.claims.map((c, i) => (
        <p key={i}>{c.text}{references(c.evidence_ids)}</p>
      ))}
      {result.suggestions.length > 0 && (
        <div className="suggest stack">
          <h2>AI-generated suggestions</h2>
          <p className="small muted">Proposals by the assistant, not statements from the papers. Each is tied to the evidence that motivates it.</p>
          {result.suggestions.map((s, i) => (
            <p key={i}>{s.text}{references(s.evidence_ids)}</p>
          ))}
        </div>
      )}
      {result.evidence_gaps.length > 0 && <p className="small muted">What is missing: {result.evidence_gaps.join(' ')}</p>}
      {sourceIds.length > 0 && (
        <section className="answer-sources">
          <h2>Sources</h2>
          <ol>
            {sourceIds.map((id) => {
              const source = evidenceById.get(id)
              return (
                <li key={id}>
                  <a className="cite" href={sourceHref(id)}>
                    {source.document_id} p{source.pdf_page}
                    {source.figure_number ? ` Figure ${source.figure_number}` : ''}
                    {source.table_number ? ` Table ${source.table_number}` : ''}
                  </a>
                </li>
              )
            })}
          </ol>
        </section>
      )}
      <p className="small muted">Models: {Object.values(result.models).join(' · ')}</p>
    </div>
  )
}
