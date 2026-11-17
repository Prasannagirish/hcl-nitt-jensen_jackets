"""Find structure on one page: headings, captions, figure regions and tables.

All positions are PDF points. A figure is the graphics band just above its caption;
a table counts only when a table caption sits next to it, so code listings and
algorithm boxes are not mistaken for tables.
"""

import re
from dataclasses import dataclass

import pymupdf

from app.ingest.pdf_blocks import CAPTION_RE, IEEE_TABLE_RE, Block

HEADING_RE = re.compile(r"^((?:\d+(?:\.\d+)*|[IVX]+|[A-Z](?:\.\d+)*)\.?)\s+([A-Z][^.]{2,90})$")
HEADING_CHARS_RE = re.compile(r"^[A-Za-z0-9 .&,:?\-–'’()/]+$")  # headings hold plain words only
KNOWN_HEADINGS = {
    "abstract",
    "introduction",
    "related work",
    "conclusion",
    "conclusions",
    "limitations",
    "references",
    "acknowledgements",
    "acknowledgments",
    "appendix",
}
PARAGRAPH_SIZE_TOLERANCE = 0.4  # points; figure labels are usually smaller than body text
MIN_PARAGRAPH_CHARS = 120
CELL_GAP_PT = 5  # a horizontal gap wider than this starts a new table cell
ROW_TOLERANCE_PT = 3.5  # words whose centres differ by less than this are on one row
MIN_TABLE_HEIGHT_PT = 20
MIN_TABLE_ROWS = 2  # fewer rows than this is not a table
ABOVE_PENALTY_PT = 6  # a table above its caption is treated as this much farther away
CAPTION_LINE_GAP_PT = 3  # a block this close under a caption is the rest of that caption
MAX_SECTION_NUMBER = 15  # larger leading numbers are table values such as '56 MNLI'
BAND_SLACK_PT = 3  # tolerance when comparing edges


@dataclass
class FigureItem:
    """A figure caption and, when found, the page region that holds the picture."""

    number: str
    caption: str
    crop: pymupdf.Rect | None
    caption_block: Block


@dataclass
class TableItem:
    """A table caption and, when found, the extracted cell text."""

    number: str
    caption: str
    rows: list[list[str]] | None
    region: pymupdf.Rect | None
    caption_block: Block


def parse_caption(block: Block) -> tuple[str, str] | None:
    """Return ("figure" or "table", number) when the block starts a caption."""
    ieee = IEEE_TABLE_RE.match(block.text)
    if ieee:
        return "table", ieee.group(1)
    match = CAPTION_RE.match(block.text)
    if not match:
        return None
    kind = "table" if match.group(1).lower() == "table" else "figure"
    return kind, match.group(2)


def caption_extent(block: Block, blocks: list[Block]) -> tuple[str, list[pymupdf.Rect]]:
    """Full caption text and the rectangles it covers.

    Two cases are joined to the first caption block: IEEE tables put "TABLE I" in one block and
    the title in the next, and a long caption can run on into a second block with the same
    font size and almost no gap (for example a line holding maths).
    """
    text, rects = block.text, [block.rect]
    start = blocks.index(block) + 1
    for following in blocks[start:]:
        gap = following.rect.y0 - rects[-1].y1
        is_title = re.fullmatch(r"TABLE\s+\w+", block.text) and len(rects) == 1 and 0 <= gap < 20
        same_style = abs(following.size - block.size) <= 0.3 and -1 <= gap <= CAPTION_LINE_GAP_PT
        other = parse_caption(following) or parse_heading(following)
        if other or not (is_title or same_style) or not _x_overlap(following.rect, block.rect):
            break
        text = f"{text} {following.text}"
        rects.append(following.rect)
    return text, rects


def parse_heading(block: Block) -> tuple[int, str] | None:
    """Return (level, title) when the block is a section heading."""
    if block.n_lines > 2 or len(block.text) > 100 or block.text.endswith((",", ".")):
        return None
    if not HEADING_CHARS_RE.match(block.text) or block.text[-1].isdigit():
        return None  # maths, symbols, or a running header ending in a page number
    if block.text.lower() in KNOWN_HEADINGS:
        return 1, block.text
    match = HEADING_RE.match(block.text)
    if not match:
        return None
    prefix = match.group(1)
    if prefix.isdigit() and int(prefix) > MAX_SECTION_NUMBER:
        return None
    if re.fullmatch(r"[A-Z]\.", prefix):  # IEEE style "A. Subsection" sits under "II. SECTION"
        return 2, block.text
    return prefix.rstrip(".").count(".") + 1, block.text


def is_paragraph(block: Block, body_size: float) -> bool:
    """True for ordinary body text: body font size and long enough not to be a figure label."""
    if parse_caption(block) or abs(block.size - body_size) > PARAGRAPH_SIZE_TOLERANCE:
        return False
    return len(block.text) >= MIN_PARAGRAPH_CHARS


def _x_overlap(a: pymupdf.Rect, b: pymupdf.Rect) -> bool:
    """True when two rectangles share some horizontal range."""
    return min(a.x1, b.x1) - max(a.x0, b.x0) > 0


def find_graphics(page: pymupdf.Page) -> list[pymupdf.Rect]:
    """Rectangles of images and drawing clusters, without page-sized backgrounds."""
    rects = [pymupdf.Rect(info["bbox"]) for info in page.get_image_info()]
    rects += [pymupdf.Rect(r) for r in page.cluster_drawings()]
    page_area = page.rect.width * page.rect.height
    return [r for r in rects if r.width > 8 and r.height > 8 and r.get_area() < 0.8 * page_area]


@dataclass
class PageContext:
    """Facts about the document that figure detection needs."""

    width: float
    height: float
    body_size: float
    two_column: bool


def _column_rect(caption: Block, ctx: PageContext) -> tuple[float, float]:
    """Left and right edge of the column a caption belongs to (the whole page if one column)."""
    middle = ctx.width / 2
    if not ctx.two_column or (caption.rect.x0 < middle - 10 and caption.rect.x1 > middle + 10):
        return 0.0, ctx.width
    if caption.rect.x1 <= middle + 10:
        return 0.0, middle
    return middle, ctx.width


def _band_top(caption: Block, blocks: list[Block], ctx: PageContext, left: float, right: float):
    """Bottom edge of the closest paragraph, heading or caption above, in the same column."""
    top = 0.0
    for block in blocks:
        in_column = block.rect.x1 > left and block.rect.x0 < right
        above = block.rect.y1 <= caption.rect.y0 + BAND_SLACK_PT
        # an earlier caption also ends the band, so two stacked figures are not cropped together
        is_text = is_paragraph(block, ctx.body_size) or parse_heading(block) is not None
        is_text = is_text or (parse_caption(block) is not None and block is not caption)
        if in_column and above and is_text:
            top = max(top, block.rect.y1)
    return top


def figure_crop(
    caption: Block, blocks: list[Block], graphics: list[pymupdf.Rect], ctx: PageContext
) -> pymupdf.Rect | None:
    """Region holding the figure and its caption, or None when nothing sits above the caption.

    The region is the column band between the closest paragraph above and the caption, cut down
    to the content inside it. Drawing clusters are only clipped to the band, because on busy
    pages the PDF library can return one rectangle covering several figures and tables.
    """
    left, right = _column_rect(caption, ctx)
    top = _band_top(caption, blocks, ctx, left, right)
    band = pymupdf.Rect(left, top, right, caption.rect.y0 + BAND_SLACK_PT)
    content = [g & band for g in graphics if g.intersects(band)]
    content += [b.rect for b in blocks if b is not caption and band.contains(b.rect)]
    if not content:
        return None
    box = pymupdf.Rect(content[0])
    for rect in content[1:]:
        box |= rect
    box |= caption.rect
    return box + (-4, -4, 4, 4)


def _unique_words(words: list) -> list:
    """Drop words printed twice at the same spot (a faux-bold trick some PDFs use)."""
    kept: list = []
    for word in words:
        twin = any(
            word[4] == k[4] and abs(word[0] - k[0]) < 1 and abs(word[1] - k[1]) < 1
            for k in kept[-5:]
        )
        if not twin:
            kept.append(word)
    return kept


def _split_cells(words: list) -> list[str]:
    """Split the words of one row into cells at wide horizontal gaps."""
    cells, current, last_x1 = [], [], None
    for word in sorted(words, key=lambda w: w[0]):
        if last_x1 is not None and word[0] - last_x1 > CELL_GAP_PT:
            cells.append(" ".join(current))
            current = []
        current.append(word[4])
        last_x1 = word[2]
    return cells + [" ".join(current)]


def rows_from_region(page: pymupdf.Page, region: pymupdf.Rect) -> list[list[str]]:
    """Rebuild table rows from the words inside a region.

    PyMuPDF's own table extraction splits numbers from their decimal points ("88.8" became
    "888"), so the cell text is rebuilt from the words, which keep each number whole.
    """
    words = _unique_words(page.get_text("words", clip=region))
    rows: list[list] = []
    row_y: list[float] = []
    for word in sorted(words, key=lambda w: (w[1] + w[3]) / 2):
        centre = (word[1] + word[3]) / 2
        if rows and abs(centre - row_y[-1]) <= ROW_TOLERANCE_PT:
            rows[-1].append(word)
        else:
            rows.append([word])
            row_y.append(centre)
    return [_split_cells(row) for row in rows]


def _gap_to_caption(region: pymupdf.Rect, caption: Block) -> float | None:
    """Vertical gap between a caption and a table, or None when they do not line up.

    Captions usually sit above their table, so a table below the caption counts as closer: a
    table above gets ABOVE_PENALTY_PT added to its gap.
    """
    if not _x_overlap(region, caption.rect):
        return None
    if region.y0 >= caption.rect.y1 - BAND_SLACK_PT:
        return max(region.y0 - caption.rect.y1, 0.0)
    if region.y1 <= caption.rect.y0 + BAND_SLACK_PT:
        return max(caption.rect.y0 - region.y1, 0.0) + ABOVE_PENALTY_PT
    return None


def _best_pairing(costs: list[list[float | None]], index: int, used: tuple, unmatched: float):
    """Cheapest way to give captions index.. their own table. Returns (total cost, pairs).

    A caption may stay without a table at the price `unmatched`. Plain recursion: a page holds
    only a few captions, so trying every pairing is fast.
    """
    if index == len(costs):
        return 0.0, []
    best_cost, best_pairs = _best_pairing(costs, index + 1, used, unmatched)
    best_cost += unmatched
    for column, cost in enumerate(costs[index]):
        if cost is None or column in used:
            continue
        rest_cost, rest_pairs = _best_pairing(costs, index + 1, used + (column,), unmatched)
        if cost + rest_cost < best_cost:
            best_cost, best_pairs = cost + rest_cost, [(index, column)] + rest_pairs
    return best_cost, best_pairs


def assign_tables(
    captions: list[Block], regions: list[pymupdf.Rect], max_gap: float
) -> dict[int, pymupdf.Rect]:
    """Pair table captions with detected tables so that the total gap on the page is smallest.

    Looking at the whole page matters: some papers put a caption above one table and below the
    next, and pairing one caption at a time lets a caption take a neighbour's table.
    """
    limit = max_gap + ABOVE_PENALTY_PT
    costs = []
    for caption in captions:
        row = [_gap_to_caption(region, caption) for region in regions]
        costs.append([gap if gap is not None and gap <= limit else None for gap in row])
    _total, pairs = _best_pairing(costs, 0, (), limit + 1)
    return {index: regions[column] for index, column in pairs}


def _reach_caption(region: pymupdf.Rect, caption: Block) -> pymupdf.Rect:
    """Stretch a detected table toward its caption so a header line outside the box is kept."""
    if region.y0 >= caption.rect.y1 - BAND_SLACK_PT:
        return pymupdf.Rect(region.x0, caption.rect.y1, region.x1, region.y1)
    return pymupdf.Rect(region.x0, region.y0, region.x1, caption.rect.y0)


def _fallback_region(caption: Block, blocks: list[Block], ctx: PageContext) -> pymupdf.Rect | None:
    """Region below a caption up to the next paragraph or heading (tables the detector missed)."""
    left, right = _column_rect(caption, ctx)
    bottom = ctx.height * 0.92
    for block in blocks:
        in_column = block.rect.x1 > left and block.rect.x0 < right
        stops = is_paragraph(block, ctx.body_size) or parse_heading(block) or parse_caption(block)
        if in_column and block.rect.y0 > caption.rect.y1 + 2 and stops:
            bottom = min(bottom, block.rect.y0)
    region = pymupdf.Rect(left, caption.rect.y1, right, bottom)
    return region if region.height >= MIN_TABLE_HEIGHT_PT else None


def _closest_region(caption: Block, regions: list[pymupdf.Rect]) -> pymupdf.Rect | None:
    """The detected table nearest to the caption, even if another caption already claimed it."""
    gaps = [(_gap_to_caption(r, caption), r) for r in regions]
    gaps = [(gap, region) for gap, region in gaps if gap is not None]
    return min(gaps, key=lambda g: g[0])[1] if gaps else None


def table_for_caption(
    page: pymupdf.Page,
    caption: Block,
    blocks: list[Block],
    ctx: PageContext,
    assigned: pymupdf.Rect | None,
    regions: list[pymupdf.Rect],
) -> tuple[list[list[str]], pymupdf.Rect] | None:
    """Rows and region of the table that belongs to a caption, or None when none is found.

    Order of attempts: the table assigned to this caption, then the text band below the caption,
    then the nearest detected table shared with another caption. The last case happens when the
    detector merged two stacked tables into one region.
    """
    region = (
        _reach_caption(assigned, caption) if assigned else _fallback_region(caption, blocks, ctx)
    )
    rows = rows_from_region(page, region) if region else []
    if len(rows) < MIN_TABLE_ROWS:
        region = _closest_region(caption, regions)
        rows = rows_from_region(page, region) if region else []
    return (rows, region) if len(rows) >= MIN_TABLE_ROWS else None


def rows_to_text(rows: list[list[str]]) -> str:
    """One line per row, cells separated by ' | '."""
    return "\n".join(" | ".join(row) for row in rows if any(row))


def inside(block: Block, region: pymupdf.Rect) -> bool:
    """True when the centre of the block lies inside the region."""
    centre = pymupdf.Point((block.rect.x0 + block.rect.x1) / 2, (block.rect.y0 + block.rect.y1) / 2)
    return region.contains(centre)
