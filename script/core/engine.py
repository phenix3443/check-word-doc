from __future__ import annotations

from typing import List

from docx import Document

from .context import Context
from .model import Issue
from .rule import FinalizeRule, Rule
from .walker import Walker


class DocxLint:
    def __init__(self, rules: List[Rule], config: dict):
        self.rules = rules
        self.config = config

    def run(self, docx_path: str) -> List[Issue]:
        doc = Document(docx_path)
        blocks = list(Walker().iter_blocks(doc))
        ctx = Context(doc=doc, config=self.config, blocks=blocks)

        issues: List[Issue] = []

        for block in blocks:
            for rule in self.rules:
                if rule.applies_to(block, ctx):
                    issues.extend(rule.check(block, ctx))

        for rule in self.rules:
            if isinstance(rule, FinalizeRule):
                issues.extend(rule.finalize(ctx))

        return issues

