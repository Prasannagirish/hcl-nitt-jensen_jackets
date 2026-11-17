"""Run the evaluation: answer every question, score it, and write the result files.

Usage: uv run python scripts/run_eval.py
Writes eval/eval_results.csv, eval/ablation.csv, eval/judge_details.jsonl and eval/eval_report.md.
Every number in the report is computed here from the rows, never typed by hand. Output files hold
no timestamps, so two runs on the same index and cache can be compared with diff.
"""

import csv
import json

from app import evaluation as ev
from app import index as idx
from app.answer import answer, default_snapshot
from app.config import PROJECT_ROOT, load_config, load_env
from app.judge import judge_answer
from app.retrieval import open_index

OUT = PROJECT_ROOT / "eval"
COLUMNS = [
    "qid",
    "actual_answer",
    "status",
    "cited_ids",
    "correct",
    "grounded",
    "citation_ok",
    "retrieved_ids",
    "recall_at_k",
    "rr",
]


def snapshot_for(question: dict, default: list[str]) -> list[str]:
    """Versions the question may use: its named targets, or all papers, plus any test fixture."""
    base = question["grading"]["targets"] or default
    return base + question["grading"]["extra_docvers"]


def score_question(question: dict, cfg: dict, default: list[str]) -> tuple[dict, dict]:
    """Answer one question and return its result row and its judge details."""
    result = answer(
        question["question"],
        snapshot_for(question, default),
        cfg,
        per_paper=question["grading"]["per_paper"],
    ).to_dict()
    verdict = judge_answer(result, cfg)
    entries = ev.expected_entries(question)
    recall, rr = ev.retrieval_scores(result["retrieved_ids"], entries, len(result["retrieved_ids"]))
    row = {
        "qid": question["qid"],
        "actual_answer": result["answer"].replace("\n", " / "),
        "status": result["status"],
        "cited_ids": ";".join(e["evidence_id"] for e in result["evidence"]),
        "correct": str(ev.is_correct(question, result)).lower(),
        "grounded": str(verdict["grounded"]).lower(),
        "citation_ok": str(ev.citation_ok(question, result)).lower(),
        "retrieved_ids": ";".join(result["retrieved_ids"]),
        "recall_at_k": "" if recall is None else f"{recall:.3f}",
        "rr": "" if rr is None else f"{rr:.3f}",
    }
    detail = {"qid": question["qid"], "degraded": result["degraded"], **verdict}
    return row, detail


def run_ablation(questions: list[dict], cfg: dict, default: list[str]) -> list[dict]:
    """Recall@k and MRR for dense only, BM25 only, fusion, and fusion plus rerank."""
    pc, index = open_index(cfg)
    scores: dict = {}
    for question in questions:
        entries = ev.expected_entries(question)
        if not entries:
            continue
        vector = idx.embed_texts([question["question"]], cfg["models"]["embedding"], 1)[0]
        ranks = ev.variant_rankings(
            pc, index, cfg, question["question"], vector, snapshot_for(question, default)
        )
        for variant, ids in ranks.items():
            for k in cfg["evaluation"]["k_values"]:
                recall, rr = ev.retrieval_scores(ids, entries, k)
                scores.setdefault((variant, k), []).append((recall, rr))
    rows = []
    for (variant, k), pairs in scores.items():
        rows.append(
            {
                "variant": variant,
                "k": k,
                "questions": len(pairs),
                "recall": round(sum(p[0] for p in pairs) / len(pairs), 3),
                "mrr": round(sum(p[1] for p in pairs) / len(pairs), 3),
            }
        )
    return rows


def mean(values: list[float]) -> str:
    """Mean to three decimals, or a dash when there is nothing to average."""
    return f"{sum(values) / len(values):.3f}" if values else "-"


def count_true(group: list[dict], column: str) -> int:
    """How many rows in the group have the column set to true."""
    return sum(1 for row in group if row[column] == "true")


def summarise(rows: list[dict], questions: dict) -> list[str]:
    """Markdown table rows: overall and per category."""
    groups = {"all": rows}
    for row in rows:
        groups.setdefault(questions[row["qid"]]["category"], []).append(row)
    lines = []
    for name, group in groups.items():
        recalls = [float(r["recall_at_k"]) for r in group if r["recall_at_k"]]
        rrs = [float(r["rr"]) for r in group if r["rr"]]
        lines.append(
            f"| {name} | {len(group)} | {count_true(group, 'correct')} | "
            f"{count_true(group, 'citation_ok')} | {count_true(group, 'grounded')} | "
            f"{mean(recalls)} | {mean(rrs)} |"
        )
    return lines


def failures(rows: list[dict], questions: dict) -> list[str]:
    """Markdown rows for every question that failed at least one check."""
    lines = []
    for row in rows:
        failed = [c for c in ("correct", "citation_ok", "grounded") if row[c] != "true"]
        if failed:
            text = row["actual_answer"][:140].replace("|", "/")
            lines.append(
                f"| {row['qid']} | {questions[row['qid']]['category']} | {', '.join(failed)} | "
                f"{row['status']} | {text} |"
            )
    return lines


def write_report(rows, ablation, questions: dict, cfg: dict) -> None:
    """Fill eval/report_template.md with the computed tables and write eval/eval_report.md."""
    counts: dict = {}
    for q in questions.values():
        counts[q["category"]] = counts.get(q["category"], 0) + 1
    notes_path = OUT / "failure_notes.md"
    notes = (
        notes_path.read_text(encoding="utf-8").strip()
        if notes_path.exists()
        else "Not written yet."
    )
    ablation_lines = [
        f"| {r['variant']} | {r['k']} | {r['recall']} | {r['mrr']} | {r['questions']} |"
        for r in sorted(ablation, key=lambda r: (r["k"], r["variant"]))
    ]
    what = [
        f"- {len(questions)} questions: " + ", ".join(f"{n} {c}" for c, n in counts.items()),
        f"- Answer model `{cfg['answer']['model']}`, reranker `{cfg['models']['rerank']}`, "
        f"embedding `{cfg['models']['embedding']}`",
        f"- Groundedness judge `{cfg['evaluation']['judge_model']}` (an LLM, not a human)",
        "- Papers: the 8-paper catalogue; the injection question also sees one test fixture",
    ]
    fill = {
        "WHAT_WAS_RUN": "\n".join(what),
        "RESULTS_TABLE": "\n".join(summarise(rows, questions)),
        "ABLATION_TABLE": "\n".join(ablation_lines),
        "FAILED_TABLE": "\n".join(failures(rows, questions) or ["| none | | | | |"]),
        "FAILURE_NOTES": notes,
    }
    text = (OUT / "report_template.md").read_text(encoding="utf-8")
    for key, value in fill.items():
        text = text.replace("{{" + key + "}}", value)
    (OUT / "eval_report.md").write_text(text, encoding="utf-8")


def main() -> None:
    """Run all questions and write all result files."""
    load_env()
    cfg = load_config()
    questions = ev.load_questions()
    default = default_snapshot()
    rows, details = [], []
    for question in questions:
        row, detail = score_question(question, cfg, default)
        rows.append(row)
        details.append(detail)
        print(
            f"{row['qid']}: status={row['status']} correct={row['correct']} "
            f"citation_ok={row['citation_ok']} grounded={row['grounded']}"
        )
    with open(OUT / "eval_results.csv", "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    (OUT / "judge_details.jsonl").write_text(
        "\n".join(json.dumps(d, ensure_ascii=False) for d in details) + "\n", encoding="utf-8"
    )
    ablation = run_ablation(questions, cfg, default)
    with open(OUT / "ablation.csv", "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["variant", "k", "questions", "recall", "mrr"])
        writer.writeheader()
        writer.writerows(sorted(ablation, key=lambda r: (r["k"], r["variant"])))
    write_report(rows, ablation, {q["qid"]: q for q in questions}, cfg)
    print("wrote eval/eval_results.csv, ablation.csv, judge_details.jsonl, eval_report.md")


if __name__ == "__main__":
    main()
