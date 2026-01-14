from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from core.context import Context
from core.model import Block, Issue, Location, ParagraphBlock, Severity
from core.rule import FinalizeRule, Rule


def _para_hint(p: ParagraphBlock) -> str:
    return ((p.paragraph.text or "").strip()[:50]) or "(paragraph)"


@dataclass
class NoOpRule(Rule):
    id: str = "BASE_NOOP"
    emit_issue: bool = False
    severity: Severity = Severity.INFO
    message: str = "Rule is not implemented"

    def applies_to(self, block: Block, ctx: Context) -> bool:
        return False

    def check(self, block: Block, ctx: Context) -> List[Issue]:
        return []


@dataclass
class StructureMinBodyRule(FinalizeRule):
    id: str = "STR001"
    name: str = "Structure: minimum body paragraphs"
    description: str = "Ensure the document has at least N non-empty paragraphs."
    min_body_paragraphs: int = 1
    legacy_check: str = "structure"
    legacy_config: Dict[str, Any] = field(default_factory=dict)

    def applies_to(self, block: Block, ctx: Context) -> bool:
        return False

    def check(self, block: Block, ctx: Context) -> List[Issue]:
        return []

    def finalize(self, ctx: Context) -> List[Issue]:
        non_empty = 0
        for b in ctx.blocks:
            if isinstance(b, ParagraphBlock) and (b.paragraph.text or "").strip():
                non_empty += 1
        if non_empty >= self.min_body_paragraphs:
            return []
        return [
            Issue(
                code=self.id,
                severity=Severity.ERROR,
                message=f"{self.name}: expected >= {self.min_body_paragraphs}, got {non_empty}",
                location=Location(block_index=0, kind="document", hint="(document)"),
                evidence={"min_body_paragraphs": self.min_body_paragraphs, "actual": non_empty},
            )
        ]


@dataclass
class TocPresenceRule(FinalizeRule):
    id: str = "TOC001"
    name: str = "Table of contents: presence"
    description: str = "Ensure the table of contents exists (by title or TOC styles)."
    required: bool = True
    title_text: str = "目录"
    style_prefixes: List[str] = None  # type: ignore[assignment]
    legacy_check: str = "table_of_contents"
    legacy_config: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.style_prefixes is None:
            self.style_prefixes = ["TOC"]

    def applies_to(self, block: Block, ctx: Context) -> bool:
        return False

    def check(self, block: Block, ctx: Context) -> List[Issue]:
        return []

    def finalize(self, ctx: Context) -> List[Issue]:
        if not self.required:
            return []

        for b in ctx.blocks:
            if not isinstance(b, ParagraphBlock):
                continue
            p = b.paragraph
            text = (p.text or "").strip()
            style_name = (getattr(p.style, "name", "") or "").strip()
            if text == self.title_text:
                return []
            for pref in self.style_prefixes:
                if pref and style_name.startswith(pref):
                    return []

        return [
            Issue(
                code=self.id,
                severity=Severity.ERROR,
                message=f"{self.name}: not found",
                location=Location(block_index=0, kind="document", hint="(document)"),
            )
        ]


@dataclass
class ReferencesHeadingRule(FinalizeRule):
    id: str = "REF001"
    name: str = "References: heading presence"
    description: str = "Ensure the references heading exists."
    required: bool = True
    heading_text: str = "参考文献"
    legacy_check: str = "references"
    legacy_config: Dict[str, Any] = field(default_factory=dict)

    def applies_to(self, block: Block, ctx: Context) -> bool:
        return False

    def check(self, block: Block, ctx: Context) -> List[Issue]:
        return []

    def finalize(self, ctx: Context) -> List[Issue]:
        if not self.required:
            return []

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
                message=f"{self.name}: not found ({self.heading_text})",
                location=Location(block_index=0, kind="document", hint="(document)"),
                evidence={"heading_text": self.heading_text},
            )
        ]


@dataclass
class ReferencesCitationRule(FinalizeRule):
    id: str = "REF002"
    name: str = "References: superscript citation"
    description: str = "参考文献必须在正文中通过上标引用"
    check_superscript_citation: bool = True
    reference_heading: str = "参考文献"
    citation_pattern: str = "^\\[\\d+(-\\d+)?(,\\s*\\d+)*\\]$"

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
        references = []
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
            import re
            ref_match = re.match(r'^\[(\d+)\]', text)
            if ref_match:
                ref_num = int(ref_match.group(1))
                references.append({
                    'number': ref_num,
                    'block_index': b.index,
                    'text': text,
                    'cited': False  # 是否被引用
                })

        if not references:
            return []

        # 收集正文中的引用
        citations_found = set()
        citation_issues = []
        
        for b in ctx.blocks:
            if b.index >= ref_start_index:
                break  # 到达参考文献章节，停止检查
            if not isinstance(b, ParagraphBlock):
                continue
                
            p = b.paragraph
            text = (p.text or "").strip()
            if not text:
                continue
                
            # 跳过标题、目录等
            if ctx.is_heading(p) or ctx.is_caption(p):
                continue
                
            # 查找引用
            import re
            # 查找所有符合模式的引用
            citation_matches = re.finditer(self.citation_pattern, text)
            
            for match in citation_matches:
                citation_text = match.group(0)
                
                # 检查是否是上标格式
                is_superscript = self._check_superscript_in_paragraph(p, match.start(), match.end())
                
                if not is_superscript:
                    citation_issues.append(
                        Issue(
                            code=self.id,
                            severity=Severity.ERROR,
                            message=f"{self.name}: citation '{citation_text}' is not in superscript format",
                            location=Location(
                                block_index=b.index,
                                kind="paragraph",
                                hint=text[:50]
                            ),
                            evidence={
                                "citation": citation_text,
                                "paragraph_text": text
                            }
                        )
                    )
                
                # 提取引用的编号
                numbers = re.findall(r'\d+', citation_text)
                for num_str in numbers:
                    num = int(num_str)
                    citations_found.add(num)
                    
                    # 标记对应的参考文献为已引用
                    for ref in references:
                        if ref['number'] == num:
                            ref['cited'] = True

        # 检查未被引用的参考文献
        issues = citation_issues
        for ref in references:
            if not ref['cited']:
                issues.append(
                    Issue(
                        code=self.id,
                        severity=Severity.WARN,
                        message=f"{self.name}: reference [{ref['number']}] is not cited in the text",
                        location=Location(
                            block_index=ref['block_index'],
                            kind="paragraph",
                            hint=ref['text'][:50]
                        ),
                        evidence={
                            "reference_number": ref['number'],
                            "reference_text": ref['text']
                        }
                    )
                )

        # 检查引用了但不存在的参考文献
        ref_numbers = {ref['number'] for ref in references}
        for cited_num in citations_found:
            if cited_num not in ref_numbers:
                issues.append(
                    Issue(
                        code=self.id,
                        severity=Severity.ERROR,
                        message=f"{self.name}: citation [{cited_num}] not found in references list",
                        location=Location(block_index=0, kind="document", hint="(document)"),
                        evidence={"cited_number": cited_num}
                    )
                )

        return issues

    def _check_superscript_in_paragraph(self, paragraph, start_pos: int, end_pos: int) -> bool:
        """检查段落中指定位置的文本是否为上标格式"""
        try:
            # 遍历段落中的所有run，查找包含引用文本的run
            current_pos = 0
            for run in paragraph.runs:
                run_text = run.text or ""
                run_end = current_pos + len(run_text)
                
                # 检查这个run是否包含我们要检查的文本范围
                if current_pos <= start_pos < run_end or current_pos < end_pos <= run_end:
                    # 检查run的上标属性
                    if hasattr(run.font, 'superscript') and run.font.superscript:
                        return True
                    # 检查run的vertical alignment属性
                    if hasattr(run.font, 'vertical_alignment'):
                        from docx.enum.text import WD_ALIGN_VERTICAL
                        if run.font.vertical_alignment == WD_ALIGN_VERTICAL.SUPERSCRIPT:
                            return True
                
                current_pos = run_end
                
        except Exception:
            # 如果检查失败，假设不是上标（保守处理）
            pass
            
        return False


@dataclass
class ReferencesHeadingLevelRule(FinalizeRule):
    id: str = "REF003"
    name: str = "References: heading level"
    description: str = "参考文献必须是一级标题"
    check_heading_level: bool = True
    reference_heading: str = "参考文献"
    required_level: int = 1
    level1_styles: List[str] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.level1_styles is None:
            self.level1_styles = ["Heading 1", "标题 1"]

    def applies_to(self, block: Block, ctx: Context) -> bool:
        return False

    def check(self, block: Block, ctx: Context) -> List[Issue]:
        return []

    def finalize(self, ctx: Context) -> List[Issue]:
        if not self.check_heading_level:
            return []

        # 查找参考文献标题
        ref_heading_block = None
        for b in ctx.blocks:
            if not isinstance(b, ParagraphBlock):
                continue
            p = b.paragraph
            text = (p.text or "").strip()
            
            if text == self.reference_heading:
                ref_heading_block = b
                break

        if not ref_heading_block:
            return []  # 没有找到参考文献标题，不检查级别

        p = ref_heading_block.paragraph
        style_name = (getattr(p.style, "name", "") or "").strip()
        
        # 检查是否是一级标题样式
        is_level1 = any(level1_style in style_name for level1_style in self.level1_styles)
        
        # 如果不是预定义的一级标题样式，检查是否是标题并且是一级
        if not is_level1 and ctx.is_heading(p):
            # 尝试从样式名中提取级别信息
            import re
            level_match = re.search(r'(\d+)', style_name)
            if level_match:
                level = int(level_match.group(1))
                is_level1 = (level == self.required_level)
            else:
                # 如果无法确定级别，但是是标题，假设可能是一级标题
                is_level1 = True

        if not is_level1:
            return [
                Issue(
                    code=self.id,
                    severity=Severity.ERROR,
                    message=f"{self.name}: '{self.reference_heading}' must be a level {self.required_level} heading, found style: '{style_name}'",
                    location=Location(
                        block_index=ref_heading_block.index,
                        kind="paragraph",
                        hint=ref_heading_block.paragraph.text[:50] if ref_heading_block.paragraph.text else "(empty)"
                    ),
                    evidence={
                        "heading_text": self.reference_heading,
                        "required_level": self.required_level,
                        "actual_style": style_name,
                        "expected_styles": self.level1_styles
                    }
                )
            ]

        return []


@dataclass
class EmptyLinesRule(Rule):
    id: str = "PAR002"
    name: str = "Paragraphs: empty lines"
    description: str = "Limit consecutive empty paragraphs."
    max_consecutive: int = 0
    legacy_check: str = "paragraphs"
    legacy_config: Dict[str, Any] = field(default_factory=dict)

    def applies_to(self, block: Block, ctx: Context) -> bool:
        return isinstance(block, ParagraphBlock)

    def check(self, block: Block, ctx: Context) -> List[Issue]:
        if not isinstance(block, ParagraphBlock):
            return []

        issues: List[Issue] = []
        run_len = 0
        i = block.index

        if (block.paragraph.text or "").strip() != "":
            return []

        while i < len(ctx.blocks):
            b = ctx.blocks[i]
            if not isinstance(b, ParagraphBlock):
                break
            if (b.paragraph.text or "").strip() != "":
                break
            run_len += 1
            i += 1

        if run_len > self.max_consecutive:
            issues.append(
                Issue(
                    code=self.id,
                    severity=Severity.ERROR,
                    message=f"{self.name}: {run_len} (max {self.max_consecutive})",
                    location=Location(block_index=block.index, kind="paragraph", hint=_para_hint(block)),
                    evidence={"run_length": run_len, "max_consecutive": self.max_consecutive},
                )
            )

        return issues


@dataclass
class ParagraphPunctuationRule(Rule):
    id: str = "PAR003"
    name: str = "Paragraphs: punctuation"
    description: str = "正文或者列表段落末尾必须使用句号或冒号"
    check_punctuation: bool = True
    required_punctuation: List[str] = None  # type: ignore[assignment]
    check_styles: List[str] = None  # type: ignore[assignment]
    exclude_short_paragraphs: bool = True
    min_length: int = 10

    def __post_init__(self) -> None:
        if self.required_punctuation is None:
            self.required_punctuation = ["。", "："]
        if self.check_styles is None:
            self.check_styles = ["Normal", "正文", "List Paragraph", "列表段落"]

    def applies_to(self, block: Block, ctx: Context) -> bool:
        return isinstance(block, ParagraphBlock)

    def check(self, block: Block, ctx: Context) -> List[Issue]:
        if not self.check_punctuation:
            return []
        
        if not isinstance(block, ParagraphBlock):
            return []

        p = block.paragraph
        text = (p.text or "").strip()
        
        # 跳过空段落
        if not text:
            return []
            
        # 跳过过短的段落（如果启用了排除选项）
        if self.exclude_short_paragraphs and len(text) < self.min_length:
            return []

        # 检查段落样式是否在检查范围内
        style_name = (getattr(p.style, "name", "") or "").strip()
        should_check = any(check_style in style_name for check_style in self.check_styles)
        
        # 如果样式不匹配，但是不是标题、题注等特殊段落，也检查
        if not should_check:
            if not (ctx.is_heading(p) or ctx.is_caption(p)):
                # 检查是否是列表项（通过缩进或编号判断）
                import re
                if (re.match(r'^\s*[\d\w]+[.)]\s+', text) or  # 编号列表 "1. " "a) "
                    re.match(r'^\s*[•·▪▫-]\s+', text) or      # 符号列表
                    text.startswith('    ') or text.startswith('\t')):  # 缩进段落
                    should_check = True
                elif style_name == "Normal" or not style_name:  # 默认样式
                    should_check = True

        if not should_check:
            return []

        # 检查末尾标点符号
        last_char = text[-1] if text else ""
        
        if last_char not in self.required_punctuation:
            # 检查是否以其他标点符号结尾（可能是合理的）
            other_punctuation = [".", "!", "?", "；", "，", "、", """, "'", ")", "）", "]", "】"]
            
            severity = Severity.ERROR
            message = f"{self.name}: paragraph must end with one of {self.required_punctuation}, found: '{last_char}'"
            
            # 如果以其他标点结尾，降低严重程度
            if last_char in other_punctuation:
                severity = Severity.WARN
                message = f"{self.name}: paragraph should preferably end with one of {self.required_punctuation}, found: '{last_char}'"
            elif not last_char or last_char.isalnum() or ord(last_char) > 127:  # 无标点或以字母数字结尾
                message = f"{self.name}: paragraph must end with punctuation, found: '{last_char or '(no punctuation)'}'"

            return [
                Issue(
                    code=self.id,
                    severity=severity,
                    message=message,
                    location=Location(
                        block_index=block.index,
                        kind="paragraph",
                        hint=text[:50]
                    ),
                    evidence={
                        "paragraph_text": text,
                        "last_character": last_char,
                        "required_punctuation": self.required_punctuation,
                        "style_name": style_name
                    }
                )
            ]

        return []


@dataclass
class ChineseSpacingRule(Rule):
    id: str = "PAR004"
    name: str = "Paragraphs: Chinese spacing"
    description: str = "中文字符之间不能有一个或多个空格"
    check_chinese_spacing: bool = True
    check_styles: List[str] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.check_styles is None:
            self.check_styles = ["Normal", "正文", "List Paragraph", "列表段落"]

    def applies_to(self, block: Block, ctx: Context) -> bool:
        return isinstance(block, ParagraphBlock)

    def check(self, block: Block, ctx: Context) -> List[Issue]:
        if not self.check_chinese_spacing:
            return []
        
        if not isinstance(block, ParagraphBlock):
            return []

        p = block.paragraph
        text = (p.text or "").strip()
        
        # 跳过空段落
        if not text:
            return []

        # 检查段落样式是否在检查范围内
        style_name = (getattr(p.style, "name", "") or "").strip()
        should_check = any(check_style in style_name for check_style in self.check_styles)
        
        # 如果样式不匹配，但是不是标题、题注等特殊段落，也检查
        if not should_check:
            if not (ctx.is_heading(p) or ctx.is_caption(p)):
                should_check = True

        if not should_check:
            return []

        # 检查中文字符之间的空格
        issues = []
        import re
        
        # 查找中文字符之间的空格模式
        # 匹配：中文字符 + 一个或多个空格 + 中文字符
        chinese_spacing_pattern = r'([\u4e00-\u9fff])\s+([\u4e00-\u9fff])'
        
        matches = list(re.finditer(chinese_spacing_pattern, text))
        
        for match in matches:
            start_pos = match.start()
            end_pos = match.end()
            matched_text = match.group(0)
            char_before = match.group(1)
            char_after = match.group(2)
            spaces = matched_text[1:-1]  # 提取中间的空格
            
            # 计算在原文中的位置信息
            before_text = text[:start_pos]
            after_text = text[end_pos:]
            
            issues.append(
                Issue(
                    code=self.id,
                    severity=Severity.ERROR,
                    message=f"{self.name}: unnecessary space(s) between Chinese characters: '{char_before}' and '{char_after}'",
                    location=Location(
                        block_index=block.index,
                        kind="paragraph",
                        hint=text[:50]
                    ),
                    evidence={
                        "matched_text": matched_text,
                        "char_before": char_before,
                        "char_after": char_after,
                        "spaces": spaces,
                        "space_count": len(spaces),
                        "position": start_pos,
                        "context_before": before_text[-10:] if len(before_text) > 10 else before_text,
                        "context_after": after_text[:10] if len(after_text) > 10 else after_text
                    }
                )
            )

        # 额外检查：中文标点符号前后的空格
        # 检查中文标点符号前的空格
        punct_before_pattern = r'\s+([\u3000-\u303f\uff00-\uffef])'
        punct_before_matches = list(re.finditer(punct_before_pattern, text))
        
        for match in punct_before_matches:
            punct = match.group(1)
            spaces = match.group(0)[:-1]  # 去掉标点符号，只保留空格
            
            # 只检查中文标点符号
            if punct in '，。；：！？""''（）【】《》':
                issues.append(
                    Issue(
                        code=self.id,
                        severity=Severity.WARN,
                        message=f"{self.name}: unnecessary space before Chinese punctuation: '{punct}'",
                        location=Location(
                            block_index=block.index,
                            kind="paragraph",
                            hint=text[:50]
                        ),
                        evidence={
                            "punctuation": punct,
                            "spaces": spaces,
                            "space_count": len(spaces),
                            "position": match.start()
                        }
                    )
                )

        # 检查中文标点符号后的空格（某些情况下可能是合理的，所以用WARN）
        punct_after_pattern = r'([\u3000-\u303f\uff00-\uffef])\s+'
        punct_after_matches = list(re.finditer(punct_after_pattern, text))
        
        for match in punct_after_matches:
            punct = match.group(1)
            spaces = match.group(0)[1:]  # 去掉标点符号，只保留空格
            
            # 只检查某些中文标点符号（句号、感叹号、问号后的空格可能是合理的）
            if punct in '，；：""''（【《':
                issues.append(
                    Issue(
                        code=self.id,
                        severity=Severity.WARN,
                        message=f"{self.name}: unnecessary space after Chinese punctuation: '{punct}'",
                        location=Location(
                            block_index=block.index,
                            kind="paragraph",
                            hint=text[:50]
                        ),
                        evidence={
                            "punctuation": punct,
                            "spaces": spaces,
                            "space_count": len(spaces),
                            "position": match.start()
                        }
                    )
                )

        return issues


@dataclass
class EnglishQuotesRule(Rule):
    id: str = "PAR005"
    name: str = "Paragraphs: English quotes"
    description: str = "中文不能被成对的英文双引号或英文单引号包围"
    check_english_quotes: bool = True
    check_styles: List[str] = None  # type: ignore[assignment]
    min_chinese_ratio: float = 0.5  # 引号内容中文字符占比阈值

    def __post_init__(self) -> None:
        if self.check_styles is None:
            self.check_styles = ["Normal", "正文", "List Paragraph", "列表段落"]

    def applies_to(self, block: Block, ctx: Context) -> bool:
        return isinstance(block, ParagraphBlock)

    def check(self, block: Block, ctx: Context) -> List[Issue]:
        if not self.check_english_quotes:
            return []
        
        if not isinstance(block, ParagraphBlock):
            return []

        p = block.paragraph
        text = (p.text or "").strip()
        
        # 跳过空段落
        if not text:
            return []

        # 检查段落样式是否在检查范围内
        style_name = (getattr(p.style, "name", "") or "").strip()
        should_check = any(check_style in style_name for check_style in self.check_styles)
        
        # 如果样式不匹配，但是不是标题、题注等特殊段落，也检查
        if not should_check:
            if not (ctx.is_heading(p) or ctx.is_caption(p)):
                should_check = True

        if not should_check:
            return []

        # 检查英文引号包围中文内容
        issues = []
        import re
        
        # 检查英文双引号包围的内容
        double_quote_pattern = r'"([^"]+)"'
        double_matches = list(re.finditer(double_quote_pattern, text))
        
        for match in double_matches:
            quoted_content = match.group(1)
            full_match = match.group(0)
            start_pos = match.start()
            
            # 检查引号内容是否主要是中文
            if self._is_mainly_chinese(quoted_content):
                issues.append(
                    Issue(
                        code=self.id,
                        severity=Severity.ERROR,
                        message=f"{self.name}: Chinese content should use Chinese quotes ("""), not English quotes (\"\"), found: {full_match}",
                        location=Location(
                            block_index=block.index,
                            kind="paragraph",
                            hint=text[:50]
                        ),
                        evidence={
                            "quoted_content": quoted_content,
                            "full_match": full_match,
                            "quote_type": "double",
                            "position": start_pos,
                            "suggested_replacement": f""{quoted_content}"",
                            "chinese_ratio": self._calculate_chinese_ratio(quoted_content)
                        }
                    )
                )

        # 检查英文单引号包围的内容
        single_quote_pattern = r"'([^']+)'"
        single_matches = list(re.finditer(single_quote_pattern, text))
        
        for match in single_matches:
            quoted_content = match.group(1)
            full_match = match.group(0)
            start_pos = match.start()
            
            # 检查引号内容是否主要是中文
            if self._is_mainly_chinese(quoted_content):
                issues.append(
                    Issue(
                        code=self.id,
                        severity=Severity.ERROR,
                        message=f"{self.name}: Chinese content should use Chinese quotes (''), not English quotes (''), found: {full_match}",
                        location=Location(
                            block_index=block.index,
                            kind="paragraph",
                            hint=text[:50]
                        ),
                        evidence={
                            "quoted_content": quoted_content,
                            "full_match": full_match,
                            "quote_type": "single",
                            "position": start_pos,
                            "suggested_replacement": f"'{quoted_content}'",
                            "chinese_ratio": self._calculate_chinese_ratio(quoted_content)
                        }
                    )
                )

        return issues

    def _is_mainly_chinese(self, text: str) -> bool:
        """判断文本是否主要是中文字符"""
        if not text.strip():
            return False
        
        chinese_ratio = self._calculate_chinese_ratio(text)
        return chinese_ratio >= self.min_chinese_ratio

    def _calculate_chinese_ratio(self, text: str) -> float:
        """计算文本中中文字符的占比"""
        if not text:
            return 0.0
        
        # 统计中文字符数量（包括中文标点）
        chinese_count = 0
        total_chars = len(text.strip())
        
        if total_chars == 0:
            return 0.0
        
        for char in text:
            # 中文字符范围
            if ('\u4e00' <= char <= '\u9fff' or  # CJK统一汉字
                '\u3000' <= char <= '\u303f' or  # CJK符号和标点
                '\uff00' <= char <= '\uffef'):   # 全角ASCII、全角标点
                chinese_count += 1
        
        return chinese_count / total_chars


@dataclass
class ChineseQuoteMatchingRule(Rule):
    id: str = "PAR006"
    name: str = "Paragraphs: Chinese quote matching"
    description: str = "中文引号应该左右匹配"
    check_quote_matching: bool = True
    check_styles: List[str] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.check_styles is None:
            self.check_styles = ["Normal", "正文", "List Paragraph", "列表段落"]

    def applies_to(self, block: Block, ctx: Context) -> bool:
        return isinstance(block, ParagraphBlock)

    def check(self, block: Block, ctx: Context) -> List[Issue]:
        if not self.check_quote_matching:
            return []
        
        if not isinstance(block, ParagraphBlock):
            return []

        p = block.paragraph
        text = (p.text or "").strip()
        
        # 跳过空段落
        if not text:
            return []

        # 检查段落样式是否在检查范围内
        style_name = (getattr(p.style, "name", "") or "").strip()
        should_check = any(check_style in style_name for check_style in self.check_styles)
        
        # 如果样式不匹配，但是不是标题、题注等特殊段落，也检查
        if not should_check:
            if not (ctx.is_heading(p) or ctx.is_caption(p)):
                should_check = True

        if not should_check:
            return []

        # 检查中文引号匹配
        issues = []
        
        # 定义中文引号对
        quote_pairs = [
            (""", """, "double"),  # 中文双引号
            ("'", "'", "single"),  # 中文单引号
        ]
        
        for left_quote, right_quote, quote_type in quote_pairs:
            quote_issues = self._check_quote_pair(text, left_quote, right_quote, quote_type, block.index)
            issues.extend(quote_issues)

        return issues

    def _check_quote_pair(self, text: str, left_quote: str, right_quote: str, quote_type: str, block_index: int) -> List[Issue]:
        """检查特定引号对的匹配情况"""
        issues = []
        
        # 统计左右引号的位置
        left_positions = []
        right_positions = []
        
        for i, char in enumerate(text):
            if char == left_quote:
                left_positions.append(i)
            elif char == right_quote:
                right_positions.append(i)
        
        # 检查引号数量匹配
        left_count = len(left_positions)
        right_count = len(right_positions)
        
        if left_count != right_count:
            severity = Severity.ERROR
            if left_count > right_count:
                missing_type = "right"
                missing_quote = right_quote
                message = f"{self.name}: unmatched {quote_type} quotes - missing {right_count - left_count} closing quote(s) '{right_quote}'"
            else:
                missing_type = "left"
                missing_quote = left_quote
                message = f"{self.name}: unmatched {quote_type} quotes - missing {left_count - right_count} opening quote(s) '{left_quote}'"
            
            issues.append(
                Issue(
                    code=self.id,
                    severity=severity,
                    message=message,
                    location=Location(
                        block_index=block_index,
                        kind="paragraph",
                        hint=text[:50]
                    ),
                    evidence={
                        "quote_type": quote_type,
                        "left_quote": left_quote,
                        "right_quote": right_quote,
                        "left_count": left_count,
                        "right_count": right_count,
                        "left_positions": left_positions,
                        "right_positions": right_positions,
                        "missing_type": missing_type,
                        "missing_quote": missing_quote
                    }
                )
            )
        
        # 检查引号顺序（如果数量匹配）
        if left_count == right_count and left_count > 0:
            order_issues = self._check_quote_order(text, left_positions, right_positions, 
                                                 left_quote, right_quote, quote_type, block_index)
            issues.extend(order_issues)
        
        return issues

    def _check_quote_order(self, text: str, left_positions: List[int], right_positions: List[int], 
                          left_quote: str, right_quote: str, quote_type: str, block_index: int) -> List[Issue]:
        """检查引号的顺序是否正确"""
        issues = []
        
        # 使用栈来检查引号匹配
        stack = []
        all_quotes = []
        
        # 收集所有引号及其位置和类型
        for pos in left_positions:
            all_quotes.append((pos, 'left', left_quote))
        for pos in right_positions:
            all_quotes.append((pos, 'right', right_quote))
        
        # 按位置排序
        all_quotes.sort(key=lambda x: x[0])
        
        for pos, quote_side, quote_char in all_quotes:
            if quote_side == 'left':
                stack.append((pos, quote_char))
            else:  # quote_side == 'right'
                if not stack:
                    # 右引号没有对应的左引号
                    issues.append(
                        Issue(
                            code=self.id,
                            severity=Severity.ERROR,
                            message=f"{self.name}: closing {quote_type} quote '{quote_char}' at position {pos} has no matching opening quote",
                            location=Location(
                                block_index=block_index,
                                kind="paragraph",
                                hint=text[:50]
                            ),
                            evidence={
                                "quote_type": quote_type,
                                "quote_char": quote_char,
                                "position": pos,
                                "context": text[max(0, pos-10):pos+10],
                                "issue_type": "unmatched_closing"
                            }
                        )
                    )
                else:
                    # 正常匹配，从栈中弹出
                    stack.pop()
        
        # 检查栈中剩余的左引号（没有匹配的右引号）
        for pos, quote_char in stack:
            issues.append(
                Issue(
                    code=self.id,
                    severity=Severity.ERROR,
                    message=f"{self.name}: opening {quote_type} quote '{quote_char}' at position {pos} has no matching closing quote",
                    location=Location(
                        block_index=block_index,
                        kind="paragraph",
                        hint=text[:50]
                    ),
                    evidence={
                        "quote_type": quote_type,
                        "quote_char": quote_char,
                        "position": pos,
                        "context": text[max(0, pos-10):pos+10],
                        "issue_type": "unmatched_opening"
                    }
                )
            )
        
        return issues


@dataclass
class ConsecutiveEmptyLinesRule(FinalizeRule):
    id: str = "PAR007"
    name: str = "Paragraphs: consecutive empty lines"
    description: str = "段落之间不要存在连续空行"
    check_consecutive_empty: bool = True
    max_consecutive_empty: int = 1  # 允许的最大连续空行数
    ignore_page_breaks: bool = True  # 是否忽略分页符附近的空行

    def applies_to(self, block: Block, ctx: Context) -> bool:
        return False  # 使用 finalize 方法检查整个文档

    def check(self, block: Block, ctx: Context) -> List[Issue]:
        return []

    def finalize(self, ctx: Context) -> List[Issue]:
        if not self.check_consecutive_empty:
            return []

        issues = []
        consecutive_empty_count = 0
        consecutive_empty_start = -1
        consecutive_empty_blocks = []

        for i, block in enumerate(ctx.blocks):
            if isinstance(block, ParagraphBlock):
                p = block.paragraph
                text = (p.text or "").strip()
                
                # 检查是否为空段落
                is_empty = not text
                
                # 检查是否包含分页符（如果启用忽略分页符选项）
                has_page_break = False
                if self.ignore_page_breaks:
                    # 检查段落是否包含分页符
                    for run in p.runs:
                        if run.element.xml and 'w:br' in run.element.xml:
                            # 检查是否为分页符
                            if 'type="page"' in run.element.xml or 'clear="all"' in run.element.xml:
                                has_page_break = True
                                break
                
                if is_empty and not has_page_break:
                    if consecutive_empty_count == 0:
                        consecutive_empty_start = i
                        consecutive_empty_blocks = []
                    consecutive_empty_count += 1
                    consecutive_empty_blocks.append(block)
                else:
                    # 检查是否超过允许的连续空行数
                    if consecutive_empty_count > self.max_consecutive_empty:
                        # 报告连续空行问题
                        excess_count = consecutive_empty_count - self.max_consecutive_empty
                        
                        # 找到多余空行的范围
                        start_block = consecutive_empty_blocks[self.max_consecutive_empty]
                        end_block = consecutive_empty_blocks[-1]
                        
                        issues.append(
                            Issue(
                                code=self.id,
                                severity=Severity.WARN,
                                message=f"{self.name}: found {consecutive_empty_count} consecutive empty paragraphs, maximum allowed is {self.max_consecutive_empty}",
                                location=Location(
                                    block_index=start_block.index,
                                    kind="empty_paragraphs",
                                    hint=f"empty paragraphs from block {start_block.index} to {end_block.index}"
                                ),
                                evidence={
                                    "consecutive_count": consecutive_empty_count,
                                    "max_allowed": self.max_consecutive_empty,
                                    "excess_count": excess_count,
                                    "start_block_index": start_block.index,
                                    "end_block_index": end_block.index,
                                    "empty_block_indices": [b.index for b in consecutive_empty_blocks]
                                }
                            )
                        )
                    
                    # 重置计数器
                    consecutive_empty_count = 0
                    consecutive_empty_start = -1
                    consecutive_empty_blocks = []
            
            elif isinstance(block, TableBlock):
                # 表格打断连续空行的计数
                if consecutive_empty_count > self.max_consecutive_empty:
                    excess_count = consecutive_empty_count - self.max_consecutive_empty
                    start_block = consecutive_empty_blocks[self.max_consecutive_empty]
                    end_block = consecutive_empty_blocks[-1]
                    
                    issues.append(
                        Issue(
                            code=self.id,
                            severity=Severity.WARN,
                            message=f"{self.name}: found {consecutive_empty_count} consecutive empty paragraphs before table, maximum allowed is {self.max_consecutive_empty}",
                            location=Location(
                                block_index=start_block.index,
                                kind="empty_paragraphs",
                                hint=f"empty paragraphs from block {start_block.index} to {end_block.index}"
                            ),
                            evidence={
                                "consecutive_count": consecutive_empty_count,
                                "max_allowed": self.max_consecutive_empty,
                                "excess_count": excess_count,
                                "start_block_index": start_block.index,
                                "end_block_index": end_block.index,
                                "empty_block_indices": [b.index for b in consecutive_empty_blocks],
                                "followed_by": "table"
                            }
                        )
                    )
                
                consecutive_empty_count = 0
                consecutive_empty_start = -1
                consecutive_empty_blocks = []

        # 检查文档末尾的连续空行
        if consecutive_empty_count > self.max_consecutive_empty:
            excess_count = consecutive_empty_count - self.max_consecutive_empty
            start_block = consecutive_empty_blocks[self.max_consecutive_empty]
            end_block = consecutive_empty_blocks[-1]
            
            issues.append(
                Issue(
                    code=self.id,
                    severity=Severity.WARN,
                    message=f"{self.name}: found {consecutive_empty_count} consecutive empty paragraphs at document end, maximum allowed is {self.max_consecutive_empty}",
                    location=Location(
                        block_index=start_block.index,
                        kind="empty_paragraphs",
                        hint=f"empty paragraphs from block {start_block.index} to {end_block.index}"
                    ),
                    evidence={
                        "consecutive_count": consecutive_empty_count,
                        "max_allowed": self.max_consecutive_empty,
                        "excess_count": excess_count,
                        "start_block_index": start_block.index,
                        "end_block_index": end_block.index,
                        "empty_block_indices": [b.index for b in consecutive_empty_blocks],
                        "location": "document_end"
                    }
                )
            )

        return issues


@dataclass
class HeadingNumberingRule(FinalizeRule):
    id: str = "HDG001"
    name: str = "Headings: numbering sequence"
    description: str = "各级标题的编号应该连续"
    check_heading_numbering: bool = True
    heading_styles: List[str] = None  # type: ignore[assignment]
    numbering_patterns: List[str] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.heading_styles is None:
            self.heading_styles = [
                "Heading 1", "Heading 2", "Heading 3", "Heading 4", "Heading 5", "Heading 6",
                "标题 1", "标题 2", "标题 3", "标题 4", "标题 5", "标题 6"
            ]
        if self.numbering_patterns is None:
            self.numbering_patterns = [
                r"^(\d+)\.",           # 1.
                r"^(\d+\.\d+)",        # 1.1
                r"^(\d+\.\d+\.\d+)",   # 1.1.1
                r"^(\d+\.\d+\.\d+\.\d+)"  # 1.1.1.1
            ]

    def applies_to(self, block: Block, ctx: Context) -> bool:
        return False  # 使用 finalize 方法检查整个文档

    def check(self, block: Block, ctx: Context) -> List[Issue]:
        return []

    def finalize(self, ctx: Context) -> List[Issue]:
        if not self.check_heading_numbering:
            return []

        issues = []
        headings = []

        # 收集所有标题
        for block in ctx.blocks:
            if isinstance(block, ParagraphBlock):
                p = block.paragraph
                if ctx.is_heading(p) or self._is_heading_style(p):
                    text = (p.text or "").strip()
                    if text:
                        level = self._get_heading_level(p)
                        numbering = self._extract_numbering(text)
                        headings.append({
                            "block": block,
                            "paragraph": p,
                            "text": text,
                            "level": level,
                            "numbering": numbering,
                            "style_name": (getattr(p.style, "name", "") or "").strip()
                        })

        if not headings:
            return []

        # 按层级检查编号连续性
        issues.extend(self._check_numbering_continuity(headings))
        
        return issues

    def _is_heading_style(self, paragraph) -> bool:
        """检查段落是否使用标题样式"""
        style_name = (getattr(paragraph.style, "name", "") or "").strip()
        return style_name in self.heading_styles

    def _get_heading_level(self, paragraph) -> int:
        """获取标题级别"""
        style_name = (getattr(paragraph.style, "name", "") or "").strip()
        
        # 从样式名提取级别
        import re
        match = re.search(r'(\d+)', style_name)
        if match:
            return int(match.group(1))
        
        # 默认返回1级标题
        return 1

    def _extract_numbering(self, text: str) -> Optional[str]:
        """从标题文本中提取编号"""
        import re
        
        for pattern in self.numbering_patterns:
            match = re.match(pattern, text.strip())
            if match:
                return match.group(1)
        
        return None

    def _check_numbering_continuity(self, headings: List[dict]) -> List[Issue]:
        """检查编号连续性"""
        issues = []
        
        # 按级别分组检查
        level_counters = {}  # {level: expected_next_number}
        level_sequences = {}  # {level: [actual_numbers]}
        
        for heading in headings:
            level = heading["level"]
            numbering = heading["numbering"]
            
            if numbering is None:
                # 标题没有编号，可能是合理的（如前言、附录等）
                continue
            
            # 解析编号
            number_parts = self._parse_numbering(numbering)
            if not number_parts:
                continue
            
            # 检查当前级别的编号
            current_level_number = number_parts[level - 1] if len(number_parts) >= level else None
            if current_level_number is None:
                continue
            
            # 初始化级别计数器
            if level not in level_counters:
                level_counters[level] = 1
                level_sequences[level] = []
            
            # 检查编号连续性
            expected = level_counters[level]
            actual = current_level_number
            
            level_sequences[level].append(actual)
            
            if actual != expected:
                # 检查是否是跳号
                if actual > expected:
                    issues.append(
                        Issue(
                            code=self.id,
                            severity=Severity.ERROR,
                            message=f"{self.name}: heading level {level} number jumped from {expected-1} to {actual}, expected {expected}",
                            location=Location(
                                block_index=heading["block"].index,
                                kind="heading",
                                hint=heading["text"][:50]
                            ),
                            evidence={
                                "heading_level": level,
                                "expected_number": expected,
                                "actual_number": actual,
                                "full_numbering": numbering,
                                "heading_text": heading["text"],
                                "style_name": heading["style_name"]
                            }
                        )
                    )
                elif actual < expected:
                    # 检查是否是重复编号
                    if actual in level_sequences[level][:-1]:  # 排除当前这个
                        issues.append(
                            Issue(
                                code=self.id,
                                severity=Severity.ERROR,
                                message=f"{self.name}: duplicate heading level {level} number {actual}",
                                location=Location(
                                    block_index=heading["block"].index,
                                    kind="heading",
                                    hint=heading["text"][:50]
                                ),
                                evidence={
                                    "heading_level": level,
                                    "duplicate_number": actual,
                                    "full_numbering": numbering,
                                    "heading_text": heading["text"],
                                    "style_name": heading["style_name"]
                                }
                            )
                        )
                    else:
                        # 编号回退，可能是合理的（如新章节开始）
                        # 重置计数器
                        level_counters[level] = actual + 1
                        # 重置下级计数器
                        for sub_level in range(level + 1, 7):  # 假设最多6级标题
                            if sub_level in level_counters:
                                level_counters[sub_level] = 1
                        continue
            
            # 更新计数器
            level_counters[level] = actual + 1
            
            # 重置下级标题计数器（当上级标题递增时）
            for sub_level in range(level + 1, 7):
                if sub_level in level_counters:
                    level_counters[sub_level] = 1

        return issues

    def _parse_numbering(self, numbering: str) -> List[int]:
        """解析编号字符串为数字列表"""
        if not numbering:
            return []
        
        # 移除末尾的点号
        clean_numbering = numbering.rstrip('.')
        
        # 按点号分割
        parts = clean_numbering.split('.')
        
        try:
            return [int(part) for part in parts if part.isdigit()]
        except ValueError:
            return []


@dataclass
class PlaceholderRule(FinalizeRule):
    id: str = "BASE_PLACEHOLDER"
    name: str = "Placeholder rule"
    description: str = ""
    enabled: bool = True
    emit_issue: bool = False
    severity: Severity = Severity.INFO
    message: str = "Rule is a placeholder"
    kind: str = "document"
    hint: str = "(document)"
    legacy_check: str = ""
    legacy_config: Dict[str, Any] = field(default_factory=dict)

    def applies_to(self, block: Block, ctx: Context) -> bool:
        return False

    def check(self, block: Block, ctx: Context) -> List[Issue]:
        return []

    def finalize(self, ctx: Context) -> List[Issue]:
        if not self.enabled or not self.emit_issue:
            return []
        return [
            Issue(
                code=self.id,
                severity=self.severity,
                message=f"{self.name}: {self.message}",
                location=Location(block_index=0, kind=self.kind, hint=self.hint),
            )
        ]


@dataclass
class CoverRule(FinalizeRule):
    id: str = "COV001"
    name: str = "Cover: presence"
    description: str = "Document must contain a cover page"
    required: bool = True
    legacy_check: str = "cover"
    legacy_config: Dict[str, Any] = field(default_factory=dict)

    def applies_to(self, block: Block, ctx: Context) -> bool:
        return False

    def check(self, block: Block, ctx: Context) -> List[Issue]:
        return []

    def finalize(self, ctx: Context) -> List[Issue]:
        if not self.required:
            return []

        # 检查是否存在封面：通过样式名或特定内容判断
        for b in ctx.blocks:
            if not isinstance(b, ParagraphBlock):
                continue
            p = b.paragraph
            style_name = (getattr(p.style, "name", "") or "").strip().lower()
            
            # 检查封面相关样式
            if any(cover_style in style_name for cover_style in ["cover", "封面", "title"]):
                return []
            
            # 检查是否包含封面相关文本（前几个段落）
            if b.index < 5:  # 只检查前5个段落
                text = (p.text or "").strip()
                if any(keyword in text for keyword in ["封面", "标题页", "题目", "作者", "单位"]):
                    return []

        return [
            Issue(
                code=self.id,
                severity=Severity.ERROR,
                message=f"{self.name}: Document must contain a cover page",
                location=Location(block_index=0, kind="document", hint="(document)"),
                evidence={"required": self.required},
            )
        ]


@dataclass
class FigureListRule(PlaceholderRule):
    id: str = "FIG001"


@dataclass
class FigureListPageContinuityRule(FinalizeRule):
    id: str = "FIG002"
    name: str = "Figure list: page continuity"
    description: str = "如果存在插图目录，页码必须连续"
    check_continuity: bool = True
    title_text: str = "插图目录"
    style_prefixes: List[str] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.style_prefixes is None:
            self.style_prefixes = ["图目录", "插图目录"]

    def applies_to(self, block: Block, ctx: Context) -> bool:
        return False

    def check(self, block: Block, ctx: Context) -> List[Issue]:
        return []

    def finalize(self, ctx: Context) -> List[Issue]:
        if not self.check_continuity:
            return []

        # 首先检查是否存在插图目录
        has_figure_list = False
        figure_list_start_index = -1
        
        for b in ctx.blocks:
            if not isinstance(b, ParagraphBlock):
                continue
            p = b.paragraph
            text = (p.text or "").strip()
            style_name = (getattr(p.style, "name", "") or "").strip()
            
            # 检查是否是插图目录标题
            if text == self.title_text or ctx.is_heading(p) and self.title_text in text:
                has_figure_list = True
                figure_list_start_index = b.index
                break
            
            # 检查样式名
            if any(pref in style_name for pref in self.style_prefixes):
                has_figure_list = True
                figure_list_start_index = b.index
                break

        # 如果不存在插图目录，则不检查
        if not has_figure_list:
            return []

        # 收集插图目录条目及其页码
        figure_entries = []
        in_figure_list = False
        
        for b in ctx.blocks:
            if not isinstance(b, ParagraphBlock):
                continue
            p = b.paragraph
            text = (p.text or "").strip()
            style_name = (getattr(p.style, "name", "") or "").strip()
            
            # 判断是否进入插图目录区域
            if b.index >= figure_list_start_index:
                if text == self.title_text or any(pref in style_name for pref in self.style_prefixes):
                    in_figure_list = True
                    continue
                
                # 遇到其他标题时退出插图目录区域
                if ctx.is_heading(p) and self.title_text not in text:
                    break
                
                if in_figure_list and text:
                    # 提取页码（假设格式为 "图X-X 标题...页码" 或包含制表符分隔）
                    import re
                    # 匹配行末的数字（页码）
                    match = re.search(r'(\d+)\s*$', text)
                    if match:
                        page_num = int(match.group(1))
                        # 检查是否是图的条目（包含"图"字）
                        if '图' in text or re.match(r'^图\s*\d+', text):
                            figure_entries.append({
                                'block_index': b.index,
                                'text': text,
                                'page_num': page_num
                            })

        if len(figure_entries) < 2:
            return []  # 少于2个条目无法检查连续性

        # 按页码排序
        figure_entries.sort(key=lambda x: x['page_num'])
        
        issues = []
        for i in range(1, len(figure_entries)):
            prev_page = figure_entries[i-1]['page_num']
            curr_page = figure_entries[i]['page_num']
            
            # 检查页码是否连续
            if curr_page < prev_page:
                issues.append(
                    Issue(
                        code=self.id,
                        severity=Severity.ERROR,
                        message=f"{self.name}: page numbers not in order: {prev_page} -> {curr_page}",
                        location=Location(
                            block_index=figure_entries[i]['block_index'],
                            kind="paragraph",
                            hint=figure_entries[i]['text'][:50]
                        ),
                        evidence={
                            "prev_page": prev_page,
                            "curr_page": curr_page
                        }
                    )
                )
            elif curr_page > prev_page + 1:
                # 页码跳跃
                issues.append(
                    Issue(
                        code=self.id,
                        severity=Severity.WARN,
                        message=f"{self.name}: page numbers have gap: {prev_page} -> {curr_page}",
                        location=Location(
                            block_index=figure_entries[i]['block_index'],
                            kind="paragraph", 
                            hint=figure_entries[i]['text'][:50]
                        ),
                        evidence={
                            "prev_page": prev_page,
                            "curr_page": curr_page,
                            "gap": curr_page - prev_page
                        }
                    )
                )

        return issues


@dataclass
class TableListRule(PlaceholderRule):
    id: str = "TBL001"


@dataclass
class TableListPageAccuracyRule(FinalizeRule):
    id: str = "TBL003"
    name: str = "Table list: page accuracy"
    description: str = "附表目录的页码必须和实际情况一致"
    check_page_accuracy: bool = True
    title_text: str = "附表目录"
    style_prefixes: List[str] = None  # type: ignore[assignment]
    caption_styles: List[str] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.style_prefixes is None:
            self.style_prefixes = ["表目录", "附表目录"]
        if self.caption_styles is None:
            self.caption_styles = ["Caption", "题注", "表题"]

    def applies_to(self, block: Block, ctx: Context) -> bool:
        return False

    def check(self, block: Block, ctx: Context) -> List[Issue]:
        return []

    def finalize(self, ctx: Context) -> List[Issue]:
        if not self.check_page_accuracy:
            return []

        # 首先检查是否存在附表目录
        has_table_list = False
        table_list_start_index = -1
        
        for b in ctx.blocks:
            if not isinstance(b, ParagraphBlock):
                continue
            p = b.paragraph
            text = (p.text or "").strip()
            style_name = (getattr(p.style, "name", "") or "").strip()
            
            # 检查是否是附表目录标题
            if text == self.title_text or ctx.is_heading(p) and self.title_text in text:
                has_table_list = True
                table_list_start_index = b.index
                break
            
            # 检查样式名
            if any(pref in style_name for pref in self.style_prefixes):
                has_table_list = True
                table_list_start_index = b.index
                break

        # 如果不存在附表目录，则不检查
        if not has_table_list:
            return []

        # 收集附表目录条目
        table_list_entries = []
        in_table_list = False
        
        for b in ctx.blocks:
            if not isinstance(b, ParagraphBlock):
                continue
            p = b.paragraph
            text = (p.text or "").strip()
            style_name = (getattr(p.style, "name", "") or "").strip()
            
            # 判断是否进入附表目录区域
            if b.index >= table_list_start_index:
                if text == self.title_text or any(pref in style_name for pref in self.style_prefixes):
                    in_table_list = True
                    continue
                
                # 遇到其他标题时退出附表目录区域
                if ctx.is_heading(p) and self.title_text not in text:
                    break
                
                if in_table_list and text:
                    # 提取表格标题和页码
                    import re
                    # 匹配行末的数字（页码）
                    page_match = re.search(r'(\d+)\s*$', text)
                    if page_match:
                        page_num = int(page_match.group(1))
                        # 提取表格标题（去掉页码部分）
                        table_title = re.sub(r'\s*\d+\s*$', '', text).strip()
                        # 去掉可能的制表符、点号等
                        table_title = re.sub(r'[.\t\s]+$', '', table_title).strip()
                        
                        # 检查是否是表的条目（包含"表"字或以"表"开头）
                        if '表' in table_title or re.match(r'^表\s*\d+', table_title):
                            table_list_entries.append({
                                'block_index': b.index,
                                'title': table_title,
                                'list_page': page_num,
                                'original_text': text
                            })

        if not table_list_entries:
            return []

        # 收集文档中的实际表格题注
        actual_tables = []
        for b in ctx.blocks:
            if not isinstance(b, ParagraphBlock):
                continue
            p = b.paragraph
            text = (p.text or "").strip()
            style_name = (getattr(p.style, "name", "") or "").strip()
            
            # 检查是否是表格题注
            is_caption = (ctx.is_caption(p) or 
                         any(style in style_name for style in self.caption_styles) or
                         re.match(r'^表\s*\d+', text))
            
            if is_caption and text and '表' in text:
                # 清理表格标题进行匹配
                clean_title = text.strip()
                # 去掉可能的编号格式变化
                clean_title = re.sub(r'^表\s*(\d+[-.]?\d*)\s*[：:]\s*', '表\\1 ', clean_title)
                
                if clean_title:
                    actual_tables.append({
                        'block_index': b.index,
                        'title': clean_title,
                        'original_text': text,
                        'actual_page': self._estimate_page_number(b.index, ctx)
                    })

        # 比较附表目录条目与实际表格
        issues = []
        for list_entry in table_list_entries:
            list_title = list_entry['title']
            list_page = list_entry['list_page']
            
            # 查找匹配的实际表格
            best_match = None
            best_similarity = 0
            
            for table in actual_tables:
                # 计算标题相似度
                similarity = self._calculate_table_similarity(list_title, table['title'])
                if similarity > best_similarity and similarity > 0.6:  # 表格标题相似度阈值
                    best_similarity = similarity
                    best_match = table
            
            if best_match:
                actual_page = best_match['actual_page']
                if abs(list_page - actual_page) > 1:  # 允许1页的误差
                    issues.append(
                        Issue(
                            code=self.id,
                            severity=Severity.ERROR,
                            message=f"{self.name}: page mismatch for '{list_title}': Table list shows {list_page}, actual ~{actual_page}",
                            location=Location(
                                block_index=list_entry['block_index'],
                                kind="paragraph",
                                hint=list_entry['original_text'][:50]
                            ),
                            evidence={
                                "list_title": list_title,
                                "list_page": list_page,
                                "actual_page": actual_page,
                                "actual_title": best_match['title']
                            }
                        )
                    )
            else:
                # 附表目录中的表格在文档中找不到对应项
                issues.append(
                    Issue(
                        code=self.id,
                        severity=Severity.WARN,
                        message=f"{self.name}: Table list entry '{list_title}' not found in document captions",
                        location=Location(
                            block_index=list_entry['block_index'],
                            kind="paragraph",
                            hint=list_entry['original_text'][:50]
                        ),
                        evidence={
                            "list_title": list_title,
                            "list_page": list_page
                        }
                    )
                )

        return issues

    def _estimate_page_number(self, block_index: int, ctx: Context) -> int:
        """估算段落所在页码（简单估算：假设每页约25个段落）"""
        return max(1, block_index // 25 + 1)

    def _calculate_table_similarity(self, text1: str, text2: str) -> float:
        """计算两个表格标题的相似度"""
        if not text1 or not text2:
            return 0.0
        
        import re
        # 提取表格编号进行比较
        num1_match = re.search(r'表\s*(\d+[-.]?\d*)', text1)
        num2_match = re.search(r'表\s*(\d+[-.]?\d*)', text2)
        
        if num1_match and num2_match:
            num1 = num1_match.group(1)
            num2 = num2_match.group(1)
            if num1 == num2:
                return 0.9  # 表格编号相同，高相似度
        
        # 去掉表格编号后比较标题内容
        clean1 = re.sub(r'^表\s*\d+[-.]?\d*\s*[：:]\s*', '', text1).strip()
        clean2 = re.sub(r'^表\s*\d+[-.]?\d*\s*[：:]\s*', '', text2).strip()
        
        if not clean1 or not clean2:
            return 0.3 if num1_match and num2_match else 0.0
        
        # 去掉空格和标点符号进行比较
        clean1 = re.sub(r'[^\w\u4e00-\u9fff]', '', clean1.lower())
        clean2 = re.sub(r'[^\w\u4e00-\u9fff]', '', clean2.lower())
        
        if clean1 == clean2:
            return 1.0
        
        # 简单的包含关系检查
        if clean1 in clean2 or clean2 in clean1:
            return 0.7
        
        # 计算字符重叠度
        set1 = set(clean1)
        set2 = set(clean2)
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        
        return intersection / union if union > 0 else 0.0


@dataclass
class ParagraphsRule(PlaceholderRule):
    id: str = "PAR001"


@dataclass
class HeadingsRule(PlaceholderRule):
    id: str = "HDG001"


@dataclass
class CaptionsRule(PlaceholderRule):
    id: str = "CAP001"


@dataclass
class AttachmentsRule(PlaceholderRule):
    id: str = "ATT001"


@dataclass
class HeadersRule(PlaceholderRule):
    id: str = "HDR001"


@dataclass
class FootersRule(PlaceholderRule):
    id: str = "FTR001"


@dataclass
class TocPageContinuityRule(FinalizeRule):
    id: str = "TOC002"
    name: str = "TOC: page continuity"
    description: str = "目录页码必须连续"
    check_continuity: bool = True
    style_prefixes: List[str] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.style_prefixes is None:
            self.style_prefixes = ["TOC"]

    def applies_to(self, block: Block, ctx: Context) -> bool:
        return False

    def check(self, block: Block, ctx: Context) -> List[Issue]:
        return []

    def finalize(self, ctx: Context) -> List[Issue]:
        if not self.check_continuity:
            return []

        # 收集所有目录条目及其页码
        toc_entries = []
        for b in ctx.blocks:
            if not isinstance(b, ParagraphBlock):
                continue
            p = b.paragraph
            style_name = (getattr(p.style, "name", "") or "").strip()
            
            # 检查是否是目录样式
            is_toc = any(pref and style_name.startswith(pref) for pref in self.style_prefixes)
            if not is_toc:
                continue
                
            text = (p.text or "").strip()
            if not text:
                continue
                
            # 提取页码（假设格式为 "标题...页码" 或 "标题\t页码"）
            import re
            # 匹配行末的数字（页码）
            match = re.search(r'(\d+)\s*$', text)
            if match:
                page_num = int(match.group(1))
                toc_entries.append({
                    'block_index': b.index,
                    'text': text,
                    'page_num': page_num
                })

        if len(toc_entries) < 2:
            return []  # 少于2个条目无法检查连续性

        # 按页码排序
        toc_entries.sort(key=lambda x: x['page_num'])
        
        issues = []
        for i in range(1, len(toc_entries)):
            prev_page = toc_entries[i-1]['page_num']
            curr_page = toc_entries[i]['page_num']
            
            # 检查页码是否连续（允许相同页码，但不允许跳跃）
            if curr_page < prev_page:
                issues.append(
                    Issue(
                        code=self.id,
                        severity=Severity.ERROR,
                        message=f"{self.name}: page numbers not in order: {prev_page} -> {curr_page}",
                        location=Location(
                            block_index=toc_entries[i]['block_index'],
                            kind="paragraph",
                            hint=toc_entries[i]['text'][:50]
                        ),
                        evidence={
                            "prev_page": prev_page,
                            "curr_page": curr_page
                        }
                    )
                )
            elif curr_page > prev_page + 1:
                # 页码跳跃（允许差1或相等，不允许跳跃超过1）
                issues.append(
                    Issue(
                        code=self.id,
                        severity=Severity.WARN,
                        message=f"{self.name}: page numbers have gap: {prev_page} -> {curr_page}",
                        location=Location(
                            block_index=toc_entries[i]['block_index'],
                            kind="paragraph", 
                            hint=toc_entries[i]['text'][:50]
                        ),
                        evidence={
                            "prev_page": prev_page,
                            "curr_page": curr_page,
                            "gap": curr_page - prev_page
                        }
                    )
                )

        return issues


@dataclass
class FigureListPageAccuracyRule(FinalizeRule):
    id: str = "FIG003"
    name: str = "Figure list: page accuracy"
    description: str = "插图目录中各个图片的页码必须和实际情况一致"
    check_page_accuracy: bool = True
    title_text: str = "插图目录"
    style_prefixes: List[str] = None  # type: ignore[assignment]
    caption_styles: List[str] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.style_prefixes is None:
            self.style_prefixes = ["图目录", "插图目录"]
        if self.caption_styles is None:
            self.caption_styles = ["Caption", "题注", "图题"]

    def applies_to(self, block: Block, ctx: Context) -> bool:
        return False

    def check(self, block: Block, ctx: Context) -> List[Issue]:
        return []

    def finalize(self, ctx: Context) -> List[Issue]:
        if not self.check_page_accuracy:
            return []

        # 首先检查是否存在插图目录
        has_figure_list = False
        figure_list_start_index = -1
        
        for b in ctx.blocks:
            if not isinstance(b, ParagraphBlock):
                continue
            p = b.paragraph
            text = (p.text or "").strip()
            style_name = (getattr(p.style, "name", "") or "").strip()
            
            # 检查是否是插图目录标题
            if text == self.title_text or ctx.is_heading(p) and self.title_text in text:
                has_figure_list = True
                figure_list_start_index = b.index
                break
            
            # 检查样式名
            if any(pref in style_name for pref in self.style_prefixes):
                has_figure_list = True
                figure_list_start_index = b.index
                break

        # 如果不存在插图目录，则不检查
        if not has_figure_list:
            return []

        # 收集插图目录条目
        figure_list_entries = []
        in_figure_list = False
        
        for b in ctx.blocks:
            if not isinstance(b, ParagraphBlock):
                continue
            p = b.paragraph
            text = (p.text or "").strip()
            style_name = (getattr(p.style, "name", "") or "").strip()
            
            # 判断是否进入插图目录区域
            if b.index >= figure_list_start_index:
                if text == self.title_text or any(pref in style_name for pref in self.style_prefixes):
                    in_figure_list = True
                    continue
                
                # 遇到其他标题时退出插图目录区域
                if ctx.is_heading(p) and self.title_text not in text:
                    break
                
                if in_figure_list and text:
                    # 提取图片标题和页码
                    import re
                    # 匹配行末的数字（页码）
                    page_match = re.search(r'(\d+)\s*$', text)
                    if page_match:
                        page_num = int(page_match.group(1))
                        # 提取图片标题（去掉页码部分）
                        figure_title = re.sub(r'\s*\d+\s*$', '', text).strip()
                        # 去掉可能的制表符、点号等
                        figure_title = re.sub(r'[.\t\s]+$', '', figure_title).strip()
                        
                        # 检查是否是图的条目（包含"图"字或以"图"开头）
                        if '图' in figure_title or re.match(r'^图\s*\d+', figure_title):
                            figure_list_entries.append({
                                'block_index': b.index,
                                'title': figure_title,
                                'list_page': page_num,
                                'original_text': text
                            })

        if not figure_list_entries:
            return []

        # 收集文档中的实际图片题注
        actual_figures = []
        for b in ctx.blocks:
            if not isinstance(b, ParagraphBlock):
                continue
            p = b.paragraph
            text = (p.text or "").strip()
            style_name = (getattr(p.style, "name", "") or "").strip()
            
            # 检查是否是图片题注
            is_caption = (ctx.is_caption(p) or 
                         any(style in style_name for style in self.caption_styles) or
                         re.match(r'^图\s*\d+', text))
            
            if is_caption and text and '图' in text:
                # 清理图片标题进行匹配
                clean_title = text.strip()
                # 去掉可能的编号格式变化
                clean_title = re.sub(r'^图\s*(\d+[-.]?\d*)\s*[：:]\s*', '图\\1 ', clean_title)
                
                if clean_title:
                    actual_figures.append({
                        'block_index': b.index,
                        'title': clean_title,
                        'original_text': text,
                        'actual_page': self._estimate_page_number(b.index, ctx)
                    })

        # 比较插图目录条目与实际图片
        issues = []
        for list_entry in figure_list_entries:
            list_title = list_entry['title']
            list_page = list_entry['list_page']
            
            # 查找匹配的实际图片
            best_match = None
            best_similarity = 0
            
            for figure in actual_figures:
                # 计算标题相似度
                similarity = self._calculate_figure_similarity(list_title, figure['title'])
                if similarity > best_similarity and similarity > 0.6:  # 图片标题相似度阈值稍低
                    best_similarity = similarity
                    best_match = figure
            
            if best_match:
                actual_page = best_match['actual_page']
                if abs(list_page - actual_page) > 1:  # 允许1页的误差
                    issues.append(
                        Issue(
                            code=self.id,
                            severity=Severity.ERROR,
                            message=f"{self.name}: page mismatch for '{list_title}': Figure list shows {list_page}, actual ~{actual_page}",
                            location=Location(
                                block_index=list_entry['block_index'],
                                kind="paragraph",
                                hint=list_entry['original_text'][:50]
                            ),
                            evidence={
                                "list_title": list_title,
                                "list_page": list_page,
                                "actual_page": actual_page,
                                "actual_title": best_match['title']
                            }
                        )
                    )
            else:
                # 插图目录中的图片在文档中找不到对应项
                issues.append(
                    Issue(
                        code=self.id,
                        severity=Severity.WARN,
                        message=f"{self.name}: Figure list entry '{list_title}' not found in document captions",
                        location=Location(
                            block_index=list_entry['block_index'],
                            kind="paragraph",
                            hint=list_entry['original_text'][:50]
                        ),
                        evidence={
                            "list_title": list_title,
                            "list_page": list_page
                        }
                    )
                )

        return issues

    def _estimate_page_number(self, block_index: int, ctx: Context) -> int:
        """估算段落所在页码（简单估算：假设每页约25个段落）"""
        return max(1, block_index // 25 + 1)

    def _calculate_figure_similarity(self, text1: str, text2: str) -> float:
        """计算两个图片标题的相似度"""
        if not text1 or not text2:
            return 0.0
        
        import re
        # 提取图片编号进行比较
        num1_match = re.search(r'图\s*(\d+[-.]?\d*)', text1)
        num2_match = re.search(r'图\s*(\d+[-.]?\d*)', text2)
        
        if num1_match and num2_match:
            num1 = num1_match.group(1)
            num2 = num2_match.group(1)
            if num1 == num2:
                return 0.9  # 图片编号相同，高相似度
        
        # 去掉图片编号后比较标题内容
        clean1 = re.sub(r'^图\s*\d+[-.]?\d*\s*[：:]\s*', '', text1).strip()
        clean2 = re.sub(r'^图\s*\d+[-.]?\d*\s*[：:]\s*', '', text2).strip()
        
        if not clean1 or not clean2:
            return 0.3 if num1_match and num2_match else 0.0
        
        # 去掉空格和标点符号进行比较
        clean1 = re.sub(r'[^\w\u4e00-\u9fff]', '', clean1.lower())
        clean2 = re.sub(r'[^\w\u4e00-\u9fff]', '', clean2.lower())
        
        if clean1 == clean2:
            return 1.0
        
        # 简单的包含关系检查
        if clean1 in clean2 or clean2 in clean1:
            return 0.7
        
        # 计算字符重叠度
        set1 = set(clean1)
        set2 = set(clean2)
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        
        return intersection / union if union > 0 else 0.0


@dataclass
class TocPageAccuracyRule(FinalizeRule):
    id: str = "TOC003"
    name: str = "TOC: page accuracy"
    description: str = "目录中各级 toc 的页码必须与实际情况一致"
    check_page_accuracy: bool = True
    style_prefixes: List[str] = None  # type: ignore[assignment]
    heading_styles: List[str] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.style_prefixes is None:
            self.style_prefixes = ["TOC"]
        if self.heading_styles is None:
            self.heading_styles = ["Heading 1", "Heading 2", "Heading 3", "标题 1", "标题 2", "标题 3"]

    def applies_to(self, block: Block, ctx: Context) -> bool:
        return False

    def check(self, block: Block, ctx: Context) -> List[Issue]:
        return []

    def finalize(self, ctx: Context) -> List[Issue]:
        if not self.check_page_accuracy:
            return []

        # 收集目录条目
        toc_entries = []
        for b in ctx.blocks:
            if not isinstance(b, ParagraphBlock):
                continue
            p = b.paragraph
            style_name = (getattr(p.style, "name", "") or "").strip()
            
            # 检查是否是目录样式
            is_toc = any(pref and style_name.startswith(pref) for pref in self.style_prefixes)
            if not is_toc:
                continue
                
            text = (p.text or "").strip()
            if not text:
                continue
                
            # 提取标题文本和页码
            import re
            # 匹配行末的数字（页码）
            page_match = re.search(r'(\d+)\s*$', text)
            if page_match:
                page_num = int(page_match.group(1))
                # 提取标题文本（去掉页码部分）
                title_text = re.sub(r'\s*\d+\s*$', '', text).strip()
                # 去掉可能的制表符、点号等
                title_text = re.sub(r'[.\t\s]+$', '', title_text).strip()
                
                if title_text:
                    toc_entries.append({
                        'block_index': b.index,
                        'title': title_text,
                        'toc_page': page_num,
                        'original_text': text
                    })

        if not toc_entries:
            return []

        # 收集文档中的实际标题及其页码
        actual_headings = []
        for b in ctx.blocks:
            if not isinstance(b, ParagraphBlock):
                continue
            p = b.paragraph
            style_name = (getattr(p.style, "name", "") or "").strip()
            
            # 检查是否是标题样式
            is_heading = any(style in style_name for style in self.heading_styles) or ctx.is_heading(p)
            if not is_heading:
                continue
                
            text = (p.text or "").strip()
            if not text:
                continue
                
            # 简化标题文本进行匹配（去掉编号等）
            clean_title = re.sub(r'^\d+(\.\d+)*\s*', '', text).strip()  # 去掉章节编号
            clean_title = re.sub(r'^[第一二三四五六七八九十]+[章节部分]\s*', '', clean_title).strip()  # 去掉中文编号
            
            if clean_title:
                actual_headings.append({
                    'block_index': b.index,
                    'title': clean_title,
                    'original_text': text,
                    'actual_page': self._estimate_page_number(b.index, ctx)  # 估算页码
                })

        # 比较目录条目与实际标题
        issues = []
        for toc_entry in toc_entries:
            toc_title = toc_entry['title']
            toc_page = toc_entry['toc_page']
            
            # 查找匹配的实际标题
            best_match = None
            best_similarity = 0
            
            for heading in actual_headings:
                # 计算标题相似度
                similarity = self._calculate_similarity(toc_title, heading['title'])
                if similarity > best_similarity and similarity > 0.7:  # 相似度阈值
                    best_similarity = similarity
                    best_match = heading
            
            if best_match:
                actual_page = best_match['actual_page']
                if abs(toc_page - actual_page) > 1:  # 允许1页的误差
                    issues.append(
                        Issue(
                            code=self.id,
                            severity=Severity.ERROR,
                            message=f"{self.name}: page mismatch for '{toc_title}': TOC shows {toc_page}, actual ~{actual_page}",
                            location=Location(
                                block_index=toc_entry['block_index'],
                                kind="paragraph",
                                hint=toc_entry['original_text'][:50]
                            ),
                            evidence={
                                "toc_title": toc_title,
                                "toc_page": toc_page,
                                "actual_page": actual_page,
                                "actual_title": best_match['title']
                            }
                        )
                    )
            else:
                # 目录中的标题在文档中找不到对应项
                issues.append(
                    Issue(
                        code=self.id,
                        severity=Severity.WARN,
                        message=f"{self.name}: TOC entry '{toc_title}' not found in document headings",
                        location=Location(
                            block_index=toc_entry['block_index'],
                            kind="paragraph",
                            hint=toc_entry['original_text'][:50]
                        ),
                        evidence={
                            "toc_title": toc_title,
                            "toc_page": toc_page
                        }
                    )
                )

        return issues

    def _estimate_page_number(self, block_index: int, ctx: Context) -> int:
        """估算段落所在页码（简单估算：假设每页约25个段落）"""
        return max(1, block_index // 25 + 1)

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """计算两个文本的相似度（简单的字符匹配）"""
        if not text1 or not text2:
            return 0.0
        
        # 去掉空格和标点符号进行比较
        import re
        clean1 = re.sub(r'[^\w\u4e00-\u9fff]', '', text1.lower())
        clean2 = re.sub(r'[^\w\u4e00-\u9fff]', '', text2.lower())
        
        if not clean1 or not clean2:
            return 0.0
        
        # 计算最长公共子序列的比例
        if clean1 == clean2:
            return 1.0
        
        # 简单的包含关系检查
        if clean1 in clean2 or clean2 in clean1:
            return 0.8
        
        # 计算字符重叠度
        set1 = set(clean1)
        set2 = set(clean2)
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        
        return intersection / union if union > 0 else 0.0


@dataclass
class PageNumbersRule(PlaceholderRule):
    id: str = "PGN001"

