"""The SQLite catalogue: users, papers, versions, audit log and answer log.

Publication has one source of truth: documents.active_version_id. A version is visible to users
only when it is the active one for its paper. Rollback is publishing an older READY version.
"""

import csv
import hashlib
import sqlite3
from pathlib import Path

from app import security
from app.config import PROJECT_ROOT, load_config

ROLES = ("ADMIN", "USER")
STATES = ("DRAFT", "INDEXING", "READY", "FAILED")

SCHEMA = f"""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    login TEXT NOT NULL UNIQUE,
    role TEXT NOT NULL CHECK (role IN {ROLES}),
    password_hash TEXT NOT NULL,
    disabled INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS documents (
    document_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    authors TEXT NOT NULL,
    year INTEGER NOT NULL,
    source_url TEXT NOT NULL,
    active_version_id TEXT          -- the published version; NULL means retired
);
CREATE TABLE IF NOT EXISTS document_versions (
    document_id TEXT NOT NULL REFERENCES documents(document_id),
    version_id TEXT NOT NULL,
    file_sha256 TEXT NOT NULL,
    pdf_path TEXT NOT NULL,
    processing_state TEXT NOT NULL CHECK (processing_state IN {STATES}),
    parser_version TEXT NOT NULL,
    embedding_model TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (document_id, version_id)
);
CREATE TABLE IF NOT EXISTS audit_events (
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    actor_id INTEGER,
    action TEXT NOT NULL,
    document_id TEXT,
    version_id TEXT,
    outcome TEXT NOT NULL,
    detail TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS answer_log (
    query_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    question TEXT NOT NULL,
    snapshot TEXT NOT NULL,         -- the paper:version pairs searched, as JSON
    status TEXT NOT NULL,
    model_names TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
-- ADVANCED CODE: database triggers that refuse any change to audit rows. Each trigger runs
--   inside SQLite before an UPDATE or DELETE and aborts it, so the audit log can only grow.
-- WHY: the audit log must be append-only and enforced by the database, not only by habit
--   (master prompt section 6; brief requirement for an audit trail).
-- SIMPLER OPTION REJECTED: a code convention of never updating audit rows. Any future route,
--   script or manual SQL could break it silently; a trigger cannot be skipped by application code.
CREATE TRIGGER IF NOT EXISTS audit_no_update BEFORE UPDATE ON audit_events
BEGIN SELECT RAISE(ABORT, 'audit_events is append-only'); END;
CREATE TRIGGER IF NOT EXISTS audit_no_delete BEFORE DELETE ON audit_events
BEGIN SELECT RAISE(ABORT, 'audit_events is append-only'); END;
"""


def connect(path: Path | None = None) -> sqlite3.Connection:
    """Open the database with rows readable by column name and foreign keys enforced."""
    path = path or PROJECT_ROOT / load_config()["database"]["path"]
    path.parent.mkdir(parents=True, exist_ok=True)
    # FastAPI may open the connection in one worker thread and use it in another. That is safe here:
    # one connection serves one request at a time and is never shared between requests.
    conn = sqlite3.connect(path, timeout=10, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def create_schema(conn: sqlite3.Connection) -> None:
    """Create all tables and triggers if they do not exist yet."""
    conn.executescript(SCHEMA)


def seed_users(conn: sqlite3.Connection, accounts: list[tuple[str, str, str]]) -> None:
    """Insert (login, password, role) accounts that do not exist yet. Existing ones are kept."""
    for login, password, role in accounts:
        if conn.execute("SELECT 1 FROM users WHERE login = ?", (login,)).fetchone():
            continue
        conn.execute(
            "INSERT INTO users (login, role, password_hash) VALUES (?, ?, ?)",
            (login, role, security.hash_password(password)),
        )
    conn.commit()


def file_sha256(path: Path) -> str:
    """SHA-256 of a file's bytes."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def seed_papers(conn: sqlite3.Connection, cfg: dict | None = None) -> int:
    """Add the catalogue papers as published READY versions. Returns how many were added."""
    cfg = cfg or load_config()
    version = cfg["ingest"]["version_id"]
    catalogue = PROJECT_ROOT / "data" / "papers_catalogue.csv"
    added = 0
    with open(catalogue, encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            if conn.execute(
                "SELECT 1 FROM documents WHERE document_id = ?", (row["document_id"],)
            ).fetchone():
                continue
            pdf = Path("data") / "papers" / row["local_filename"]
            conn.execute(
                "INSERT INTO documents VALUES (?, ?, ?, ?, ?, ?)",
                (
                    row["document_id"],
                    row["title"],
                    row["authors"],
                    int(row["year"]),
                    row["source_url"],
                    version,
                ),
            )
            conn.execute(
                "INSERT INTO document_versions (document_id, version_id, file_sha256, pdf_path, "
                "processing_state, parser_version, embedding_model) "
                "VALUES (?, ?, ?, ?, 'READY', ?, ?)",
                (
                    row["document_id"],
                    version,
                    file_sha256(PROJECT_ROOT / pdf),
                    str(pdf),
                    "v1",
                    cfg["models"]["embedding"],
                ),
            )
            added += 1
    conn.commit()
    return added


def published_snapshot(conn: sqlite3.Connection) -> list[str]:
    """The paper:version pairs users may search: each paper's active version."""
    rows = conn.execute(
        "SELECT document_id, active_version_id FROM documents "
        "WHERE active_version_id IS NOT NULL ORDER BY document_id"
    ).fetchall()
    return [f"{r['document_id']}:{r['active_version_id']}" for r in rows]


def write_audit(
    conn, actor_id, action, outcome, document_id=None, version_id=None, detail=""
) -> None:
    """Append one audit event. The table's triggers make sure it can never be changed later."""
    conn.execute(
        "INSERT INTO audit_events (actor_id, action, document_id, version_id, outcome, detail) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (actor_id, action, document_id, version_id, outcome, detail[:500]),
    )
    conn.commit()
