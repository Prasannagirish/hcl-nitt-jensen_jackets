"""The one evidence record used everywhere: parser output, vector index fields, API answers.

Defined once so field names cannot drift between design files (validation V-03).
"""

import hashlib
from dataclasses import asdict, dataclass, field, fields

TEXT = "text"
TABLE = "table"
FIGURE = "figure"


@dataclass
class Evidence:
    """One citable piece of a paper: a text chunk, a whole table or a figure."""

    evidence_id: str
    document_id: str
    version_id: str
    element_type: str  # TEXT, TABLE or FIGURE
    pdf_page: int  # physical page of the PDF, starting at 1 (not the printed number)
    section_path: str
    body: str
    content_sha256: str
    figure_number: str = ""
    table_number: str = ""
    asset_id: str = ""  # file name of the saved figure crop, empty when there is none
    related_ids: list[str] = field(default_factory=list)  # text chunks that mention this item
    # AI-written description of a figure, used only to help search find it. It is not paper text,
    # so answers must show the paper's own caption and the crop, never this description.
    description: str = ""

    @property
    def docver(self) -> str:
        """Combined key used as the version filter in the vector index (validation V-04)."""
        return f"{self.document_id}:{self.version_id}"

    @classmethod
    def from_dict(cls, data: dict) -> "Evidence":
        """Rebuild a record from a dictionary, ignoring computed keys such as docver."""
        names = {f.name for f in fields(cls)}
        return cls(**{key: value for key, value in data.items() if key in names})

    def to_dict(self) -> dict:
        """Plain dictionary for JSON files and index metadata."""
        record = asdict(self)
        record["docver"] = self.docver
        return record


def make_evidence_id(document_id: str, version_id: str, pdf_page: int, element: str) -> str:
    """Stable ID: same paper, version, page and element always give the same ID."""
    return f"{document_id}:{version_id}:p{pdf_page}:{element}"


def sha256_of(data: str | bytes) -> str:
    """Hex SHA-256 of text or bytes."""
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(data).hexdigest()
