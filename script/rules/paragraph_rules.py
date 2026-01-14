"""段落格式相关规则

规则设计理念：
- 使用通用的规则类，通过配置参数控制具体行为
- 每个规则类对应一类检查（如 PunctuationRule 检查标点符号）
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Optional

from script.core.context import Context
from script.core.model import Block, Issue, Location, ParagraphBlock, Severity
from script.core.rule import FinalizeRule, Rule


@dataclass
class ConsecutiveEmptyRule(FinalizeRule):
    """PAR002/PAR007: 检查连续空段落/空行"""

    id: str
    description: str = ""
    max_consecutive: int = 0  # PAR002 用于检查空段落
    max_consecutive_empty: int = 1  # PAR007 用于检查空行
    check_consecutive_empty: bool = False  # 是否检查空行
    ignore_page_breaks: bool = True

    def applies_to(self, block: Block, ctx: Context) -> bool:
        return False

    def check(self, block: Block, ctx: Context) -> List[Issue]:
        return []

    def finalize(self, ctx: Context) -> List[Issue]:
        issues: List[Issue] = []
        consecutive_count = 0
        start_index = None

        for b in ctx.blocks:
            if not isinstance(b, ParagraphBlock):
                consecutive_count = 0
                start_index = None
                continue

            p = b.paragraph
            text = (p.text or "").strip()
            is_empty = not text

            # 如果检查空行模式，需要检查是否包含分页符
            if self.check_consecutive_empty and self.ignore_page_breaks and is_empty:
                # TODO: 检查是否包含分页符
                # 这需要访问段落的 XML 或格式信息
                pass

            if is_empty:
                if consecutive_count == 0:
                    start_index = b.index
                consecutive_count += 1
            else:
                # 检查是否超过限制
                threshold = (
                    self.max_consecutive_empty
                    if self.check_consecutive_empty
                    else self.max_consecutive
                )
                if consecutive_count > threshold:
                    issues.append(
                        Issue(
                            code=self.id,
                            severity=Severity.ERROR,
                            message=f"{self.description}: 发现 {consecutive_count} 个连续空段落",
                            location=Location(
                                block_index=start_index or 0,
                                kind="paragraph",
                                hint="(empty paragraph)",
                            ),
                            evidence={"count": consecutive_count},
                        )
                    )
                consecutive_count = 0
                start_index = None

        # 检查结尾的连续空段落
        threshold = (
            self.max_consecutive_empty
            if self.check_consecutive_empty
            else self.max_consecutive
        )
        if consecutive_count > threshold:
            issues.append(
                Issue(
                    code=self.id,
                    severity=Severity.ERROR,
                    message=f"{self.description}: 发现 {consecutive_count} 个连续空段落",
                    location=Location(
                        block_index=start_index or 0, kind="paragraph", hint="(empty paragraph)"
                    ),
                    evidence={"count": consecutive_count},
                )
            )

        return issues


@dataclass
class PunctuationRule(Rule):
    """PAR003: 段落末尾标点检查"""

    id: str
    description: str = ""
    check_punctuation: bool = True
    required_punctuation: List[str] = field(default_factory=list)
    check_styles: List[str] = field(default_factory=list)
    exclude_short_paragraphs: bool = True
    min_length: int = 10

    def applies_to(self, block: Block, ctx: Context) -> bool:
        if not self.check_punctuation:
            return False
        if not isinstance(block, ParagraphBlock):
            return False

        p = block.paragraph
        style_name = (getattr(p.style, "name", "") or "").strip()

        # 检查样式是否匹配
        if self.check_styles:
            return style_name in self.check_styles
        return True

    def check(self, block: Block, ctx: Context) -> List[Issue]:
        if not isinstance(block, ParagraphBlock):
            return []

        p = block.paragraph
        text = (p.text or "").strip()

        if not text:
            return []

        # 跳过短段落
        if self.exclude_short_paragraphs and len(text) < self.min_length:
            return []

        # 跳过标题和题注
        if ctx.is_heading(p) or ctx.is_caption(p):
            return []

        # 检查末尾标点
        last_char = text[-1]

        if last_char not in self.required_punctuation:
            return [
                Issue(
                    code=self.id,
                    severity=Severity.WARN,
                    message=f"{self.description}: 段落末尾应使用 {self.required_punctuation}，当前为 '{last_char}'",
                    location=Location(
                        block_index=block.index, kind="paragraph", hint=text[:50]
                    ),
                    evidence={"last_char": last_char, "text_preview": text[:100]},
                )
            ]

        return []


@dataclass
class ChineseSpacingRule(Rule):
    """PAR004: 中文字符之间不能有空格"""

    id: str
    description: str = ""
    check_chinese_spacing: bool = True
    check_styles: List[str] = field(default_factory=list)

    def applies_to(self, block: Block, ctx: Context) -> bool:
        if not self.check_chinese_spacing:
            return False
        if not isinstance(block, ParagraphBlock):
            return False

        if self.check_styles:
            p = block.paragraph
            style_name = (getattr(p.style, "name", "") or "").strip()
            return style_name in self.check_styles
        return True

    def check(self, block: Block, ctx: Context) -> List[Issue]:
        if not isinstance(block, ParagraphBlock):
            return []

        p = block.paragraph
        text = (p.text or "").strip()

        if not text:
            return []

        # 查找中文字符之间的空格
        pattern = r"([\u4e00-\u9fff])\s+([\u4e00-\u9fff])"
        matches = list(re.finditer(pattern, text))

        if not matches:
            return []

        issues: List[Issue] = []
        for match in matches:
            issues.append(
                Issue(
                    code=self.id,
                    severity=Severity.ERROR,
                    message=f"{self.description}: 中文字符 '{match.group(1)}' 和 '{match.group(2)}' 之间不应有空格",
                    location=Location(
                        block_index=block.index, kind="paragraph", hint=text[:50]
                    ),
                    evidence={
                        "char1": match.group(1),
                        "char2": match.group(2),
                        "position": match.start(),
                    },
                )
            )

        return issues


@dataclass
class EnglishQuotesRule(Rule):
    """PAR005: 中文内容不应使用英文引号"""

    id: str
    description: str = ""
    check_english_quotes: bool = True
    check_styles: List[str] = field(default_factory=list)
    min_chinese_ratio: float = 0.5

    def applies_to(self, block: Block, ctx: Context) -> bool:
        if not self.check_english_quotes:
            return False
        if not isinstance(block, ParagraphBlock):
            return False

        if self.check_styles:
            p = block.paragraph
            style_name = (getattr(p.style, "name", "") or "").strip()
            return style_name in self.check_styles
        return True

    def check(self, block: Block, ctx: Context) -> List[Issue]:
        if not isinstance(block, ParagraphBlock):
            return []

        p = block.paragraph
        text = (p.text or "").strip()

        if not text:
            return []

        issues: List[Issue] = []

        # 检查英文双引号包围的内容
        double_quote_pattern = r'"([^"]+)"'
        for match in re.finditer(double_quote_pattern, text):
            quoted_content = match.group(1)
            if self._is_mainly_chinese(quoted_content):
                issues.append(
                    Issue(
                        code=self.id,
                        severity=Severity.ERROR,
                        message=f'{self.description}: 中文内容应使用中文引号，而不是英文引号 "',
                        location=Location(
                            block_index=block.index, kind="paragraph", hint=text[:50]
                        ),
                        evidence={"quoted_content": quoted_content},
                    )
                )

        return issues

    def _is_mainly_chinese(self, text: str) -> bool:
        """判断文本是否主要是中文"""
        if not text:
            return False

        chinese_count = sum(1 for char in text if "\u4e00" <= char <= "\u9fff")
        total_chars = len(text.strip())

        if total_chars == 0:
            return False

        return chinese_count / total_chars >= self.min_chinese_ratio


@dataclass
class ChineseQuoteMatchingRule(Rule):
    """PAR006: 中文引号应该左右匹配"""

    id: str
    description: str = ""
    check_quote_matching: bool = True
    check_styles: List[str] = field(default_factory=list)

    def applies_to(self, block: Block, ctx: Context) -> bool:
        if not self.check_quote_matching:
            return False
        if not isinstance(block, ParagraphBlock):
            return False

        if self.check_styles:
            p = block.paragraph
            style_name = (getattr(p.style, "name", "") or "").strip()
            return style_name in self.check_styles
        return True

    def check(self, block: Block, ctx: Context) -> List[Issue]:
        if not isinstance(block, ParagraphBlock):
            return []

        p = block.paragraph
        text = (p.text or "").strip()

        if not text:
            return []

        issues: List[Issue] = []

        # 检查双引号配对
        left_double = text.count(""")
        right_double = text.count(""")

        if left_double != right_double:
            issues.append(
                Issue(
                    code=self.id,
                    severity=Severity.ERROR,
                    message=f"{self.description}: 中文双引号不匹配，左引号 {left_double} 个，右引号 {right_double} 个",
                    location=Location(
                        block_index=block.index, kind="paragraph", hint=text[:50]
                    ),
                    evidence={"left_count": left_double, "right_count": right_double},
                )
            )

        # 检查单引号配对
        left_single = text.count("'")
        right_single = text.count("'")

        if left_single != right_single:
            issues.append(
                Issue(
                    code=self.id,
                    severity=Severity.ERROR,
                    message=f"{self.description}: 中文单引号不匹配，左引号 {left_single} 个，右引号 {right_single} 个",
                    location=Location(
                        block_index=block.index, kind="paragraph", hint=text[:50]
                    ),
                    evidence={"left_count": left_single, "right_count": right_single},
                )
            )

        return issues


@dataclass
class ParagraphContentRule(Rule):
    """检查特定位置段落的内容是否符合要求"""

    id: str
    description: str = ""
    target_blocks: Optional[List[int]] = None  # 要检查的block索引列表
    min_length: int = 0  # 最小长度
    max_length: Optional[int] = None  # 最大长度
    required: bool = True  # 是否必须存在

    def applies_to(self, block: Block, ctx: Context) -> bool:
        if not isinstance(block, ParagraphBlock):
            return False
        
        # 如果指定了目标block，只检查这些block
        if self.target_blocks is not None:
            return block.index in self.target_blocks
        
        return False

    def check(self, block: Block, ctx: Context) -> List[Issue]:
        if not isinstance(block, ParagraphBlock):
            return []

        issues: List[Issue] = []
        p = block.paragraph
        text = (p.text or "").strip()

        # 检查是否为空
        if self.required and not text:
            issues.append(
                Issue(
                    code=self.id,
                    severity=Severity.ERROR,
                    message=f"{self.description}: 段落不能为空",
                    location=Location(
                        block_index=block.index,
                        kind="paragraph",
                        hint=f"(block {block.index})",
                    ),
                )
            )
            return issues

        # 检查最小长度
        if text and len(text) < self.min_length:
            issues.append(
                Issue(
                    code=self.id,
                    severity=Severity.WARN,
                    message=f"{self.description}: 内容过短（{len(text)}字符，至少需要{self.min_length}字符）",
                    location=Location(
                        block_index=block.index,
                        kind="paragraph",
                        hint=text[:30],
                    ),
                    evidence={"actual_length": len(text), "min_length": self.min_length},
                )
            )

        # 检查最大长度
        if self.max_length and text and len(text) > self.max_length:
            issues.append(
                Issue(
                    code=self.id,
                    severity=Severity.WARN,
                    message=f"{self.description}: 内容过长（{len(text)}字符，不应超过{self.max_length}字符）",
                    location=Location(
                        block_index=block.index,
                        kind="paragraph",
                        hint=text[:30],
                    ),
                    evidence={"actual_length": len(text), "max_length": self.max_length},
                )
            )

        return issues
