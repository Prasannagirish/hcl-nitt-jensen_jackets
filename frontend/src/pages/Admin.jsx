import { useCallback, useEffect, useState } from 'react'
import { ApiError, getJson, postForm, postJson } from '../api.js'
import { Heading, Notice, Pill } from '../ui.jsx'

function UploadForm({ onDone }) {
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  async function submit(event) {
    event.preventDefault()
    const form = new FormData(event.target)
    setBusy(true)
    setError('')
    try {
      const result = await postForm('/admin/documents', form)
      setMessage(`Accepted as ${result.document_id} ${result.version_id}. It is being processed; publish it once it shows READY.`)
      event.target.reset()
      onDone()
    } catch (e) {
      setError(e instanceof ApiError ? e.message : 'Upload failed.')
    } finally {
      setBusy(false)
    }
  }

  return (
    <form className="card panel" onSubmit={submit}>
      <h2>Add a paper</h2>
      <div><label htmlFor="file">PDF file</label><input id="file" name="file" type="file" accept="application/pdf" required /></div>
      <div><label htmlFor="title">Title</label><input id="title" name="title" type="text" required /></div>
      <div><label htmlFor="authors">Authors</label><input id="authors" name="authors" type="text" required /></div>
      <div className="row">
        <div><label htmlFor="year">Year</label><input id="year" name="year" type="number" min="1990" max="2100" required /></div>
        <div className="grow"><label htmlFor="source_url">Source link (optional)</label><input id="source_url" name="source_url" type="text" /></div>
      </div>
      <div className="row"><button className="primary" type="submit" disabled={busy}>{busy ? 'Uploading…' : 'Upload'}</button></div>
      <Notice>{message}</Notice>
      <Notice error>{error}</Notice>
    </form>
  )
}

export default function Admin() {
  const [docs, setDocs] = useState(null)
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')

  const load = useCallback(() => {
    getJson('/admin/documents').then(setDocs).catch((e) => setError(e.message))
  }, [])

  useEffect(() => {
    load()
  }, [load])

  // Keep refreshing while any version is still being processed.
  const busy = docs?.some((d) => d.versions.some((v) => v.processing_state === 'DRAFT' || v.processing_state === 'INDEXING'))
  useEffect(() => {
    if (!busy) return undefined
    const timer = setInterval(load, 4000)
    return () => clearInterval(timer)
  }, [busy, load])

  async function publish(doc, version) {
    if (!window.confirm(`Publish ${doc.document_id} ${version.version_id}? Readers will see it immediately.`)) return
    setError('')
    try {
      await postJson(`/admin/documents/${doc.document_id}/versions/${version.version_id}/publish`, { expected_active_version_id: doc.active_version_id })
      setMessage(`${doc.document_id} now shows ${version.version_id} to readers.`)
    } catch (e) {
      setError(e instanceof ApiError ? e.message : 'Publish failed.')
    }
    load()
  }

  return (
    <>
      <Heading eyebrow="Admin" lead="Manage papers" bold="and versions." />
      <div className="row"><a className="btnlink" href="#/admin/audit">View the audit log →</a></div>
      <Notice error>{error}</Notice>
      <Notice>{message}</Notice>
      <UploadForm onDone={load} />
      {docs && (
        <section className="card table-card" aria-label="Papers and versions">
          <div className="table-head">
            <h2>Papers and versions</h2>
            <span className="muted small">{docs.length} {docs.length === 1 ? 'paper' : 'papers'}</span>
          </div>
          <table className="versions">
            <thead>
              <tr><th>Paper</th><th>Version</th><th>Status</th><th>Readers see</th><th className="actions">Action</th></tr>
            </thead>
            {docs.map((d) => (
              <tbody key={d.document_id}>
                {d.versions.length === 0 && (
                  <tr>
                    <td><b>{d.title}</b><div className="mono">{d.document_id}</div></td>
                    <td colSpan={4} className="muted">No versions yet.</td>
                  </tr>
                )}
                {d.versions.map((v, i) => {
                  const live = v.version_id === d.active_version_id
                  return (
                    <tr key={v.version_id}>
                      {i === 0 && (
                        <td rowSpan={d.versions.length} className="paper-cell">
                          <b>{d.title}</b>
                          <div className="mono">{d.document_id}</div>
                          {!d.active_version_id && <span className="pill">Not published</span>}
                        </td>
                      )}
                      <td><span className="mono">{v.version_id}</span></td>
                      <td><Pill status={v.processing_state} /></td>
                      <td>{live ? <span className="pill ok">Live</span> : <span className="muted">—</span>}</td>
                      <td className="actions">
                        {v.processing_state === 'READY' && !live && (
                          <button className="secondary" onClick={() => publish(d, v)}>
                            {d.active_version_id && v.version_id < d.active_version_id ? 'Roll back to this' : 'Publish'}
                          </button>
                        )}
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            ))}
          </table>
        </section>
      )}
    </>
  )
}
