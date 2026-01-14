from __future__ import annotations

from typing import Iterator

from docx import Document
from docx.oxml.table import CT_Tbl
from docx.oxml.text.paragraph import CT_P
from docx.table import Table
from docx.text.paragraph import Paragraph

from .model import Block, ParagraphBlock, TableBlock


class Walker:
    def iter_blocks(self, doc: Document) -> Iterator[Block]:
        body = doc.element.body
        idx = 0
        for child in body.iterchildren():
            if isinstance(child, CT_P):
                yield ParagraphBlock(idx, Paragraph(child, doc))
                idx += 1
            elif isinstance(child, CT_Tbl):
                yield TableBlock(idx, Table(child, doc))
                idx += 1

