"""规则注册表

从声明式配置动态创建规则实例
"""

from __future__ import annotations

from typing import List

from script.core.rule import Rule


def build_rules(config: dict) -> List[Rule]:
    """从声明式配置构建规则列表

    配置格式:
    document:
      defaults:
        font_size: 10.5pt
      structure:
        - type: paragraph
          name: 标题
          content: {...}
          font: {...}
          paragraph: {...}
      headings:
        styles: [...]
        check_sequence: true
        check_hierarchy: true
      references:
        heading: 参考文献
        check_citations: true

    Args:
        config: 配置字典（必须包含 document 节）

    Returns:
        规则实例列表

    Raises:
        ValueError: 如果配置格式不正确
    """
    if "document" not in config:
        raise ValueError(
            "配置文件必须使用声明式格式（包含 'document' 节）。\n"
            "请参考 config/data_paper_declarative.yaml 示例。"
        )

    return _build_rules_from_declarative(config)


def _build_rules_from_declarative(config: dict) -> List[Rule]:
    """从声明式配置构建规则

    Args:
        config: 配置字典（包含 document 节）

    Returns:
        规则实例列表
    """
    from script.core.rule_generator import generate_rules_from_config

    try:
        rules = generate_rules_from_config(config)
        return rules
    except Exception as e:
        print(f"❌ 规则生成失败: {e}")
        import traceback

        traceback.print_exc()
        return []
