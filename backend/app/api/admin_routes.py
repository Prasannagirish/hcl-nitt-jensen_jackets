"""Routes for admins: upload papers and new versions, check processing, publish, read the audit log.

Uploads are checked (type, size, PDF header, page count), saved under a generated name, and
processed in the background. Readers see nothing new until an admin publishes a READY version.
"""

import sqlite3

import pymupdf
from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, UploadFile
from pydantic import BaseModel

from app import db
from app.api.deps import get_db, require_admin
from app.config import PROJECT_ROOT, load_config
from app.ingestion import process_version

router = APIRouter(prefix="/admin")
MAX_PAGES = 100
UPLOAD_DIR = PROJECT_ROOT / "data" / "uploads"


class PublishRequest(BaseModel):
    """The pointer the admin saw. Publishing is refused if it has moved since."""

    expected_active_version_id: str | None  # required, but may be null for an unpublished paper


def read_pdf_upload(file: UploadFile) -> bytes:
    """The uploaded bytes, after checks on size, PDF header and page count (422 if one fails)."""
    limit = load_config()["auth"]["max_upload_mb"] * 1024 * 1024
    data = file.file.read(limit + 1)
    if len(data) > limit:
        raise HTTPException(status_code=422, detail="The file is too large")
    if not data.startswith(b"%PDF-"):
        raise HTTPException(status_code=422, detail="The file is not a PDF")
    try:
        with pymupdf.open(stream=data, filetype="pdf") as doc:
            pages = len(doc)
    except Exception:
        raise HTTPException(status_code=422, detail="The PDF could not be opened") from None
    if not 1 <= pages <= MAX_PAGES:
        raise HTTPException(status_code=422, detail=f"The PDF must have 1 to {MAX_PAGES} pages")
    return data


def next_paper_id(conn: sqlite3.Connection) -> str:
    """Next paper identifier such as paper-009."""
    ids = [r[0] for r in conn.execute("SELECT document_id FROM documents")]
    numbers = [int(i[6:]) for i in ids if i.startswith("paper-") and i[6:].isdigit()]
    return f"paper-{(max(numbers) + 1 if numbers else 1):03d}"


def next_version_id(conn: sqlite3.Connection, document_id: str) -> str:
    """Next version identifier of a paper, such as v3."""
    rows = conn.execute(
        "SELECT version_id FROM document_versions WHERE document_id = ?", (document_id,)
    ).fetchall()
    numbers = [int(r[0][1:]) for r in rows if r[0][1:].isdigit()]
    return f"v{(max(numbers) + 1 if numbers else 1)}"


def store_version(conn, document_id: str, data: bytes, actor_id: int) -> tuple[str, bool]:
    """Save the PDF as a new version, or return the existing one for identical bytes."""
    sha = db.hashlib.sha256(data).hexdigest()
    same = conn.execute(
        "SELECT version_id FROM document_versions WHERE document_id = ? AND file_sha256 = ?",
        (document_id, sha),
    ).fetchone()
    if same:
        return same["version_id"], True
    version_id = next_version_id(conn, document_id)
    path = UPLOAD_DIR / document_id / f"{version_id}.pdf"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    cfg = load_config()
    conn.execute(
        "INSERT INTO document_versions (document_id, version_id, file_sha256, pdf_path, "
        "processing_state, parser_version, embedding_model) VALUES (?, ?, ?, ?, 'DRAFT', 'v1', ?)",
        (
            document_id,
            version_id,
            sha,
            str(path.relative_to(PROJECT_ROOT)),
            cfg["models"]["embedding"],
        ),
    )
    conn.commit()
    db.write_audit(conn, actor_id, "upload", "ok", document_id, version_id)
    return version_id, False


@router.post("/documents", status_code=202)
def upload_document(
    background: BackgroundTasks,
    file: UploadFile = File(...),
    title: str = Form(min_length=1, max_length=300),
    authors: str = Form(min_length=1, max_length=500),
    year: int = Form(ge=1990, le=2100),
    source_url: str = Form(default="", max_length=500),
    admin: dict = Depends(require_admin),
    conn: sqlite3.Connection = Depends(get_db),
) -> dict:
    """Add a new paper. It is processed in the background and is not visible until published."""
    data = read_pdf_upload(file)
    document_id = next_paper_id(conn)
    conn.execute(
        "INSERT INTO documents (document_id, title, authors, year, source_url, active_version_id) "
        "VALUES (?, ?, ?, ?, ?, NULL)",
        (document_id, title, authors, year, source_url),
    )
    version_id, _ = store_version(conn, document_id, data, admin["user_id"])
    background.add_task(process_version, document_id, version_id, admin["user_id"])
    return {"document_id": document_id, "version_id": version_id, "processing_state": "DRAFT"}


@router.post("/documents/{document_id}/versions", status_code=202)
def upload_version(
    document_id: str,
    background: BackgroundTasks,
    file: UploadFile = File(...),
    admin: dict = Depends(require_admin),
    conn: sqlite3.Connection = Depends(get_db),
) -> dict:
    """Add a new version of an existing paper. The same file twice returns the existing version."""
    if (
        conn.execute("SELECT 1 FROM documents WHERE document_id = ?", (document_id,)).fetchone()
        is None
    ):
        raise HTTPException(status_code=404, detail="Paper not found")
    data = read_pdf_upload(file)
    version_id, duplicate = store_version(conn, document_id, data, admin["user_id"])
    if not duplicate:
        background.add_task(process_version, document_id, version_id, admin["user_id"])
    state = conn.execute(
        "SELECT processing_state FROM document_versions WHERE document_id = ? AND version_id = ?",
        (document_id, version_id),
    ).fetchone()["processing_state"]
    return {
        "document_id": document_id,
        "version_id": version_id,
        "processing_state": state,
        "duplicate": duplicate,
    }


@router.get("/documents")
def list_documents(
    admin: dict = Depends(require_admin), conn: sqlite3.Connection = Depends(get_db)
) -> list:
    """Every paper with its active version and all versions, whether published or not."""
    documents = []
    for doc in conn.execute("SELECT * FROM documents ORDER BY document_id").fetchall():
        versions = conn.execute(
            "SELECT version_id, processing_state, created_at FROM document_versions "
            "WHERE document_id = ? ORDER BY version_id",
            (doc["document_id"],),
        ).fetchall()
        documents.append({**dict(doc), "versions": [dict(v) for v in versions]})
    return documents


@router.get("/documents/{document_id}/versions")
def list_versions(
    document_id: str,
    admin: dict = Depends(require_admin),
    conn: sqlite3.Connection = Depends(get_db),
) -> list:
    """The versions of one paper with their processing state."""
    rows = conn.execute(
        "SELECT version_id, processing_state, file_sha256, created_at FROM document_versions "
        "WHERE document_id = ? ORDER BY version_id",
        (document_id,),
    ).fetchall()
    if not rows:
        raise HTTPException(status_code=404, detail="Paper not found")
    return [dict(r) for r in rows]


@router.post("/documents/{document_id}/versions/{version_id}/publish")
def publish(
    document_id: str,
    version_id: str,
    body: PublishRequest,
    admin: dict = Depends(require_admin),
    conn: sqlite3.Connection = Depends(get_db),
) -> dict:
    """Make a READY version the one readers see. Publishing an older READY version is a rollback.

    The update only succeeds if the pointer still holds the value the admin saw (409 otherwise),
    so two admins publishing at once cannot silently overwrite each other.
    """
    row = conn.execute(
        "SELECT processing_state FROM document_versions WHERE document_id = ? AND version_id = ?",
        (document_id, version_id),
    ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Version not found")
    if row["processing_state"] != "READY":
        db.write_audit(
            conn, admin["user_id"], "publish", "refused", document_id, version_id, "not READY"
        )
        raise HTTPException(status_code=409, detail="Only a READY version can be published")
    moved = conn.execute(
        "UPDATE documents SET active_version_id = ? "
        "WHERE document_id = ? AND active_version_id IS ?",
        (version_id, document_id, body.expected_active_version_id),
    ).rowcount
    conn.commit()
    if not moved:
        db.write_audit(
            conn, admin["user_id"], "publish", "refused", document_id, version_id, "pointer changed"
        )
        raise HTTPException(
            status_code=409, detail="The published version changed; reload and try again"
        )
    db.write_audit(conn, admin["user_id"], "publish", "ok", document_id, version_id)
    return {"document_id": document_id, "active_version_id": version_id}


@router.get("/audit")
def audit(admin: dict = Depends(require_admin), conn: sqlite3.Connection = Depends(get_db)) -> list:
    """The newest 200 audit events."""
    rows = conn.execute("SELECT * FROM audit_events ORDER BY event_id DESC LIMIT 200").fetchall()
    return [dict(r) for r in rows]
