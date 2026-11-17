# Validation of `decisions.md`

Checked against the challenge brief (`ReseacrhIQ_AI_Usecase.docx`) with the analyzer prompt. Companion to [researchiq_analysis.md](researchiq_analysis.md).

**What was and was not checked.** Reading plus three scripted checks (file existence, field-name comparison with `HLD.md`, arithmetic). **Not checked:** live Pinecone, OpenAI model access, SDK versions, latency, cost. `decisions.md` says the same about itself (§8, §12), and so do I. Those items are marked **UNVERIFIED** and need the M0 smoke test.

## Verdict

`decisions.md` is a sound design for the brief. It meets every MUST in the brief that it addresses, and its corrections (RRF vs rerank, one scoring type per Pinecone call, ColPali as optional) are right. It needs **14 fixes** (V-01 to V-14), 2 of them high. User-decided items are not re-argued; where a cost is flagged, a cheaper way to deliver the same decision is given.

| Verdict (27 decisions) | Count |
|---|---|
| CONFIRMED | 17 (includes D-20 and D-21, which are beyond the brief, see V-01) |
| CONFIRMED with a condition | 9 (D-06, D-08, D-09, D-11, D-14, D-15, D-16, D-24, D-26) |
| UNVERIFIED (needs a smoke test) | 1 (D-05) |

## Decision by decision

| ID | Verdict | Check against the brief / note |
|---|---|---|
| D-01 Pinecone | CONFIRMED | Any vector store is allowed [S §7]. Account access is untested |
| D-02 Adaptive chunking | CONFIRMED | Matches [S §5.1] structure, caption links, tables |
| D-03 OpenAI vision + ColPali roles | CONFIRMED | Roles are correctly kept separate |
| D-04 Hybrid, RRF then rerank | CONFIRMED | Good for the ablation the brief's metrics invite [S §9] |
| D-05 Documents API | **UNVERIFIED** | Cannot be checked offline. The decision already requires a startup probe and a legacy fallback. Keep both |
| D-06 Search modes + version filters | CONFIRMED with condition | See V-04 (simpler filter) |
| D-07 KB-only answering | CONFIRMED | [S §5.2, §13] |
| D-08 Gate in code | CONFIRMED with condition | See V-06 (calibration) |
| D-09 Per-paper comparison | CONFIRMED with condition | See V-07 (rerank must be per paper) and V-08 (synthesis) |
| D-10 Immutable per-version assets | CONFIRMED | Adds storage only |
| D-11 Paid vision API + fallback | CONFIRMED with condition | Model IDs (`gpt-6.1-terra`, `gpt-6.1-sol`) cannot be verified here. Keep them in config and probe at startup (V-12) |
| D-12 Embeddings pinned to schema | CONFIRMED | |
| D-13 ColPali optional | CONFIRMED | Correct pushback |
| D-14 Deterministic table maths | CONFIRMED with condition | The brief only asks to explain a table and relate it to the conclusions [S §5.4]. Limit arithmetic to 1–2 verified tables |
| D-15 FastAPI + UI | CONFIRMED with a condition | `decisions.md` says Streamlit; the team has since chosen React, which [S §7] allows. React costs more build time: keep to three plain screens and update D-15 |
| D-16 Synchronous ingest | CONFIRMED with condition | See V-05 |
| D-17 Eval first-class | CONFIRMED | [S §9, §12] |
| D-18 No GraphRAG etc. | CONFIRMED | Note: GraphRAG is a listed sub-area of topic 1 [S §2]; not required |
| D-19 Authorised published versions only | CONFIRMED | |
| D-20 Two roles | CONFIRMED, **beyond the brief** | See V-01 |
| D-21 Immutable versions | CONFIRMED, beyond the brief | V-01 |
| D-22 Lifecycle vs publication | CONFIRMED | Single source of truth for publication is right |
| D-23 SQLite pointer | CONFIRMED | |
| D-24 Snapshot + filter + re-validate | CONFIRMED with condition | V-04 |
| D-25 Audit | CONFIRMED | Add database-enforced append-only |
| D-26 Server-side auth | CONFIRMED with condition | V-01 (drop CSRF by using bearer tokens) and V-14 (no default passwords) |
| D-27 USER sees published only | CONFIRMED | Open policy choice left at "no" is right |

Arithmetic check: IDs D-01 to D-27 are continuous with no duplicates. The 15-question split (4+4+3+2+1+1) sums to 15 and meets the brief's minimums (≥3 visual, ≥1 unsupported, ≥1 injection).

## Findings and fixes

| # | Sev | Finding | Evidence | Fix |
|---|---|---|---|---|
| V-01 | **High** | **Scope vs 8 hours.** Roles, versions, publish, rollback, audit, signed handles, CSRF are not in the brief and compete with evaluation, visuals and comparison, which are scored. `decisions.md` §11 admits the brief does not require them | Brief §1–§14 has no auth or versioning | Keep both decisions; build the **minimum cut**: two env-seeded accounts, one role dependency on routes, `documents.active_version_id`, publish endpoint, audit insert, pair filter. **Rollback = publish of an older READY version** (same endpoint). Use **bearer tokens** instead of cookies, so no CSRF work. Defer signed citation handles: return the excerpt and crop inside the answer, which §12 already offers. Time estimate for the cut is a guess `[A]`: plan for about 1.5 to 2 of the 8 hours |
| V-02 | **High** | **Injection test vs "no fabricated papers".** The brief needs an adversarial document [S §9] yet forbids fabricated or unrelated papers [S §3]. `decisions.md` lists the injection question but not where the poisoned document lives | Brief §3 vs §9; `decisions.md` §9 | Keep a labelled fixture (`kind=test_fixture`, or a real paper with one added line) in `tests/`, ingested only for the test, never counted in the 8–10 or the catalogue |
| V-03 | Med | **Field names differ between the two design files.** `decisions.md` §3.1 uses `content_text`, `page_number`, `figure_id`, `chunk_id`, `paper_id`; `HLD.md` §7 uses `body`, `pdf_page`, `section_path`, `figure_number`, `evidence_id`, no `paper_id` | Scripted count: `content_text` 1 vs 0, `page_number` 1 vs 0, `body` 0 vs 1, `section_path` 0 vs 1, `paper_id` 5 vs 0 | Define the record once in code (one schema module) and generate docs from it. Pick `pdf_page`, `evidence_id`, `document_id` |
| V-04 | Med | **Version filter shape.** An `$or` of per-paper `$and` pairs is untested for the Documents API and grows with paper count | `decisions.md` §2.3 step 3 | Store a combined `docver` field (`paper-007:v2`) and filter with `$in`. Still re-check each returned pair in code |
| V-05 | Med | **D-16 vs lifecycle.** "Synchronous" ingestion conflicts with the INDEXING state a UI polls | D-16 vs §2.2 | Upload returns **202**; ingestion runs in a background task with bounded concurrency; the UI polls status |
| V-06 | Med | **Abstention threshold has no value and no data.** The brief needs only 1 unsupported question; tuning on the 15 eval questions would leak | D-08, §6 step 3 | Write about 5 dev negatives separate from the eval set; tune there; freeze before evaluating |
| V-07 | Med | **Rerank can break the per-paper quota.** One global pool of 25 [config `rerank_pool`] vs 60 candidates for two papers and 300 for ten (15 dense + 15 BM25 each) | Scripted check; `decisions.md` §3.3 steps 4 and 6 | Fuse and rerank **inside each paper**, then merge. Set pool per paper |
| V-08 | Med | **No retrieval design for whole-collection synthesis** [S §5.3] | `decisions.md` §7 covers named targets only | Run the per-paper path for every published paper with a small quota (for example 3 chunks each), then synthesise |
| V-09 | Med | **Brief §8 items missing.** No rule for sanitised errors (no stack traces or paths), for never executing model output, for malformed or unsupported uploads beyond MIME and size, or for escaping model text in the UI. Provider-outage behaviour (a judge question, [S §12]) is only "fail closed" | `decisions.md` §2.4, §6 | Add: generic error bodies with a request ID; JSON-only parsing, no `eval`; PDF magic-byte check and parser timeout → FAILED; render model text as plain text; a visible "service unavailable" state |
| V-10 | Low | **Deliverables not tracked:** team list, AI-assistance acknowledgement, demo recording or screenshots, design-decisions and limitations section, meaningful commit history [S §11, §11.1] | Not mentioned | Add to the M5 checklist |
| V-11 | Low | **Dangling references.** Cited files are absent from the supplied set: `researchiq_hld.mmd`, `IMPLEMENTATION_PLAN.md`, `CLAUDE.md`, `prompts/grounded_answer.txt`, `config/researchiq.yaml` (HLD.md and the SVG are present) | Scripted existence check | Create them, or drop the references. The config YAML in §5 is the spec for the last one |
| V-12 | Low | **Unverifiable vendor claims:** model IDs, SDK surface, reranker name, Documents API behaviour | Cannot be checked offline | Keep as config; probe at M0; record what was found in the README |
| V-13 | Low | **Topic and papers unset.** Eval labelling cannot start | `HLD.md` §12 item 1 | Decide in the first 30 minutes; label expected pages while reading |
| V-14 | Low | **Seed credentials.** No rule on initial accounts | D-26 | Seed from env vars; refuse to start if unset |

## What `decisions.md` gets right (keep)

Pinecone as the only search store with SQLite as a separate catalogue; one scoring type per search call; RRF and reranking as separate stages; ColPali as optional; gate in code; page, figure and version in every citation; "retained is not visible"; honest "not verified" list; no PDFs or internal brief in the public repo.

## Open item for the user

The topic. Everything else above can proceed with the stated defaults.
