#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
语言设置模块
提供语言格式验证功能
"""

import re
from typing import Tuple, Optional, Callable, Any
from dataclasses import dataclass


@dataclass
class LanguageSettings:
    """语言设置结构体

    表示文档中文本的语言类型要求，包括中文、英文等。
    """

    language: Optional[str] = None  # 语言类型："中文" 或 "英文"

    def __post_init__(self):
        """验证 language 参数"""
        if self.language is not None and self.language not in ["中文", "英文"]:
            raise ValueError(
                f"language 必须是 '中文' 或 '英文'，当前值: {self.language}"
            )

    def __str__(self) -> str:
        """返回语言设置的字符串表示"""
        if self.language:
            return f"语言：{self.language}"
        return "无语言设置"

    def validator(
        self,
    ) -> Optional[Callable[[Any, Any, str, str], Tuple[bool, Optional[str]]]]:
        """创建语言验证器

        Returns:
            验证器函数，符合标准验证器接口 (doc, para_or_cell, field_name, field_value) -> (bool, Optional[str])
            如果未设置语言，返回 None
        """
        if not self.language:
            return None

        if self.language == "中文":
            return self._chinese_language_validator()
        elif self.language == "英文":
            return self._english_language_validator()
        else:
            return None

    def _chinese_language_validator(
        self,
    ) -> Callable[[Any, Any, str, str], Tuple[bool, Optional[str]]]:
        """创建中文语言验证器（检查文本是否大部分为中文）

        允许：中文字符、中文标点符号、空格、少量英文字符
        要求：中文字符应占大部分（超过70%）
        """

        def validator(
            doc: Any, para_or_cell: Any, field_name: str, field_value: str
        ) -> Tuple[bool, Optional[str]]:
            if not field_value:
                return True, None
            try:
                # 移除空格和标点符号，只检查实际字符
                text = re.sub(r"[\s\W]", "", field_value)  # 移除空格和所有标点符号
                if not text:
                    return True, None  # 空文本跳过检查

                # 统计中文字符数量
                chinese_chars = re.findall(r"[\u4e00-\u9fa5]", text)
                chinese_count = len(chinese_chars)

                # 统计总字符数量（字母、数字、中文等）
                total_count = len(text)

                if total_count == 0:
                    return True, None  # 空文本跳过检查

                # 计算中文字符比例
                chinese_ratio = chinese_count / total_count

                # 如果中文字符比例低于70%，认为不符合要求
                if chinese_ratio < 0.7:
                    return (
                        False,
                        f"{field_name}应大部分为中文（中文字符应占70%以上），当前中文字符占比为{chinese_ratio:.1%}",
                    )
            except Exception:
                pass
            return True, None

        return validator

    def _english_language_validator(
        self,
    ) -> Callable[[Any, Any, str, str], Tuple[bool, Optional[str]]]:
        """创建英文语言验证器（检查文本是否全部是英文）

        允许：英文字母、数字、英文标点符号、空格
        不允许：中文字符、其他语言的字符
        """

        def validator(
            doc: Any, para_or_cell: Any, field_name: str, field_value: str
        ) -> Tuple[bool, Optional[str]]:
            if not field_value:
                return True, None
            try:
                # 移除空格和常见标点符号，只检查实际字符
                text = re.sub(r"[\s\W]", "", field_value)  # 移除空格和标点符号
                if not text:
                    return True, None  # 空文本跳过检查

                # 检查是否包含非英文字符（中文字符、其他语言字符等）
                # 允许英文字母和数字
                non_english = re.search(
                    r"[^\x00-\x7F]", text
                )  # 检查非ASCII字符（包括中文）
                if non_english:
                    return (
                        False,
                        f"{field_name}应全部为英文，但包含非英文字符（如中文）",
                    )
            except Exception:
                pass
            return True, None

        return validator
