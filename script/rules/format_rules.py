"""通用规则类集合

这个文件包含高度抽象的通用规则类，通过参数配置适配不同文档需求。

设计原则：
1. 规则类代表检查模式（如何检查），而非检查对象（检查什么）
2. 所有文档特异性通过参数传入
3. 一个规则类可以服务多个规则 ID

通用规则类清单：
- FontStyleRule: 字体样式检查（字体、字号、加粗等）
- ParagraphFormatRule: 段落格式检查（行距、对齐、缩进等）
- SequenceRule: 序列/编号检查（标题、图表编号连续性）
- MatchingRule: 文本匹配检查（正则表达式）
- CountingRule: 数量统计检查
- OrderingRule: 顺序检查
- RelationRule: 关系检查（元素间的前后、配对关系）
- ConsistencyRule: 一致性检查
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Pattern, Tuple

from script.core.context import Context
from script.core.model import Block, Issue, Location, ParagraphBlock, Severity, TableBlock
from script.core.rule import FinalizeRule, Rule


@dataclass
class FontStyleRule(Rule):
    """通用的字体样式检查规则
    
    用途：检查字体名称、字号、颜色、加粗、斜体等
    
    参数：
        target_styles: 目标段落样式列表（如 ["Heading 1", "Normal"]）
        target_blocks: 或指定block索引范围（如 [0, 5] 表示前5个block）
        expected_font_name: 期望的字体名称
        font_name_alternatives: 备选字体名称（西文字体）
        expected_font_size: 期望的字号（EMU单位）
        font_size_tolerance: 字号容差
        expected_bold: 是否应该加粗
        expected_italic: 是否应该斜体
        expected_color: 期望的颜色（RGB hex）
        check_consistency: 是否检查一致性（同类元素格式应相同）
    """
    
    id: str
    description: str = ""
    target_styles: List[str] = field(default_factory=list)
    target_blocks: Optional[List[int]] = None  # [start, end] 或 None
    expected_font_name: Optional[str] = None
    font_name_alternatives: List[str] = field(default_factory=list)
    expected_font_size: Optional[int] = None  # EMU 单位
    font_size_tolerance: int = 635  # 默认容差 0.5pt
    expected_bold: Optional[bool] = None
    expected_italic: Optional[bool] = None
    expected_color: Optional[str] = None
    check_consistency: bool = False
    
    def applies_to(self, block: Block, ctx: Context) -> bool:
        if not isinstance(block, ParagraphBlock):
            return False
        
        # 如果指定了 block 范围
        if self.target_blocks is not None:
            if len(self.target_blocks) == 2:
                start, end = self.target_blocks
                if not (start <= block.index < end):
                    return False
            elif block.index not in self.target_blocks:
                return False
        
        # 如果指定了样式
        if self.target_styles:
            p = block.paragraph
            style_name = getattr(p.style, "name", "") or ""
            if style_name not in self.target_styles:
                return False
        
        return True
    
    def check(self, block: Block, ctx: Context) -> List[Issue]:
        if not isinstance(block, ParagraphBlock):
            return []
        
        issues = []
        p = block.paragraph
        
        # 检查每个 run 的字体
        for run in p.runs:
            # 检查字体名称
            if self.expected_font_name:
                actual_font = run.font.name
                if actual_font != self.expected_font_name:
                    # 检查是否在备选字体中
                    if not (self.font_name_alternatives and actual_font in self.font_name_alternatives):
                        issues.append(Issue(
                            code=self.id,
                            severity=Severity.WARN,
                            message=f"{self.description}: 期望字体 '{self.expected_font_name}'，实际为 '{actual_font}'",
                            location=Location(
                                block_index=block.index,
                                kind="paragraph",
                                hint=p.text[:50] if p.text else ""
                            ),
                            evidence={"expected": self.expected_font_name, "actual": actual_font}
                        ))
                        break
            
            # 检查字号
            if self.expected_font_size is not None and run.font.size:
                actual_size = run.font.size
                if abs(actual_size - self.expected_font_size) > self.font_size_tolerance:
                    issues.append(Issue(
                        code=self.id,
                        severity=Severity.WARN,
                        message=f"{self.description}: 期望字号 {self.expected_font_size}，实际为 {actual_size}",
                        location=Location(
                            block_index=block.index,
                            kind="paragraph",
                            hint=p.text[:50] if p.text else ""
                        ),
                        evidence={"expected": self.expected_font_size, "actual": actual_size}
                    ))
                    break
            
            # 检查加粗
            if self.expected_bold is not None:
                actual_bold = run.font.bold or False
                if actual_bold != self.expected_bold:
                    issues.append(Issue(
                        code=self.id,
                        severity=Severity.INFO,
                        message=f"{self.description}: 期望{'加粗' if self.expected_bold else '不加粗'}，实际为{'加粗' if actual_bold else '不加粗'}",
                        location=Location(
                            block_index=block.index,
                            kind="paragraph",
                            hint=p.text[:50] if p.text else ""
                        )
                    ))
                    break
            
            # 检查斜体
            if self.expected_italic is not None:
                actual_italic = run.font.italic or False
                if actual_italic != self.expected_italic:
                    issues.append(Issue(
                        code=self.id,
                        severity=Severity.INFO,
                        message=f"{self.description}: 期望{'斜体' if self.expected_italic else '不斜体'}",
                        location=Location(
                            block_index=block.index,
                            kind="paragraph",
                            hint=p.text[:50] if p.text else ""
                        )
                    ))
                    break
        
        return issues


@dataclass
class ParagraphFormatRule(Rule):
    """通用的段落格式检查规则
    
    用途：检查行距、对齐、缩进、段间距等
    
    参数：
        target_styles: 目标段落样式
        line_spacing: 期望的行距（倍数，如 1.5）
        line_spacing_rule: 行距规则类型（"multiple", "exactly", "atLeast"）
        line_spacing_tolerance: 行距容差
        alignment: 对齐方式（"left", "center", "right", "justify"）
        first_line_indent: 首行缩进（twips）
        left_indent: 左缩进
        right_indent: 右缩进
        space_before: 段前间距
        space_after: 段后间距
    """
    
    id: str
    description: str = ""
    target_styles: List[str] = field(default_factory=list)
    target_blocks: Optional[List[int]] = None  # 指定block索引列表
    line_spacing: Optional[float] = None
    line_spacing_rule: str = "multiple"  # "multiple", "exactly", "atLeast"
    line_spacing_tolerance: float = 0.05
    alignment: Optional[str] = None  # "left", "center", "right", "justify"
    first_line_indent: Optional[int] = None
    left_indent: Optional[int] = None
    right_indent: Optional[int] = None
    space_before: Optional[int] = None
    space_after: Optional[int] = None
    indent_tolerance: int = 72  # 默认容差 0.05 inch
    
    def applies_to(self, block: Block, ctx: Context) -> bool:
        if not isinstance(block, ParagraphBlock):
            return False
        
        # 如果指定了 block 列表
        if self.target_blocks is not None:
            if block.index not in self.target_blocks:
                return False
        
        # 如果指定了样式
        if self.target_styles:
            p = block.paragraph
            style_name = getattr(p.style, "name", "") or ""
            if style_name not in self.target_styles:
                return False
        
        return True
    
    def check(self, block: Block, ctx: Context) -> List[Issue]:
        if not isinstance(block, ParagraphBlock):
            return []
        
        issues = []
        p = block.paragraph
        fmt = p.paragraph_format
        
        # 检查行距
        if self.line_spacing is not None:
            actual_spacing = getattr(fmt, 'line_spacing', None)
            if actual_spacing is not None:
                # 转换为倍数（如果是倍数行距）
                if self.line_spacing_rule == "multiple":
                    # line_spacing 在倍数模式下是浮点数
                    if abs(actual_spacing - self.line_spacing) > self.line_spacing_tolerance:
                        issues.append(Issue(
                            code=self.id,
                            severity=Severity.WARN,
                            message=f"{self.description}: 期望行距 {self.line_spacing}倍，实际为 {actual_spacing}倍",
                            location=Location(
                                block_index=block.index,
                                kind="paragraph",
                                hint=p.text[:50] if p.text else ""
                            ),
                            evidence={"expected": self.line_spacing, "actual": actual_spacing}
                        ))
        
        # 检查对齐方式
        if self.alignment:
            actual_alignment = str(getattr(fmt, 'alignment', '')).lower()
            expected_align_map = {
                "left": "left",
                "center": "center",
                "right": "right",
                "justify": "justify",
                "both": "justify"
            }
            
            expected = expected_align_map.get(self.alignment.lower(), self.alignment.lower())
            if expected not in actual_alignment:
                issues.append(Issue(
                    code=self.id,
                    severity=Severity.INFO,
                    message=f"{self.description}: 期望对齐方式 '{self.alignment}'",
                    location=Location(
                        block_index=block.index,
                        kind="paragraph",
                        hint=p.text[:50] if p.text else ""
                    )
                ))
        
        # 检查首行缩进
        if self.first_line_indent is not None:
            actual = getattr(fmt, 'first_line_indent', None)
            if actual is not None:
                if abs(actual - self.first_line_indent) > self.indent_tolerance:
                    issues.append(Issue(
                        code=self.id,
                        severity=Severity.INFO,
                        message=f"{self.description}: 首行缩进不符",
                        location=Location(
                            block_index=block.index,
                            kind="paragraph",
                            hint=p.text[:50] if p.text else ""
                        )
                    ))
        
        return issues


@dataclass
class SequenceRule(FinalizeRule):
    """通用的序列/编号检查规则
    
    用途：检查标题、图表、公式等的编号连续性
    
    参数：
        target_type: 目标类型（"heading", "figure", "table", "equation"）
        numbering_pattern: 编号提取正则表达式（如 "^(\\d+)\\."）
        numbering_levels: 检查的层级列表（如 [1, 2, 3]）
        check_continuity: 是否检查连续性
        allow_skips: 是否允许跳号
        start_from: 起始编号（数字或字母）
        heading_styles: 标题样式列表（用于 heading 类型）
    """
    
    id: str
    description: str = ""
    target_type: str = "heading"  # "heading", "figure", "table", "equation"
    numbering_pattern: str = r"^(\d+)"
    numbering_levels: List[int] = field(default_factory=lambda: [1, 2, 3])
    check_continuity: bool = True
    allow_skips: bool = False
    start_from: int = 1
    heading_styles: List[str] = field(default_factory=lambda: ["Heading 1", "Heading 2", "Heading 3"])
    
    def __post_init__(self):
        self._pattern: Pattern = re.compile(self.numbering_pattern)
    
    def applies_to(self, block: Block, ctx: Context) -> bool:
        return False
    
    def check(self, block: Block, ctx: Context) -> List[Issue]:
        return []
    
    def finalize(self, ctx: Context) -> List[Issue]:
        if self.target_type == "heading":
            return self._check_heading_sequence(ctx)
        elif self.target_type in ["figure", "table", "equation"]:
            return self._check_element_sequence(ctx)
        return []
    
    def _check_heading_sequence(self, ctx: Context) -> List[Issue]:
        """检查标题编号连续性"""
        issues = []
        
        # 按级别提取标题编号
        headings_by_level = {level: [] for level in self.numbering_levels}
        
        for block in ctx.blocks:
            if not isinstance(block, ParagraphBlock):
                continue
            
            p = block.paragraph
            style_name = getattr(p.style, "name", "") or ""
            
            # 确定标题级别
            level = None
            for i, style in enumerate(self.heading_styles, 1):
                if style == style_name:
                    level = i
                    break
            
            if level and level in self.numbering_levels:
                text = (p.text or "").strip()
                match = self._pattern.match(text)
                if match:
                    number = int(match.group(1))
                    headings_by_level[level].append({
                        "number": number,
                        "block_index": block.index,
                        "text": text
                    })
        
        # 检查每个级别的连续性
        if self.check_continuity:
            for level in self.numbering_levels:
                headings = headings_by_level[level]
                if not headings:
                    continue
                
                expected = self.start_from
                for h in headings:
                    if h["number"] != expected:
                        issues.append(Issue(
                            code=self.id,
                            severity=Severity.ERROR,
                            message=f"{self.description}: {level}级标题编号不连续，期望 {expected}，实际为 {h['number']}",
                            location=Location(
                                block_index=h["block_index"],
                                kind="heading",
                                hint=h["text"][:50]
                            ),
                            evidence={"expected": expected, "actual": h["number"], "level": level}
                        ))
                    expected = h["number"] + 1 if not self.allow_skips else expected + 1
        
        return issues
    
    def _check_element_sequence(self, ctx: Context) -> List[Issue]:
        """检查图表等元素的编号连续性"""
        # TODO: 实现图表编号检查
        return []


@dataclass
class MatchingRule(Rule):
    """通用的文本匹配检查规则
    
    用途：检查文本内容是否符合特定模式
    
    参数：
        pattern: 正则表达式模式
        match_type: 匹配类型（"contains", "full", "starts", "ends"）
        target_styles: 目标段落样式
        case_sensitive: 是否大小写敏感
        negate: 反向匹配（内容不应匹配该模式）
    """
    
    id: str
    description: str = ""
    pattern: str = ""
    match_type: str = "contains"  # "contains", "full", "starts", "ends"
    target_styles: List[str] = field(default_factory=list)
    case_sensitive: bool = True
    negate: bool = False
    
    def __post_init__(self):
        flags = 0 if self.case_sensitive else re.IGNORECASE
        self._pattern: Pattern = re.compile(self.pattern, flags)
    
    def applies_to(self, block: Block, ctx: Context) -> bool:
        if not isinstance(block, ParagraphBlock):
            return False
        
        if self.target_styles:
            p = block.paragraph
            style_name = getattr(p.style, "name", "") or ""
            if style_name not in self.target_styles:
                return False
        
        return True
    
    def check(self, block: Block, ctx: Context) -> List[Issue]:
        if not isinstance(block, ParagraphBlock):
            return []
        
        p = block.paragraph
        text = (p.text or "").strip()
        
        # 执行匹配
        matched = False
        if self.match_type == "contains":
            matched = self._pattern.search(text) is not None
        elif self.match_type == "full":
            matched = self._pattern.fullmatch(text) is not None
        elif self.match_type == "starts":
            matched = self._pattern.match(text) is not None
        elif self.match_type == "ends":
            matched = text and self._pattern.search(text[-len(self.pattern):]) is not None
        
        # 根据 negate 决定是否报告问题
        should_report = matched if self.negate else not matched
        
        if should_report:
            message = f"{self.description}: "
            if self.negate:
                message += f"不应包含模式 '{self.pattern}'"
            else:
                message += f"应匹配模式 '{self.pattern}'"
            
            return [Issue(
                code=self.id,
                severity=Severity.WARN,
                message=message,
                location=Location(
                    block_index=block.index,
                    kind="paragraph",
                    hint=text[:50]
                )
            )]
        
        return []


@dataclass
class CountingRule(FinalizeRule):
    """通用的数量统计检查规则
    
    用途：统计某类元素的数量并验证
    
    参数：
        target_type: 统计对象类型（"paragraph", "table", "image", "heading"）
        pattern: 筛选模式（正则表达式，可选）
        target_styles: 目标样式（用于筛选）
        min_count: 最小数量
        max_count: 最大数量
        exact_count: 精确数量
    """
    
    id: str
    description: str = ""
    target_type: str = "paragraph"
    pattern: Optional[str] = None
    target_styles: List[str] = field(default_factory=list)
    min_count: Optional[int] = None
    max_count: Optional[int] = None
    exact_count: Optional[int] = None
    
    def applies_to(self, block: Block, ctx: Context) -> bool:
        return False
    
    def check(self, block: Block, ctx: Context) -> List[Issue]:
        return []
    
    def finalize(self, ctx: Context) -> List[Issue]:
        count = 0
        
        for block in ctx.blocks:
            # 类型筛选
            if self.target_type == "paragraph" and not isinstance(block, ParagraphBlock):
                continue
            elif self.target_type == "table" and not isinstance(block, TableBlock):
                continue
            elif self.target_type == "heading":
                if not isinstance(block, ParagraphBlock):
                    continue
                p = block.paragraph
                style_name = getattr(p.style, "name", "") or ""
                if not style_name.startswith("Heading"):
                    continue
            
            # 样式筛选
            if self.target_styles and isinstance(block, ParagraphBlock):
                p = block.paragraph
                style_name = getattr(p.style, "name", "") or ""
                if style_name not in self.target_styles:
                    continue
            
            # 模式筛选
            if self.pattern and isinstance(block, ParagraphBlock):
                p = block.paragraph
                text = (p.text or "").strip()
                if not re.search(self.pattern, text):
                    continue
            
            count += 1
        
        # 验证数量
        issues = []
        
        if self.exact_count is not None and count != self.exact_count:
            issues.append(Issue(
                code=self.id,
                severity=Severity.ERROR,
                message=f"{self.description}: 期望 {self.exact_count} 个，实际为 {count} 个",
                location=Location(block_index=0, kind="document", hint="(document)"),
                evidence={"expected": self.exact_count, "actual": count}
            ))
        elif self.min_count is not None and count < self.min_count:
            issues.append(Issue(
                code=self.id,
                severity=Severity.ERROR,
                message=f"{self.description}: 最少 {self.min_count} 个，实际为 {count} 个",
                location=Location(block_index=0, kind="document", hint="(document)"),
                evidence={"min": self.min_count, "actual": count}
            ))
        elif self.max_count is not None and count > self.max_count:
            issues.append(Issue(
                code=self.id,
                severity=Severity.WARN,
                message=f"{self.description}: 最多 {self.max_count} 个，实际为 {count} 个",
                location=Location(block_index=0, kind="document", hint="(document)"),
                evidence={"max": self.max_count, "actual": count}
            ))
        
        return issues


@dataclass
class RelationRule(Rule):
    """通用的关系检查规则
    
    用途：检查元素间的关系（前后、配对等）
    
    参数：
        element_a_type: 元素A的类型（"table", "image", "paragraph"）
        element_a_pattern: 元素A的文本模式（可选）
        element_b_type: 元素B的类型
        element_b_pattern: 元素B的文本模式
        relation_type: 关系类型（"before", "after", "paired"）
        max_distance: 最大距离（blocks数）
        required: 是否必需
    """
    
    id: str
    description: str = ""
    element_a_type: str = "table"
    element_a_pattern: Optional[str] = None
    element_b_type: str = "paragraph"
    element_b_pattern: str = ""
    relation_type: str = "before"  # "before", "after", "paired"
    max_distance: int = 2
    required: bool = True
    
    def applies_to(self, block: Block, ctx: Context) -> bool:
        # 这个规则在 check 中批量处理，不需要 applies_to
        return False
    
    def check(self, block: Block, ctx: Context) -> List[Issue]:
        # 在 finalize 中统一处理
        return []


# TODO: 实现更多通用规则类
# - OrderingRule: 顺序检查
# - ConsistencyRule: 一致性检查  
# - CustomPatternRule: 自定义模式检查
