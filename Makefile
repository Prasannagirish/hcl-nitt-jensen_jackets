.PHONY: install ingest lint index calibrate eval eval-repeat serve

install:
	uv sync --python 3.11

# Parse every paper in data/papers into evidence records (no API keys needed)
ingest:
	uv run python scripts/ingest_papers.py

lint:
	uv run ruff check backend scripts
	uv run ruff format --check backend scripts

# Index all papers (needs API keys and `make ingest` first); then the injection test fixture
index:
	uv run python scripts/index_papers.py
	uv run python scripts/index_fixture.py

# Choose the evidence-gate threshold from the dev set
calibrate:
	uv run python scripts/calibrate_gate.py

# Run the evaluation and write eval/eval_results.csv, eval/ablation.csv and eval/eval_report.md
eval:
	uv run python scripts/run_eval.py

# Run the evaluation twice and show any difference between the two sets of outputs
eval-repeat:
	uv run python scripts/run_eval.py > /dev/null
	mkdir -p eval/.run1 && cp eval/eval_results.csv eval/ablation.csv eval/judge_details.jsonl eval/eval_report.md eval/.run1/
	uv run python scripts/run_eval.py > /dev/null
	-for f in eval_results.csv ablation.csv judge_details.jsonl eval_report.md; do diff -q eval/.run1/$$f eval/$$f && echo "identical: $$f"; done
	rm -rf eval/.run1

# Start the API on http://127.0.0.1:8000 (needs .env filled in, see .env.example)
serve:
	uv run uvicorn app.main:app --host 127.0.0.1 --port 8000
