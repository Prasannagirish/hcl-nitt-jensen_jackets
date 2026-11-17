# Module 0: Intake (ResearchIQ)

Status: **proposed and probed, not built.** Written under `master_prompt_v2_engineering.md`, section 4. Design detail lives in [analysis/researchiq_analysis.md](analysis/researchiq_analysis.md), fixes in [analysis/decisions_validation.md](analysis/decisions_validation.md), build order in [analysis/implementation_brief.md](analysis/implementation_brief.md). Nothing is repeated here except what Module 0 adds.

## 1. Run parameters

| Parameter | Value | Note |
|---|---|---|
| STAGE | `BUILD` | Default. Smallest end-to-end solution first, then extend by priority |
| BRIEF | `ReseacrhIQ_AI_Usecase.docx` | Not in the repo. Read through the analysis, whose section references use `[S §x]` |
| DATA | none | The brief has no data pack. Teams choose their own papers |
| AUDIENCE | mixed | Technical and non-technical reviewers |
| TIME_BUDGET | 8 hours | Stated in the brief cover |
| MODE | `STANDARD` | 8 hours is above the 6-hour `FAST` line |

## 2. Environment probe (run on this machine)

| Item | Found | Decision |
|---|---|---|
| Git | Repo on `main`, **no commits** | Baseline commit with `.gitignore` (done in this step) |
| Python | 3.11.15, 3.14, 3.15.2 (default `python3` is 3.15.2) | Use **3.11** in a `uv` virtual environment. Newest releases risk missing wheels for PDF and vector libraries |
| `uv` | 0.11.16 | Use it for the virtual environment and installs |
| Ruff | not installed | Add as a dev dependency |
| Node | 23.11.0, npm 11.18.0 | Fine for the React frontend (Module 3) |
| Docker daemon | **not running** | No container build. Listed under "not run" in the final report. Compose file is optional (P2) |
| `make` | GNU Make 3.81 | Use plain targets only (`make eval`, `make serve`), nothing 4.x-specific |
| `OPENAI_API_KEY` | **not set** | **Blocks M0.** The user supplies it in a local `.env` file (never committed) |
| `PINECONE_API_KEY` | **not set** | **Blocks M0.** Same |
| Database | SQLite (a file under `backend/storage/`) | No server needed, so no credential question arises |

## 3. Traceability: how each MUST is verified

IDs, wording and "done when" are in analysis section A4. This adds the verification method.

| ID | Verified by | Module |
|---|---|---|
| R-01, R-02, R-03, R-22 | `scripts/validate_outputs.py` on `papers_catalogue.csv` (row count 8–10, columns, ≥5 visual, ≥3 experimental, year flags) | 4 |
| R-04, R-05, R-07 | Unit test: chunker keeps a table whole and a figure linked to its caption; a scanned or empty page is flagged, not a crash | 2, 4 |
| R-06 | README section, read by a reviewer | 5 |
| R-08, R-09 | Integration test: cited answer lists paper and page; unsupported question returns the exact abstention string | 4 |
| R-10, R-11, R-12 | Scenario tests from brief §6 (comparison cites every selected paper; synthesis touches all papers; suggestions labelled AI-generated) | 4 |
| R-13, R-14 | Two demo answers (diagram, chart) with page and figure; blank-crop test gives `VISUAL_UNAVAILABLE` | 4 |
| R-15 | Browser check of each role (master prompt 6A, item 9) | 4 |
| R-16 | Injection test per free-text path; secret scan; error-body test; non-PDF upload returns 422 | 4 |
| R-17, R-18 | `make eval` writes the result files; output contract check; second run diffs empty | 2, 4 |
| R-19, R-21 | Checklist in README; `CONTRIBUTORS`; git log | 5 |
| R-20 | Screenshots or recording, if permitted | 5 |

## 4. Module plan (master prompt section 10, adapted to this brief)

Each module ends with a short report and a **pause for review** before the next starts. No module is begun until the one before is accepted.

| Module | Scope | Done when |
|---|---|---|
| **0 Intake** | This document; git baseline; blockers listed | Topic and papers resolved (section 6). Keys still open (B-3), which only blocks embedding and indexing |
| **1 Design** | Already covered by the analysis and the design-review deck. Remaining: the evidence record schema (one module, validation V-03) and the config file (V-11) | A reviewer can see what will be built and why. Mostly met today |
| **2 Data and retrieval** | 2a: parse, chunk and index one PDF with page numbers and one figure crop. 2b: all papers indexed; `answer()` with hybrid search, RRF, per-paper rerank, gate and abstention. 2c: evaluation runner and metrics (`make eval`) | One command reproduces the index and the evaluation outputs |
| **3 Application** | FastAPI routes, roles and publish (the V-01 minimum cut), `/compare`, figure answers, source view, three-screen React UI | Question to cited answer works through the API and the UI. Checked by running it, no test suite yet |
| **4 Verification** | All tests written once and run once; output contract check; injection test; security pass; simplicity review; browser check | Section 8 of the master prompt complete |
| **5 Finalisation** | Clean-run verification, README, `.env.example`, catalogue, diagram, team list, secret scan | Checklist R-19 to R-21 ticked |
| **6 Design artefacts** | Already produced for the design review. Final deck is a later, separate step | n/a |

Priority inside every module: P0 before P1 before P2 (analysis B1). The V-01 minimum cut applies: two env-seeded accounts, one role dependency, `active_version_id` pointer, publish endpoint, audit insert; rollback is publishing an older READY version.

## 5. Assumptions register

Entries marked **new** were added in this module. The rest are carried from the analysis.

| # | Ambiguity | Options | Choice | Reason |
|---|---|---|---|---|
| A-01 | Paper count: "8–10" vs "at least 5–6" | 6 or 8 | 8 to 10 | Repeated in three places in the brief. Safer |
| A-02 | Injection test vs "no fabricated papers" | In catalogue or separate | Labelled fixture, outside the catalogue and the paper count | Satisfies both sentences |
| A-03 | Roles and versioning (beyond the brief) | None or ADMIN/USER | ADMIN/USER, minimum cut | User decision, scoped by V-01 |
| A-04 | USER on an unpublished source | 403 or 404 | 404 | Hides that the record exists. Brief is silent |
| A-05 | RRF tie | Dense rank, sparse rank | Lower dense rank wins | Deterministic |
| A-06 | Metric rounding | Any | 3 decimals, round once at output | Matches the examples in the analysis |
| A-07 | Abstention threshold | Invented number or calibrated | Calibrated on about 5 dev negatives, kept apart from the 15 eval questions | Validation V-06 |
| A-08 | Python version (**new**) | 3.11, 3.14, 3.15 | 3.11 | Wheel availability; the default 3.15.2 is too new to trust |
| A-09 | Style file location (**new**) | Prompt says `docs/deck_style.md` | Use `.idea/docs/prompts/deck_style.md` as is | The file exists only there. Copy it into `docs/` at Module 3 if needed |
| A-10 | Auth token type (**new**) | Cookie or bearer | Bearer token | No CSRF work (validation V-01) |
| A-11 | Upload endpoint (**new**) | Synchronous or background | Return 202, ingest in a background task | Validation V-05 |
| A-12 | Test timing (**new**) | Test-first per task or one pass | One pass in Module 4 | Master prompt section 8 overrides the generic test-first habit |
| A-13 | Topic (**new**) | `Final.zip` or `HCL.zip` | `Final.zip`: memory-efficient LLM fine-tuning | See section 6 |
| A-14 | Paper `year` (**new**) | Year on the PDF or arXiv submission year | arXiv submission year, 2026 for all 8 | The PDFs carry arXiv stamps dated Oct–Nov 2026 |
| A-15 | Catalogue flags (**new**) | Manual or computed | `has_visuals` = at least 3 figure captions found; `is_experimental` = reports its own benchmark results. The Workloads paper (`paper-004`) is a characterisation study, so it is marked false | Conservative reading. Recomputed by script in Module 4 |
| A-16 | `source_url` (**new**) | Fetched or derived | Derived from the arXiv identifier, not fetched | No network call was made. Check before submission |
| A-18 | Repeatable model output (**new**) | Temperature 0, or cache | Cache each model reply on disk, keyed by a hash of the exact request | Both 6.1 models reject temperature 0 ("only the default 1"), so the design's "temperature 0" is impossible. A second evaluation run replays cached answers; retrieval is re-run live. Changing the question, evidence or prompt changes the key, so the cache never hides a real change |
| A-19 | Answer text (**new**) | Model writes free prose, or code builds text from claims | Code builds the answer only from claims that cite retrieved evidence | No uncited sentence can reach the user |
| A-20 | Evidence gate role (**new**) | Score threshold decides answerable, or a coarse filter | Coarse off-topic filter at 0.0185; the model's own no-claims answer decides the rest | A reranker score measures relevance, not answerability. The two groups overlap on the dev set (see build_log.md) |
| A-21 | Compare coverage (**new**) | Fixed dimension table, or a question answered per paper | Question answered per paper, each selected paper shown as statements or `NOT REPORTED` | Smallest design that meets "cites every selected paper"; limits in build_log.md |
| A-22 | `evidence_manifest` table (**new**) | Keep in the database, or derive from files | Not built; source access is checked from the publish pointer and the file path | The V-01 minimum cut. No feature needed it |
| A-17 | Licence (**new**) | Guess or "unknown" | `unknown`, except `paper-005`, whose text states CC BY-NC | Brief says never guess. PDFs are not committed either way |

## 6. Topic and paper decision

The user supplied two archives. Both were extracted and measured (page count, text layer, figure and table captions, dates, shared benchmarks).

| | `Final.zip` | `HCL.zip` |
|---|---|---|
| Content | 8 papers, one theme: memory-efficient LLM fine-tuning and optimisation | 46 PDFs in three folders (Advanced Retrieval, Agentic AI, Multimodal LLM), 3 exact duplicates |
| Theme fit | All 8 on topic (the safety-alignment paper is the loosest fit) | Mixed even inside a folder. The retrieval folder holds fluid dynamics, firewall logs, Alzheimer's caregiving, gradient boosting. About 6 of 16 are real RAG papers |
| Dates | All Oct–Nov 2026 (inside the brief's window) | arXiv 2611 and 2610 IDs, plus one ICLR 2025 paper |
| Cross-paper comparison | ENGINE, StructZO and the Riemannian paper share SST-2, BoolQ, RTE, WiC, CB on OPT models with MeZO baselines | Different tasks and benchmarks, so few fair comparisons |
| Text layer | 8 of 8 pages fully extractable | Almost all |

**Decision: use `Final.zip`.** It meets the brief's 8–10 count exactly and gives the comparison, shared-benchmark and conflicting-claims questions (brief §6) real material. The catalogue is [data/papers_catalogue.csv](../data/papers_catalogue.csv); the PDFs sit in `data/papers/` and are ignored by git.

Checks against the brief's minimums, from the extracted PDFs: 8 papers (at the minimum); 7 with figure captions (needs 5); 7 experimental (needs 3); 0 scanned pages found.

## 7. Open items and blockers

| # | Item | Needed for | Status |
|---|---|---|---|
| B-1 | Topic | Module 2 | **Resolved**: memory-efficient LLM fine-tuning (`Final.zip`) |
| B-2 | Paper list | Module 2 | **Resolved**: 8 papers, `paper-001` to `paper-008` |
| B-3 | API keys in a local `.env` (OpenAI, Pinecone). Not pasted in chat | M0 smoke test, embedding, indexing | **Resolved** |
| B-4 | Pinecone Documents API, embedding and vision model IDs are unverified | M0 smoke test | **Resolved**: see build_log.md |
| B-5 | Whether this topic is one of the brief's six was not checked: the brief `.docx` is not in the repo | Brief compliance | **Open**: user to confirm |
| B-7 | Validation V-04: `$in` version filter | Module 2b | **Resolved**: works, and isolates versions (build_log.md) |
| B-6 | Exactly 8 papers leaves no margin if one PDF fails to parse. An optional ninth on the same theme is `2611.20565` (memory-efficient speculative decoding) from `HCL.zip` | Resilience | Optional, user's call |

## 8. Not done and not verified (Module 0)

- No API, model or Pinecone call made. Papers were taken from the user's archives, not downloaded.
- The brief itself was not re-read from the .docx; this record relies on the analysis files.
- Docker was not available, so no container work is planned in this build.
