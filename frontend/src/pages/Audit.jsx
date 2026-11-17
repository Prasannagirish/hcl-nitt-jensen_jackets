import { useEffect, useState } from 'react'
import { getJson } from '../api.js'
import { goBack } from '../router.js'
import { Heading, Notice } from '../ui.jsx'

export default function Audit() {
  const [events, setEvents] = useState(null)
  const [error, setError] = useState('')
  useEffect(() => {
    getJson('/admin/audit').then(setEvents).catch((e) => setError(e.message))
  }, [])
  return (
    <>
      <div><button className="secondary" onClick={() => goBack('/admin')}>← Back</button></div>
      <Heading eyebrow="Admin" lead="Audit log," bold="newest first." />
      <Notice error>{error}</Notice>
      {events && (
        <div className="card table-card">
        <table>
          <thead><tr><th>When (UTC)</th><th>Action</th><th>Paper</th><th>Outcome</th><th>Detail</th></tr></thead>
          <tbody>
            {events.map((e) => (
              <tr key={e.event_id}>
                <td className="small">{e.created_at}</td>
                <td>{e.action}</td>
                <td className="mono">{e.document_id ? `${e.document_id} ${e.version_id || ''}` : ''}</td>
                <td><span className={`pill ${e.outcome === 'ok' ? 'ok' : 'stop'}`}>{e.outcome}</span></td>
                <td className="small muted">{e.detail}</td>
              </tr>
            ))}
          </tbody>
        </table>
        </div>
      )}
    </>
  )
}
