"""Process one uploaded paper version in the background: parse, describe, embed, index.

The version moves DRAFT -> INDEXING -> READY, or ends FAILED. A failure never changes what readers
see, because only publishing moves the active-version pointer.
"""

import logging

from pinecone import Pinecone

from app import db, schema
from app import index as idx
from app.config import PROJECT_ROOT, load_config, load_env
from app.ingest.chunker import parse_pdf
from app.schema import Evidence
from app.vision import describe_figure

log = logging.getLogger("researchiq")
STORAGE = PROJECT_ROOT / "backend" / "storage"


def describe_figures(records: list[Evidence], cfg: dict) -> int:
    """Add a search description to every figure that has a crop. Returns how many got one."""
    done = 0
    for record in records:
        if record.element_type != schema.FIGURE or not record.asset_id:
            continue
        crop = STORAGE / "assets" / record.document_id / record.version_id / record.asset_id
        limit = cfg["indexing"]["vision_max_tokens"]
        record.description = describe_figure(crop, cfg["models"], STORAGE / "vision_cache", limit)
        done += bool(record.description)
    return done


def index_records(records: list[Evidence], title: str, cfg: dict) -> None:
    """Embed the records and write them to the index, replacing any earlier copy of this version."""
    texts = [idx.embedding_text(r, title, cfg["indexing"]["max_embed_chars"]) for r in records]
    vectors = idx.embed_texts(texts, cfg["models"]["embedding"], cfg["indexing"]["embed_batch"])
    pc = Pinecone()
    index = pc.index(cfg["pinecone"]["index_name"])
    namespace = cfg["pinecone"]["namespace"]
    docver = records[0].docver
    index.documents.delete(namespace=namespace, filter={"docver": {"$eq": docver}})
    dense = cfg["pinecone"]["dense_field"]
    documents = [idx.to_document(r, v, dense) for r, v in zip(records, vectors, strict=True)]
    idx.upsert_documents(index, documents, namespace, cfg["indexing"]["upsert_batch"])


def set_state(conn, document_id: str, version_id: str, state: str) -> None:
    """Update the processing state of one version."""
    conn.execute(
        "UPDATE document_versions SET processing_state = ? "
        "WHERE document_id = ? AND version_id = ?",
        (state, document_id, version_id),
    )
    conn.commit()


def process_version(document_id: str, version_id: str, actor_id: int) -> None:
    """Run the whole pipeline for one uploaded version. Safe to call from a background task."""
    load_env()
    cfg = load_config()
    conn = db.connect()
    try:
        set_state(conn, document_id, version_id, "INDEXING")
        row = conn.execute(
            "SELECT v.pdf_path, d.title FROM document_versions v "
            "JOIN documents d USING (document_id) WHERE v.document_id = ? AND v.version_id = ?",
            (document_id, version_id),
        ).fetchone()
        records = parse_pdf(
            PROJECT_ROOT / row["pdf_path"],
            document_id,
            STORAGE / "assets",
            cfg["ingest"],
            version_id,
        )
        if not records:
            raise ValueError("no text could be read from the PDF")
        describe_figures(records, cfg)
        index_records(records, row["title"], cfg)
        set_state(conn, document_id, version_id, "READY")
        db.write_audit(
            conn, actor_id, "ingest", "ok", document_id, version_id, f"{len(records)} records"
        )
    except Exception as error:  # any failure ends in FAILED; details go to the log, not to users
        log.exception("ingestion failed for %s %s", document_id, version_id)
        set_state(conn, document_id, version_id, "FAILED")
        db.write_audit(
            conn, actor_id, "ingest", "failed", document_id, version_id, type(error).__name__
        )
    finally:
        conn.close()
