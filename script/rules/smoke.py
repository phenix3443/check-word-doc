from __future__ import annotations

from dataclasses import dataclass
from typing import List

from core.context import Context
from core.model import Block, Issue, Location, Severity
from core.rule import Rule


@dataclass
class SmokeRule(Rule):
    id: str = "SMOKE"

    def applies_to(self, block: Block, ctx: Context) -> bool:
        return block.index == 0

    def check(self, block: Block, ctx: Context) -> List[Issue]:
        return []

