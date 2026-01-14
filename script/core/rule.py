from __future__ import annotations

from typing import List, Protocol, runtime_checkable

from .context import Context
from .model import Block, Issue


@runtime_checkable
class Rule(Protocol):
    id: str

    def applies_to(self, block: Block, ctx: Context) -> bool: ...

    def check(self, block: Block, ctx: Context) -> List[Issue]: ...


@runtime_checkable
class FinalizeRule(Rule, Protocol):
    def finalize(self, ctx: Context) -> List[Issue]: ...

