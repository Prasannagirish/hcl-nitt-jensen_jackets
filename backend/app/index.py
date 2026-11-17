"""Embed evidence records and store them in the Pinecone index.

The index is a schema index: one dense vector field and full-text (BM25) fields, so dense and
keyword search run over the same documents. Version and paper fields are plain filterable metadata.
"""

import time

from openai import OpenAI
from pinecone import Pinecone, SchemaBuilder

from app.schema import Evidence


def embedding_text(record: Evidence, title: str, max_chars: int) -> str:
    """Text that is embedded: paper title, section, the record's text and any figure description."""
    parts = [f"{title} | {record.section_path}".strip(" |"), record.body]
    if record.description:
        parts.append(f"Figure description: {record.description}")
    return "\n".join(parts)[:max_chars]


def embed_texts(texts: list[str], model: str, batch: int) -> list[list[float]]:
    """Embed texts in batches, keeping the input order."""
    client = OpenAI()
    vectors: list[list[float]] = []
    for start in range(0, len(texts), batch):
        response = client.embeddings.create(model=model, input=texts[start : start + batch])
        vectors += [item.embedding for item in response.data]
    return vectors


def ensure_index(pc: Pinecone, cfg: dict) -> bool:
    """Create the index when it does not exist. Returns True if it was created now."""
    name = cfg["pinecone"]["index_name"]
    if pc.has_index(name):
        return False
    fields = cfg["pinecone"]
    built = (
        SchemaBuilder()
        .add_dense_vector_field(
            fields["dense_field"], dimension=cfg["models"]["embedding_dimension"], metric="cosine"
        )
        .add_string_field(fields["text_field"], full_text_search={"language": "en"})
        .add_string_field("description", full_text_search={"language": "en"})
        .build()
    )
    pc.indexes.create(name=name, schema=built, timeout=300)
    return True


def to_document(record: Evidence, vector: list[float], dense_field: str) -> dict:
    """Pinecone document for one record. Empty values are left out."""
    document = {key: value for key, value in record.to_dict().items() if value not in ("", [])}
    document["_id"] = document.pop("evidence_id")
    document[dense_field] = vector
    return document


def reset_namespace(index, namespace: str, document_ids: list[str]) -> None:
    """Delete the records of the given papers, so records that no longer exist do not linger.

    Only these papers are cleared. Anything else in the namespace, such as the injection test
    fixture, is left alone.
    """
    try:
        index.documents.delete(namespace=namespace, filter={"document_id": {"$in": document_ids}})
    except Exception as error:  # a namespace that was never written to cannot be cleared
        print(f"  namespace not cleared ({type(error).__name__}); continuing")


def upsert_documents(index, documents: list[dict], namespace: str, batch: int) -> None:
    """Upsert documents in batches."""
    for start in range(0, len(documents), batch):
        index.documents.upsert(namespace=namespace, documents=documents[start : start + batch])


def wait_for_count(index, namespace: str, expected: int, seconds: int = 120) -> int:
    """Poll the namespace until it holds the expected number of documents, or time runs out."""
    deadline = time.time() + seconds
    count = 0
    while time.time() < deadline:
        stats = index.describe_index_stats()
        count = (
            stats.namespaces.get(namespace, {}).get("vector_count", 0) if stats.namespaces else 0
        )
        if count >= expected:
            break
        time.sleep(5)
    return count
