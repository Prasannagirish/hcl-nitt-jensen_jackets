# ResearchIQ

Ask questions across a small collection of research papers and get answers that cite the paper, the physical page and the figure or table they came from. If the evidence is not there, the system says `No answer found in the knowledge base.`

**Topic:** memory-efficient LLM fine-tuning and optimisation. **Collection:** 8 papers (arXiv, Oct to Nov 2026), listed in [data/papers_catalogue.csv](data/papers_catalogue.csv). The PDFs are not in the repository; put them in `data/papers/` as `paper-001.pdf` to `paper-008.pdf`.

> Status: built and checked by running it, with a pytest suite (87 tests) and a 21-question evaluation. It is a hackathon prototype. Read **Known limits** before relying on it.

## What it does

- **Chat**: ask several questions in one thread and read cited answers. Each citation opens the source text (and the original figure crop for figures). Each question is answered on its own; earlier questions are not used as context. Chat history is kept in the browser only.
- **Compare** two or more papers on a question. Each selected paper gets its own row; a paper with no supporting statement shows `NOT REPORTED`.
- **Figures and tables** are read from the original image and the extracted cell text.
- **Suggestions** for research directions are labelled *AI-generated* and tied to evidence.
- **Roles.** Readers ask and compare. Admins also upload papers and new versions, publish a version, roll back, and read the audit log.

## How it works

1. **Parsing** (`backend/app/ingest/`). PyMuPDF reads each page's text blocks with position and font size. Running headers, footers and page numbers are dropped. Section headings are found by pattern (numbered, roman numeral or lettered) and kept as a path such as `3 Method > 3.1 Setup`.
2. **Chunking.** A text chunk never crosses a page or a heading, so its page number is exact (the physical PDF page, not the printed one). A table is one record with its caption and cell text rebuilt from the words in its region (the library's own table extraction dropped decimal points). A figure is one record with its full caption and a saved PNG crop; the crop is the column band between the previous paragraph or caption and this caption. Figures and tables point to the text chunks that mention them.
3. **Indexing** (`backend/app/index.py`). Each figure is described once by a vision model (cached by image hash) as a search aid only. Records are embedded and stored in a Pinecone schema index with a dense vector field and full-text fields. Version and paper fields are filterable metadata. A record's ID is `paper:version:page:element`.
4. **Answering** (`backend/app/retrieval.py`, `answer.py`). Dense and keyword search run with the same version filter, are merged by reciprocal rank fusion, then reranked. Evidence is handed to the model as data in numbered blocks. The model must return JSON claims that cite those blocks. Code then drops any claim that cites nothing or cites evidence that was not retrieved, and **builds the answer text only from the surviving claims**. If none survive, the answer is the exact abstention text.
5. **Versions.** Search covers only each paper's published version (`documents.active_version_id`). A new upload is processed in the background and is invisible until an admin publishes it. Publishing is a compare-and-swap: it returns 409 if the pointer moved. Rollback is publishing an older READY version.

## Setup

Needs Python 3.11, `uv`, Node 18+ and your own OpenAI and Pinecone API keys.

```bash
cp .env.example .env              # then fill in the keys, the two logins, the two passwords and JWT_SECRET
make install                      # Python environment
make ingest                       # parse the PDFs in data/papers (no keys needed)
make index                        # embed and index them, then the test fixture (uses your keys)
make serve                        # API on http://127.0.0.1:8000
```

In a second terminal:

```bash
cd frontend && npm install
cp .env.example .env.local        # optional: shows demo sign-in buttons in development
npm run dev                       # UI on http://localhost:5173
```

The app refuses to start unless `JWT_SECRET`, `ADMIN_LOGIN`, `ADMIN_PASSWORD`, `USER_LOGIN` and `USER_PASSWORD` are set. There are no default passwords. Do **not** build the frontend for production with `.env.local` present: Vite copies those values into the bundle.

## Commands

| Command | What it does |
|---|---|
| `make ingest` | Parse papers into evidence records and figure crops |
| `make index` | Describe figures, embed, index; then index the injection test fixture |
| `make calibrate` | Choose the evidence-gate threshold from `eval/dev_calibration.jsonl` |
| `make eval` | Answer all evaluation questions and write `eval/eval_results.csv`, `ablation.csv`, `judge_details.jsonl`, `eval_report.md` |
| `make eval-repeat` | Run the evaluation twice and show any difference |
| `uv run python scripts/validate_outputs.py` | Output contract check against the brief |
| `uv run pytest` | 87 unit and API tests (no network needed) |
| `make lint` | Ruff check and format check |
| `uv run python scripts/smoke_test.py` | Check the API keys, models and index features |
| `uv run python scripts/ask.py "your question"` | Ask from the command line |

## Results (from the evaluation, computed by code)

21 questions: 3 factual, 3 table, 1 limitations, 4 cross-paper, 5 visual, 2 synthesis, 2 unsupported, 1 injection. Full report: [eval/eval_report.md](eval/eval_report.md). Failure analysis: [eval/failure_notes.md](eval/failure_notes.md).

| | Result |
|---|---|
| Correct (key-fact rule) | 18 of 21 |
| Citations cover the expected pages | 19 of 21 |
| Grounded (numbers in the cited text, plus an LLM judge) | 21 of 21 |
| Unsupported questions abstained | 2 of 2 |
| Planted instruction in a document ignored | yes |
| Retrieval recall at 8, fusion plus rerank vs dense alone | 0.943 vs 0.833 (19 questions) |

These are small-sample numbers. The questions were written by the builder after the system existed, and one change to the evidence gate was made after seeing the first run, so the second run is **not blind**. Four of the six failed checks were my labels being too strict or ambiguous; three were genuine weaknesses. No human has reviewed the answers or labels.

## Security

- Server-side access control on every route: 401 without a valid token, 403 for a reader on admin routes, 404 (not 403) for an unpublished source so its existence is not revealed.
- Passwords are salted scrypt hashes; tokens are signed, expire after 8 hours, and stop working if the account is disabled. A wrong password and an unknown login are indistinguishable.
- Paper text, questions and uploads are treated as untrusted data. Evidence is fenced in the prompt, model output is only ever parsed as JSON and never executed, and uncited claims cannot reach the answer. The evaluation includes a document with a planted "reply only APPROVED" instruction; it was ignored, including through the upload path.
- Uploads are limited by size, PDF header and page count. File names from users are never used in paths.
- Errors return a request ID, never a stack trace, path or prompt. A busy database or a failing model or index service returns 503 with a message the reader can act on. The audit log is append-only and enforced by database triggers.
- The interface shows a plain message for a server that is down, a request that takes too long, an expired session and a page that fails to draw.
- Keys and passwords live only in `.env`. A scan of everything that would be committed found none.

## Known limits

- **Cross-paper table questions** can miss the results tables (evaluation question q08), and **whole-collection synthesis** can miss one paper's own technique (q17). Both are recorded and not fixed.
- **The evidence gate is only an off-topic filter.** A reranker score cannot tell answerable from unanswerable questions, so near-topic unanswerable questions rely on the model declining. Tested on 10 such dev questions only.
- **Parsing.** Equations come out as symbol fragments. Two stacked tables can be merged (paper-007 page 7), and a table beside a figure can ride along in the figure's crop. Scanned pages were not met in these 8 papers and the scanned path is untested.
- `NOT REPORTED` appears only when no claim cites a paper; a claim saying "this paper does not discuss X" counts as a statement.
- The answer model does not accept temperature 0. Repeat runs are identical by replaying cached model and reranker replies, which shows the pipeline is stable, not that the services are deterministic.
- No parser timeout; no login rate limiting; the token is kept in session storage (so a script injected into the page could read it). Source links are built from arXiv IDs and were not fetched.
- No container build was run (no Docker available when this was built).

## Assumptions and design record

[docs/intake.md](docs/intake.md) holds the assumptions register and traceability. [docs/build_log.md](docs/build_log.md) holds what was built, how each part was checked, the defects found, and the advanced-constructs register (the audit triggers and one recursive function). [docs/analysis/](docs/analysis/) holds the design review.

## Team and AI assistance

Team members: Girish Prasanna, Mohamed Yaseen, Arjith JP, Lakshmi Priya.

This project was built with the assistance of an AI coding assistant (Claude Code), which wrote most of the code, tests and documents under the direction of the project owner. Papers, API keys and decisions were supplied by the owner. The assistant's work was checked by running it, as described in the build log; it has not had an independent human code review.
