export function filterPapers(papers, query) {
  const terms = query.trim().toLowerCase().split(/\s+/)
  if (!terms[0]) return papers

  return papers.filter(({ title, authors, year, document_id }) => {
    const metadata = [title, authors, year, document_id].join(' ').toLowerCase()
    return terms.every((term) => metadata.includes(term))
  })
}
