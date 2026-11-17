"""Find evidence for a question: dense and keyword search, rank fusion, then reranking.

Search only ever covers the versions in the snapshot (a list of "paper:version" keys), so an
unpublished version can never be returned. Dense and BM25 run as separate searches because the
index cannot score both in one call; their ranked lists are merged here by reciprocal rank fusion.
"""

import json
from dataclasses import dataclass, field

from pinecone import Pinecone
from pinecone.models.documents.score_by import DenseVectorQuery, TextQuery

from app import index as idx
from app.config import PROJECT_ROOT, load_config
from app.schema import sha256_of

FIELDS = [
    "document_id",
    "version_id",
    "docver",
    "element_type",
    "pdf_page",
    "section_path",
    "body",
    "description",
    "figure_number",
    "table_number",
    "asset_id",
    "related_ids",
]


@dataclass
class Hit:
    """One piece of evidence returned by search."""

    evidence_id: str
    document_id: str
    version_id: str
    element_type: str
    pdf_page: int
    section_path: str
    body: str
    description: str = ""
    figure_number: str = ""
    table_number: str = ""
    asset_id: str = ""
    related_ids: list[str] = field(default_factory=list)
    dense_rank: int | None = None  # 1 = best; used to break fusion ties
    rrf_score: float = 0.0
    rerank_score: float | None = None
    via: str = "search"  # "search" or "related" (fetched because a figure or table points to it)


@dataclass
class Retrieval:
    """Evidence found for one question, with notes on anything that degraded."""

    hits: list[Hit]
    degraded: list[str] = field(default_factory=list)


def hit_from_document(doc) -> Hit:
    """Build a Hit from a Pinecone document."""
    return Hit(
        evidence_id=doc.id,
        document_id=doc.get("document_id", ""),
        version_id=doc.get("version_id", ""),
        element_type=doc.get("element_type", ""),
        pdf_page=int(doc.get("pdf_page", 0)),
        section_path=doc.get("section_path", ""),
        body=doc.get("body", ""),
        description=doc.get("description", ""),
        figure_number=doc.get("figure_number", ""),
        table_number=doc.get("table_number", ""),
        asset_id=doc.get("asset_id", ""),
        related_ids=list(doc.get("related_ids", []) or []),
    )


def open_index(cfg: dict):
    """Pinecone client and the index handle."""
    pc = Pinecone()
    return pc, pc.index(cfg["pinecone"]["index_name"])


def search_both(index, cfg: dict, question: str, vector: list[float], docvers: list[str]):
    """Run the dense search and the BM25 search with the same version filter."""
    names, rcfg = cfg["pinecone"], cfg["retrieval"]
    scope = {"docver": {"$in": docvers}}
    dense = index.documents.search(
        namespace=names["namespace"],
        top_k=rcfg["branch_top_k"],
        include_fields=FIELDS,
        filter=scope,
        score_by=[DenseVectorQuery(values=vector, field=names["dense_field"])],
    )
    keyword = index.documents.search(
        namespace=names["namespace"],
        top_k=rcfg["branch_top_k"],
        include_fields=FIELDS,
        filter=scope,
        score_by=[TextQuery(query=question, fields=[names["text_field"], "description"])],
    )
    return dense.matches, keyword.matches


def rrf_fuse(dense_docs: list, keyword_docs: list, k: int) -> list[Hit]:
    """Merge two ranked lists by rank only. Ties go to the better dense rank."""
    hits: dict[str, Hit] = {}
    for rank, doc in enumerate(dense_docs, start=1):
        hit = hits.setdefault(doc.id, hit_from_document(doc))
        hit.dense_rank = rank
        hit.rrf_score += 1 / (k + rank)
    for rank, doc in enumerate(keyword_docs, start=1):
        hit = hits.setdefault(doc.id, hit_from_document(doc))
        hit.rrf_score += 1 / (k + rank)
    return sorted(hits.values(), key=lambda h: (-h.rrf_score, h.dense_rank or 10**6))


def rerank_text(hit: Hit, max_chars: int) -> str:
    """Text shown to the reranker for one hit."""
    parts = [hit.section_path, hit.body]
    if hit.description:
        parts.append(f"Figure description: {hit.description}")
    return "\n".join(p for p in parts if p)[:max_chars]


def rerank_call(
    pc, question: str, texts: list[str], cfg: dict, top_n: int
) -> list[tuple[int, float]]:
    """Ask the reranker for (index, score) pairs. Identical requests are replayed from disk.

    The hosted reranker can order near-tied passages differently between calls, which would make
    two evaluation runs differ. Replaying the first answer keeps repeat runs identical.
    """
    model = cfg["models"]["rerank"]
    use_cache = cfg["retrieval"]["cache_rerank"]
    key = sha256_of(json.dumps([model, question, texts, top_n]))
    cache_file = PROJECT_ROOT / "backend" / "storage" / "rerank_cache" / f"{key}.json"
    if use_cache and cache_file.exists():
        return [tuple(pair) for pair in json.loads(cache_file.read_text(encoding="utf-8"))]
    result = pc.inference.rerank(
        model=model,
        query=question,
        documents=texts,
        top_n=top_n,
        return_documents=False,
        parameters={"truncate": "END"},  # long pairs are cut, not rejected (1024-token limit)
    )
    pairs = [(row.index, row.score) for row in result.data]
    if use_cache:
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        cache_file.write_text(json.dumps(pairs), encoding="utf-8")
    return pairs


def rerank(pc, question: str, hits: list[Hit], cfg: dict, top_n: int) -> list[Hit]:
    """Order hits by the reranker and store each score. Raises if the reranker call fails."""
    rcfg = cfg["retrieval"]
    pool = hits[: rcfg["rerank_pool"]]
    texts = [rerank_text(h, rcfg["rerank_chars"]) for h in pool]
    ranked = []
    for index, score in rerank_call(pc, question, texts, cfg, min(top_n, len(pool))):
        pool[index].rerank_score = score
        ranked.append(pool[index])
    return ranked


def retrieve_scope(pc, index, cfg, question, vector, docvers, top_n, degraded) -> list[Hit]:
    """Search, fuse and rerank inside one set of versions. Falls back to fusion order on failure."""
    dense, keyword = search_both(index, cfg, question, vector, docvers)
    fused = rrf_fuse(dense, keyword, cfg["retrieval"]["rrf_k"])
    if not fused:
        return []
    try:
        return rerank(pc, question, fused, cfg, top_n)
    except Exception as error:
        degraded.append(f"rerank_failed:{type(error).__name__}")
        return fused[:top_n]


def add_related(index, cfg: dict, hits: list[Hit]) -> list[Hit]:
    """Append the text chunks a kept figure or table points to, so its explanation comes along."""
    have = {h.evidence_id for h in hits}
    wanted: list[str] = []
    for hit in hits:
        if hit.element_type == "text":
            continue
        for related_id in hit.related_ids[: cfg["retrieval"]["max_related"]]:
            if related_id not in have and related_id not in wanted:
                wanted.append(related_id)
    if not wanted:
        return hits
    fetched = index.documents.fetch(
        namespace=cfg["pinecone"]["namespace"], ids=wanted, include_fields=FIELDS
    )
    # in the order asked for: the server's dictionary order can change between calls
    extra = [hit_from_document(fetched.documents[i]) for i in wanted if i in fetched.documents]
    for hit in extra:
        hit.via = "related"
    return hits + extra


def retrieve(question: str, docvers: list[str], cfg: dict | None = None, per_paper: bool = False):
    """Evidence for a question, from the given versions only.

    per_paper=False searches all versions together. per_paper=True searches each paper on its own
    and keeps a small quota from each, so a comparison cannot be won by one paper.
    """
    cfg = cfg or load_config()
    pc, index = open_index(cfg)
    vector = idx.embed_texts([question], cfg["models"]["embedding"], 1)[0]
    rcfg, degraded = cfg["retrieval"], []
    if not per_paper:
        hits = retrieve_scope(
            pc, index, cfg, question, vector, docvers, rcfg["final_top_n"], degraded
        )
    else:
        hits = []
        for docver in docvers:
            quota = rcfg["per_paper_quota"]
            hits += retrieve_scope(pc, index, cfg, question, vector, [docver], quota, degraded)
    return Retrieval(add_related(index, cfg, hits), degraded)
