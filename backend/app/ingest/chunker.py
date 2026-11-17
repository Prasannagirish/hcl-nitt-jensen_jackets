"""Turn one PDF into evidence records: text chunks, whole tables and figure crops.

Rules: a text chunk never crosses a page or a section heading, so its page number is exact.
A table is one record. A figure is one record with its caption, and its crop is saved as a PNG.
"""

import re
from dataclasses import dataclass, field
from pathlib import Path

import pymupdf

from app import schema
from app.ingest import layout, pdf_blocks
from app.ingest.pdf_blocks import Block
from app.schema import Evidence


@dataclass
class SectionState:
    """Where we are in the paper while reading blocks in order."""

    titles: list[str] = field(default_factory=list)
    skipping: bool = False  # inside a section that is not indexed, such as References

    def path(self) -> str:
        """Section path such as '3 Method > 3.4 Analysis'."""
        return " > ".join(self.titles)


def update_section(state: SectionState, level: int, title: str, skip_titles: list[str]) -> None:
    """Apply a heading: replace the titles below its level and set the skip flag."""
    state.titles = state.titles[: level - 1] + [title]
    if level == 1:
        bare = re.sub(r"^[\dA-Z.]+\s+", "", title).lower()
        state.skipping = bare in skip_titles


def split_long(text: str, max_chars: int) -> list[str]:
    """Split a very long paragraph at sentence ends so no piece is much longer than max_chars."""
    pieces, current = [], ""
    for sentence in re.split(r"(?<=[.!?])\s+", text):
        if current and len(current) + len(sentence) > max_chars:
            pieces.append(current)
            current = ""
        current = f"{current} {sentence}".strip()
    return pieces + [current] if current else pieces


class DocumentBuilder:
    """Collects evidence records for one paper version."""

    def __init__(self, document_id: str, version_id: str, assets_dir: Path, cfg: dict):
        self.document_id = document_id
        self.version_id = version_id
        self.assets_dir = assets_dir
        self.cfg = cfg
        self.records: list[Evidence] = []
        self.section = SectionState()
        self._text_count: dict[int, int] = {}

    def add(self, page: int, element: str, kind: str, body: str, **extra) -> Evidence:
        """Create one record, store it and return it."""
        record = Evidence(
            evidence_id=schema.make_evidence_id(self.document_id, self.version_id, page, element),
            document_id=self.document_id,
            version_id=self.version_id,
            element_type=kind,
            pdf_page=page,
            section_path=self.section.path(),
            body=body,
            content_sha256=extra.pop("sha", None) or schema.sha256_of(body),
            **extra,
        )
        self.records.append(record)
        return record

    def add_text(self, page: int, body: str) -> None:
        """Store one text chunk, numbered within its page."""
        number = self._text_count.get(page, 0) + 1
        self._text_count[page] = number
        self.add(page, f"text-{number}", schema.TEXT, body)


def flush_pending(builder: DocumentBuilder, page_no: int, pending: list[str]) -> None:
    """Close the chunk being collected: store it and empty the list."""
    if pending:
        builder.add_text(page_no, "\n".join(pending))
        pending.clear()


def build_text_chunks(builder: DocumentBuilder, page_no: int, blocks: list[Block]) -> None:
    """Walk the remaining text blocks of a page, tracking headings and closing chunks."""
    limit = builder.cfg["max_chunk_chars"]
    pending: list[str] = []
    for block in blocks:
        heading = layout.parse_heading(block)
        if heading:
            flush_pending(builder, page_no, pending)
            update_section(builder.section, heading[0], heading[1], builder.cfg["skip_sections"])
            continue
        if builder.section.skipping or len(block.text) < 25:
            continue
        for piece in split_long(block.text, limit):
            if sum(len(p) for p in pending) + len(piece) > limit:
                flush_pending(builder, page_no, pending)
            pending.append(piece)
    flush_pending(builder, page_no, pending)


def save_crop(page: pymupdf.Page, crop: pymupdf.Rect, path: Path, dpi: int) -> bytes:
    """Render the crop to a PNG file and return its bytes."""
    path.parent.mkdir(parents=True, exist_ok=True)
    pixmap = page.get_pixmap(clip=crop & page.rect, dpi=dpi)
    pixmap.save(path)
    return path.read_bytes()


def add_figures_and_tables(builder: DocumentBuilder, page: pymupdf.Page, parts: dict) -> None:
    """Create records for the figures and tables found on this page."""
    for fig in parts["figures"]:
        extra = {"figure_number": fig.number}
        if fig.crop is not None:
            name = f"figure-{fig.number}-p{page.number + 1}.png"
            data = save_crop(page, fig.crop, builder.assets_dir / name, builder.cfg["figure_dpi"])
            extra.update(asset_id=name, sha=schema.sha256_of(data))
        builder.add(page.number + 1, f"figure-{fig.number}", schema.FIGURE, fig.caption, **extra)
    for tab in parts["tables"]:
        body = tab.caption
        if tab.rows:
            body = f"{tab.caption}\n{layout.rows_to_text(tab.rows)}"
        builder.add(
            page.number + 1, f"table-{tab.number}", schema.TABLE, body, table_number=tab.number
        )


def read_page_parts(page, blocks, ctx: layout.PageContext, cfg: dict) -> dict:
    """Find figures and tables on a page and return them with the blocks left over as text."""
    graphics = layout.find_graphics(page)
    figures, found_tables, covered = [], [], []
    regions = [pymupdf.Rect(t.bbox) for t in page.find_tables().tables]
    table_blocks = [b for b in blocks if (layout.parse_caption(b) or ("", ""))[0] == "table"]
    assigned = layout.assign_tables(table_blocks, regions, cfg["caption_gap_pt"])
    for block in blocks:
        caption = layout.parse_caption(block)
        if caption is None:
            continue
        kind, number = caption
        text, caption_rects = layout.caption_extent(block, blocks)
        if kind == "figure":
            crop = layout.figure_crop(block, blocks, graphics, ctx)
            for rect in caption_rects:
                crop = (crop | rect) if crop is not None else None
            figures.append(layout.FigureItem(number, text, crop, block))
            covered += [crop] if crop is not None else caption_rects
            continue
        chosen = assigned.get(table_blocks.index(block))
        match = layout.table_for_caption(page, block, blocks, ctx, chosen, regions)
        rows, region = match if match else (None, None)
        found_tables.append(layout.TableItem(number, text, rows, region, block))
        covered += caption_rects + ([region] if region else [])
    left = [b for b in blocks if not any(layout.inside(b, r) for r in covered)]
    return {"figures": figures, "tables": found_tables, "text_blocks": left}


def link_related(records: list[Evidence], max_related: int) -> None:
    """Point each figure and table at the text chunks that mention it by number."""
    texts = [r for r in records if r.element_type == schema.TEXT]
    for record in records:
        if record.element_type == schema.FIGURE:
            pattern = rf"\b(?:Figure|Fig\.)\s*{re.escape(record.figure_number)}\b"
        elif record.element_type == schema.TABLE:
            pattern = rf"\bTable\s*{re.escape(record.table_number)}\b"
        else:
            continue
        mentions = [t.evidence_id for t in texts if re.search(pattern, t.body, re.IGNORECASE)]
        record.related_ids = mentions[:max_related]


def parse_pdf(
    pdf_path: Path, document_id: str, assets_dir: Path, cfg: dict, version_id: str | None = None
) -> list[Evidence]:
    """Read one PDF and return its evidence records in page order."""
    version_id = version_id or cfg["version_id"]
    builder = DocumentBuilder(document_id, version_id, assets_dir / document_id / version_id, cfg)
    with pymupdf.open(pdf_path) as doc:
        pages = [pdf_blocks.read_page_blocks(page, i + 1) for i, page in enumerate(doc)]
        pages = pdf_blocks.drop_page_furniture(pages, doc[0].rect.height)
        width = doc[0].rect.width
        ctx = layout.PageContext(
            width,
            doc[0].rect.height,
            pdf_blocks.body_font_size(pages),
            pdf_blocks.is_two_column(pages, width),
        )
        for page, blocks in zip(doc, pages, strict=True):
            parts = read_page_parts(page, blocks, ctx, cfg)
            build_text_chunks(builder, page.number + 1, parts["text_blocks"])
            add_figures_and_tables(builder, page, parts)
    link_related(builder.records, cfg["max_related"])
    return builder.records
