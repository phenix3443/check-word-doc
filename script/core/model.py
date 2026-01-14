from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional, Union

from docx.table import Table
from docx.text.paragraph import Paragraph


class Severity(str, Enum):
    INFO = "info"
    WARN = "warn"
    ERROR = "error"


@dataclass(frozen=True)
class Location:
    block_index: int
    kind: str
    hint: str


@dataclass(frozen=True)
class Issue:
    code: str
    severity: Severity
    message: str
    location: Location
    evidence: Optional[dict[str, Any]] = None


@dataclass(frozen=True)
class ParagraphBlock:
    index: int
    paragraph: Paragraph


@dataclass(frozen=True)
class TableBlock:
    index: int
    table: Table


Block = Union[ParagraphBlock, TableBlock]

