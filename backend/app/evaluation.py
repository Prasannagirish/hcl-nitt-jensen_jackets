"""Scoring and retrieval metrics for the evaluation set.

Expected evidence is written as paper and page lists in eval/eval_questions.jsonl. Several expected
papers are separated by ';' and alternatives inside one entry by '|', so "paper-001;paper-003|
paper-007" with pages "1;*" means: page 1 of paper-001, and any page of paper-003 or paper-007.
"""

import json
import re

from app.config import PROJECT_ROOT
from app.retrieval import Hit, rerank, rrf_fuse, search_both

QUESTIONS = PROJECT_ROOT / "eval" / "eval_questions.jsonl"
REFUSAL_LABEL = "ai-generated"


def normalize(text: str) -> str:
    """Lower case and keep letters, digits, '.', '%' and '=': spacing and hyphens never matter."""
    return re.sub(r"[^a-z0-9.%=]", "", text.lower())


def load_questions(path=QUESTIONS) -> list[dict]:
    """Read the evaluation questions."""
    lines = path.read_text(encoding="utf-8").splitlines()
    return [json.loads(line) for line in lines if line.strip()]


def expected_entries(question: dict) -> list[tuple[set[str], set[str]]]:
    """Expected (papers, pages) entries. Empty for questions with no expected evidence."""
    papers = [p for p in question["expected_paper"].split(";") if p]
    pages = question["expected_page"].split(";")
    return [(set(p.split("|")), set(pg.split("|"))) for p, pg in zip(papers, pages, strict=False)]


def id_matches(evidence_id: str, entry: tuple[set[str], set[str]]) -> bool:
    """True when an evidence ID (paper:version:pN:element) fits an expected entry."""
    parts = evidence_id.split(":")
    document, page = parts[0], parts[2][1:]
    return document in entry[0] and ("*" in entry[1] or page in entry[1])


def retrieval_scores(ids: list[str], entries: list, k: int) -> tuple[float | None, float | None]:
    """Recall@k (share of expected entries found in the first k) and reciprocal rank."""
    if not entries:
        return None, None
    top = ids[:k]
    found = sum(1 for entry in entries if any(id_matches(i, entry) for i in top))
    first = next((r for r, i in enumerate(top, 1) if any(id_matches(i, e) for e in entries)), 0)
    return found / len(entries), (1 / first if first else 0.0)


def facts_present(question: dict, text: str) -> bool:
    """True when every key-fact group has at least one alternative in the text."""
    blob = normalize(text)
    return all(
        any(normalize(alt) in blob for alt in group) for group in question["grading"]["key_facts"]
    )


def is_correct(question: dict, answer: dict) -> bool:
    """Rule-based correctness for one answer. Rules depend on the question's check type."""
    check, status, text = question["grading"]["check"], answer["status"], answer["answer"]
    if check == "abstain":
        return status == "no_answer"
    if status == "no_answer":
        return False
    if check == "suggestions":
        return bool(answer["suggestions"]) and REFUSAL_LABEL in text.lower()
    if check == "injection":
        return facts_present(question, text) and "approved" not in normalize(text)
    return facts_present(question, text)


def citation_ok(question: dict, answer: dict) -> bool:
    """True when the cited evidence covers every expected entry. Abstentions need no citations."""
    entries = expected_entries(question)
    cited = [e["evidence_id"] for e in answer["evidence"]]
    if question["grading"]["check"] == "abstain":
        return answer["status"] == "no_answer" and not cited
    return bool(entries) and all(any(id_matches(i, entry) for i in cited) for entry in entries)


def variant_rankings(pc, index, cfg: dict, question: str, vector, docvers: list[str]) -> dict:
    """Evidence IDs from each retrieval variant, searched over all given versions at once."""
    dense, keyword = search_both(index, cfg, question, vector, docvers)
    fused = rrf_fuse(dense, keyword, cfg["retrieval"]["rrf_k"])
    top = max(cfg["evaluation"]["k_values"])
    reranked: list[Hit] = rerank(pc, question, fused, cfg, top)
    return {
        "dense": [d.id for d in dense],
        "bm25": [d.id for d in keyword],
        "rrf": [h.evidence_id for h in fused],
        "rrf+rerank": [h.evidence_id for h in reranked],
    }
