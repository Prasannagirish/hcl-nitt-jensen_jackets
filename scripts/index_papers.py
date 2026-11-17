"""Describe figures, embed every evidence record and upsert them into Pinecone.

Usage: uv run python scripts/index_papers.py
Needs OPENAI_API_KEY and PINECONE_API_KEY in .env and the output of `make ingest`.
Safe to re-run: it clears these papers' records first, then writes every record again.
"""

import csv
import json

from pinecone import Pinecone

from app import index as idx
from app.config import PROJECT_ROOT, load_config, load_env
from app.ingestion import describe_figures
from app.schema import Evidence

STORAGE = PROJECT_ROOT / "backend" / "storage"


def load_titles() -> dict[str, str]:
    """Paper titles from the catalogue, by document ID."""
    path = PROJECT_ROOT / "data" / "papers_catalogue.csv"
    with open(path, encoding="utf-8", newline="") as handle:
        return {row["document_id"]: row["title"] for row in csv.DictReader(handle)}


def load_records() -> list[Evidence]:
    """All evidence records written by `make ingest`."""
    records = []
    for path in sorted((STORAGE / "evidence").glob("paper-*.jsonl")):
        for line in path.read_text(encoding="utf-8").splitlines():
            records.append(Evidence.from_dict(json.loads(line)))
    return records


def main() -> None:
    """Run the whole indexing flow and print a summary."""
    load_env()
    cfg = load_config()
    records = load_records()
    print(f"{len(records)} records loaded")
    described = describe_figures(records, cfg)
    titles = load_titles()
    limit = cfg["indexing"]["max_embed_chars"]
    texts = [idx.embedding_text(r, titles[r.document_id], limit) for r in records]
    vectors = idx.embed_texts(texts, cfg["models"]["embedding"], cfg["indexing"]["embed_batch"])
    print(f"embedded {len(vectors)} records; {described} figures have a description")
    pc = Pinecone()
    created = idx.ensure_index(pc, cfg)
    print("index created" if created else "index already existed")
    index = pc.index(cfg["pinecone"]["index_name"])
    dense = cfg["pinecone"]["dense_field"]
    documents = [idx.to_document(r, v, dense) for r, v in zip(records, vectors, strict=True)]
    namespace = cfg["pinecone"]["namespace"]
    idx.reset_namespace(index, namespace, sorted({r.document_id for r in records}))
    idx.upsert_documents(index, documents, namespace, cfg["indexing"]["upsert_batch"])
    count = idx.wait_for_count(index, namespace, len(documents))
    print(f"upserted {len(documents)} documents; namespace now reports {count}")


if __name__ == "__main__":
    main()
