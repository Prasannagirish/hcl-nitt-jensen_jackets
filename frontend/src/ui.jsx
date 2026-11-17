// Small shared pieces: eyebrow heading, status pill, notice.
const PILL_CLASS = {
  supported: 'ok',
  partially_supported: 'ask',
  no_answer: 'stop',
  READY: 'ok',
  INDEXING: 'ask',
  DRAFT: '',
  FAILED: 'stop',
  published: 'ok',
}

const PILL_WORD = {
  supported: 'Supported',
  partially_supported: 'Partly supported',
  no_answer: 'No answer',
}

export function Pill({ status }) {
  return <span className={`pill ${PILL_CLASS[status] ?? ''}`}>{PILL_WORD[status] ?? status}</span>
}

export function Heading({ eyebrow, lead, bold }) {
  return (
    <header className="stack">
      <p className="eyebrow">{eyebrow}</p>
      <h1>
        {lead} <b>{bold}</b>
      </h1>
    </header>
  )
}

export function Notice({ error, children }) {
  if (!children) return null
  return (
    <p className={`notice ${error ? 'error' : ''}`} role={error ? 'alert' : 'status'}>
      {children}
    </p>
  )
}

export function PaperSearch({ query, onChange, count, total }) {
  return (
    <div className="paper-search">
      <label>
        Search papers
        <input
          type="search"
          placeholder="Title, author, year, or paper ID"
          value={query}
          onChange={(event) => onChange(event.target.value)}
        />
      </label>
      <p className="muted small" role="status">
        {total === 0 ? 'No papers available.' : count === 0 ? 'No papers match your search.' : `${count} of ${total} papers`}
      </p>
    </div>
  )
}
