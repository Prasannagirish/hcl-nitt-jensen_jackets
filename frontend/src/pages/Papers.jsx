import { useEffect, useState } from 'react'
import { getJson } from '../api.js'
import { Heading, Notice } from '../ui.jsx'

export default function Papers() {
  const [papers, setPapers] = useState(null)
  const [error, setError] = useState('')
  useEffect(() => {
    getJson('/papers').then(setPapers).catch((e) => setError(e.message))
  }, [])
  return (
    <>
      <Heading eyebrow="Collection" lead="The papers" bold="you can ask about." />
      <Notice error>{error}</Notice>
      {papers && (
        <div className="card table-card">
        <table>
          <thead><tr><th>Paper</th><th>Authors</th><th>Year</th><th>Version</th></tr></thead>
          <tbody>
            {papers.map((p) => (
              <tr key={p.document_id}>
                <td>
                  {p.source_url ? <a className="rowlink" href={p.source_url} target="_blank" rel="noreferrer">{p.title}</a> : p.title}
                  <div className="mono">{p.document_id}</div>
                </td>
                <td>{p.authors}</td>
                <td>{p.year}</td>
                <td><span className="pill ok">Published {p.active_version_id}</span></td>
              </tr>
            ))}
          </tbody>
        </table>
        </div>
      )}
    </>
  )
}
