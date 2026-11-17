"""API tests: access control, login, published-only search, publish rules, uploads, audit log.

Uses a temporary database and stubs the background indexer and the answer function, so no
network, model or index is touched. Live behaviour is covered by the evaluation run."""

import sqlite3
import threading

import pymupdf
import pytest
from fastapi.testclient import TestClient

from app import db, security
from app.answer import Answer, Claim
from app.config import PROJECT_ROOT, load_config

SECRET = "test-signing-secret-" + "x" * 24
ADMIN, USER = ("adm", "test-admin-pw"), ("usr", "test-user-pw")


@pytest.fixture()
def api(tmp_path, monkeypatch):
    """A running app on a temporary database, with the indexer stubbed."""
    env = {
        "JWT_SECRET": SECRET,
        "ADMIN_LOGIN": ADMIN[0],
        "ADMIN_PASSWORD": ADMIN[1],
        "USER_LOGIN": USER[0],
        "USER_PASSWORD": USER[1],
    }
    for key, value in env.items():
        monkeypatch.setenv(key, value)
    cfg = {**load_config(), "database": {"path": str(tmp_path / "test.sqlite")}}
    monkeypatch.setattr(db, "load_config", lambda: cfg)

    def fake_index(document_id, version_id, actor_id):
        conn = db.connect()
        conn.execute(
            "UPDATE document_versions SET processing_state = 'READY' "
            "WHERE document_id = ? AND version_id = ?",
            (document_id, version_id),
        )
        conn.commit()
        conn.close()

    monkeypatch.setattr("app.api.admin_routes.process_version", fake_index)
    from app.main import create_app

    with TestClient(create_app(), raise_server_exceptions=False) as client:
        yield client


def headers(api, who) -> dict:
    token = api.post("/auth/login", json={"login": who[0], "password": who[1]}).json()[
        "access_token"
    ]
    return {"Authorization": f"Bearer {token}"}


def pdf_bytes(pages=1, text="adapter rank note") -> bytes:
    doc = pymupdf.open()
    for number in range(pages):
        doc.new_page().insert_text((50, 50), f"{text} {number}")
    return doc.tobytes()


def upload(api, head, data, title="Test note"):
    form = {"title": title, "authors": "T", "year": "2026"}
    return api.post("/admin/documents", headers=head, data=form, files={"file": ("n.pdf", data)})


def fake_answer(snapshot, claims, evidence=None):
    ev = evidence or [
        {
            "evidence_id": "paper-003:v1:p1:text-1",
            "document_id": "paper-003",
            "version_id": "v1",
            "pdf_page": 1,
            "element_type": "text",
            "section_path": "",
            "figure_number": "",
            "table_number": "",
            "asset_id": "",
            "body": "full cited text",
            "description": "machine text that must not be sent",
            "excerpt": "old field",
        }
    ]
    return Answer(
        "supported", "x", claims=claims, evidence=ev, snapshot=snapshot, retrieved_ids=["a"]
    )


def retire(paper):
    conn = db.connect()
    conn.execute("UPDATE documents SET active_version_id = NULL WHERE document_id = ?", (paper,))
    conn.commit()
    conn.close()


# ---- access control ----------------------------------------------------------------------

PROTECTED = [
    ("get", "/me"),
    ("get", "/papers"),
    ("post", "/query"),
    ("post", "/compare"),
    ("get", "/sources/paper-003/v1/figure-1-p2.png"),
    ("get", "/admin/documents"),
    ("get", "/admin/audit"),
    ("get", "/admin/documents/paper-001/versions"),
    ("post", "/admin/documents"),
    ("post", "/admin/documents/paper-001/versions"),
    ("post", "/admin/documents/paper-001/versions/v1/publish"),
]
ADMIN_ONLY = [p for p in PROTECTED if p[1].startswith("/admin")]


@pytest.mark.parametrize("method,path", PROTECTED)
def test_no_token_is_401_everywhere(api, method, path):
    assert getattr(api, method)(path).status_code == 401


@pytest.mark.parametrize("method,path", ADMIN_ONLY)
def test_a_reader_gets_403_on_every_admin_route(api, method, path):
    assert getattr(api, method)(path, headers=headers(api, USER)).status_code == 403


def test_tampered_expired_and_wrong_secret_tokens_are_rejected(api):
    good = headers(api, USER)["Authorization"].split()[1]
    for token in (
        good[:-4] + "AAAA",
        security.make_token(2, "USER", SECRET, -1),
        security.make_token(2, "USER", "other-secret-" + "y" * 24, 1),
    ):
        assert api.get("/me", headers={"Authorization": f"Bearer {token}"}).status_code == 401
    assert api.get("/me", headers={"Authorization": "Basic abc"}).status_code == 401


def test_a_token_for_a_deleted_or_disabled_account_stops_working(api):
    head = headers(api, USER)
    conn = db.connect()
    conn.execute("UPDATE users SET disabled = 1 WHERE login = ?", (USER[0],))
    conn.commit()
    conn.close()
    assert api.get("/me", headers=head).status_code == 401
    assert api.post("/auth/login", json={"login": USER[0], "password": USER[1]}).status_code == 401


# ---- login -------------------------------------------------------------------------------


def test_wrong_password_and_unknown_login_look_identical(api):
    wrong = api.post("/auth/login", json={"login": ADMIN[0], "password": "nope"})
    unknown = api.post("/auth/login", json={"login": "ghost", "password": "nope"})
    assert wrong.status_code == unknown.status_code == 401 and wrong.json() == unknown.json()


def test_invalid_login_bodies_name_the_field_and_never_echo_input(api):
    response = api.post("/auth/login", json={"login": "a", "password": ""})
    assert (
        response.status_code == 422
        and "password" in response.text
        and '"input"' not in response.text
    )
    assert api.post("/auth/login", json={"login": "a", "password": "x" * 201}).status_code == 422


def test_roles_come_back_correctly(api):
    assert api.get("/me", headers=headers(api, ADMIN)).json()["role"] == "ADMIN"
    assert api.get("/me", headers=headers(api, USER)).json()["role"] == "USER"


# ---- published-only search ---------------------------------------------------------------


def test_readers_see_only_published_papers_and_admins_see_all(api):
    assert len(api.get("/papers", headers=headers(api, USER)).json()) == 8
    retire("paper-002")
    assert len(api.get("/papers", headers=headers(api, USER)).json()) == 7
    assert len(api.get("/admin/documents", headers=headers(api, ADMIN)).json()) == 8


def test_query_searches_only_published_versions_and_logs_the_query(api, monkeypatch):
    seen = {}

    def fake(question, snapshot, per_paper=False):
        seen["snapshot"], seen["per_paper"] = snapshot, per_paper
        return fake_answer(snapshot, [Claim("A", ["paper-003:v1:p1:text-1"])])

    monkeypatch.setattr("app.api.query_routes.answer", fake)
    retire("paper-005")
    body = api.post("/query", headers=headers(api, USER), json={"question": "What?"}).json()
    assert "paper-005:v1" not in seen["snapshot"] and len(seen["snapshot"]) == 7
    assert "retrieved_ids" not in body and "description" not in body["evidence"][0]
    assert body["evidence"][0]["body"] == "full cited text"
    conn = db.connect()
    assert (
        conn.execute("SELECT COUNT(*) FROM answer_log WHERE status = 'supported'").fetchone()[0]
        == 1
    )
    conn.close()


def test_query_input_limits_and_service_failure(api, monkeypatch):
    head = headers(api, USER)
    assert api.post("/query", headers=head, json={"question": ""}).status_code == 422
    assert api.post("/query", headers=head, json={"question": "x" * 1001}).status_code == 422

    def boom(*args, **kwargs):
        raise RuntimeError("secret internal detail at /Users/someone/path")

    monkeypatch.setattr("app.api.query_routes.answer", boom)
    response = api.post("/query", headers=head, json={"question": "ok"})
    assert (
        response.status_code == 503
        and "secret" not in response.text
        and "/Users" not in response.text
    )


def test_an_unexpected_error_returns_a_request_id_and_no_internals(api, monkeypatch):
    def boom(conn):
        raise RuntimeError("unexpected failure at /private/path")

    monkeypatch.setattr(db, "published_snapshot", boom)
    response = api.post("/query", headers=headers(api, USER), json={"question": "ok"})
    assert response.status_code == 500 and set(response.json()) == {"detail", "request_id"}
    assert "private" not in response.text and "Traceback" not in response.text


def test_compare_marks_papers_without_support_as_not_reported(api, monkeypatch):
    monkeypatch.setattr(
        "app.api.query_routes.answer",
        lambda q, s, per_paper=False: fake_answer(s, [Claim("Only A", ["paper-003:v1:p1:text-1"])]),
    )
    head = headers(api, USER)
    rows = api.post(
        "/compare", headers=head, json={"document_ids": ["paper-003", "paper-004"]}
    ).json()["comparison_rows"]
    assert rows[0]["statements"] == ["Only A"] and rows[1]["statements"] == ["NOT REPORTED"]


def test_compare_input_rules(api):
    head = headers(api, USER)
    assert (
        api.post("/compare", headers=head, json={"document_ids": ["paper-003"]}).status_code == 422
    )
    assert (
        api.post(
            "/compare", headers=head, json={"document_ids": ["paper-003", "paper-999"]}
        ).status_code
        == 404
    )
    retire("paper-004")
    assert (
        api.post(
            "/compare", headers=head, json={"document_ids": ["paper-003", "paper-004"]}
        ).status_code
        == 404
    )


# ---- source viewer -----------------------------------------------------------------------


def test_source_access_rules(api):
    head = headers(api, USER)
    for path in (
        "/sources/paper-003/v2/figure-1-p2.png",  # unpublished version
        "/sources/paper-003/v1/..%2F..%2F.env",  # traversal
        "/sources/paper-003/v1/paper-003.jsonl",  # not a png
        "/sources/paper-003/v1/nothere.png",  # missing
        "/sources/nobody/v1/figure-1-p2.png",  # unknown paper
    ):
        assert api.get(path, headers=head).status_code == 404
    crop = PROJECT_ROOT / "backend/storage/assets/paper-003/v1/figure-1-p2.png"
    if crop.exists():
        assert (
            api.get("/sources/paper-003/v1/figure-1-p2.png", headers=head).content[:4] == b"\x89PNG"
        )


# ---- publishing --------------------------------------------------------------------------


def add_version(paper, version, state):
    conn = db.connect()
    conn.execute(
        "INSERT INTO document_versions (document_id, version_id, file_sha256, pdf_path, "
        "processing_state, parser_version, embedding_model) VALUES (?, ?, ?, 'x', ?, 'v1', 'e')",
        (paper, version, f"sha-{paper}-{version}", state),
    )
    conn.commit()
    conn.close()


def publish(api, paper, version, expected):
    return api.post(
        f"/admin/documents/{paper}/versions/{version}/publish",
        headers=headers(api, ADMIN),
        json={"expected_active_version_id": expected},
    )


def test_publish_rules_and_rollback(api):
    add_version("paper-001", "v2", "READY")
    add_version("paper-001", "v3", "DRAFT")
    assert publish(api, "paper-001", "v2", "v9").status_code == 409  # pointer moved
    assert publish(api, "paper-001", "v3", "v1").status_code == 409  # not READY
    assert publish(api, "paper-001", "v7", "v1").status_code == 404  # unknown
    assert (
        api.post(
            "/admin/documents/paper-001/versions/v2/publish", headers=headers(api, ADMIN), json={}
        ).status_code
        == 422
    )
    assert publish(api, "paper-001", "v2", "v1").json()["active_version_id"] == "v2"
    assert publish(api, "paper-001", "v1", "v2").status_code == 200  # rollback to the older version
    conn = db.connect()
    active = conn.execute(
        "SELECT active_version_id FROM documents WHERE document_id = 'paper-001'"
    ).fetchone()[0]
    outcomes = [
        r[0] for r in conn.execute("SELECT outcome FROM audit_events WHERE action = 'publish'")
    ]
    conn.close()
    assert active == "v1" and outcomes.count("refused") == 2 and outcomes.count("ok") == 2


def test_two_simultaneous_publishes_cannot_both_win():
    path = PROJECT_ROOT / "backend/storage/race-test.sqlite"
    conn = db.connect(path)
    db.create_schema(conn)
    conn.execute("INSERT INTO documents VALUES ('p', 't', 'a', 2026, 'u', 'v1')")
    conn.commit()
    wins = []

    def attempt(version):
        own = db.connect(path)
        moved = own.execute(
            "UPDATE documents SET active_version_id = ? "
            "WHERE document_id = 'p' AND active_version_id IS ?",
            (version, "v1"),
        ).rowcount
        own.commit()
        own.close()
        wins.append(moved)

    threads = [threading.Thread(target=attempt, args=(v,)) for v in ("v2", "v3")]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    conn.close()
    path.unlink()
    assert sorted(wins) == [0, 1]


# ---- uploads -----------------------------------------------------------------------------


def test_invalid_uploads_are_rejected(api):
    head = headers(api, ADMIN)
    assert upload(api, head, b"hello world").status_code == 422  # not a PDF
    assert upload(api, head, b"%PDF-1.4 garbage").status_code == 422  # header only
    assert upload(api, head, pdf_bytes(pages=101)).status_code == 422  # too many pages
    form = {"title": "", "authors": "T", "year": "2026"}
    assert (
        api.post(
            "/admin/documents", headers=head, data=form, files={"file": ("n.pdf", pdf_bytes())}
        ).status_code
        == 422
    )
    form = {"title": "t", "authors": "T", "year": "1800"}
    assert (
        api.post(
            "/admin/documents", headers=head, data=form, files={"file": ("n.pdf", pdf_bytes())}
        ).status_code
        == 422
    )


def test_upload_is_hidden_until_published_and_identical_bytes_reuse_the_version(api):
    head, data = headers(api, ADMIN), pdf_bytes(text="unique note")
    created = upload(api, head, data)
    assert created.status_code == 202
    paper, version = created.json()["document_id"], created.json()["version_id"]
    assert paper not in [
        p["document_id"] for p in api.get("/papers", headers=headers(api, USER)).json()
    ]
    again = api.post(
        f"/admin/documents/{paper}/versions", headers=head, files={"file": ("n.pdf", data)}
    )
    assert again.json()["duplicate"] is True and again.json()["version_id"] == version
    assert publish(api, paper, version, None).status_code == 200
    assert paper in [
        p["document_id"] for p in api.get("/papers", headers=headers(api, USER)).json()
    ]


def test_upload_to_an_unknown_paper_is_404(api):
    r = api.post(
        "/admin/documents/paper-999/versions",
        headers=headers(api, ADMIN),
        files={"file": ("n.pdf", pdf_bytes())},
    )
    assert r.status_code == 404


# ---- audit log ---------------------------------------------------------------------------


def test_the_database_refuses_to_change_or_delete_audit_rows(api):
    headers(api, ADMIN)  # writes a login event
    conn = db.connect()
    for sql in ("UPDATE audit_events SET outcome = 'x'", "DELETE FROM audit_events"):
        with pytest.raises(sqlite3.DatabaseError, match="append-only"):
            conn.execute(sql)
    assert conn.execute("SELECT COUNT(*) FROM audit_events").fetchone()[0] >= 1
    conn.close()


def test_logins_succeed_and_fail_into_the_audit_log(api):
    api.post("/auth/login", json={"login": ADMIN[0], "password": "bad"})
    headers(api, ADMIN)
    events = api.get("/admin/audit", headers=headers(api, ADMIN)).json()
    assert {(e["action"], e["outcome"]) for e in events} >= {("login", "denied"), ("login", "ok")}


def test_startup_refuses_to_run_without_credentials(monkeypatch, tmp_path):
    monkeypatch.setenv("JWT_SECRET", "change-me")
    monkeypatch.setenv("ADMIN_PASSWORD", "choose-a-password")
    from app.main import create_app

    with pytest.raises(RuntimeError, match="JWT_SECRET"):
        with TestClient(create_app()):
            pass


# ---- error handling ----------------------------------------------------------------------


def test_a_locked_database_gives_a_503_the_reader_can_retry(api, monkeypatch):
    def locked(conn):
        raise sqlite3.OperationalError("database is locked: /private/path/x.sqlite")

    monkeypatch.setattr(db, "published_snapshot", locked)
    response = api.post("/query", headers=headers(api, USER), json={"question": "ok"})
    assert response.status_code == 503 and "busy" in response.json()["detail"]
    assert "private" not in response.text and "sqlite" not in response.text.lower()


def test_malformed_and_wrongly_typed_json_gives_422_without_echoing_input(api):
    head = headers(api, USER)
    broken = api.post(
        "/query", headers={**head, "Content-Type": "application/json"}, content=b'{"question": '
    )
    assert broken.status_code == 422 and "Invalid request" in broken.text
    typed = api.post("/query", headers=head, json={"question": 12345})
    assert typed.status_code == 422 and "12345" not in typed.text
    assert api.post("/compare", headers=head, json={"document_ids": "paper-003"}).status_code == 422


def test_unknown_routes_and_wrong_methods_return_plain_json_errors(api):
    assert api.get("/nothing-here").status_code == 404
    assert api.get("/nothing-here").json() == {"detail": "Not Found"}
    assert api.get("/query", headers=headers(api, USER)).status_code == 405
    assert api.delete("/papers", headers=headers(api, USER)).status_code == 405


def test_a_missing_upload_file_or_field_is_a_422_naming_the_problem(api):
    head = headers(api, ADMIN)
    response = api.post(
        "/admin/documents", headers=head, data={"title": "t", "authors": "a", "year": "2026"}
    )
    assert response.status_code == 422 and "file" in response.text
    response = api.post("/admin/documents", headers=head, files={"file": ("n.pdf", pdf_bytes())})
    assert response.status_code == 422


def test_a_failed_background_job_marks_the_version_failed_and_never_publishes(api, monkeypatch):
    from app import ingestion

    def broken(*args, **kwargs):
        raise ValueError("cannot parse")

    monkeypatch.setattr(ingestion, "parse_pdf", broken)
    monkeypatch.setattr("app.api.admin_routes.process_version", ingestion.process_version)
    head = headers(api, ADMIN)
    created = upload(api, head, pdf_bytes(text="will fail"))
    paper, version = created.json()["document_id"], created.json()["version_id"]
    states = {
        v["version_id"]: v["processing_state"]
        for v in api.get(f"/admin/documents/{paper}/versions", headers=head).json()
    }
    assert states[version] == "FAILED"
    assert publish(api, paper, version, None).status_code == 409
    assert paper not in [
        p["document_id"] for p in api.get("/papers", headers=headers(api, USER)).json()
    ]
    events = api.get("/admin/audit", headers=head).json()
    failed = [e for e in events if e["action"] == "ingest" and e["outcome"] == "failed"]
    assert failed and failed[0]["detail"] == "ValueError"  # the type only, never the message
