"""Read text blocks from PDF pages.

Each block keeps its page, position and font size, so later steps can find headings,
captions and page numbers. Rotated text (for example the arXiv side stamp) is skipped.
"""

import re
from collections import Counter
from dataclasses import dataclass

import pymupdf

CAPTION_RE = re.compile(r"^(Figure|Fig\.|Table)\s*([A-Z]?\d+|[IVXL]+)\s*[:.|]")
IEEE_TABLE_RE = re.compile(
    r"^TABLE\s+([IVXL]+|\d+)\b"
)  # IEEE style: "TABLE II", title on next line
FURNITURE_ZONE = 0.12  # top and bottom share of a page where headers and footers live
MIN_PAGES_FOR_HEADER = 3  # a header text must repeat on this many pages to be removed


@dataclass
class Block:
    """One paragraph-like block of text on one page."""

    page: int  # physical page, starting at 1
    rect: pymupdf.Rect
    text: str
    size: float  # font size of the first span
    bold: bool
    n_lines: int


def _join_lines(lines: list[dict]) -> str:
    """Join the lines of a block. A hyphen at a line end is kept and the next line follows it.

    Joining without the hyphen would turn real terms such as "first-order" into "firstorder",
    which search could never match. The cost is that a word broken by hyphenation stays split.
    """
    text = ""
    for line in lines:
        piece = "".join(span["text"] for span in line["spans"]).strip()
        joiner = "" if text.endswith("-") else " "
        text = f"{text}{joiner}{piece}".strip()
    return re.sub(r"\s+", " ", text)


def _is_horizontal(line: dict) -> bool:
    """True for normal left-to-right lines."""
    return line["dir"][0] > 0.9 and abs(line["dir"][1]) < 0.1


def _line_text(line: dict) -> str:
    """Text of one line."""
    return "".join(span["text"] for span in line["spans"]).strip()


def _split_at_captions(lines: list[dict]) -> list[list[dict]]:
    """Cut a block into groups so that every caption line starts its own group.

    The PDF library sometimes joins a caption to the equation or text above it.
    """
    groups: list[list[dict]] = [[]]
    for line in lines:
        text = _line_text(line)
        match = CAPTION_RE.match(text)
        # "Table 23." can end a sentence that wrapped onto a new line, so only "Figure 1:" splits
        starts_caption = (match and match.group(0)[-1] in ":|") or IEEE_TABLE_RE.match(text)
        if starts_caption and groups[-1]:
            groups.append([])
        groups[-1].append(line)
    return groups


def _block_from_lines(lines: list[dict], page_no: int) -> Block | None:
    """Turn a group of lines into a Block, or None when it has no usable text."""
    text = _join_lines(lines)
    spans = [span for line in lines for span in line["spans"] if span["text"].strip()]
    if not text or not spans:
        return None
    rect = pymupdf.Rect(lines[0]["bbox"])
    for line in lines[1:]:
        rect |= pymupdf.Rect(line["bbox"])
    first = spans[0]
    bold = bool(first["flags"] & 16) or "bold" in first["font"].lower()
    return Block(page_no, rect, text, first["size"], bold, len(lines))


def read_page_blocks(page: pymupdf.Page, page_no: int) -> list[Block]:
    """All text blocks of one page, in the order the PDF stores them."""
    blocks = []
    for raw in page.get_text("dict")["blocks"]:
        if raw["type"] != 0:
            continue
        lines = [line for line in raw["lines"] if _is_horizontal(line)]
        for group in _split_at_captions(lines):
            block = _block_from_lines(group, page_no)
            if block:
                blocks.append(block)
    return blocks


def body_font_size(pages: list[list[Block]]) -> float:
    """The font size used for most characters: the size of normal paragraph text."""
    counts: Counter = Counter()
    for blocks in pages:
        for block in blocks:
            counts[round(block.size, 1)] += len(block.text)
    if not counts:
        raise ValueError("no text could be read from the PDF")
    return counts.most_common(1)[0][0]


def _in_furniture_zone(block: Block, page_height: float) -> bool:
    """True when the block sits in the top or bottom margin band."""
    top_edge = page_height * FURNITURE_ZONE
    return block.rect.y1 < top_edge or block.rect.y0 > page_height - top_edge


def drop_page_furniture(pages: list[list[Block]], page_height: float) -> list[list[Block]]:
    """Remove running headers, running footers and bare page numbers."""
    seen_on: dict[str, set[int]] = {}
    for blocks in pages:
        for block in blocks:
            if _in_furniture_zone(block, page_height):
                key = re.sub(r"\d+", "#", block.text)
                seen_on.setdefault(key, set()).add(block.page)
    repeated = {key for key, found in seen_on.items() if len(found) >= MIN_PAGES_FOR_HEADER}
    kept = []
    for blocks in pages:
        kept.append([b for b in blocks if not _is_furniture(b, page_height, repeated)])
    return kept


def _is_furniture(block: Block, page_height: float, repeated: set[str]) -> bool:
    """True for a header or footer block."""
    if not _in_furniture_zone(block, page_height):
        return False
    return re.sub(r"\d+", "#", block.text) in repeated or block.text.isdigit()


def is_two_column(pages: list[list[Block]], page_width: float) -> bool:
    """True when most long paragraphs are narrower than 60% of the page (two-column layout)."""
    widths = [b.rect.width for blocks in pages for b in blocks if len(b.text) >= 120]
    if not widths:
        return False
    narrow = sum(1 for w in widths if w < 0.6 * page_width)
    return narrow > len(widths) / 2
