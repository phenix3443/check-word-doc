#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
段落设置模块
提供段落格式验证功能
"""

import re
from typing import List, Tuple, Optional, Callable, Any
from dataclasses import dataclass

# 尝试导入文档处理模块
DOCX_AVAILABLE = False
try:
    from docx.enum.text import WD_ALIGN_PARAGRAPH

    DOCX_AVAILABLE = True
except ImportError:
    pass


@dataclass
class ParagraphSettings:
    """段落设置结构体

    表示Word文档中段落的格式设置，包括对齐方式、缩进、间距等属性。
    对应Word段落对话框中的设置项。
    """

    # 常规设置
    alignment: Optional[str] = (
        None  # 对齐方式：居中、左对齐、右对齐、两端对齐、分散对齐
    )
    outline_level: Optional[int] = None  # 大纲级别：0-9，0表示正文文本

    # 缩进设置
    left_indent: Optional[float] = None  # 左侧缩进（厘米）
    right_indent: Optional[float] = None  # 右侧缩进（厘米）
    special_format: Optional[str] = None  # 特殊格式：无、首行缩进、悬挂缩进
    special_format_value: Optional[float] = None  # 特殊格式的值（厘米）

    # 间距设置
    space_before: Optional[float] = None  # 段前间距（磅）
    space_after: Optional[float] = None  # 段后间距（磅）
    line_spacing_type: Optional[str] = (
        None  # 行距类型：单倍行距、1.5倍行距、多倍行距、固定值等
    )
    line_spacing_value: Optional[float] = None  # 行距设置值（倍数或磅值）

    def __str__(self) -> str:
        """返回段落设置的字符串表示"""
        parts = []
        if self.alignment:
            parts.append(f"对齐方式：{self.alignment}")
        if self.outline_level is not None:
            parts.append(f"大纲级别：{self.outline_level}")
        if self.left_indent is not None:
            parts.append(f"左侧缩进：{self.left_indent}厘米")
        if self.right_indent is not None:
            parts.append(f"右侧缩进：{self.right_indent}厘米")
        if self.special_format:
            if self.special_format_value is not None:
                parts.append(
                    f"特殊格式：{self.special_format} {self.special_format_value}厘米"
                )
            else:
                parts.append(f"特殊格式：{self.special_format}")
        if self.space_before is not None:
            parts.append(f"段前：{self.space_before}磅")
        if self.space_after is not None:
            parts.append(f"段后：{self.space_after}磅")
        if self.line_spacing_type:
            if self.line_spacing_value is not None:
                parts.append(
                    f"行距：{self.line_spacing_type} {self.line_spacing_value}"
                )
            else:
                parts.append(f"行距：{self.line_spacing_type}")
        return "；".join(parts) if parts else "无设置"

    def alignment_validator(
        self,
    ) -> Optional[Callable[[Any, Any, str, str], Tuple[bool, Optional[str]]]]:
        """创建对齐方式验证器，使用 self.alignment 作为期望值

        Returns:
            验证器函数，符合标准验证器接口 (doc, para_or_cell, field_name, field_value) -> (bool, Optional[str])
            如果未设置对齐方式或 DOCX 不可用，返回 None
        """
        if not DOCX_AVAILABLE:
            return None

        # 如果没有设置对齐方式，返回 None
        if not self.alignment:
            return None

        # 对齐方式映射
        alignment_mapping = {
            "居中": WD_ALIGN_PARAGRAPH.CENTER,
            "左对齐": WD_ALIGN_PARAGRAPH.LEFT,
            "右对齐": WD_ALIGN_PARAGRAPH.RIGHT,
            "两端对齐": WD_ALIGN_PARAGRAPH.JUSTIFY,
            "分散对齐": WD_ALIGN_PARAGRAPH.JUSTIFY,
        }

        expected_alignment = alignment_mapping.get(self.alignment)
        if expected_alignment is None:
            return None

        alignment_name = self.alignment

        def validator(
            doc: Any, para_or_cell: Any, field_name: str, field_value: str
        ) -> Tuple[bool, Optional[str]]:
            if para_or_cell is None:
                return True, None
            try:
                if hasattr(para_or_cell, "paragraph_format"):
                    alignment = para_or_cell.paragraph_format.alignment
                    if alignment != expected_alignment:
                        return False, f"{field_name}对齐方式应为{alignment_name}"
            except Exception:
                pass
            return True, None

        return validator

    def line_spacing_validator(
        self,
    ) -> Optional[Callable[[Any, Any, str, str], Tuple[bool, Optional[str]]]]:
        """创建行距验证器，使用 self.line_spacing_value 作为期望值

        Returns:
            验证器函数，符合标准验证器接口 (doc, para_or_cell, field_name, field_value) -> (bool, Optional[str])
            如果未设置行距，返回 None
        """
        # 如果没有设置行距，返回 None
        if self.line_spacing_value is None:
            return None

        expected_spacing = self.line_spacing_value

        def validator(
            doc: Any, para_or_cell: Any, field_name: str, field_value: str
        ) -> Tuple[bool, Optional[str]]:
            if para_or_cell is None:
                return True, None
            try:
                if hasattr(para_or_cell, "paragraph_format"):
                    line_spacing = para_or_cell.paragraph_format.line_spacing
                    if line_spacing and abs(line_spacing - expected_spacing) > 0.01:
                        return (
                            False,
                            f"{field_name}行距应为{expected_spacing}倍，当前为{line_spacing}",
                        )
            except Exception:
                pass
            return True, None

        return validator

    def space_before_validator(
        self,
    ) -> Optional[Callable[[Any, Any, str, str], Tuple[bool, Optional[str]]]]:
        """创建段前间距验证器，使用 self.space_before 作为期望值

        Returns:
            验证器函数，符合标准验证器接口 (doc, para_or_cell, field_name, field_value) -> (bool, Optional[str])
            如果未设置段前间距，返回 None
        """
        # 如果没有设置段前间距，返回 None
        if self.space_before is None:
            return None

        expected_spacing_pt = self.space_before

        def validator(
            doc: Any, para_or_cell: Any, field_name: str, field_value: str
        ) -> Tuple[bool, Optional[str]]:
            if para_or_cell is None:
                return True, None
            try:
                if hasattr(para_or_cell, "paragraph_format"):
                    space_before = para_or_cell.paragraph_format.space_before
                    if space_before is not None:
                        # 允许一定的误差范围（±1磅）
                        if abs(space_before.pt - expected_spacing_pt) > 1.0:
                            return (
                                False,
                                f"{field_name}段前间距应为{expected_spacing_pt:.1f}磅，当前为{space_before.pt:.1f}磅",
                            )
            except Exception:
                pass
            return True, None

        return validator

    def space_after_validator(
        self,
    ) -> Optional[Callable[[Any, Any, str, str], Tuple[bool, Optional[str]]]]:
        """创建段后间距验证器，使用 self.space_after 作为期望值

        Returns:
            验证器函数，符合标准验证器接口 (doc, para_or_cell, field_name, field_value) -> (bool, Optional[str])
            如果未设置段后间距，返回 None
        """
        # 如果没有设置段后间距，返回 None
        if self.space_after is None:
            return None

        expected_spacing_pt = self.space_after

        def validator(
            doc: Any, para_or_cell: Any, field_name: str, field_value: str
        ) -> Tuple[bool, Optional[str]]:
            if para_or_cell is None:
                return True, None
            try:
                if hasattr(para_or_cell, "paragraph_format"):
                    space_after = para_or_cell.paragraph_format.space_after
                    if space_after is not None:
                        # 允许一定的误差范围（±1磅）
                        if abs(space_after.pt - expected_spacing_pt) > 1.0:
                            return (
                                False,
                                f"{field_name}段后间距应为{expected_spacing_pt:.1f}磅，当前为{space_after.pt:.1f}磅",
                            )
            except Exception:
                pass
            return True, None

        return validator

    def indent_validator(
        self,
    ) -> Optional[Callable[[Any, Any, str, str], Tuple[bool, Optional[str]]]]:
        """创建首行缩进验证器，使用 self.special_format_value 作为期望值（当 special_format 为"首行缩进"时）

        Returns:
            验证器函数，符合标准验证器接口 (doc, para_or_cell, field_name, field_value) -> (bool, Optional[str])
            如果未设置首行缩进，返回 None
        """
        # 只有当 special_format 为"首行缩进"且有值时，才创建验证器
        if self.special_format != "首行缩进" or self.special_format_value is None:
            return None

        # 将厘米转换为磅（points），1厘米约等于28.35磅
        expected_indent_pt = self.special_format_value * 28.35

        def validator(
            doc: Any, para_or_cell: Any, field_name: str, field_value: str
        ) -> Tuple[bool, Optional[str]]:
            if para_or_cell is None:
                return True, None
            try:
                if hasattr(para_or_cell, "paragraph_format"):
                    first_line_indent = para_or_cell.paragraph_format.first_line_indent
                    if first_line_indent is not None:
                        # 允许一定的误差范围（±1磅）
                        if abs(first_line_indent.pt - expected_indent_pt) > 1.0:
                            return (
                                False,
                                f"{field_name}首行缩进应为{expected_indent_pt:.1f}磅，当前为{first_line_indent.pt:.1f}磅",
                            )
            except Exception:
                pass
            return True, None

        return validator

    def hanging_indent_validator(
        self,
    ) -> Optional[Callable[[Any, Any, str, str], Tuple[bool, Optional[str]]]]:
        """创建悬挂缩进验证器，使用 self.special_format_value 作为期望值（当 special_format 为"悬挂缩进"时）

        Returns:
            验证器函数，符合标准验证器接口 (doc, para_or_cell, field_name, field_value) -> (bool, Optional[str])
            如果未设置悬挂缩进，返回 None
        """
        # 只有当 special_format 为"悬挂缩进"时，才创建验证器
        if self.special_format != "悬挂缩进":
            return None

        # 如果指定了值，转换为磅；否则只检查是否有悬挂缩进
        expected_indent_pt = None
        if self.special_format_value is not None:
            expected_indent_pt = self.special_format_value * 28.35

        def validator(
            doc: Any, para_or_cell: Any, field_name: str, field_value: str
        ) -> Tuple[bool, Optional[str]]:
            if para_or_cell is None:
                return True, None
            try:
                if hasattr(para_or_cell, "paragraph_format"):
                    first_line_indent = para_or_cell.paragraph_format.first_line_indent
                    if first_line_indent is not None:
                        # 悬挂缩进是负的首行缩进
                        if first_line_indent.pt >= 0:
                            return (
                                False,
                                f"{field_name}应为悬挂缩进（首行缩进应为负值），当前首行缩进为{first_line_indent.pt:.1f}磅",
                            )
                        # 如果指定了期望值，检查是否匹配
                        if expected_indent_pt is not None:
                            # 悬挂缩进的绝对值应该等于期望值
                            if (
                                abs(abs(first_line_indent.pt) - expected_indent_pt)
                                > 1.0
                            ):
                                return (
                                    False,
                                    f"{field_name}悬挂缩进应为{expected_indent_pt:.1f}磅，当前为{abs(first_line_indent.pt):.1f}磅",
                                )
            except Exception:
                pass
            return True, None

        return validator

    def no_indent_validator(
        self,
    ) -> Optional[Callable[[Any, Any, str, str], Tuple[bool, Optional[str]]]]:
        """创建无缩进验证器，当 self.special_format 为"无"时使用

        Returns:
            验证器函数，符合标准验证器接口 (doc, para_or_cell, field_name, field_value) -> (bool, Optional[str])
            如果未设置无缩进，返回 None
        """
        # 只有当 special_format 为"无"时，才创建验证器
        if self.special_format != "无":
            return None

        def validator(
            doc: Any, para_or_cell: Any, field_name: str, field_value: str
        ) -> Tuple[bool, Optional[str]]:
            if para_or_cell is None:
                return True, None
            try:
                if hasattr(para_or_cell, "paragraph_format"):
                    first_line_indent = para_or_cell.paragraph_format.first_line_indent
                    left_indent = para_or_cell.paragraph_format.left_indent
                    right_indent = para_or_cell.paragraph_format.right_indent

                    # 检查所有缩进是否都为0或None
                    has_indent = False
                    indent_details = []

                    if (
                        first_line_indent is not None
                        and abs(first_line_indent.pt) > 0.5
                    ):
                        has_indent = True
                        indent_details.append(f"首行缩进{first_line_indent.pt:.1f}磅")

                    if left_indent is not None and abs(left_indent.pt) > 0.5:
                        has_indent = True
                        indent_details.append(f"左缩进{left_indent.pt:.1f}磅")

                    if right_indent is not None and abs(right_indent.pt) > 0.5:
                        has_indent = True
                        indent_details.append(f"右缩进{right_indent.pt:.1f}磅")

                    if has_indent:
                        return (
                            False,
                            f"{field_name}应为无缩进，但存在：{', '.join(indent_details)}",
                        )
            except Exception:
                pass
            return True, None

        return validator

    def left_indent_validator(
        self,
    ) -> Optional[Callable[[Any, Any, str, str], Tuple[bool, Optional[str]]]]:
        """创建左缩进验证器，使用 self.left_indent 作为期望值

        Returns:
            验证器函数，符合标准验证器接口 (doc, para_or_cell, field_name, field_value) -> (bool, Optional[str])
            如果未设置左缩进，返回 None
        """
        # 如果没有设置左缩进，返回 None
        if self.left_indent is None:
            return None

        # 将厘米转换为磅（points），1厘米约等于28.35磅
        expected_indent_pt = self.left_indent * 28.35

        def validator(
            doc: Any, para_or_cell: Any, field_name: str, field_value: str
        ) -> Tuple[bool, Optional[str]]:
            if para_or_cell is None:
                return True, None
            try:
                if hasattr(para_or_cell, "paragraph_format"):
                    left_indent = para_or_cell.paragraph_format.left_indent
                    if left_indent is not None:
                        # 允许一定的误差范围（±1磅）
                        if abs(left_indent.pt - expected_indent_pt) > 1.0:
                            return (
                                False,
                                f"{field_name}左缩进应为{expected_indent_pt:.1f}磅，当前为{left_indent.pt:.1f}磅",
                            )
            except Exception:
                pass
            return True, None

        return validator

    def right_indent_validator(
        self,
    ) -> Optional[Callable[[Any, Any, str, str], Tuple[bool, Optional[str]]]]:
        """创建右缩进验证器，使用 self.right_indent 作为期望值

        Returns:
            验证器函数，符合标准验证器接口 (doc, para_or_cell, field_name, field_value) -> (bool, Optional[str])
            如果未设置右缩进，返回 None
        """
        # 如果没有设置右缩进，返回 None
        if self.right_indent is None:
            return None

        # 将厘米转换为磅（points），1厘米约等于28.35磅
        expected_indent_pt = self.right_indent * 28.35

        def validator(
            doc: Any, para_or_cell: Any, field_name: str, field_value: str
        ) -> Tuple[bool, Optional[str]]:
            if para_or_cell is None:
                return True, None
            try:
                if hasattr(para_or_cell, "paragraph_format"):
                    right_indent = para_or_cell.paragraph_format.right_indent
                    if right_indent is not None:
                        # 允许一定的误差范围（±1磅）
                        if abs(right_indent.pt - expected_indent_pt) > 1.0:
                            return (
                                False,
                                f"{field_name}右缩进应为{expected_indent_pt:.1f}磅，当前为{right_indent.pt:.1f}磅",
                            )
            except Exception:
                pass
            return True, None

        return validator

    def outline_level_validator(
        self,
    ) -> Optional[Callable[[Any, Any, str, str], Tuple[bool, Optional[str]]]]:
        """创建大纲级别验证器，使用 self.outline_level 作为期望值

        Returns:
            验证器函数，符合标准验证器接口 (doc, para_or_cell, field_name, field_value) -> (bool, Optional[str])
            如果未设置大纲级别，返回 None
        """
        # 如果没有设置大纲级别，返回 None
        if self.outline_level is None:
            return None

        expected_level = self.outline_level

        def validator(
            doc: Any, para_or_cell: Any, field_name: str, field_value: str
        ) -> Tuple[bool, Optional[str]]:
            if para_or_cell is None:
                return True, None
            try:
                # 检查段落的大纲级别
                # 可以通过 paragraph_format.outline_level 或 style 来判断
                if hasattr(para_or_cell, "paragraph_format"):
                    # 方法1：通过 outline_level 属性
                    outline_level = para_or_cell.paragraph_format.outline_level
                    if outline_level is not None:
                        # outline_level 是 0-9 的数字，0 表示正文，1-9 表示标题级别
                        # 但实际中，1级标题对应 outline_level=1，2级标题对应 outline_level=2，以此类推
                        if outline_level != expected_level:
                            return (
                                False,
                                f"{field_name}大纲级别应为{expected_level}级标题，当前为{outline_level}级",
                            )
                        return True, None

                # 方法2：通过样式名称判断（如 "Heading 1", "Heading 2" 等）
                if hasattr(para_or_cell, "style"):
                    style_name = str(para_or_cell.style.name)
                    # 检查是否是标题样式
                    if "Heading" in style_name or "标题" in style_name:
                        # 从样式名称中提取级别
                        # 例如 "Heading 1" -> 1, "标题 1" -> 1
                        level_match = re.search(r"(\d+)", style_name)
                        if level_match:
                            actual_level = int(level_match.group(1))
                            if actual_level != expected_level:
                                return (
                                    False,
                                    f"{field_name}大纲级别应为{expected_level}级标题，当前为{actual_level}级（样式：{style_name}）",
                                )
                            return True, None
                        # 如果没有找到数字，可能是自定义样式，跳过检查
                        return True, None

            except Exception:
                pass
            return True, None

        return validator

    def validators(
        self,
    ) -> List[Callable[[Any, Any, str, str], Tuple[bool, Optional[str]]]]:
        """返回所有相关的验证器列表

        调用所有已设置的验证器函数，包括：
        - alignment_validator（如果设置了对齐方式）
        - line_spacing_validator（如果设置了行距）
        - space_before_validator（如果设置了段前间距）
        - space_after_validator（如果设置了段后间距）
        - indent_validator（如果设置了首行缩进）
        - hanging_indent_validator（如果设置了悬挂缩进）
        - no_indent_validator（如果设置了无缩进）
        - left_indent_validator（如果设置了左缩进）
        - right_indent_validator（如果设置了右缩进）
        - outline_level_validator（如果设置了大纲级别）

        Returns:
            验证器函数列表，每个函数符合标准验证器接口 (doc, para_or_cell, field_name, field_value) -> (bool, Optional[str])
            只包含已设置的验证器，未设置的验证器（返回 None）会被过滤掉
        """
        validators_list = []

        # 添加对齐方式验证器（如果设置了）
        validator = self.alignment_validator()
        if validator is not None:
            validators_list.append(validator)

        # 添加行距验证器（如果设置了）
        validator = self.line_spacing_validator()
        if validator is not None:
            validators_list.append(validator)

        # 添加段前间距验证器（如果设置了）
        validator = self.space_before_validator()
        if validator is not None:
            validators_list.append(validator)

        # 添加段后间距验证器（如果设置了）
        validator = self.space_after_validator()
        if validator is not None:
            validators_list.append(validator)

        # 添加首行缩进验证器（如果设置了）
        validator = self.indent_validator()
        if validator is not None:
            validators_list.append(validator)

        # 添加悬挂缩进验证器（如果设置了）
        validator = self.hanging_indent_validator()
        if validator is not None:
            validators_list.append(validator)

        # 添加无缩进验证器（如果设置了）
        validator = self.no_indent_validator()
        if validator is not None:
            validators_list.append(validator)

        # 添加左缩进验证器（如果设置了）
        validator = self.left_indent_validator()
        if validator is not None:
            validators_list.append(validator)

        # 添加右缩进验证器（如果设置了）
        validator = self.right_indent_validator()
        if validator is not None:
            validators_list.append(validator)

        # 添加大纲级别验证器（如果设置了）
        validator = self.outline_level_validator()
        if validator is not None:
            validators_list.append(validator)

        return validators_list
