"""Routes for readers: list papers, ask a question, compare papers, open a figure crop.

Every search covers only the versions published in the database right now (the active pointer of
each paper). A reader can never reach an unpublished version through any of these routes.
"""

import json
import logging
import re
import sqlite3

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from app import db
from app.answer import Answer, answer
from app.api.deps import current_user, get_db
from app.config import PROJECT_ROOT

router = APIRouter()
log = logging.getLogger("researchiq")
NOT_REPORTED = "NOT REPORTED"
ASSET_RE = re.compile(r"^[A-Za-z0-9._-]+\.png$")
ID_RE = re.compile(r"^[A-Za-z0-9._-]+$")
DEFAULT_COMPARISON = (
    "Compare these papers on their objectives, methods, architecture, data, metrics and results, "
    "and state similarities, differences, trade-offs and limitations."
)


class QueryRequest(BaseModel):
    """A question for the whole published collection."""

    question: str = Field(min_length=1, max_length=1000)


class CompareRequest(BaseModel):
    """Papers to compare and an optional question about them."""

    document_ids: list[str] = Field(min_length=2, max_length=10)
    question: str = Field(default="", max_length=1000)


def run_answer(question: str, snapshot: list[str], per_paper: bool) -> Answer:
    """Call answer(); a failure in a backing service becomes a clear 503, not a stack trace."""
    try:
        return answer(question, snapshot, per_paper=per_paper)
    except Exception:
        log.exception("answer failed")
        raise HTTPException(
            status_code=503, detail="The search service is unavailable. Try again later."
        ) from None


def public_answer(result: Answer) -> dict:
    """The answer as sent to the browser: the cited text in full, with source links for crops."""
    data = result.to_dict()
    data.pop("retrieved_ids", None)
    for item in data["evidence"]:
        item.pop("description", None)  # machine-written, never shown as paper text
        item.pop("excerpt", None)  # the full text of the cited piece is sent as "body"
        if item["asset_id"]:
            item["source_url"] = (
                f"/sources/{item['document_id']}/{item['version_id']}/{item['asset_id']}"
            )
    return data


def log_query(conn: sqlite3.Connection, user: dict, question: str, result: Answer) -> None:
    """Record who asked, what versions were searched, the outcome and the models used."""
    conn.execute(
        "INSERT INTO answer_log (user_id, question, snapshot, status, model_names) "
        "VALUES (?, ?, ?, ?, ?)",
        (
            user["user_id"],
            question[:1000],
            json.dumps(result.snapshot),
            result.status,
            json.dumps(result.models),
        ),
    )
    conn.commit()


@router.get("/papers")
def list_papers(
    user: dict = Depends(current_user), conn: sqlite3.Connection = Depends(get_db)
) -> list:
    """The published papers."""
    rows = conn.execute(
        "SELECT document_id, title, authors, year, source_url, active_version_id FROM documents "
        "WHERE active_version_id IS NOT NULL ORDER BY document_id"
    ).fetchall()
    return [dict(row) for row in rows]


@router.post("/query")
def query(
    body: QueryRequest,
    user: dict = Depends(current_user),
    conn: sqlite3.Connection = Depends(get_db),
) -> dict:
    """Answer a question from the published papers."""
    snapshot = db.published_snapshot(conn)
    result = run_answer(body.question, snapshot, per_paper=False)
    log_query(conn, user, body.question, result)
    return public_answer(result)


def comparison_rows(result: Answer, titles: dict[str, str]) -> list[dict]:
    """One row per selected paper: the claims that cite it, or NOT REPORTED when none do."""
    rows = []
    for document_id, title in titles.items():
        statements = [
            c.text
            for c in result.claims
            if any(i.startswith(f"{document_id}:") for i in c.evidence_ids)
        ]
        rows.append(
            {"document_id": document_id, "title": title, "statements": statements or [NOT_REPORTED]}
        )
    return rows


@router.post("/compare")
def compare(
    body: CompareRequest,
    user: dict = Depends(current_user),
    conn: sqlite3.Connection = Depends(get_db),
) -> dict:
    """Compare the selected published papers. Each paper is searched on its own."""
    published = {p.split(":")[0]: p for p in db.published_snapshot(conn)}
    unknown = [d for d in body.document_ids if d not in published]
    if unknown:
        raise HTTPException(status_code=404, detail="One or more papers were not found")
    snapshot = [published[d] for d in dict.fromkeys(body.document_ids)]
    question = body.question.strip() or DEFAULT_COMPARISON
    result = run_answer(question, snapshot, per_paper=True)
    log_query(conn, user, question, result)
    titles = {
        d: conn.execute("SELECT title FROM documents WHERE document_id = ?", (d,)).fetchone()[
            "title"
        ]
        for d in dict.fromkeys(body.document_ids)
    }
    data = public_answer(result)
    data["comparison_rows"] = comparison_rows(result, titles)
    return data


@router.get("/sources/{document_id}/{version_id}/{asset_id}")
def source_asset(
    document_id: str,
    version_id: str,
    asset_id: str,
    user: dict = Depends(current_user),
    conn: sqlite3.Connection = Depends(get_db),
) -> FileResponse:
    """A saved figure crop. Readers get published versions only; anything else is a 404."""
    if not (ID_RE.match(document_id) and ID_RE.match(version_id) and ASSET_RE.match(asset_id)):
        raise HTTPException(status_code=404, detail="Not found")
    if user["role"] != "ADMIN":
        row = conn.execute(
            "SELECT active_version_id FROM documents WHERE document_id = ?", (document_id,)
        ).fetchone()
        if row is None or row["active_version_id"] != version_id:
            raise HTTPException(status_code=404, detail="Not found")
    base = (PROJECT_ROOT / "backend" / "storage" / "assets").resolve()
    path = (base / document_id / version_id / asset_id).resolve()
    if base not in path.parents or not path.is_file():
        raise HTTPException(status_code=404, detail="Not found")
    return FileResponse(path, media_type="image/png")
