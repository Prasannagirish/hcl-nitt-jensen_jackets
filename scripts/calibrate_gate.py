"""Choose the evidence-gate threshold from a small dev set (validation V-06).

Usage: uv run python scripts/calibrate_gate.py
Reads eval/dev_calibration.jsonl (kept apart from the evaluation questions), retrieves evidence for
each question, and looks at the best rerank score. Writes config/calibration.json.
The rule for the threshold is in choose_threshold.
"""

import json

from app.answer import default_snapshot
from app.config import PROJECT_ROOT, load_config, load_env
from app.retrieval import retrieve

DEV_SET = PROJECT_ROOT / "eval" / "dev_calibration.jsonl"
OUT = PROJECT_ROOT / "config" / "calibration.json"


def best_score(question: str, snapshot: list[str], cfg: dict) -> float:
    """Highest rerank score among the evidence found for the question."""
    found = retrieve(question, snapshot, cfg)
    scores = [h.rerank_score for h in found.hits if h.rerank_score is not None]
    return max(scores) if scores else 0.0


def choose_threshold(positives: list[float], negatives: list[float]) -> tuple[float, str]:
    """Threshold and a plain statement of how well the two groups separate.

    If every negative scores below every positive, the threshold sits halfway between them. If the
    groups overlap, a score cannot tell answerable from unanswerable, so the gate becomes a coarse
    off-topic filter: half the lowest positive score, a safety margin below what was observed.
    The finer decision is then left to the model's own "no supporting claims" answer.
    """
    low_pos, high_neg = min(positives), max(negatives)
    if high_neg < low_pos:
        return round((low_pos + high_neg) / 2, 4), "separable"
    return round(low_pos / 2, 4), "overlap: the gate is only an off-topic filter"


def main() -> None:
    """Score every dev question, choose the threshold and write it."""
    load_env()
    cfg = load_config()
    snapshot = default_snapshot()
    rows = [json.loads(line) for line in DEV_SET.read_text(encoding="utf-8").splitlines()]
    scores = {"positive": [], "negative": []}
    for row in rows:
        score = best_score(row["question"], snapshot, cfg)
        scores[row["label"]].append(score)
        print(f"{row['qid']:8} {row['label']:8} best rerank score {score:.4f}")
    threshold, note = choose_threshold(scores["positive"], scores["negative"])
    result = {
        "min_evidence": threshold,
        "separation": note,
        "dev_positives": len(scores["positive"]),
        "dev_negatives": len(scores["negative"]),
        "lowest_positive": round(min(scores["positive"]), 4),
        "highest_negative": round(max(scores["negative"]), 4),
        "rerank_model": cfg["models"]["rerank"],
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
