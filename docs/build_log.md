# Build log

What is built, how it was checked, and what is known to be weak. Updated at each milestone. Plan and assumptions: [intake.md](intake.md).

## Status

| Module | State |
|---|---|
| 0 Intake | Done. Topic: memory-efficient LLM fine-tuning, 8 papers |
| 1 Design (schema and config) | Done: `backend/app/schema.py`, `config/researchiq.yaml` |
| 2a Parse, chunk, figure crops (local) | Done and checked by running and by eye (below) |
| M0 smoke test (keys, embedding, vision, Pinecone, rerank) | Done, all passed (below) |
| 2a Embed and index in Pinecone | Done: 606 records in index `researchiq`, namespace `papers` |
| 2b `answer()` with hybrid search, gate, abstention | Done (below) |
| 2c Evaluation set, runner, metrics, failure analysis | Done: 21 questions, 15 of 21 correct by rule (below) |
| 3 Application: API, roles, publish, React UI | Built and checked by running (below). No automated test suite yet (Module 4) |
| 4 Verification | Done for the critical checks (below). Several planned checks were not run |
| 5 Finalisation | README written; the full clean rebuild was not run (below) |

## M0 smoke test results

Command: `uv run python scripts/smoke_test.py`. Run once on 2026-11-17. It creates a temporary Pinecone index, uses it and deletes it; a follow-up check showed no indexes left.

| Probe | Result |
|---|---|
| OpenAI embedding `text-embedding-3-small` | OK, 1536-dimension vectors |
| Vision on paper-003 Fig 1 (one question each) | `gpt-6.1-sol` OK 2.7s, named the 1.1x to 2.6x range correctly; `gpt-6.1-terra` OK 4.7s, less detail; `gpt-4o` OK 1.5s, less detail |
| Pinecone schema index (dense vector field + BM25 text field) | Created; dense search returned the right document; BM25 search with a metadata filter returned the right document |
| Pinecone rerank (`bge-reranker-v2-m3`, `pinecone-rerank-v0`) | Both OK, both ranked the right passage first; `bge` separated scores more clearly (0.648 vs 0.001) |

This closes the design's unverified items D-05 (Documents API), D-11 and V-12 (model IDs, reranker name). Note that Pinecone's `dense_vector` clause must be alone in a search call, so dense and BM25 are separate calls fused by RRF in code, as designed.

**Limits of this test.** Three documents and one figure only. It does not show answer quality, latency under load, cost, or that the answer model can return structured JSON (tested in Module 2b). The `$in` form of the version filter (validation V-04) was not tried; only `$eq`. The vision test used one question on one figure, so the choice of `gpt-6.1-sol` is a first impression, not a comparison on a quality measure. No fallback path (a model or service failing) was exercised.

## Indexing results

Command: `uv run python scripts/index_papers.py` (about 8 minutes; the 56 vision calls dominate). Safe to re-run: IDs are fixed, and figure descriptions are cached by image hash in `backend/storage/vision_cache/`.

- 606 records upserted; the namespace reports 606. 56 of 56 figures have a description (about 850 to 1400 characters each). Largest record 3.3 KB.
- Figure descriptions are a search aid only. They are stored in a separate `description` field and answers show the paper's caption and the crop, not the description.
- Only 4 of the 56 descriptions were read by a person (indirectly, through answers that used them). The rest are unreviewed.

## Module 2b: retrieval and answers

Code: `backend/app/retrieval.py` (dense + BM25, rank fusion, per-paper rerank), `backend/app/answer.py` (the single decision function), `scripts/calibrate_gate.py`, `scripts/ask.py`.

**Checked by running (real index, real models):**

| Check | Result |
|---|---|
| Retrieval on "speed-up of ENGINE over LOREN" | The right figure ranked first (rerank 0.992); all 8 hits from paper-003 |
| Version filter with `$in` (closes validation V-04) | Restricting to `paper-007:v1` returned only paper-007; the nonexistent `paper-003:v2` returned nothing |
| Supported answer, text evidence | Correct numbers (2.61x forward-pass, 2.58x wall-clock), verified against the PDF text |
| Supported answer, table evidence | SST-2 values (FO-Adam 93.0, StructZO 92.4) match the parsed table |
| Two-paper comparison (per-paper mode) | Cites both papers. Numbers verified against Table 2: GPT-2-XL average 73.4 vs MeZO 59.4, OPT-13B 66.4 vs 63.3. "Wins every cell" checked on all 16 cells. StructZO details (q = 100, O(rn) memory) found in the PDF |
| Visual question (MeltKV Fig 4) | Bit-packing layout read correctly from the crop |
| Off-topic or near-topic unsupported question (ImageNet) | Exact abstention, stopped by the score gate before the model was called |
| Unsupported detail that passes the gate (StructZO on LLaMA-3-70B) | Model returned no claims and named the gap; exact abstention |
| Identical question asked twice | Identical answer (second run 4.4 s: retrieval live, model reply from cache) |

**Gate calibration** (`config/calibration.json`, from `eval/dev_calibration.jsonl`: 7 answerable, 6 unsupported): lowest answerable score 0.954, highest unsupported 0.785, threshold 0.869 (halfway). The two groups separate.

**Defect found and fixed:** the reranker rejects any question-plus-passage pair above 1024 tokens. A number-heavy table triggered this and the system silently fell back to fusion order (flagged as `rerank_failed`). Fixed by asking the reranker to truncate and shortening the character cut. The calibration was re-run after the fix with the same result.

**Limits, stated plainly.**
- The dev set is 13 questions and the evaluation set does not exist yet. These 7 answers are spot checks, not metrics.
- Near-topic unsupported questions scored 0.78 (ImageNet) and 0.60 (Llama-3-405B) against a threshold of 0.869. That margin is thin. For those the score gate is not the only protection: the claim check and the model's own "no claims" answer also apply, but only one such case was exercised end to end.
- Temperature 0 is rejected by both 6.1 models. Repeatability comes from the reply cache (assumption A-18), so a second evaluation run proves the pipeline is deterministic around the model, not that the model is.
- After the truncate fix, the rerank-failure fallback path was not exercised again. Its first accidental run did produce a valid answer.
- Not yet tested: prompt injection inside a paper (Module 4), a model or Pinecone outage, concurrency, latency (single questions took 5 to 17 s), cost, the whole-collection synthesis path, and claims that cite a wrong page.
- Per-paper mode was tried on two papers only.

## Module 2c: evaluation

Command: `make eval` (writes `eval/eval_results.csv`, `ablation.csv`, `judge_details.jsonl`, `eval_report.md`). Full report and the hand-written failure analysis: [eval/eval_report.md](../eval/eval_report.md), [eval/failure_notes.md](../eval/failure_notes.md). Questions: `eval/eval_questions.jsonl` (21: 3 factual, 3 table, 1 limitations, 4 cross-paper, 5 visual, 2 synthesis, 2 unsupported, 1 injection).

| | Run 1 (first) | Run 2 (after the gate change) |
|---|---|---|
| correct (rule-based) | 15 / 21 | 15 / 21 |
| citation_ok | 15 / 21 | 16 / 21 |
| grounded (numbers + LLM judge) | 21 / 21 | 21 / 21 |

Run 2 followed a look at run 1's failures, so it is **not a blind result**. Retrieval ablation at k=8 (19 questions with expected evidence): dense 0.833, BM25 0.825, fusion 0.785, fusion + rerank **0.943** recall. Plain fusion scored below dense alone.

Real system weaknesses found: the evidence gate rejected broad answerable questions (fixed, see below); a cross-paper question lost its result tables (not fixed); whole-collection synthesis missed one paper's own technique (not fixed). Four of the six failed checks were my labels being too strict or ambiguous.

**The evidence gate was the biggest finding.** A reranker score cannot separate answerable from unanswerable questions: on a 23-question dev set the groups overlap (answerable 0.04 to 0.99, unanswerable up to 0.81). The gate is now only an off-topic filter (threshold 0.0185) and the model's own "no supporting claims" answer decides the rest. On the dev set that gave 13 of 13 answered and 10 of 10 unanswerable abstained; ten is a small sample.

**Checks on the checker.** The groundedness judge (a different model from the answerer) rejected a claim with wrong numbers and a claim with an invented fact, so it is not simply agreeing.

**Repeatability.** The first repeat run did not diff empty: the hosted reranker orders near-tied passages differently between calls, which changed 4 of 21 rows (two answers reworded; statuses and scores unchanged). Model replies and rerank results are now both replayed from disk caches keyed by the exact request, so a repeat run is identical by replay. That shows the pipeline around the services is stable, not that the services are deterministic.

**Not done.** No human has reviewed the answers or the labels. The question set was written after the system existed. Two visual facts (q12, q14) were checked only against images.

## Module 3: application

Run: `make serve` (API on port 8000) and `npm --prefix frontend run dev` (UI on port 5173). Code: `backend/app/api/`, `backend/app/db.py`, `backend/app/security.py`, `backend/app/ingestion.py`, `frontend/src/`.

**Checked by running against the live server** (scratch scripts, not a committed test suite; real tests are Module 4):
- Roles and access: 29 of 29 checks. Covers 401 without or with a bad token, 403 for a reader on admin routes, identical failure for wrong password and unknown login, 422 that names the field without echoing input, path traversal and unpublished crops returning 404, stale publish pointer returning 409, invalid uploads returning 422.
- Lifecycle: 23 of 23 checks. Upload returns 202 and reaches READY in the background; an unpublished paper is invisible; publish makes it visible with the right cited value; a staged v2 does not change what readers see; publishing v2 then rolling back to v1 changes the cited value each time; two simultaneous publishes give exactly one 200 and one 409; a blank PDF ends FAILED and publishing it is refused; the published pointer is unchanged after a failed ingest; the database refuses UPDATE and DELETE on audit rows; the planted injection instruction in an uploaded PDF was ignored.
- Browser (reader and admin): sign in with the demo button, ask a question, open a citation page, Back, the error message with the API stopped, the Admin screen, the audit page and its Back, a reader typing the admin URL, a wide and a narrow width.

**Defects found by those runs and fixed:** database connections crossing worker threads (a 500 under concurrent publishes); the citation page showed only the first 600 characters, so the cited sentence could be missing; the Back button ignored in-app history; a stale answer stayed on screen under a new error; a blank PDF failed through an unplanned error instead of a clear one.

**Known limitations.**
- The comparison view shows `NOT REPORTED` only when no claim cites a paper. A claim that says "this paper does not discuss X" counts as a statement.
- No fixed comparison table by dimension (objective, method, data and so on); the comparison is a question answered per paper.
- The parser timeout in validation V-09 is not implemented; uploads are limited by size (25 MB), header and a 100-page cap instead.
- Source links on the Papers page are built from arXiv IDs and were not fetched.
- Uploading is checked in a browser only up to the form; the file-chooser upload was exercised through the API, not the UI.
- Vite embeds the demo passwords from `frontend/.env.local` into any build made with that file present. Build for production without it.
- The audit log keeps the rows from my test runs by design: they cannot be deleted.
- Accounts and the signing secret live in `.env`. The seeded accounts are only created if they do not exist, so changing a password in `.env` later does not update an existing account.

## Module 4: verification

**Tests** (`uv run pytest`, no network, about 4 seconds): **87 passed**, 45 in `tests/test_rules.py` and 42 in `tests/test_api.py`. Written once, after the application worked, and run once, as the master prompt asks.
- Rules: rank fusion (formula, tie order, one-search-only documents), the evidence gate at just below, at and just above the threshold, claim checking (unknown, empty and duplicate citations), answer text built only from claims, JSON retry then fallback model then exact abstention, partly supported answers, injection text staying inside its evidence block and an uncited "APPROVED" claim never reaching the answer, rerank failure falling back to fusion order, recall and reciprocal rank, correctness rules per question type, the judge's number check, password hashing and token expiry or tampering, caption and heading detection (including the cases that broke earlier), and table pairing.
- API (temporary database, indexer and answerer stubbed): 401 on 11 protected routes without a token; 403 for a reader on 6 admin routes; bad, expired and wrong-secret tokens; a disabled account; identical failure for wrong password and unknown login; 422 without echoed input; published-only search and logging; compare coverage and `NOT REPORTED`; source access (unpublished, traversal, wrong type, unknown paper); publish rules (stale pointer, not READY, unknown version, missing body, rollback); invalid uploads (not a PDF, bad header, 101 pages, empty title, bad year); uploads hidden until published and identical bytes reusing a version; the append-only audit triggers; startup refusing placeholder credentials; and a generic 500 with only a request ID.
- Concurrency: the publish compare-and-swap was tested at the database level with two threads (exactly one wins), and live through the running server earlier (one 200 and one 409).

**Output contract check** (`scripts/validate_outputs.py`): 30 of 30 checks pass. Catalogue columns and counts, question keys and minimums, result columns and allowed values, every abstention being the exact text, and the report's overall numbers matching the results file. **Deviation:** the brief's analysis says injection questions have no expected page; ours names the test fixture's page 1, because the fixture holds the true answer.

**Security pass.**
- No secret in anything that would be committed (checked against the real `.env` values and key-shaped patterns); `.env` and `.env.local` are ignored.
- No unsafe HTML in the frontend, and model output is never executed.
- One fragile pattern found and removed: an f-string SQL helper (`next_id`). Values were always bound parameters, so it was not exploitable.
- A production frontend build made without `.env.local` contains none of the real credentials.
- The reader account's password in `.env` is a short plain word. It is not leaked, but it is weak; seeded accounts are only created once, so changing `.env` later does not change an existing account.

**Not run, and the plain reason.**
- No latency test (95th percentile) and no load test.
- No automated browser tests. The UI was driven by hand once for each role.
- The planted-instruction test through a live model runs only inside the evaluation (q21) and the lifecycle script, not once per free-text field. Free-text fields: the question, the compare question, upload title, authors and source link. The question path is covered live and by unit test; the other fields are only stored and shown as text, and were not tested with an injection string.
- No Pinecone or OpenAI outage test beyond the unit-level fallbacks.
- No accessibility audit (keyboard use was tried only through the browser pane).
- A full clean rebuild (delete the index, re-parse, re-index, re-run everything) was not run in this session. Parsing, indexing, evaluation, tests, lint and the frontend build were each run on the current code.
- The simplicity review found 14 functions above the length guide (see above).

**Repeatability.** Two sources of difference between evaluation runs were found and fixed: the hosted reranker (now cached) and the order in which related evidence was fetched (now fixed to the requested order). **Result:** `make eval-repeat` now shows all four output files identical across two consecutive runs, with unchanged scores (15 of 21 correct, 16 of 21 citation, 21 of 21 grounded). This is identity by replay of cached reranker and model replies, not proof that those services are deterministic.

**Error handling (checked).**
- *Server.* Invalid input returns 422 naming the field and never echoing the value, including malformed JSON and wrong types. Unknown routes return 404 and wrong methods 405, as plain JSON. A failing model or index service returns 503 "search service unavailable"; a locked database returns 503 "busy, try again"; anything unexpected returns 500 with a request ID only (the stack trace and the request path go to the server log). Model failures are retried once, then a fallback model, then an exact abstention. A reranker failure falls back to fusion order and is flagged on the answer. A background ingest failure marks the version FAILED, writes the exception type (not its message) to the audit log, and never touches the published pointer. Startup refuses to run without the signing secret and both accounts, naming the missing variables and never printing values.
- *Browser.* Every request has a 90-second timeout with its own message. A server that is down shows "Cannot reach the server. Start the API (make serve) and try again." An expired or invalid session returns to sign-in with "Your session ended. Please sign in again." A crash while drawing a page shows a plain message and a button back to the start (an error boundary); load failures on the Papers, Admin and Audit pages and a failed figure image each show a message on the page. Actions that cannot succeed are disabled (Ask with no text, Compare with fewer than two papers).
- *Tested:* 5 new automated tests (locked database, malformed JSON, unknown route and wrong method, missing upload fields, failed background job). The session-expiry message and the server-down message were checked in the browser. **Not tested:** the 90-second timeout and the error boundary (no fault was injected into them), a full disk, and an uploaded PDF that crashes the parser in a way that is not an ordinary exception (a hang would not time out; see the parser timeout limit).

## Chat threads (added after Module 4)

The Ask page is now a chat: several questions in one thread. Code: `frontend/src/chat/` (store, thread, answer view, styles) and `frontend/src/pages/Ask.jsx`. The recent-chats sidebar was built by a separate session (`Sidebar.jsx`, `chats.js`, `App.jsx`) and reads the store described below; the two sessions agreed on file ownership and a small store contract by message.

- **What it does.** Questions and answers stack in order; Enter sends and Shift+Enter adds a line; the newest answer scrolls into view; a second question cannot be sent while one is pending; the first question moves the address to `#/chat/<id>`; a thread survives a page reload; a citation from any earlier answer opens its source; a failed question shows its error in the thread with Try again; the empty chat offers three example questions.
- **Checked in a browser** (as the admin account): two questions in one thread, reload keeping both, a citation from the first answer opening the right source with the second present, Back returning to the thread, the button disabled while pending, the server stopped mid-thread (error under its own question, earlier answers untouched, Try again succeeding after restart), and the sidebar listing the chat.
- **Limits.**
  - **Each question stands alone.** The assistant does not use earlier questions in the same chat as context, so a follow-up like "and what about its memory?" will not work. The page says so under the input. Using history would mean rewriting the question before search; it was not built.
  - **History lives in this browser only** (localStorage, one list per signed-in account). It is not shared between devices, and cited text is stored locally, so anyone using the same browser profile and account can read it. Up to 50 chats; if storage is full the oldest are dropped.
  - A question whose page was closed before the answer arrived is shown as interrupted, but only after a 2-minute grace period (longer than the 90-second request timeout). Before that it shows as still pending, which is also how it looks in a second tab or after a hot reload. A bug found by the sidebar session (false "interrupted" messages while a question was still running) was fixed this way.
  - **No automated tests for the store or the thread** (the frontend has no test runner yet); the checks above were by hand. The backend is unchanged and its 87 tests still pass.
  - Two questions cannot run at once in one chat, by design.

## Advanced constructs register

| File | Concept | Reason |
|---|---|---|
| `backend/app/db.py` | SQLite triggers that abort UPDATE and DELETE on `audit_events` | The audit log must be append-only and enforced by the database. A code convention could be broken by any future route or manual SQL |
| `backend/app/ingest/layout.py` | `_best_pairing` is recursive | Pairing table captions with detected tables needs the cheapest pairing on a page; pairing one caption at a time let a caption take a neighbour's table. A page has only a few captions |
| `layout.py`, `retrieval.py`, `scripts/run_eval.py` | `lambda` as a one-expression sort key | Plain sort keys, not lambda tables. Judged readable as they are |
| (framework idioms, no entry needed) | FastAPI `Depends` and a `yield` database dependency, Pydantic models, React hooks | Documented standard use of the chosen frameworks |

**Simplicity review (master prompt 3A, point 9), done at the end of Module 3.** Searched the backend and scripts for the advanced list: no custom decorators, closures that return functions, metaclasses, generators we wrote, threads or reflection. The `async` and `yield` hits are FastAPI's own lifespan, exception-handler and database-dependency patterns. **Deviation:** 14 functions are longer than the "about 25 lines" guide (longest: `answer()` 41 lines, `seed_papers` 40, `publish` 38, `process_version` 35). Most of that length is SQL, docstrings and sequential steps. They were not split, so a new reader will need a little longer on those. The team-readability test (could a new member explain each module after one read?) was not run with a real person.

## Module 2a: parser results

Command: `make ingest` (no API keys needed). Output goes to `backend/storage/` (ignored by git).

| Paper | Text chunks | Figures (crops) | Tables (with cell text) |
|---|---|---|---|
| paper-001 | 44 | 4 (4) | 7 (7) |
| paper-002 | 89 | 16 (16) | 23 (22) |
| paper-003 | 72 | 9 (9) | 11 (11) |
| paper-004 | 26 | 6 (6) | 3 (3) |
| paper-005 | 39 | 10 (10) | 5 (5) |
| paper-006 | 62 | 5 (5) | 5 (5) |
| paper-007 | 43 | 4 (4) | 10 (10) |
| paper-008 | 88 | 2 (2) | 23 (23) |

**How it was checked.**
- Caption counts were measured independently by a separate script before the parser existed, then compared. Where they differed the cause was found: IEEE `TABLE I` captions (paper-006), a caption merged into the block above (paper-008), and appendix tables my first regex missed (paper-001). All were fixed.
- Evidence IDs are unique within every paper and no record has an empty body (checked on the output).
- Figure crops viewed by eye: paper-003 Fig 1, paper-004 Fig 2, paper-005 Fig 4, paper-006 Fig 2, paper-008 Fig 1. All show the whole figure, its labels and the full caption.
- Table cell values spot-checked on paper-007 Table 1: `MeZO | 88.8 | 66.4 | ...` matches the PDF text layer.
- Section paths spot-checked on paper-003 (`3 Method > 3.1 ...`) and the IEEE paper-006 (`IV. EVALUATION > A. ...`).

**Defects found and fixed along the way** (kept so the same mistakes are not repeated): table extraction by the PDF library dropped decimal points (`88.8` became `888`), so rows are rebuilt from words; a character filter meant to reject maths also rejected every numbered heading; joining hyphenated line ends turned `first-order` into `firstorder`.

**Not checked.** Every crop and table was not viewed; five crops and two tables were. The one table without cell text (paper-002) was not investigated. No automated tests exist yet (written once in Module 4 by design).

## Known limitations of the parser

- A word hyphenated at a line end stays split (`optimi- zation`). Real hyphens are kept on purpose.
- Equations come out as fragments of symbols. They are indexed as text and add noise.
- Table columns are inferred from horizontal gaps (more than 5 points). Merged or multi-line cells can land in the wrong column. Values themselves stay whole.
- A figure or table record takes the section path in force at the end of its page, which can be the next section if a heading falls between the figure and the page end.
- A table the detector misses falls back to the text below its caption up to the next paragraph, which can include extra lines.
- Appendix-style headings of one letter without a dot (`A Related Work`) are level 1; IEEE-style `A.` is level 2. Other styles were not seen in these 8 papers.
- Scanned pages were not met in these 8 papers, so the scanned-page path (R-07) has no real example. A test fixture is needed in Module 4.
- Two tables stacked on one page can be merged by the table detector (paper-007 page 7: Tables 1 and 2 both carry both tables' rows).
- A table placed beside a figure can ride along in that figure's crop (paper-007 Figure 4 with Table 4).
- Table and crop assignment changed late in the build (whole-page caption matching, previous caption as a figure boundary). Table cell text was checked on about ten tables and crops on about eight; the rest were not viewed.
