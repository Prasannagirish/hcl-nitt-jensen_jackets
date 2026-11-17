# ResearchIQ — Implementation Brief (proposed, nothing built)

Hand-off after the design-review deck, as step 10 of `master_prompt_presentation_1_design.md`. Everything here is **proposed**. Detail: [researchiq_analysis.md](researchiq_analysis.md). Corrections to the decision log: [decisions_validation.md](decisions_validation.md).

## 1. Build order (Goal 1 first)

| # | Milestone | Done when |
|---|---|---|
| M0 | Topic and 8–10 papers fixed; keys in env; Pinecone Documents API, one embedding call and one vision call smoke-tested | Each probe prints OK or the documented fallback is chosen |
| M1 | One PDF parsed, chunked, indexed with page numbers and one figure crop | A search returns that page |
| M2 | All papers indexed; `/query` answers with citations or abstains | A cited answer and the exact abstention both appear |
| M3 | `/compare`, figure answers, source view, roles, publish | Comparison cites every selected paper; USER on an admin route gets 403 |
| M4 | 15+ questions run by script; metrics; two failures written | `make eval` writes every result file; a second run diffs empty |
| M5 | README, diagram, tests, demo, secret scan | Checklist in the analysis (R-19 to R-21) is ticked |

## 2. Decision function

`answer(question, snapshot, config) → Answer`
Inputs: question text, optional paper targets, snapshot of `(document_id, version_id)` pairs, config.
Output: `status` (`supported | partially_supported | no_answer`), `answer`, `claims[{text, evidence_ids}]`, `comparison_rows`, `evidence_gaps`, `grounded_suggestions`, `degraded` flags, model names.
Pipeline: access → scope → search (dense + BM25 per paper, same filter) → fuse (RRF k=60) → rerank per paper → expand to caption, table or crop → model writes JSON → validate (schema, IDs in set) → drop unsupported claims → answer or `No answer found in the knowledge base.`
Loop: invalid output gets one retry, then abstain.

## 3. Data model

| Table | Key fields | Values |
|---|---|---|
| `users` | `user_id, login, role, password_hash, disabled` | role: ADMIN, USER |
| `documents` | `document_id, title, authors, year, source_url, active_version_id` | pointer is nullable |
| `document_versions` | `version_id, document_id, file_sha256, pdf_path, processing_state, parser_version, embedding_model` | DRAFT, INDEXING, READY, FAILED |
| `evidence_manifest` | `evidence_id, document_id, version_id, pdf_page, kind, asset_id, figure_no, table_no, content_hash` | kind: text, table, figure |
| `audit_events` | `event_id, actor_id, action, document_id, version_id, outcome, timestamp` | append-only (triggers refuse UPDATE and DELETE) |
| `answer_log` | `query_id, user_id, snapshot_pairs, status, model_names` | one row per query |

Pinecone record fields (one schema module, see validation V-03): `evidence_id, document_id, version_id, docver, element_type, pdf_page, section_path, figure_number, body, embedding, asset_id, content_sha256`.

## 4. Interfaces

| Route | Caller | Request → response |
|---|---|---|
| `POST /auth/login`, `GET /me` | anyone / signed in | credentials → token; 401 on failure |
| `GET /papers` | USER, ADMIN | → published papers |
| `POST /query` | USER, ADMIN | `question` → Answer; 200 |
| `POST /compare` | USER, ADMIN | `document_ids[], question` → comparison rows; 200 |
| `GET /sources/{doc}/{version}/{asset}` | USER (published only), ADMIN | → file; 403 or 404 otherwise |
| `POST /admin/documents` | ADMIN | PDF → `202` + version ID; 422 invalid file |
| `POST /admin/documents/{id}/versions` | ADMIN | PDF → `202` |
| `POST /admin/documents/{id}/versions/{v}/publish` | ADMIN | → pointer moved; 409 if not READY or pointer changed. Rollback is publish of an older READY version |
| `GET /admin/documents/{id}/versions`, `GET /admin/audit` | ADMIN | history |

## 5. Configuration (in a YAML file or table, not code)

Roles; default deny; published-only search; Pinecone index and namespace; embedding model and dimension; vision model and fallback; `branch_top_k` 15; `rrf_k` 60; per-paper rerank pool; `final_top_n`; rerank model; abstention text; minimum-evidence rule **[value to be calibrated on a dev set, not invented]**; upload size and type limits; retry count. Secrets only in env vars; seed accounts from env vars and refuse to start if unset.

## 6. Acceptance tests

| Source | Check |
|---|---|
| Brief §6 nine example questions | One scenario each (problems, architecture comparison, shared benchmark, figure trend, table meaning, limitations, inconsistencies, research directions, enough-evidence) |
| Brief §9 split | 4 factual, 4 cross-paper, 3 visual, 2 synthesis, 1 unsupported, 1 injection (15; aim for 18–20) |
| Brief §8 | Poisoned fixture ignored; no key in repo (scan); error bodies contain no path or stack trace; upload of a non-PDF returns 422 |
| Roles | 401 without token; 403 for USER on admin routes; v2 staged but v1 cited; publish v2 then v2 cited; rollback restores v1; failed ingest leaves pointer unchanged |
| Boundaries | 7/8/10/11 papers; 14/15/16 questions |
| Repeatability | `make eval` twice; outputs diff empty |

## 7. Assumptions and risks

Assumptions: topic is 1 or 2; 8 papers minimum; the injection fixture is outside the catalogue; judges' live questions act as the hidden set; USER may not compare historical versions.
Risks: Documents API or model access unavailable (fallback in Pinecone only); roles and versions crowd out evaluation (use the minimum cut, V-01); table parsing errors (arithmetic on 1–2 tables only); vision cost and latency (cache by content hash); synthesis missing papers (per-paper quota).

## 8. Left open on purpose

Folder layout and library versions. They are decided when coding starts and shown in the final presentation (Prompt 2).
