from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict
from typing import List, Optional

from core.context import Context
from core.model import Block, Issue, Location, Severity, ParagraphBlock, TableBlock
from core.rule import FinalizeRule, Rule


def _table_hint(table_block: TableBlock) -> str:
    try:
        if table_block.table.rows and table_block.table.rows[0].cells:
            return (table_block.table.rows[0].cells[0].text or "").strip()[:50] or "(table)"
    except Exception:
        pass
    return "(table)"


@dataclass
class TableDimensionsRule(Rule):
    id: str = "T001"
    name: str = "Tables: dimensions"
    description: str = "Validate table rows/columns constraints."

    min_rows: Optional[int] = None
    min_cols: Optional[int] = None
    rows: Optional[int] = None
    cols: Optional[int] = None

    def applies_to(self, block: Block, ctx: Context) -> bool:
        return isinstance(block, TableBlock)

    def check(self, block: Block, ctx: Context) -> List[Issue]:
        if not isinstance(block, TableBlock):
            return []

        table = block.table
        actual_rows = len(table.rows)
        actual_cols = len(table.columns) if actual_rows > 0 else 0

        issues: List[Issue] = []
        loc = Location(block_index=block.index, kind="table", hint=_table_hint(block))

        if self.rows is not None and actual_rows != self.rows:
            issues.append(
                Issue(
                    code=self.id,
                    severity=Severity.ERROR,
                    message=f"{self.name}: rows must be {self.rows}, got {actual_rows}",
                    location=loc,
                    evidence={"expected_rows": self.rows, "actual_rows": actual_rows},
                )
            )

        if self.cols is not None and actual_cols != self.cols:
            issues.append(
                Issue(
                    code=self.id,
                    severity=Severity.ERROR,
                    message=f"{self.name}: columns must be {self.cols}, got {actual_cols}",
                    location=loc,
                    evidence={"expected_cols": self.cols, "actual_cols": actual_cols},
                )
            )

        if self.min_rows is not None and actual_rows < self.min_rows:
            issues.append(
                Issue(
                    code=self.id,
                    severity=Severity.ERROR,
                    message=f"{self.name}: rows must be >= {self.min_rows}, got {actual_rows}",
                    location=loc,
                    evidence={"min_rows": self.min_rows, "actual_rows": actual_rows},
                )
            )

        if self.min_cols is not None and actual_cols < self.min_cols:
            issues.append(
                Issue(
                    code=self.id,
                    severity=Severity.ERROR,
                    message=f"{self.name}: columns must be >= {self.min_cols}, got {actual_cols}",
                    location=loc,
                    evidence={"min_cols": self.min_cols, "actual_cols": actual_cols},
                )
            )

        return issues


@dataclass
class TableCaptionPairRule(FinalizeRule):
    id: str = "T010"
    name: str = "Tables: caption pairing"
    description: str = "Validate a caption exists near each table."

    caption_direction: str = "before"  # before | after
    max_distance: int = 1
    caption_contains: str = ""  # optional substring filter

    _table_blocks: List[TableBlock] = field(default_factory=list, init=False)
    _para_blocks: List[ParagraphBlock] = field(default_factory=list, init=False)

    def applies_to(self, block: Block, ctx: Context) -> bool:
        if isinstance(block, TableBlock):
            self._table_blocks.append(block)
            return False
        if isinstance(block, ParagraphBlock):
            self._para_blocks.append(block)
            return False
        return False

    def check(self, block: Block, ctx: Context) -> List[Issue]:
        return []

    def finalize(self, ctx: Context) -> List[Issue]:
        issues: List[Issue] = []

        para_by_index = {p.index: p for p in self._para_blocks}

        for tb in self._table_blocks:
            ok = False
            for delta in range(1, max(1, self.max_distance) + 1):
                cand_idx = tb.index - delta if self.caption_direction == "before" else tb.index + delta
                pb = para_by_index.get(cand_idx)
                if pb is None:
                    continue
                p = pb.paragraph
                text = (p.text or "").strip()
                if not text:
                    continue
                if not ctx.is_caption(p):
                    continue
                if self.caption_contains and self.caption_contains not in text:
                    continue
                ok = True
                break

            if not ok:
                issues.append(
                    Issue(
                        code=self.id,
                        severity=Severity.ERROR,
                        message=(
                            f"{self.name}: caption not found near table "
                            f"({self.caption_direction}, max_distance={self.max_distance})"
                        ),
                        location=Location(
                            block_index=tb.index,
                            kind="table",
                            hint=_table_hint(tb),
                        ),
                        evidence={
                            "caption_direction": self.caption_direction,
                            "max_distance": self.max_distance,
                            "caption_contains": self.caption_contains or None,
                        },
                    )
                )

        return issues


@dataclass
class KeyValueTableRule(Rule):
    id: str = "T003"
    name: str = "Tables: key-value layout"
    description: str = "Validate 2-column key/value tables and their required fields."

    caption_contains: str = ""
    caption_direction: str = "before"  # before | after
    max_distance: int = 1

    required_keys: List[str] = field(default_factory=list)
    optional_keys: List[str] = field(default_factory=list)
    allow_extra_keys: bool = False
    require_non_empty_values: bool = True
    value_patterns: Dict[str, str] = field(default_factory=dict)

    expected_cols: int = 2

    def applies_to(self, block: Block, ctx: Context) -> bool:
        return isinstance(block, TableBlock)

    def check(self, block: Block, ctx: Context) -> List[Issue]:
        if not isinstance(block, TableBlock):
            return []

        if self.caption_contains and not _has_matching_caption(
            ctx=ctx,
            table_block=block,
            caption_contains=self.caption_contains,
            direction=self.caption_direction,
            max_distance=self.max_distance,
        ):
            return []

        table = block.table
        loc = Location(block_index=block.index, kind="table", hint=_table_hint(block))
        issues: List[Issue] = []

        rows = table.rows
        if not rows:
            issues.append(
                Issue(
                    code=self.id,
                    severity=Severity.ERROR,
                    message=f"{self.name}: table is empty",
                    location=loc,
                )
            )
            return issues

        max_cols = 0
        for r in rows:
            max_cols = max(max_cols, len(r.cells))

        if self.expected_cols and max_cols != self.expected_cols:
            issues.append(
                Issue(
                    code=self.id,
                    severity=Severity.ERROR,
                    message=f"{self.name}: must have {self.expected_cols} columns, got {max_cols}",
                    location=loc,
                    evidence={"expected_cols": self.expected_cols, "actual_cols": max_cols},
                )
            )
            return issues

        seen: Dict[str, str] = {}
        duplicates: List[str] = []

        for r in rows:
            if len(r.cells) < 2:
                continue
            key = (r.cells[0].text or "").strip()
            value = (r.cells[1].text or "").strip()
            if not key:
                continue
            if key in seen:
                duplicates.append(key)
            seen[key] = value

        if duplicates:
            issues.append(
                Issue(
                    code=self.id,
                    severity=Severity.WARN,
                    message=f"{self.name}: duplicate keys: {', '.join(sorted(set(duplicates)))}",
                    location=loc,
                    evidence={"duplicate_keys": sorted(set(duplicates))},
                )
            )

        required = [k for k in self.required_keys if isinstance(k, str) and k.strip()]
        optional = [k for k in self.optional_keys if isinstance(k, str) and k.strip()]
        allowed = set(required) | set(optional)

        missing = [k for k in required if k not in seen]
        if missing:
            issues.append(
                Issue(
                    code=self.id,
                    severity=Severity.ERROR,
                    message=f"{self.name}: missing required keys: {', '.join(missing)}",
                    location=loc,
                    evidence={"missing_required_keys": missing},
                )
            )

        if not self.allow_extra_keys and allowed:
            extras = [k for k in seen.keys() if k not in allowed]
            if extras:
                issues.append(
                    Issue(
                        code=self.id,
                        severity=Severity.ERROR,
                        message=f"{self.name}: unexpected keys: {', '.join(extras)}",
                        location=loc,
                        evidence={"unexpected_keys": extras},
                    )
                )

        if self.require_non_empty_values:
            for k in required:
                if k in seen and not (seen[k] or "").strip():
                    issues.append(
                        Issue(
                            code=self.id,
                            severity=Severity.ERROR,
                            message=f"{self.name}: value must be non-empty: {k}",
                            location=loc,
                            evidence={"key": k},
                        )
                    )

        for k, pattern in (self.value_patterns or {}).items():
            if not isinstance(k, str) or not isinstance(pattern, str):
                continue
            if k not in seen:
                continue
            val = (seen[k] or "").strip()
            if not val:
                continue
            try:
                if re.search(pattern, val) is None:
                    issues.append(
                        Issue(
                            code=self.id,
                            severity=Severity.ERROR,
                            message=f"{self.name}: value does not match pattern: {k}",
                            location=loc,
                            evidence={"key": k, "pattern": pattern, "value": val},
                        )
                    )
            except re.error:
                issues.append(
                    Issue(
                        code=self.id,
                        severity=Severity.ERROR,
                        message=f"{self.name}: invalid regex pattern: {k}",
                        location=loc,
                        evidence={"key": k, "pattern": pattern},
                    )
                )

        return issues


def _has_matching_caption(
    ctx: Context,
    table_block: TableBlock,
    caption_contains: str,
    direction: str,
    max_distance: int,
) -> bool:
    para_by_index = {
        b.index: b
        for b in ctx.blocks
        if isinstance(b, ParagraphBlock)
    }
    for delta in range(1, max(1, max_distance) + 1):
        cand_idx = table_block.index - delta if direction == "before" else table_block.index + delta
        pb = para_by_index.get(cand_idx)
        if pb is None:
            continue
        p = pb.paragraph
        text = (p.text or "").strip()
        if not text:
            continue
        if not ctx.is_caption(p):
            continue
        if caption_contains not in text:
            continue
        return True
    return False

