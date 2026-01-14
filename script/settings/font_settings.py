#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
字体设置模块
提供字体格式验证功能
"""

import re
from typing import List, Tuple, Optional, Callable, Any
from dataclasses import dataclass


@dataclass
class FontSettings:
    """字体设置结构体

    表示Word文档中字体的格式设置，包括字体名称、字号、字形等属性。
    对应Word字体对话框中的设置项。
    """

    # 字体名称
    chinese_font: str = ""  # 中文字体名称，如：黑体、华文楷体、宋体
    western_font: str = ""  # 西文字体名称，如：Times New Roman

    # 字号设置
    font_size: float = 0.0  # 字号（磅值），如：12.0、14.0、16.0
    font_size_name: str = ""  # 字号名称，如：三号、小四、五号

    # 字形设置
    bold: Optional[bool] = None  # 粗体：True表示启用，False表示禁用，None表示不检查
    italic: Optional[bool] = None  # 斜体：True表示启用，False表示禁用，None表示不检查
    underline: Optional[bool] = None

    # 字体效果（可选）
    font_color: Optional[str] = None  # 字体颜色
    highlight_color: Optional[str] = None  # 突出显示颜色

    def __str__(self) -> str:
        """返回字体设置的字符串表示"""
        parts = []
        if self.chinese_font:
            parts.append(f"中文字体：{self.chinese_font}")
        if self.western_font:
            parts.append(f"西文字体：{self.western_font}")
        if self.font_size > 0:
            if self.font_size_name:
                parts.append(f"字号：{self.font_size_name}（{self.font_size}pt）")
            else:
                parts.append(f"字号：{self.font_size}pt")
        elif self.font_size_name:
            parts.append(f"字号：{self.font_size_name}")

        style_parts = []
        if self.bold is True:
            style_parts.append("粗体")
        if self.italic is True:
            style_parts.append("斜体")
        if self.underline is True:
            style_parts.append("下划线")
        if style_parts:
            parts.append(f"字形：{', '.join(style_parts)}")

        if self.font_color:
            parts.append(f"字体颜色：{self.font_color}")
        if self.highlight_color:
            parts.append(f"突出显示：{self.highlight_color}")

        return "；".join(parts) if parts else "无设置"

    def chinese_font_validator(
        self,
    ) -> Optional[Callable[[Any, Any, str, str], Tuple[bool, Optional[str]]]]:
        """创建中文字体验证器，使用 self.chinese_font 作为期望值

        Returns:
            验证器函数，符合标准验证器接口 (doc, para_or_cell, field_name, field_value) -> (bool, Optional[str])
            如果未设置中文字体，返回 None
        """
        # 如果没有设置中文字体，返回 None
        if not self.chinese_font:
            return None

        # 字体名称到实际字体名称列表的映射
        font_mapping = {
            "黑体": ["黑体", "SimHei"],
            "华文楷体": ["华文楷体", "KaiTi"],
            "宋体": ["宋体", "SimSun"],
        }

        expected_names = font_mapping.get(self.chinese_font, [self.chinese_font])
        font_name = self.chinese_font

        def validator(
            doc: Any, para_or_cell: Any, field_name: str, field_value: str
        ) -> Tuple[bool, Optional[str]]:
            if para_or_cell is None:
                return True, None
            try:
                runs = para_or_cell.runs if hasattr(para_or_cell, "runs") else []
                for run in runs:
                    if re.search(r"[\u4e00-\u9fa5]", run.text):
                        if run.font.name not in expected_names:
                            return (
                                False,
                                f"{field_name}中文字体应为{font_name}，当前为{run.font.name}",
                            )
            except Exception:
                pass
            return True, None

        return validator

    def western_font_validator(
        self,
    ) -> Optional[Callable[[Any, Any, str, str], Tuple[bool, Optional[str]]]]:
        """创建西文字体验证器，使用 self.western_font 作为期望值

        Returns:
            验证器函数，符合标准验证器接口 (doc, para_or_cell, field_name, field_value) -> (bool, Optional[str])
            如果未设置西文字体，返回 None
        """
        # 如果没有设置西文字体，返回 None
        if not self.western_font:
            return None

        expected_font = self.western_font

        def validator(
            doc: Any, para_or_cell: Any, field_name: str, field_value: str
        ) -> Tuple[bool, Optional[str]]:
            if para_or_cell is None:
                return True, None
            try:
                runs = para_or_cell.runs if hasattr(para_or_cell, "runs") else []
                for run in runs:
                    if re.search(r"[a-zA-Z]", run.text):
                        if run.font.name != expected_font:
                            return (
                                False,
                                f"{field_name}西文字体应为{expected_font}，当前为{run.font.name}",
                            )
            except Exception:
                pass
            return True, None

        return validator

    def font_size_validator(
        self,
    ) -> Optional[Callable[[Any, Any, str, str], Tuple[bool, Optional[str]]]]:
        """创建字号验证器，使用 self.font_size 作为期望值

        Returns:
            验证器函数，符合标准验证器接口 (doc, para_or_cell, field_name, field_value) -> (bool, Optional[str])
            如果未设置字号，返回 None
        """
        # 如果没有设置字号，返回 None
        if self.font_size <= 0:
            return None

        expected_pt = self.font_size
        size_name = self.font_size_name if self.font_size_name else f"{expected_pt}pt"

        def validator(
            doc: Any, para_or_cell: Any, field_name: str, field_value: str
        ) -> Tuple[bool, Optional[str]]:
            if para_or_cell is None:
                return True, None
            try:
                runs = para_or_cell.runs if hasattr(para_or_cell, "runs") else []
                for run in runs:
                    if run.font.size and run.font.size.pt != expected_pt:
                        return (
                            False,
                            f"{field_name}字号应为{size_name}（{expected_pt}pt），当前为{run.font.size.pt}pt",
                        )
            except Exception:
                pass
            return True, None

        return validator

    def font_style_validator(
        self,
    ) -> Optional[Callable[[Any, Any, str, str], Tuple[bool, Optional[str]]]]:
        """创建字形验证器，使用 self.bold, self.italic, self.underline 作为期望值

        Returns:
            验证器函数，符合标准验证器接口 (doc, para_or_cell, field_name, field_value) -> (bool, Optional[str])
            如果未设置任何字形，返回 None
        """
        # 收集需要检查的字形
        styles_to_check = []
        if self.bold is not None:
            styles_to_check.append(("bold", "粗体", self.bold))
        if self.italic is not None:
            styles_to_check.append(("italic", "斜体", self.italic))
        if self.underline is not None:
            styles_to_check.append(("underline", "下划线", self.underline))

        # 如果没有需要检查的字形，返回 None
        if not styles_to_check:
            return None

        def validator(
            doc: Any, para_or_cell: Any, field_name: str, field_value: str
        ) -> Tuple[bool, Optional[str]]:
            if para_or_cell is None:
                return True, None
            try:
                runs = para_or_cell.runs if hasattr(para_or_cell, "runs") else []
                if not runs:
                    return True, None  # 没有文本运行，跳过检查

                # 检查所有需要验证的字形
                for style_name, display_name, expected_value in styles_to_check:
                    # 检查所有文本运行
                    for run in runs:
                        if not run.text.strip():
                            continue  # 跳过空文本运行

                        # 根据字形类型获取实际值
                        if style_name == "bold":
                            actual_value = run.font.bold
                        elif style_name == "italic":
                            actual_value = run.font.italic
                        elif style_name == "underline":
                            actual_value = run.font.underline is not None
                        else:
                            continue

                        # 如果期望启用但实际未启用，或期望禁用但实际启用，则报错
                        if actual_value != expected_value:
                            expected_text = "启用" if expected_value else "禁用"
                            actual_text = "启用" if actual_value else "禁用"
                            return (
                                False,
                                f"{field_name}字形应为{display_name}（{expected_text}），当前为{actual_text}",
                            )
            except Exception:
                pass
            return True, None

        return validator

    def validators(
        self,
    ) -> List[Callable[[Any, Any, str, str], Tuple[bool, Optional[str]]]]:
        """返回所有相关的验证器列表

        调用所有已设置的验证器函数，包括：
        - chinese_font_validator（如果设置了中文字体）
        - western_font_validator（如果设置了西文字体）
        - font_size_validator（如果设置了字号）
        - font_style_validator（如果设置了字形）

        Returns:
            验证器函数列表，每个函数符合标准验证器接口 (doc, para_or_cell, field_name, field_value) -> (bool, Optional[str])
            只包含已设置的验证器，未设置的验证器（返回 None）会被过滤掉
        """
        validators_list = []

        # 添加中文字体验证器（如果设置了）
        validator = self.chinese_font_validator()
        if validator is not None:
            validators_list.append(validator)

        # 添加西文字体验证器（如果设置了）
        validator = self.western_font_validator()
        if validator is not None:
            validators_list.append(validator)

        # 添加字号验证器（如果设置了）
        validator = self.font_size_validator()
        if validator is not None:
            validators_list.append(validator)

        # 添加字形验证器（如果设置了）
        validator = self.font_style_validator()
        if validator is not None:
            validators_list.append(validator)

        return validators_list
