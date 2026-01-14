from __future__ import annotations

from dataclasses import dataclass
from typing import List

from docx import Document
from docx.text.paragraph import Paragraph

from .model import Block


@dataclass
class Context:
    doc: Document
    config: dict
    blocks: List[Block]

    def is_heading(self, paragraph: Paragraph) -> bool:
        name = (getattr(paragraph.style, "name", "") or "").lower()
        return name.startswith("heading") or name.startswith("标题")

    def is_caption(self, paragraph: Paragraph) -> bool:
        name = (getattr(paragraph.style, "name", "") or "").lower()
        if name in {"caption", "题注", "图题", "表题"}:
            return True
        if "caption" in name:
            return True
        return False

