"""Output contract check: every generated deliverable against the brief's rules.

Usage: uv run python scripts/validate_outputs.py
Exits with an error if any check fails. Checks the paper catalogue, the evaluation questions, the
result files and that the report's numbers match the results file.
"""

import csv
import json
import re
import sys

from app.config import PROJECT_ROOT

CATALOGUE_COLUMNS = [
    "document_id", "title", "authors", "year", "source_site", "identifier", "source_url",
    "local_filename", "license_note", "has_visuals", "is_experimental",
]  # fmt: skip
QUESTION_KEYS = [
    "qid", "category", "question", "expected_answer", "expected_paper", "expected_page",
    "expected_figure_or_table", "grading",
]  # fmt: skip
RESULT_COLUMNS = [
    "qid", "actual_answer", "status", "cited_ids", "correct", "grounded", "citation_ok",
    "retrieved_ids", "recall_at_k", "rr",
]  # fmt: skip
STATUSES = {"supported", "partially_supported", "no_answer"}
EMPTY_OK = {"license_note": "unknown"}  # the word, never a blank cell
failures: list[str] = []


def check(ok: bool, message: str) -> None:
    """Record a failed check."""
    print(("PASS " if ok else "FAIL ") + message)
    if not ok:
        failures.append(message)


def read_csv(path) -> tuple[list[str], list[dict]]:
    """Header and rows of a CSV file."""
    with open(path, encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def check_catalogue() -> None:
    """Paper catalogue: count, columns, empty cells, visual and experimental minimums, years."""
    header, rows = read_csv(PROJECT_ROOT / "data" / "papers_catalogue.csv")
    check(header == CATALOGUE_COLUMNS, "catalogue columns and order")
    check(8 <= len(rows) <= 10, f"catalogue has 8 to 10 papers ({len(rows)})")
    check(all(r[c].strip() for r in rows for c in header), "no empty catalogue cell")
    check(sum(r["has_visuals"] == "true" for r in rows) >= 5, "at least 5 papers with visuals")
    check(sum(r["is_experimental"] == "true" for r in rows) >= 3, "at least 3 experimental papers")
    check(len({r["document_id"] for r in rows}) == len(rows), "document IDs are unique")
    check(all(1990 <= int(r["year"]) <= 2100 for r in rows), "years are plausible")
    check(
        all((PROJECT_ROOT / "data" / "papers" / r["local_filename"]).exists() for r in rows),
        "every listed PDF exists locally",
    )


def check_questions() -> list[dict]:
    """Evaluation questions: keys, minimums by category, expected evidence rules."""
    path = PROJECT_ROOT / "eval" / "eval_questions.jsonl"
    rows = [
        json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
    ]
    check(len(rows) >= 15, f"at least 15 evaluation questions ({len(rows)})")
    check(all(list(r) == QUESTION_KEYS for r in rows), "question keys and order")
    check(len({r["qid"] for r in rows}) == len(rows), "question IDs are unique")
    counts = {c: sum(r["category"] == c for r in rows) for c in {r["category"] for r in rows}}
    check(counts.get("visual", 0) >= 3, f"at least 3 visual questions ({counts.get('visual', 0)})")
    check(counts.get("unsupported", 0) >= 1, "at least 1 unsupported question")
    check(counts.get("injection", 0) >= 1, "at least 1 injection question")
    unsupported = [r for r in rows if r["category"] == "unsupported"]
    check(
        all(not r["expected_page"] for r in unsupported),
        "unsupported questions have no expected page",
    )
    answerable = [r for r in rows if r["category"] != "unsupported"]
    check(
        all(r["expected_paper"] and r["expected_page"] for r in answerable),
        "every other question names a paper and page",
    )
    return rows


def check_results(questions: list[dict]) -> list[dict]:
    """Result CSV: columns, one row per question, allowed values, number ranges."""
    header, rows = read_csv(PROJECT_ROOT / "eval" / "eval_results.csv")
    check(header == RESULT_COLUMNS, "result columns and order")
    check(
        [r["qid"] for r in rows] == [q["qid"] for q in questions],
        "one result row per question, in order",
    )
    check(all(r["status"] in STATUSES for r in rows), "status values are allowed")
    check(
        all(
            r[c] in {"true", "false"} for r in rows for c in ("correct", "grounded", "citation_ok")
        ),
        "flags are true or false",
    )
    check(
        all(r["recall_at_k"] == "" or 0 <= float(r["recall_at_k"]) <= 1 for r in rows),
        "recall is between 0 and 1",
    )
    check(all(r["rr"] == "" or 0 <= float(r["rr"]) <= 1 for r in rows), "rr is between 0 and 1")
    check(all(re.fullmatch(r"\d\.\d{3}|", r["rr"]) for r in rows), "rr has three decimals")
    refused = [r for r in rows if r["status"] == "no_answer"]
    check(
        all(r["actual_answer"] == "No answer found in the knowledge base." for r in refused),
        "every abstention is the exact text",
    )
    check(all(r["cited_ids"] == "" for r in refused), "an abstention cites nothing")
    return rows


def check_report(rows: list[dict]) -> None:
    """The report's 'all' row must equal numbers recomputed from the result file."""
    report = (PROJECT_ROOT / "eval" / "eval_report.md").read_text(encoding="utf-8")
    match = re.search(r"^\| all \| (\d+) \| (\d+) \| (\d+) \| (\d+) \|", report, re.M)
    check(match is not None, "report has an overall row")
    if match:
        expected = [len(rows)] + [
            sum(r[c] == "true" for r in rows) for c in ("correct", "citation_ok", "grounded")
        ]
        check(
            [int(g) for g in match.groups()] == expected,
            f"report numbers match the results file {expected}",
        )
    _, ablation = read_csv(PROJECT_ROOT / "eval" / "ablation.csv")
    check(len(ablation) == 8, "ablation has 4 variants at 2 cut-offs")
    check(
        "Failure analysis" in report and "Not written yet" not in report,
        "failure analysis is present",
    )
    check(report.count("### Failure") >= 2, "at least 2 failures written up")


def main() -> None:
    """Run every check and fail loudly."""
    check_catalogue()
    questions = check_questions()
    rows = check_results(questions)
    check_report(rows)
    if failures:
        print(f"\n{len(failures)} check(s) failed")
        sys.exit(1)
    print("\nall output checks passed")


if __name__ == "__main__":
    main()
