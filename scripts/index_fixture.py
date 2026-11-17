"""Index the prompt-injection fixture next to the papers, under its own document ID.

Usage: uv run python scripts/index_fixture.py
The fixture is not in the paper catalogue, so the default snapshot never includes it; only the
evaluation question that targets it adds its version to the snapshot.
"""

from pinecone import Pinecone

from app import index as idx
from app.config import PROJECT_ROOT, load_config, load_env
from app.ingest.chunker import parse_pdf

FIXTURE = PROJECT_ROOT / "tests" / "fixtures" / "injection_note.pdf"
DOCUMENT_ID = "fixture-injection"
TITLE = "TEST FIXTURE (not a real paper): Adapter Rank Note"


def main() -> None:
    """Parse the fixture, embed it and upsert it."""
    load_env()
    cfg = load_config()
    records = parse_pdf(
        FIXTURE, DOCUMENT_ID, PROJECT_ROOT / "backend" / "storage" / "assets", cfg["ingest"]
    )
    limit = cfg["indexing"]["max_embed_chars"]
    texts = [idx.embedding_text(r, TITLE, limit) for r in records]
    vectors = idx.embed_texts(texts, cfg["models"]["embedding"], cfg["indexing"]["embed_batch"])
    pc = Pinecone()
    index = pc.index(cfg["pinecone"]["index_name"])
    dense = cfg["pinecone"]["dense_field"]
    documents = [idx.to_document(r, v, dense) for r, v in zip(records, vectors, strict=True)]
    idx.upsert_documents(
        index, documents, cfg["pinecone"]["namespace"], cfg["indexing"]["upsert_batch"]
    )
    for record in records:
        print(f"  {record.evidence_id} [{record.section_path}] {record.body[:70]!r}")
    print(
        f"indexed {len(documents)} fixture records as {DOCUMENT_ID}:{cfg['ingest']['version_id']}"
    )


if __name__ == "__main__":
    main()
