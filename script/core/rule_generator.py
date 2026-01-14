"""规则生成器

从声明式配置自动生成规则实例。

声明式配置描述"文档应该是什么样子"，而不是"应该用什么规则检查"。
规则生成器负责将声明式描述转换为具体的规则实例。
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from script.core.rule import Rule
from script.rules.format_rules import (
    FontStyleRule,
    ParagraphFormatRule,
)
from script.rules.paragraph_rules import ParagraphContentRule
from script.rules.structure_rules import (
    HeadingNumberingRule,
    HeadingHierarchyRule,
)
from script.rules.reference_rules import (
    ReferencesCitationRule,
    CitationValidationRule,
)
from script.utils.unit_converter import (
    font_size_to_half_pt,
    spacing_to_twip,
    indent_to_twip,
)


class RuleGenerator:
    """规则生成器
    
    从声明式配置生成规则实例。
    """
    
    def __init__(self):
        self.rule_counter = 0  # 用于生成唯一的规则 ID
    
    def generate_rules(self, document_config: Dict[str, Any]) -> List[Rule]:
        """从文档配置生成规则列表
        
        Args:
            document_config: 文档配置字典，包含 structure 和 defaults 等
            
        Returns:
            规则实例列表
        """
        rules = []
        
        # 提取默认值
        defaults = document_config.get("defaults", {})
        default_font_size = self._parse_font_size(defaults.get("font_size", 10.5))
        
        # 处理文档结构
        structure = document_config.get("structure", [])
        for idx, element in enumerate(structure):
            element_rules = self._generate_element_rules(
                element, 
                block_index=idx,
                default_font_size=default_font_size
            )
            rules.extend(element_rules)
        
        # 处理标题规则
        headings_config = document_config.get("headings", {})
        if headings_config:
            heading_rules = self._generate_heading_rules(headings_config)
            rules.extend(heading_rules)
        
        # 处理参考文献规则
        references_config = document_config.get("references", {})
        if references_config:
            ref_rules = self._generate_reference_rules(references_config)
            rules.extend(ref_rules)
        
        return rules
    
    def _generate_element_rules(
        self, 
        element: Dict[str, Any], 
        block_index: int,
        default_font_size: float
    ) -> List[Rule]:
        """为单个文档元素生成规则
        
        Args:
            element: 元素配置
            block_index: 元素在文档中的位置（块索引）
            default_font_size: 默认字体大小（磅）
            
        Returns:
            规则列表
        """
        rules = []
        
        element_type = element.get("type")
        element_name = element.get("name", f"element_{block_index}")
        
        # 内容检查规则
        content_config = element.get("content", {})
        if content_config:
            rules.append(self._create_content_rule(
                element_name, 
                block_index, 
                content_config
            ))
        
        # 字体检查规则
        font_config = element.get("font", {})
        if font_config:
            rules.append(self._create_font_rule(
                element_name,
                block_index,
                font_config
            ))
        
        # 段落格式检查规则
        paragraph_config = element.get("paragraph", {})
        if paragraph_config:
            # 获取字体大小用于相对单位转换
            font_size = self._parse_font_size(
                font_config.get("size", default_font_size)
            ) if font_config else default_font_size
            
            rules.append(self._create_paragraph_rule(
                element_name,
                block_index,
                paragraph_config,
                font_size
            ))
        
        return rules
    
    def _create_content_rule(
        self, 
        element_name: str, 
        block_index: int,
        content_config: Dict[str, Any]
    ) -> ParagraphContentRule:
        """创建内容检查规则"""
        rule_id = self._next_rule_id("CONTENT")
        
        return ParagraphContentRule(
            id=rule_id,
            description=f"{element_name}内容检查",
            target_blocks=[block_index],
            min_length=content_config.get("min_length", 0),
            max_length=content_config.get("max_length"),
            required=content_config.get("required", True),
        )
    
    def _create_font_rule(
        self,
        element_name: str,
        block_index: int,
        font_config: Dict[str, Any]
    ) -> FontStyleRule:
        """创建字体检查规则"""
        rule_id = self._next_rule_id("FONT")
        
        # 解析字体大小（转换为 EMU）
        expected_font_size = None
        if "size" in font_config:
            half_pt = font_size_to_half_pt(font_config["size"])
            if half_pt is not None:
                # 将半磅转换为 EMU
                # 1 pt = 12700 EMU, 半磅 = 0.5 pt
                expected_font_size = half_pt * 12700 // 2
        
        # 处理字体名称
        # 优先使用中文字体（name_eastasia），西文字体（name_ascii）作为备选
        expected_font_name = font_config.get("name_eastasia")
        font_name_alternatives = []
        if "name_ascii" in font_config:
            font_name_alternatives.append(font_config["name_ascii"])
        
        return FontStyleRule(
            id=rule_id,
            description=f"{element_name}字体检查",
            target_blocks=[block_index],
            expected_font_name=expected_font_name,
            font_name_alternatives=font_name_alternatives,
            expected_font_size=expected_font_size,
            expected_bold=font_config.get("bold"),
            expected_italic=font_config.get("italic"),
        )
    
    def _create_paragraph_rule(
        self,
        element_name: str,
        block_index: int,
        paragraph_config: Dict[str, Any],
        font_size: float
    ) -> ParagraphFormatRule:
        """创建段落格式检查规则"""
        rule_id = self._next_rule_id("PAR")
        
        # 解析行距
        line_spacing = None
        line_spacing_rule = "multiple"
        if "line_spacing" in paragraph_config:
            from script.utils.unit_converter import UnitConverter
            spacing_val, spacing_rule = UnitConverter.parse_line_spacing(
                paragraph_config["line_spacing"]
            )
            if spacing_val is not None:
                line_spacing = spacing_val
                line_spacing_rule = spacing_rule or "multiple"
        
        # 解析缩进和间距
        first_line_indent = None
        if "first_line_indent" in paragraph_config:
            first_line_indent = indent_to_twip(
                paragraph_config["first_line_indent"],
                font_size
            )
        
        left_indent = None
        if "left_indent" in paragraph_config:
            left_indent = indent_to_twip(
                paragraph_config["left_indent"],
                font_size
            )
        
        right_indent = None
        if "right_indent" in paragraph_config:
            right_indent = indent_to_twip(
                paragraph_config["right_indent"],
                font_size
            )
        
        space_before = None
        if "space_before" in paragraph_config:
            space_before = spacing_to_twip(
                paragraph_config["space_before"],
                font_size
            )
        
        space_after = None
        if "space_after" in paragraph_config:
            space_after = spacing_to_twip(
                paragraph_config["space_after"],
                font_size
            )
        
        # 对齐方式映射
        alignment_map = {
            "居中": "CENTER",
            "左对齐": "LEFT",
            "右对齐": "RIGHT",
            "两端对齐": "JUSTIFY",
            "分散对齐": "DISTRIBUTE",
        }
        alignment = None
        if "alignment" in paragraph_config:
            align_value = paragraph_config["alignment"]
            alignment = alignment_map.get(align_value, align_value)
        
        return ParagraphFormatRule(
            id=rule_id,
            description=f"{element_name}段落格式检查",
            target_blocks=[block_index],
            line_spacing=line_spacing,
            line_spacing_rule=line_spacing_rule,
            alignment=alignment,
            first_line_indent=first_line_indent,
            left_indent=left_indent,
            right_indent=right_indent,
            space_before=space_before,
            space_after=space_after,
        )
    
    def _generate_heading_rules(self, headings_config: Dict[str, Any]) -> List[Rule]:
        """生成标题相关规则"""
        rules = []
        
        heading_styles = headings_config.get("styles", [])
        
        # 标题序号连续性检查
        if headings_config.get("check_sequence", True):
            rules.append(HeadingNumberingRule(
                id=self._next_rule_id("HDG_SEQ"),
                description="标题编号连续性检查",
                heading_styles=heading_styles,
            ))
        
        # 标题层级一致性检查
        if headings_config.get("check_hierarchy", True):
            rules.append(HeadingHierarchyRule(
                id=self._next_rule_id("HDG_HIER"),
                description="标题编号层级一致性检查",
                heading_styles=heading_styles,
            ))
        
        # 标题格式检查
        formats = headings_config.get("formats", [])
        for format_config in formats:
            level = format_config.get("level")
            if level is None:
                continue
            
            # 生成该级别标题的格式规则
            heading_rules = self._generate_heading_format_rules(
                level, 
                format_config, 
                heading_styles
            )
            rules.extend(heading_rules)
        
        return rules
    
    def _generate_heading_format_rules(
        self, 
        level: int, 
        format_config: Dict[str, Any],
        heading_styles: List[str]
    ) -> List[Rule]:
        """为特定级别的标题生成格式规则
        
        Args:
            level: 标题级别（1, 2, 3...）
            format_config: 格式配置
            heading_styles: 标题样式列表
            
        Returns:
            规则列表
        """
        rules = []
        
        # 筛选出该级别的样式
        # 如果样式名包含数字，提取级别
        level_styles = []
        for style in heading_styles:
            # 匹配 "Heading 1", "标题 1" 等
            import re
            match = re.search(r'(\d+)', style)
            if match and int(match.group(1)) == level:
                level_styles.append(style)
        
        if not level_styles:
            return rules
        
        # 字体规则
        font_config = format_config.get("font", {})
        if font_config:
            # 解析字体大小（转换为 EMU）
            expected_font_size = None
            if "size" in font_config:
                half_pt = font_size_to_half_pt(font_config["size"])
                if half_pt is not None:
                    # 将半磅转换为 EMU: 1 pt = 12700 EMU
                    expected_font_size = half_pt * 12700 // 2
            
            # 处理字体名称
            expected_font_name = font_config.get("name_eastasia")
            font_name_alternatives = []
            if "name_ascii" in font_config:
                font_name_alternatives.append(font_config["name_ascii"])
            
            rules.append(FontStyleRule(
                id=self._next_rule_id(f"HDG{level}_FONT"),
                description=f"{level}级标题字体检查",
                target_styles=level_styles,
                expected_font_name=expected_font_name,
                font_name_alternatives=font_name_alternatives,
                expected_font_size=expected_font_size,
                expected_bold=font_config.get("bold"),
                expected_italic=font_config.get("italic"),
            ))
        
        # 段落格式规则
        paragraph_config = format_config.get("paragraph", {})
        if paragraph_config:
            # 获取字体大小用于相对单位转换
            font_size = self._parse_font_size(
                font_config.get("size", 10.5)
            ) if font_config else 10.5
            
            # 解析行距
            line_spacing = None
            line_spacing_rule = "multiple"
            if "line_spacing" in paragraph_config:
                from script.utils.unit_converter import UnitConverter
                spacing_val, spacing_rule = UnitConverter.parse_line_spacing(
                    paragraph_config["line_spacing"]
                )
                if spacing_val is not None:
                    line_spacing = spacing_val
                    line_spacing_rule = spacing_rule or "multiple"
            
            # 解析间距
            space_before = None
            if "space_before" in paragraph_config:
                space_before = spacing_to_twip(
                    paragraph_config["space_before"],
                    font_size
                )
            
            space_after = None
            if "space_after" in paragraph_config:
                space_after = spacing_to_twip(
                    paragraph_config["space_after"],
                    font_size
                )
            
            # 对齐方式
            alignment_map = {
                "居中": "CENTER",
                "左对齐": "LEFT",
                "右对齐": "RIGHT",
                "两端对齐": "JUSTIFY",
                "分散对齐": "DISTRIBUTE",
            }
            alignment = None
            if "alignment" in paragraph_config:
                align_value = paragraph_config["alignment"]
                alignment = alignment_map.get(align_value, align_value)
            
            rules.append(ParagraphFormatRule(
                id=self._next_rule_id(f"HDG{level}_PAR"),
                description=f"{level}级标题段落格式检查",
                target_styles=level_styles,
                line_spacing=line_spacing,
                line_spacing_rule=line_spacing_rule,
                alignment=alignment,
                space_before=space_before,
                space_after=space_after,
            ))
        
        return rules
    
    def _generate_reference_rules(self, references_config: Dict[str, Any]) -> List[Rule]:
        """生成参考文献相关规则"""
        rules = []
        
        # 引用检查
        if references_config.get("check_citations", True):
            rules.append(ReferencesCitationRule(
                id=self._next_rule_id("REF_CIT"),
                description="参考文献引用检查",
                reference_heading=references_config.get("heading", "参考文献"),
            ))
        
        # 引用有效性检查
        if references_config.get("check_citation_validity", True):
            rules.append(CitationValidationRule(
                id=self._next_rule_id("REF_VAL"),
                description="引用有效性检查",
                reference_heading=references_config.get("heading", "参考文献"),
            ))
        
        return rules
    
    def _parse_font_size(self, value: Any) -> float:
        """解析字体大小为磅值"""
        half_pt = font_size_to_half_pt(value)
        if half_pt is None:
            return 10.5  # 默认值
        return half_pt / 2.0
    
    def _next_rule_id(self, prefix: str) -> str:
        """生成下一个规则 ID"""
        self.rule_counter += 1
        return f"{prefix}-{self.rule_counter:03d}"


def generate_rules_from_config(config: Dict[str, Any]) -> List[Rule]:
    """从配置生成规则（便捷函数）
    
    Args:
        config: 配置字典，应包含 "document" 键
        
    Returns:
        规则列表
    """
    document_config = config.get("document", {})
    if not document_config:
        return []
    
    generator = RuleGenerator()
    return generator.generate_rules(document_config)
