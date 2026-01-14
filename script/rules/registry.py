"""规则注册表

根据配置文件动态创建规则实例
"""

from __future__ import annotations

from typing import Any, Dict, List, Type

from script.core.rule import Rule

# 导入通用规则类
from script.rules.structure_rules import (
    HeadingHierarchyRule,
    HeadingNumberingRule,
    PageAccuracyRule,
    PageContinuityRule,
    PresenceRule,
)
from script.rules.paragraph_rules import (
    ChineseQuoteMatchingRule,
    ChineseSpacingRule,
    ConsecutiveEmptyRule,
    EnglishQuotesRule,
    ParagraphContentRule,
    PunctuationRule,
)
from script.rules.reference_rules import (
    CitationValidationRule,
    ReferencesCitationRule,
    ReferencesHeadingLevelRule,
    ReferencesHeadingRule,
)
from script.rules.format_rules import (
    CountingRule,
    FontStyleRule,
    MatchingRule,
    ParagraphFormatRule,
    RelationRule,
    SequenceRule,
)
from script.rules.smoke import SmokeRule
from script.rules.table import KeyValueTableRule, TableCaptionPairRule, TableDimensionsRule


# 规则 ID 到规则类的映射
# 使用通用规则类，通过配置参数控制具体行为
_RULE_CLASSES: Dict[str, Type[Rule]] = {
    # 测试规则
    "SMOKE": SmokeRule,
    
    # === 表格规则 ===
    "T-001": TableDimensionsRule,
    "T-003": KeyValueTableRule,
    "T-010": TableCaptionPairRule,
    "TBL-002": TableCaptionPairRule,  # 表格题注位置检查
    "FIG-002": TableCaptionPairRule,  # 图片题注位置检查（复用表格规则）
    
    # === 结构规则（使用 PresenceRule）===
    # 首页元素（学术论文）
    "TITLE-001": ParagraphContentRule,  # 标题内容检查（首页第一段）
    "AUTHOR-001": PresenceRule,  # 作者信息存在性
    "ABSTRACT-001": PresenceRule,  # 中文摘要存在性
    "ABSTRACT-002": PresenceRule,  # 英文摘要存在性
    "KEYWORDS-001": PresenceRule,  # 关键词存在性
    # 封面（技术文档）
    "COV-001": PresenceRule,  # 封面存在性
    # 目录
    "TOC-001": PresenceRule,  # 目录存在性
    "FIG-001": PresenceRule,  # 插图目录存在性
    "TBL-001": PresenceRule,  # 附表目录存在性
    "STRUCT-001": PresenceRule,  # 通用章节存在性
    "STRUCT-002": PresenceRule,
    "STRUCT-003": PresenceRule,
    "STRUCT-004": PresenceRule,
    "STRUCT-005": PresenceRule,
    "STRUCT-006": PresenceRule,
    "STRUCT-007": PresenceRule,
    "ACK-001": PresenceRule,  # 致谢章节
    "AUTH-001": PresenceRule,  # 作者分工章节
    
    # === 结构规则（页码）===
    "TOC-002": PageContinuityRule,  # 目录页码连续性
    "FIG-002": PageContinuityRule,  # 插图目录页码连续性
    "TOC-003": PageAccuracyRule,  # 目录页码准确性
    "FIG-003": PageAccuracyRule,  # 插图目录页码准确性
    "TBL-003": PageAccuracyRule,  # 附表目录页码准确性
    
    # === 标题规则 ===
    "HDG-001": HeadingNumberingRule,  # 同级标题编号连续性
    "HDG-002": HeadingHierarchyRule,  # 标题编号层级一致性
    "HDG-003": FontStyleRule,  # 一级标题样式（通用）
    "HDG-004": FontStyleRule,  # 二级标题样式（通用）
    "HDG-005": FontStyleRule,  # 三级标题样式（通用）
    
    # === 段落规则 ===
    "PAR-001": ParagraphFormatRule,  # 行距检查（通用）
    "PAR-001-TITLE": ParagraphFormatRule,  # 标题段落格式
    "PAR-002": ConsecutiveEmptyRule,  # 连续空段落
    "PAR-003": PunctuationRule,  # 段落末尾标点
    "PAR-004": ChineseSpacingRule,  # 中文字符间空格
    "PAR-005": EnglishQuotesRule,  # 英文引号检查
    "PAR-006": ChineseQuoteMatchingRule,  # 中文引号配对
    "PAR-007": ConsecutiveEmptyRule,  # 连续空行
    
    # === 参考文献规则 ===
    # 注意：基础配置中的 REF-001/002 是条件规则（只在有参考文献章节时检查）
    # REF-003 等用于文档模板配置
    "REF-001": ReferencesCitationRule,  # 参考文献必须被引用（基础规则）
    "REF-002": CitationValidationRule,  # 引用必须在参考文献列表中（基础规则）
    "REF-003": ReferencesHeadingLevelRule,  # 参考文献标题级别（模板用）
    "REF_HEADING": ReferencesHeadingRule,  # 参考文献标题存在性（模板用）
    "REF_LEVEL": ReferencesHeadingLevelRule,  # 参考文献标题级别（模板用）
    
    # === 字体格式规则（通用）===
    "FONT-001": FontStyleRule,  # 封面标题字体
    "FONT-002": FontStyleRule,  # 封面作者字体
    "FONT-003": FontStyleRule,  # 摘要关键词字体
    "FONT-004": FontStyleRule,  # 正文字体
    
    # === 数值单位规则（使用通用规则）===
    "UNIT-001": MatchingRule,  # 数值单位间空格（使用 MatchingRule）
    "UNIT-002": PresenceRule,  # 量、单位和符号章节
    
    # === 通用规则类（可直接在配置中引用）===
    "SequenceRule": SequenceRule,  # 序列编号检查
    "CountingRule": CountingRule,  # 数量统计检查
    "MatchingRule": MatchingRule,  # 文本匹配检查
    "RelationRule": RelationRule,  # 关系检查
}


def build_rules(config: dict) -> List[Rule]:
    """根据配置构建规则列表
    
    支持两种配置格式：
    
    1. 传统格式（命令式）:
    rules:
      - id: "COV-001"
        enabled: true
        params:
          description: "文档必须包含封面"
          required: true
          keywords: ["题目", "标题", "作者"]
    
    2. 声明式格式:
    document:
      defaults:
        font_size: 10.5pt
      structure:
        - type: paragraph
          name: 标题
          content: {...}
          font: {...}
          paragraph: {...}
    
    Args:
        config: 配置字典
        
    Returns:
        规则实例列表
    """
    # 检查是否是声明式配置
    if "document" in config:
        return _build_rules_from_declarative(config)
    
    # 传统配置格式
    return _build_rules_from_legacy(config)


def _build_rules_from_legacy(config: dict) -> List[Rule]:
    """从传统配置格式构建规则
    
    Args:
        config: 配置字典
        
    Returns:
        规则实例列表
    """
    rules_cfg = config.get("rules", [])
    if not isinstance(rules_cfg, list):
        return []

    rules: List[Rule] = []
    for item in rules_cfg:
        if not isinstance(item, dict):
            continue

        rule_id = item.get("id")
        if not isinstance(rule_id, str) or not rule_id:
            continue

        # 检查是否启用
        enabled = item.get("enabled", True)
        if enabled is False:
            continue

        # 获取规则类
        rule_class = _RULE_CLASSES.get(rule_id)
        if rule_class is None:
            print(f"Warning: Unknown rule ID: {rule_id}")
            continue

        # 获取参数
        params = item.get("params", {})
        if params is None:
            params = {}
        if not isinstance(params, dict):
            params = {}

        # 添加 id 到参数中（规则类需要 id 参数）
        params["id"] = rule_id

        # 过滤参数（只保留规则类接受的参数）
        filtered_params = _filter_kwargs(rule_class, params)

        # 创建规则实例
        try:
            rule_instance = rule_class(**filtered_params)
            rules.append(rule_instance)
        except Exception as e:
            print(f"Error creating rule {rule_id}: {e}")
            continue

    return rules


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
        
        # 如果配置中还包含额外的传统格式规则，也加载它们
        if "rules" in config:
            legacy_rules = _build_rules_from_legacy(config)
            rules.extend(legacy_rules)
        
        return rules
    except Exception as e:
        print(f"Error building rules from declarative config: {e}")
        import traceback
        traceback.print_exc()
        return []


def _filter_kwargs(cls: Type[Any], params: dict) -> dict:
    """过滤参数，只保留类构造函数接受的参数
    
    Args:
        cls: 类
        params: 参数字典
        
    Returns:
        过滤后的参数字典
    """
    # 获取类的 __init__ 方法的参数名
    import inspect

    sig = inspect.signature(cls.__init__)
    allowed = set(sig.parameters.keys())
    allowed.discard("self")

    return {k: v for k, v in params.items() if k in allowed}
