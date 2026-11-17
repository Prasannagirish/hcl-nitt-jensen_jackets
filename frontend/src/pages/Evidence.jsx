import { useEffect, useState } from 'react'
import { imageUrl } from '../api.js'
import { goBack } from '../router.js'
import { findEvidence } from '../chat/chatStore.js'
import { Heading, Notice } from '../ui.jsx'

export default function Evidence({ id }) {
  const item = findEvidence(id)
  const [image, setImage] = useState('')
  const [error, setError] = useState('')

  useEffect(() => {
    if (!item?.source_url) return
    imageUrl(item.source_url).then(setImage).catch((e) => setError(e.message))
  }, [item?.source_url])

  if (!item) {
    return (
      <>
        <Heading eyebrow="Source" lead="That source is" bold="not available." />
        <p>Open a citation from an answer to see its source.</p>
        <button className="secondary" onClick={() => goBack('/')}>Back</button>
      </>
    )
  }
  const kind = item.figure_number ? `Figure ${item.figure_number}` : item.table_number ? `Table ${item.table_number}` : 'Text'
  return (
    <>
      <div><button className="secondary" onClick={() => goBack('/')}>← Back</button></div>
      <Heading eyebrow="Source" lead={`${item.document_id}, page ${item.pdf_page},`} bold={kind} />
      <div className="card">
        <p className="small muted">Section: {item.section_path || 'not available'} · version {item.version_id}</p>
        {image && <img className="figure" src={image} alt={`Original crop of ${kind} on page ${item.pdf_page}`} />}
        <Notice error>{error}</Notice>
        <h2>Text from the paper</h2>
        <p className="excerpt">{item.body}</p>
        <p className="small muted">The page number is the physical page of the PDF, not the printed one.</p>
      </div>
    </>
  )
}
