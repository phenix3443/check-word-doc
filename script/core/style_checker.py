"""样式检查器

根据 class 定义的样式规则检查文档元素的格式。
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from docx.enum.text import WD_ALIGN_PARAGRAPH

from script.core.model import Block, Issue, Location, ParagraphBlock, Severity
from script.utils.unit_converter import UnitConverter


class StyleChecker:
    """样式检查器
    
    根据 styles 配置检查元素的实际样式是否符合要求。
    
    工作流程：
    1. 遍历所有带 class 的元素
    2. 查找每个 class 对应的样式定义
    3. 检查元素的实际格式
    4. 生成 Issue 报告
    
    支持自定义扩展：
    - 可以通过 register_alignment_alias() 添加自定义对齐方式别名
    
    Examples:
        >>> styles = {
        ...     '.title': {
        ...         'font': {'name_eastasia': '黑体', 'size': '三号'},
        ...         'paragraph': {'alignment': '居中'}
        ...     }
        ... }
        >>> checker = StyleChecker(styles)
        >>> issues = checker.check(blocks)
    """
    
    # 对齐方式映射（中英文）
    # 将配置文件中的对齐方式名称映射到 python-docx 的枚举值
    # 支持中英文双语以提高配置文件的易用性
    # 可以通过 register_alignment_alias() 方法扩展
    ALIGNMENT_MAP = {
        '居中': WD_ALIGN_PARAGRAPH.CENTER,
        'CENTER': WD_ALIGN_PARAGRAPH.CENTER,
        '左对齐': WD_ALIGN_PARAGRAPH.LEFT,
        'LEFT': WD_ALIGN_PARAGRAPH.LEFT,
        '右对齐': WD_ALIGN_PARAGRAPH.RIGHT,
        'RIGHT': WD_ALIGN_PARAGRAPH.RIGHT,
        '两端对齐': WD_ALIGN_PARAGRAPH.JUSTIFY,
        'JUSTIFY': WD_ALIGN_PARAGRAPH.JUSTIFY,
        '分散对齐': WD_ALIGN_PARAGRAPH.DISTRIBUTE,
        'DISTRIBUTE': WD_ALIGN_PARAGRAPH.DISTRIBUTE,
    }

    def __init__(
        self,
        styles: Dict[str, Any],
        defaults: Optional[Dict[str, Any]] = None
    ):
        """
        Args:
            styles: styles 配置（如 {'.title': {font: {...}, paragraph: {...}}}）
            defaults: 全局默认样式（可选）
        """
        self.styles = styles
        self.defaults = defaults or {}
    
    @classmethod
    def register_alignment_alias(cls, alias: str, alignment: WD_ALIGN_PARAGRAPH):
        """注册自定义对齐方式别名
        
        Args:
            alias: 对齐方式别名，如 "中央揃え"（日语）
            alignment: python-docx 的对齐方式枚举值
            
        Examples:
            >>> StyleChecker.register_alignment_alias("中央揃え", WD_ALIGN_PARAGRAPH.CENTER)
        """
        cls.ALIGNMENT_MAP[alias] = alignment

    def check(self, blocks: List[Block]) -> List[Issue]:
        """检查所有元素的样式
        
        Args:
            blocks: 已标注 class 的元素列表
            
        Returns:
            Issue 列表
        """
        issues = []
        for block in blocks:
            issues.extend(self._check_block(block))
        return issues

    def _check_block(self, block: Block) -> List[Issue]:
        """检查单个元素的样式"""
        issues = []
        
        # 检查每个 class 对应的样式
        for class_name in block.classes:
            style_def = self.styles.get(f'.{class_name}')
            if style_def:
                issues.extend(
                    self._check_style(block, style_def, class_name)
                )
        
        return issues

    def _check_style(
        self,
        block: Block,
        style_def: Dict[str, Any],
        class_name: str
    ) -> List[Issue]:
        """根据样式定义检查元素"""
        issues = []
        
        # 只支持段落样式检查（表格暂不支持）
        if not isinstance(block, ParagraphBlock):
            return issues
        
        # 检查字体
        if 'font' in style_def:
            issues.extend(
                self._check_font(block, style_def['font'], class_name)
            )
        
        # 检查段落格式
        if 'paragraph' in style_def:
            issues.extend(
                self._check_paragraph(block, style_def['paragraph'], class_name)
            )
        
        return issues

    def _check_font(
        self,
        block: ParagraphBlock,
        font_def: Dict[str, Any],
        class_name: str
    ) -> List[Issue]:
        """检查字体样式"""
        issues = []
        paragraph = block.paragraph
        
        # 检查段落中的第一个 run（如果有的话）
        # 注意：Word 段落可能有多个 run，这里简化为检查第一个
        if not paragraph.runs:
            return issues
        
        run = paragraph.runs[0]
        font = run.font
        
        # 检查中文字体
        if 'name_eastasia' in font_def:
            expected_font = font_def['name_eastasia']
            actual_font = font.name
            
            # 尝试获取东亚字体名称
            try:
                if hasattr(font.element, 'rPr') and font.element.rPr is not None:
                    if hasattr(font.element.rPr, 'rFonts') and font.element.rPr.rFonts is not None:
                        # rFonts 是 XML 元素，使用 get() 方法获取属性
                        rfonts = font.element.rPr.rFonts
                        # eastAsia 属性在 XML 中是 {namespace}eastAsia
                        eastasia = rfonts.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}eastAsia')
                        if eastasia:
                            actual_font = eastasia
            except Exception:
                pass
            
            if actual_font and actual_font != expected_font:
                issues.append(Issue(
                    code=f'STYLE-FONT-NAME-{class_name.upper()}',
                    severity=Severity.ERROR,
                    message=f'.{class_name} 中文字体应为 {expected_font}，实际为 {actual_font}',
                    location=Location(
                        block_index=block.index,
                        kind='paragraph',
                        hint=paragraph.text[:50] if paragraph.text else ''
                    ),
                    evidence={
                        'expected': expected_font,
                        'actual': actual_font,
                        'class': class_name
                    }
                ))
        
        # 检查西文字体
        if 'name_ascii' in font_def:
            expected_font = font_def['name_ascii']
            actual_font = font.name
            
            # 尝试获取 ASCII 字体名称
            try:
                if hasattr(font.element, 'rPr') and font.element.rPr is not None:
                    if hasattr(font.element.rPr, 'rFonts') and font.element.rPr.rFonts is not None:
                        rfonts = font.element.rPr.rFonts
                        ascii_font = rfonts.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}ascii')
                        if ascii_font:
                            actual_font = ascii_font
            except Exception:
                pass
            
            if actual_font and actual_font != expected_font:
                issues.append(Issue(
                    code=f'STYLE-FONT-NAME-ASCII-{class_name.upper()}',
                    severity=Severity.ERROR,
                    message=f'.{class_name} 西文字体应为 {expected_font}，实际为 {actual_font}',
                    location=Location(
                        block_index=block.index,
                        kind='paragraph',
                        hint=paragraph.text[:50] if paragraph.text else ''
                    ),
                    evidence={
                        'expected': expected_font,
                        'actual': actual_font,
                        'class': class_name
                    }
                ))
        
        # 检查字号
        if 'size' in font_def:
            expected_size = font_def['size']
            # 转换为 half-points
            expected_half_pt = UnitConverter.parse_font_size(expected_size)
            
            if expected_half_pt and font.size:
                # font.size 是 EMU (English Metric Units)
                # 1 point = 12700 EMU
                # half-point = 12700 / 2 EMU
                actual_half_pt = font.size.pt * 2 if hasattr(font.size, 'pt') else None
                
                # 转换 EMU 到 half-points
                if font.size:
                    actual_half_pt = round(font.size * 2 / 12700)
                
                if actual_half_pt and abs(actual_half_pt - expected_half_pt) > 0.5:
                    issues.append(Issue(
                        code=f'STYLE-FONT-SIZE-{class_name.upper()}',
                        severity=Severity.ERROR,
                        message=f'.{class_name} 字号应为 {expected_size}，实际为 {actual_half_pt / 2}pt',
                        location=Location(
                            block_index=block.index,
                            kind='paragraph',
                            hint=paragraph.text[:50] if paragraph.text else ''
                        ),
                        evidence={
                            'expected': expected_size,
                            'expected_half_pt': expected_half_pt,
                            'actual_half_pt': actual_half_pt,
                            'class': class_name
                        }
                    ))
        
        # 检查加粗
        if 'bold' in font_def:
            expected_bold = font_def['bold']
            actual_bold = font.bold
            
            if actual_bold != expected_bold:
                issues.append(Issue(
                    code=f'STYLE-FONT-BOLD-{class_name.upper()}',
                    severity=Severity.ERROR,
                    message=f'.{class_name} 加粗应为 {expected_bold}，实际为 {actual_bold}',
                    location=Location(
                        block_index=block.index,
                        kind='paragraph',
                        hint=paragraph.text[:50] if paragraph.text else ''
                    ),
                    evidence={
                        'expected': expected_bold,
                        'actual': actual_bold,
                        'class': class_name
                    }
                ))
        
        # 检查斜体
        if 'italic' in font_def:
            expected_italic = font_def['italic']
            actual_italic = font.italic
            
            if actual_italic != expected_italic:
                issues.append(Issue(
                    code=f'STYLE-FONT-ITALIC-{class_name.upper()}',
                    severity=Severity.ERROR,
                    message=f'.{class_name} 斜体应为 {expected_italic}，实际为 {actual_italic}',
                    location=Location(
                        block_index=block.index,
                        kind='paragraph',
                        hint=paragraph.text[:50] if paragraph.text else ''
                    ),
                    evidence={
                        'expected': expected_italic,
                        'actual': actual_italic,
                        'class': class_name
                    }
                ))
        
        return issues

    def _check_paragraph(
        self,
        block: ParagraphBlock,
        para_def: Dict[str, Any],
        class_name: str
    ) -> List[Issue]:
        """检查段落格式"""
        issues = []
        paragraph = block.paragraph
        para_format = paragraph.paragraph_format
        
        # 检查对齐方式
        if 'alignment' in para_def:
            expected_align = para_def['alignment']
            actual_align = para_format.alignment
            
            # 使用类常量进行对齐方式映射
            expected_align_enum = self.ALIGNMENT_MAP.get(expected_align)
            
            if expected_align_enum is not None and actual_align != expected_align_enum:
                actual_align_name = {v: k for k, v in self.ALIGNMENT_MAP.items()}.get(actual_align, str(actual_align))
                issues.append(Issue(
                    code=f'STYLE-PARA-ALIGN-{class_name.upper()}',
                    severity=Severity.ERROR,
                    message=f'.{class_name} 对齐方式应为 {expected_align}，实际为 {actual_align_name}',
                    location=Location(
                        block_index=block.index,
                        kind='paragraph',
                        hint=paragraph.text[:50] if paragraph.text else ''
                    ),
                    evidence={
                        'expected': expected_align,
                        'actual': actual_align_name,
                        'class': class_name
                    }
                ))
        
        # 检查行距
        if 'line_spacing' in para_def:
            expected_spacing = para_def['line_spacing']
            actual_spacing = para_format.line_spacing
            
            # 解析期望的行距
            value, rule_type = UnitConverter.parse_line_spacing(expected_spacing)
            
            # 简化检查：这里只检查是否设置了行距
            # 详细的行距类型和值检查可以后续完善
            if value is not None and actual_spacing is None:
                issues.append(Issue(
                    code=f'STYLE-PARA-LINE-SPACING-{class_name.upper()}',
                    severity=Severity.WARN,
                    message=f'.{class_name} 应设置行距为 {expected_spacing}',
                    location=Location(
                        block_index=block.index,
                        kind='paragraph',
                        hint=paragraph.text[:50] if paragraph.text else ''
                    ),
                    evidence={
                        'expected': expected_spacing,
                        'actual': None,
                        'class': class_name
                    }
                ))
        
        # 检查首行缩进
        if 'first_line_indent' in para_def:
            expected_indent = para_def['first_line_indent']
            actual_indent = para_format.first_line_indent
            
            # 转换为 twips
            expected_twips = UnitConverter.parse_spacing(
                expected_indent,
                font_size=12  # 默认字号
            )
            
            if expected_twips is not None:
                actual_twips = actual_indent if actual_indent else 0
                
                # 允许一定误差（约 0.5pt）
                if abs(actual_twips - expected_twips) > 10:
                    issues.append(Issue(
                        code=f'STYLE-PARA-FIRST-INDENT-{class_name.upper()}',
                        severity=Severity.ERROR,
                        message=f'.{class_name} 首行缩进应为 {expected_indent}，实际为 {actual_twips}twips',
                        location=Location(
                            block_index=block.index,
                            kind='paragraph',
                            hint=paragraph.text[:50] if paragraph.text else ''
                        ),
                        evidence={
                            'expected': expected_indent,
                            'expected_twips': expected_twips,
                            'actual_twips': actual_twips,
                            'class': class_name
                        }
                    ))
        
        # 检查段前间距
        if 'space_before' in para_def:
            expected_space = para_def['space_before']
            actual_space = para_format.space_before
            
            expected_twips = UnitConverter.parse_spacing(expected_space, font_size=12)
            
            if expected_twips is not None:
                actual_twips = actual_space if actual_space else 0
                
                if abs(actual_twips - expected_twips) > 10:
                    issues.append(Issue(
                        code=f'STYLE-PARA-SPACE-BEFORE-{class_name.upper()}',
                        severity=Severity.WARN,
                        message=f'.{class_name} 段前间距应为 {expected_space}',
                        location=Location(
                            block_index=block.index,
                            kind='paragraph',
                            hint=paragraph.text[:50] if paragraph.text else ''
                        ),
                        evidence={
                            'expected': expected_space,
                            'expected_twips': expected_twips,
                            'actual_twips': actual_twips,
                            'class': class_name
                        }
                    ))
        
        # 检查段后间距
        if 'space_after' in para_def:
            expected_space = para_def['space_after']
            actual_space = para_format.space_after
            
            expected_twips = UnitConverter.parse_spacing(expected_space, font_size=12)
            
            if expected_twips is not None:
                actual_twips = actual_space if actual_space else 0
                
                if abs(actual_twips - expected_twips) > 10:
                    issues.append(Issue(
                        code=f'STYLE-PARA-SPACE-AFTER-{class_name.upper()}',
                        severity=Severity.WARN,
                        message=f'.{class_name} 段后间距应为 {expected_space}',
                        location=Location(
                            block_index=block.index,
                            kind='paragraph',
                            hint=paragraph.text[:50] if paragraph.text else ''
                        ),
                        evidence={
                            'expected': expected_space,
                            'expected_twips': expected_twips,
                            'actual_twips': actual_twips,
                            'class': class_name
                        }
                    ))
        
        return issues
