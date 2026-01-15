"""文档结构相关规则：封面、目录、图目录、表目录等

规则设计理念：
- 每个规则类对应一类检查（如 PresenceRule 检查元素存在性）
- 通过配置参数控制具体行为
- 从配置文件中读取参数，动态创建规则实例
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Optional

from script.core.context import Context
from script.core.model import Block, Issue, Location, ParagraphBlock, Severity
from script.core.rule import FinalizeRule


@dataclass
class PresenceRule(FinalizeRule):
    """通用的存在性检查规则

    可用于检查封面、目录、参考文献等元素是否存在
    通过配置参数适配不同的检查需求
    """

    id: str
    description: str = ""
    required: bool = True
    # 匹配条件：标题文本
    title_text: Optional[str] = None
    # 匹配条件：样式前缀列表
    style_prefixes: List[str] = field(default_factory=list)
    # 匹配条件：关键词列表（用于封面等）
    keywords: List[str] = field(default_factory=list)
    # 检查范围：前 N 个段落（用于封面等）
    check_first_n_blocks: Optional[int] = None

    def applies_to(self, block: Block, ctx: Context) -> bool:
        return False

    def check(self, block: Block, ctx: Context) -> List[Issue]:
        return []

    def finalize(self, ctx: Context) -> List[Issue]:
        if not self.required:
            return []

        # 确定检查范围
        blocks_to_check = ctx.blocks
        if self.check_first_n_blocks:
            blocks_to_check = ctx.blocks[: min(self.check_first_n_blocks, len(ctx.blocks))]

        # 检查是否找到匹配的元素
        found = False

        for b in blocks_to_check:
            if not isinstance(b, ParagraphBlock):
                continue

            p = b.paragraph
            text = (p.text or "").strip()
            style_name = (getattr(p.style, "name", "") or "").strip()

            # 检查标题文本匹配
            if self.title_text and text == self.title_text:
                found = True
                break

            # 检查样式前缀匹配
            if self.style_prefixes:
                for prefix in self.style_prefixes:
                    if prefix and style_name.startswith(prefix):
                        found = True
                        break
                if found:
                    break

            # 检查关键词匹配（用于封面等）
            if self.keywords:
                keyword_count = sum(1 for kw in self.keywords if kw in text)
                if keyword_count >= 1:  # 至少匹配一个关键词
                    found = True
                    break

        if not found:
            return [
                Issue(
                    code=self.id,
                    severity=Severity.ERROR,
                    message=f"{self.description}",
                    location=Location(block_index=0, kind="document", hint="(document)"),
                )
            ]

        return []


@dataclass
class PageContinuityRule(FinalizeRule):
    """通用的页码连续性检查规则

    用于检查目录、插图目录、表目录等的页码连续性
    """

    id: str
    description: str = ""
    check_continuity: bool = True
    # 匹配条件：样式前缀列表
    style_prefixes: List[str] = field(default_factory=list)
    # 匹配条件：标题文本（用于确定开始位置）
    title_text: Optional[str] = None
    # 页码提取正则（默认提取行末数字）
    page_pattern: str = r"(\d+)\s*$"

    def applies_to(self, block: Block, ctx: Context) -> bool:
        return False

    def check(self, block: Block, ctx: Context) -> List[Issue]:
        return []

    def finalize(self, ctx: Context) -> List[Issue]:
        if not self.check_continuity:
            return []

        # 收集条目及其页码
        entries = []
        in_section = False if self.title_text else True  # 如果指定了标题，需要先找到它

        for b in ctx.blocks:
            if not isinstance(b, ParagraphBlock):
                continue

            p = b.paragraph
            text = (p.text or "").strip()
            style_name = (getattr(p.style, "name", "") or "").strip()

            # 如果指定了标题文本，先找到对应章节
            if self.title_text and not in_section:
                if text == self.title_text:
                    in_section = True
                continue

            # 检查是否匹配样式
            if self.style_prefixes:
                matches = any(
                    style_name.startswith(prefix) for prefix in self.style_prefixes if prefix
                )
                if not matches:
                    continue
            else:
                # 如果没有样式前缀，只要在章节内就检查
                if not in_section:
                    continue

            # 提取页码
            match = re.search(self.page_pattern, text)
            if match:
                try:
                    page_num = int(match.group(1))
                    entries.append({"block_index": b.index, "text": text, "page_num": page_num})
                except (ValueError, IndexError):
                    pass

        if not entries:
            return []  # 没有条目，跳过检查

        # 检查页码连续性
        issues: List[Issue] = []
        for i in range(1, len(entries)):
            prev_page = entries[i - 1]["page_num"]
            curr_page = entries[i]["page_num"]

            # 允许相同或递增，但不允许回退
            if curr_page < prev_page:
                issues.append(
                    Issue(
                        code=self.id,
                        severity=Severity.ERROR,
                        message=f"{self.description}: 页码不连续，从 {prev_page} 回退到 {curr_page}",
                        location=Location(
                            block_index=entries[i]["block_index"],
                            kind="paragraph",
                            hint=entries[i]["text"][:50],
                        ),
                        evidence={
                            "prev_page": prev_page,
                            "curr_page": curr_page,
                        },
                    )
                )

        return issues


@dataclass
class PageAccuracyRule(FinalizeRule):
    """通用的页码准确性检查规则（占位）

    用于检查目录、插图目录、表目录中的页码是否与实际内容页码一致
    需要实现页码估算或解析逻辑
    """

    id: str
    description: str = ""
    check_page_accuracy: bool = True
    style_prefixes: List[str] = field(default_factory=list)
    heading_styles: List[str] = field(default_factory=list)
    caption_styles: List[str] = field(default_factory=list)
    title_text: Optional[str] = None

    def applies_to(self, block: Block, ctx: Context) -> bool:
        return False

    def check(self, block: Block, ctx: Context) -> List[Issue]:
        return []

    def finalize(self, ctx: Context) -> List[Issue]:
        # TODO: 实现页码准确性检查
        # 需要：1. 解析目录条目 2. 找到实际内容 3. 估算/获取页码 4. 比对
        # 由于页码估算复杂且依赖文档分页信息，这里先返回空列表
        return []


@dataclass
class HeadingNumberingRule(FinalizeRule):
    """标题编号连续性检查规则"""

    id: str
    description: str = ""
    check_heading_numbering: bool = True
    heading_styles: List[str] = field(default_factory=list)
    numbering_patterns: List[str] = field(default_factory=list)

    def applies_to(self, block: Block, ctx: Context) -> bool:
        return False

    def check(self, block: Block, ctx: Context) -> List[Issue]:
        return []

    def finalize(self, ctx: Context) -> List[Issue]:
        if not self.check_heading_numbering:
            return []

        # 收集所有标题及其编号
        headings = []

        for b in ctx.blocks:
            if not isinstance(b, ParagraphBlock):
                continue

            p = b.paragraph
            if not ctx.is_heading(p):
                continue

            style_name = (getattr(p.style, "name", "") or "").strip()
            text = (p.text or "").strip()

            # 确定标题级别
            level = self._get_heading_level(style_name)
            if level is None:
                continue

            # 提取编号
            numbering = self._extract_numbering(text, level)

            headings.append(
                {
                    "block_index": b.index,
                    "text": text,
                    "level": level,
                    "numbering": numbering,
                    "style": style_name,
                }
            )

        if not headings:
            return []

        # 检查编号连续性
        issues: List[Issue] = []
        level_counters = {}  # 每个级别的当前计数

        for heading in headings:
            level = heading["level"]
            numbering = heading["numbering"]

            if numbering is None:
                # 标题没有编号（如前言、附录等），跳过
                continue

            # 解析编号
            nums = self._parse_numbering(numbering)
            if not nums:
                continue

            # 检查当前级别的编号
            expected = level_counters.get(level, 0) + 1
            actual = nums[-1] if nums else 0

            if actual != expected:
                if actual > expected:
                    # 编号跳跃
                    issues.append(
                        Issue(
                            code=self.id,
                            severity=Severity.ERROR,
                            message=f"{self.description}: 第{level}级标题编号不连续，期望 {expected}，实际 {actual}",
                            location=Location(
                                block_index=heading["block_index"],
                                kind="paragraph",
                                hint=heading["text"][:50],
                            ),
                            evidence={
                                "expected": expected,
                                "actual": actual,
                                "level": level,
                            },
                        )
                    )

            # 更新计数器
            level_counters[level] = actual

            # 重置下级标题计数器
            for sub_level in range(level + 1, 7):
                if sub_level in level_counters:
                    del level_counters[sub_level]

        return issues

    def _get_heading_level(self, style_name: str) -> Optional[int]:
        """从样式名称提取标题级别"""
        match = re.search(r"(\d+)", style_name)
        if match:
            return int(match.group(1))
        return None

    def _extract_numbering(self, text: str, level: int) -> Optional[str]:
        """从标题文本中提取编号"""
        if level <= 0 or level > len(self.numbering_patterns):
            return None

        pattern = self.numbering_patterns[level - 1]
        match = re.match(pattern, text)
        if match:
            return match.group(1)

        return None

    def _parse_numbering(self, numbering: str) -> List[int]:
        """解析编号字符串为数字列表，如 "1.2.3" -> [1, 2, 3]"""
        try:
            nums = [int(n) for n in numbering.rstrip(".").split(".") if n]
            return nums
        except ValueError:
            return []


@dataclass
class HeadingHierarchyRule(FinalizeRule):
    """标题编号层级一致性检查规则

    检查子标题的编号前缀是否与父标题一致
    例如：2.3 的子标题应该是 2.3.1，不能是 2.4.1
    """

    id: str
    description: str = ""
    check_hierarchy: bool = True
    heading_styles: List[str] = field(default_factory=list)
    numbering_patterns: List[str] = field(default_factory=list)

    def applies_to(self, block: Block, ctx: Context) -> bool:
        return False

    def check(self, block: Block, ctx: Context) -> List[Issue]:
        return []

    def finalize(self, ctx: Context) -> List[Issue]:
        if not self.check_hierarchy:
            return []

        # 收集所有标题及其编号
        headings = []

        for b in ctx.blocks:
            if not isinstance(b, ParagraphBlock):
                continue

            p = b.paragraph
            if not ctx.is_heading(p):
                continue

            style_name = (getattr(p.style, "name", "") or "").strip()
            text = (p.text or "").strip()

            # 确定标题级别
            level = self._get_heading_level(style_name)
            if level is None:
                continue

            # 提取编号
            numbering = self._extract_numbering(text, level)
            if numbering is None:
                continue

            # 解析编号
            nums = self._parse_numbering(numbering)
            if not nums:
                continue

            headings.append(
                {
                    "block_index": b.index,
                    "text": text,
                    "level": level,
                    "numbering": numbering,
                    "nums": nums,
                    "style": style_name,
                }
            )

        if not headings:
            return []

        # 检查编号层级一致性
        issues: List[Issue] = []
        parent_stack = []  # 栈：存储每一级的父标题编号

        for heading in headings:
            level = heading["level"]
            nums = heading["nums"]

            # 调整栈：移除级别 >= 当前级别的元素
            while parent_stack and parent_stack[-1]["level"] >= level:
                parent_stack.pop()

            # 如果当前标题有父级（即编号长度 > 1），检查前缀
            if len(nums) > 1 and parent_stack:
                # 找到直接父级（应该是栈顶的标题，且级别 = level - 1）
                expected_parent_level = level - 1
                parent = None

                # 从栈顶向下查找对应级别的父标题
                for p in reversed(parent_stack):
                    if p["level"] == expected_parent_level:
                        parent = p
                        break

                if parent:
                    parent_nums = parent["nums"]
                    # 检查前缀是否匹配
                    expected_prefix = parent_nums
                    actual_prefix = nums[: len(parent_nums)]

                    if actual_prefix != expected_prefix:
                        issues.append(
                            Issue(
                                code=self.id,
                                severity=Severity.ERROR,
                                message=f"{self.description}: 标题编号 '{heading['numbering']}' 的前缀应该是 '{'.'.join(map(str, expected_prefix))}'",
                                location=Location(
                                    block_index=heading["block_index"],
                                    kind="paragraph",
                                    hint=heading["text"][:50],
                                ),
                                evidence={
                                    "actual_numbering": heading["numbering"],
                                    "expected_prefix": ".".join(map(str, expected_prefix)),
                                    "actual_prefix": ".".join(map(str, actual_prefix)),
                                    "parent_numbering": parent["numbering"],
                                    "parent_text": parent["text"][:30],
                                },
                            )
                        )

            # 将当前标题加入栈
            parent_stack.append(heading)

        return issues

    def _get_heading_level(self, style_name: str) -> Optional[int]:
        """从样式名称提取标题级别"""
        match = re.search(r"(\d+)", style_name)
        if match:
            return int(match.group(1))
        return None

    def _extract_numbering(self, text: str, level: int) -> Optional[str]:
        """从标题文本中提取编号"""
        if level <= 0 or level > len(self.numbering_patterns):
            return None

        pattern = self.numbering_patterns[level - 1]
        match = re.match(pattern, text)
        if match:
            return match.group(1)

        return None

    def _parse_numbering(self, numbering: str) -> List[int]:
        """解析编号字符串为数字列表，如 "1.2.3" -> [1, 2, 3]"""
        try:
            nums = [int(n) for n in numbering.rstrip(".").split(".") if n]
            return nums
        except ValueError:
            return []
