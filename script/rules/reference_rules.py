"""参考文献相关规则"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Optional, Set

from script.core.context import Context
from script.core.model import Block, Issue, Location, ParagraphBlock, Severity
from script.core.rule import FinalizeRule


@dataclass
class ReferencesHeadingRule(FinalizeRule):
    """REF001: 文档必须包含参考文献章节"""

    id: str
    description: str = ""
    required: bool = True
    heading_text: str = "参考文献"

    def applies_to(self, block: Block, ctx: Context) -> bool:
        return False

    def check(self, block: Block, ctx: Context) -> List[Issue]:
        return []

    def finalize(self, ctx: Context) -> List[Issue]:
        if not self.required:
            return []

        # 查找参考文献标题
        for b in ctx.blocks:
            if not isinstance(b, ParagraphBlock):
                continue

            p = b.paragraph
            if ctx.is_heading(p) and (p.text or "").strip() == self.heading_text:
                return []

        return [
            Issue(
                code=self.id,
                severity=Severity.ERROR,
                message=f"{self.description}: 未找到 '{self.heading_text}' 章节",
                location=Location(block_index=0, kind="document", hint="(document)"),
            )
        ]


@dataclass
class ReferencesCitationRule(FinalizeRule):
    """REF002: 参考文献必须在正文中通过上标引用"""

    id: str
    description: str = ""
    check_superscript_citation: bool = True
    reference_heading: str = "参考文献"
    citation_pattern: str = r"^\[\\d+(-\\d+)?(,\s*\\d+)*\]$"

    def applies_to(self, block: Block, ctx: Context) -> bool:
        return False

    def check(self, block: Block, ctx: Context) -> List[Issue]:
        return []

    def finalize(self, ctx: Context) -> List[Issue]:
        if not self.check_superscript_citation:
            return []

        # 找到参考文献章节的开始位置
        ref_start_index = -1
        for b in ctx.blocks:
            if not isinstance(b, ParagraphBlock):
                continue

            p = b.paragraph
            if ctx.is_heading(p) and (p.text or "").strip() == self.reference_heading:
                ref_start_index = b.index
                break

        if ref_start_index == -1:
            return []  # 没有参考文献章节，不检查

        # 收集参考文献列表
        references: Set[int] = set()
        for b in ctx.blocks:
            if b.index <= ref_start_index:
                continue
            if not isinstance(b, ParagraphBlock):
                continue

            p = b.paragraph
            text = (p.text or "").strip()
            if not text:
                continue

            # 遇到下一个标题时停止
            if ctx.is_heading(p):
                break

            # 提取参考文献编号
            ref_match = re.match(r"^\[(\d+)\]", text)
            if ref_match:
                ref_num = int(ref_match.group(1))
                references.add(ref_num)

        if not references:
            return []

        # 收集正文中的引用（简化版，完整实现需要检查 run 的上标属性）
        # TODO: 实现完整的上标引用检查
        # 这需要遍历每个 run 并检查其 font.superscript 属性

        citations: Set[int] = set()
        for b in ctx.blocks:
            if b.index >= ref_start_index:
                break
            if not isinstance(b, ParagraphBlock):
                continue

            p = b.paragraph
            text = (p.text or "").strip()

            # 简化版：查找 [数字] 格式的引用
            citation_matches = re.findall(r"\[(\d+)\]", text)
            for match in citation_matches:
                citations.add(int(match))

        # 检查未被引用的参考文献
        unreferenced = references - citations

        issues: List[Issue] = []
        if unreferenced:
            issues.append(
                Issue(
                    code=self.id,
                    severity=Severity.WARN,
                    message=f"{self.description}: 发现 {len(unreferenced)} 个未被引用的参考文献: {sorted(unreferenced)}",
                    location=Location(
                        block_index=ref_start_index, kind="document", hint="(references)"
                    ),
                    evidence={"unreferenced": sorted(unreferenced)},
                )
            )

        return issues


@dataclass
class CitationValidationRule(FinalizeRule):
    """REF002: 正文中引用的参考文献必须在参考文献列表中存在"""

    id: str
    description: str = ""
    reference_heading: str = "参考文献"
    citation_pattern: str = r"\[(\d+)\]"

    def applies_to(self, block: Block, ctx: Context) -> bool:
        return False

    def check(self, block: Block, ctx: Context) -> List[Issue]:
        return []

    def finalize(self, ctx: Context) -> List[Issue]:
        # 找到参考文献章节的开始位置
        ref_start_index = -1
        for b in ctx.blocks:
            if not isinstance(b, ParagraphBlock):
                continue

            p = b.paragraph
            if ctx.is_heading(p) and (p.text or "").strip() == self.reference_heading:
                ref_start_index = b.index
                break

        if ref_start_index == -1:
            return []  # 没有参考文献章节，不检查

        # 收集参考文献列表中的编号
        references: Set[int] = set()
        for b in ctx.blocks:
            if b.index <= ref_start_index:
                continue
            if not isinstance(b, ParagraphBlock):
                continue

            p = b.paragraph
            text = (p.text or "").strip()
            if not text:
                continue

            # 遇到下一个标题时停止
            if ctx.is_heading(p):
                break

            # 提取参考文献编号
            ref_match = re.match(r"^\[(\d+)\]", text)
            if ref_match:
                ref_num = int(ref_match.group(1))
                references.add(ref_num)

        if not references:
            return []

        # 收集正文中的引用
        citations: Dict[int, List[int]] = {}  # citation_num -> [block_indices]
        for b in ctx.blocks:
            if b.index >= ref_start_index:
                break
            if not isinstance(b, ParagraphBlock):
                continue

            p = b.paragraph
            text = (p.text or "").strip()

            # 查找所有引用
            citation_matches = re.finditer(self.citation_pattern, text)
            for match in citation_matches:
                cite_num = int(match.group(1))
                if cite_num not in citations:
                    citations[cite_num] = []
                citations[cite_num].append(b.index)

        # 检查正文引用是否都在参考文献列表中
        invalid_citations = {num: indices for num, indices in citations.items() if num not in references}

        issues: List[Issue] = []
        if invalid_citations:
            for cite_num, block_indices in sorted(invalid_citations.items()):
                # 只报告第一次出现的位置
                first_block_idx = block_indices[0]
                issues.append(
                    Issue(
                        code=self.id,
                        severity=Severity.ERROR,
                        message=f"{self.description}: 引用 [{cite_num}] 未在参考文献列表中找到",
                        location=Location(
                            block_index=first_block_idx,
                            kind="paragraph",
                            hint=f"(block {first_block_idx})",
                        ),
                        evidence={
                            "citation_number": cite_num,
                            "all_occurrences": block_indices,
                            "available_references": sorted(references),
                        },
                    )
                )

        return issues


@dataclass
class ReferencesHeadingLevelRule(FinalizeRule):
    """REF003: 参考文献必须是指定级别的标题"""

    id: str
    description: str = ""
    check_heading_level: bool = True
    reference_heading: str = "参考文献"
    required_level: int = 1
    level1_styles: List[str] = field(default_factory=lambda: ["Heading 1", "标题 1"])

    def applies_to(self, block: Block, ctx: Context) -> bool:
        return False

    def check(self, block: Block, ctx: Context) -> List[Issue]:
        return []

    def finalize(self, ctx: Context) -> List[Issue]:
        if not self.check_heading_level:
            return []

        # 查找参考文献标题
        for b in ctx.blocks:
            if not isinstance(b, ParagraphBlock):
                continue

            p = b.paragraph
            if not ctx.is_heading(p):
                continue

            text = (p.text or "").strip()
            if text != self.reference_heading:
                continue

            # 检查样式级别
            style_name = (getattr(p.style, "name", "") or "").strip()

            if self.required_level == 1:
                if style_name not in self.level1_styles:
                    return [
                        Issue(
                            code=self.id,
                            severity=Severity.ERROR,
                            message=f"{self.description}: '{self.reference_heading}' 应为一级标题，当前样式为 '{style_name}'",
                            location=Location(
                                block_index=b.index, kind="paragraph", hint=text[:50]
                            ),
                            evidence={"style_name": style_name, "required_styles": self.level1_styles},
                        )
                    ]

            # 如果找到且级别正确，返回空
            return []

        # 如果没有找到参考文献标题，不报错（由 REF001 处理）
        return []
