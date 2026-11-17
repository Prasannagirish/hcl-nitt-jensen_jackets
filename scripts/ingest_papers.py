"""Parse papers into evidence records (local step: no API keys needed).

Usage: uv run python scripts/ingest_papers.py [paper-001 paper-002 ...]
Writes backend/storage/evidence/<paper>.jsonl and figure crops under backend/storage/assets/.
Prints one coverage line per paper so a bad parse is visible, not hidden.
"""

import json
import sys

from app import schema
from app.config import PROJECT_ROOT, load_config
from app.ingest.chunker import parse_pdf

PAPERS_DIR = PROJECT_ROOT / "data" / "papers"
STORAGE = PROJECT_ROOT / "backend" / "storage"


def summarise(paper_id: str, records: list) -> str:
    """One line: counts per element type and how many figures and tables got real content."""
    figures = [r for r in records if r.element_type == schema.FIGURE]
    tables = [r for r in records if r.element_type == schema.TABLE]
    texts = [r for r in records if r.element_type == schema.TEXT]
    pages_with_text = len({r.pdf_page for r in texts})
    crops = sum(1 for r in figures if r.asset_id)
    rows = sum(1 for r in tables if "\n" in r.body)
    return (
        f"{paper_id}: text={len(texts)} on {pages_with_text} pages | "
        f"figures={len(figures)} crops={crops} | tables={len(tables)} with_rows={rows}"
    )


def main() -> None:
    """Parse the named papers, or every paper in data/papers."""
    cfg = load_config()["ingest"]
    names = sys.argv[1:] or sorted(p.stem for p in PAPERS_DIR.glob("paper-*.pdf"))
    out_dir = STORAGE / "evidence"
    out_dir.mkdir(parents=True, exist_ok=True)
    for name in names:
        records = parse_pdf(PAPERS_DIR / f"{name}.pdf", name, STORAGE / "assets", cfg)
        lines = (json.dumps(r.to_dict(), ensure_ascii=False) for r in records)
        (out_dir / f"{name}.jsonl").write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(summarise(name, records))


if __name__ == "__main__":
    main()
