# 通用规则类设计指南

## 设计目标

构建一套**足够抽象**的通用规则类，通过**配置参数**适配不同文档类型，避免为每个文档编写专用代码。

## 核心原则

### 1. 一个规则类 = 一种检查模式

规则类应该代表**检查逻辑**，而非**检查对象**：

- ✅ `PresenceRule` - 检查"存在性"（适用于封面、目录、参考文献等）
- ✅ `FormatRule` - 检查"格式"（适用于标题、段落、表格等）
- ❌ `CoverRule` - 只能检查封面（过于具体）
- ❌ `TocRule` - 只能检查目录（过于具体）

### 2. 参数化 = 可配置性

所有文档特异性通过参数传入：

```python
class PresenceRule:
    def __init__(
        self,
        id: str,
        description: str,
        # 可配置参数
        keywords: List[str],           # 搜索关键词
        title_text: str = None,        # 精确标题
        style_prefixes: List[str] = None,  # 样式前缀
        check_first_n_blocks: int = None,  # 检查范围
        optional: bool = False,        # 是否可选
        **kwargs
    ):
        # 通用逻辑不变，行为由参数控制
        pass
```

### 3. 组合优于继承

通过组合不同规则类实现复杂检查：

```yaml
# 复杂检查 = 多个简单规则组合
rules:
  - id: "REF_CHECK_1"
    rule_class: PresenceRule
    params:
      title_text: "参考文献"
  
  - id: "REF_CHECK_2"
    rule_class: CitationRule
    params:
      citation_pattern: "\\[\\d+\\]"
  
  - id: "REF_CHECK_3"
    rule_class: HeadingLevelRule
    params:
      title_text: "参考文献"
      required_level: 1
```

## 推荐的通用规则类清单

### 一、内容检查类

#### 1. `PresenceRule` - 存在性检查

**用途**: 检查文档是否包含某个元素（章节、关键词等）

**参数**:
```python
{
    "keywords": ["关键词1", "关键词2"],  # OR 匹配
    "title_text": "精确标题",            # 精确匹配
    "alternative_titles": ["标题A", "标题B"],  # 备选标题
    "style_prefixes": ["Heading", "Title"],    # 样式限制
    "check_first_n_blocks": 10,          # 检查范围
    "min_keyword_matches": 2,            # 最少匹配数
    "optional": false                    # 是否可选
}
```

**适用场景**:
- COV001: 封面检查
- TOC001: 目录检查
- REF001: 参考文献检查
- 任何需要验证"是否存在XX章节/元素"的场景

---

#### 2. `MatchingRule` - 文本匹配检查

**用途**: 检查文本内容是否符合特定模式

**参数**:
```python
{
    "pattern": "regex_pattern",          # 正则表达式
    "match_type": "contains|full|starts",  # 匹配类型
    "target_styles": ["Normal"],         # 目标样式
    "case_sensitive": true,              # 大小写敏感
    "negate": false                      # 反向匹配（不应包含）
}
```

**适用场景**:
- 检查标题编号格式：`"pattern": "^\\d+\\.\\d+"`
- 检查邮箱格式：`"pattern": "[a-z]+@[a-z]+\\.com"`
- 检查不应出现的内容：`"negate": true`

---

#### 3. `CountingRule` - 数量统计检查

**用途**: 统计某类元素的数量并验证

**参数**:
```python
{
    "target_type": "paragraph|table|image",  # 统计对象
    "pattern": "regex",                 # 筛选模式
    "min_count": 1,                     # 最小数量
    "max_count": 100,                   # 最大数量
    "exact_count": null                 # 精确数量
}
```

**适用场景**:
- 图表数量限制
- 参考文献数量检查
- 章节数量验证

---

### 二、格式检查类

#### 4. `FontStyleRule` - 字体样式检查

**用途**: 检查字体、字号、颜色、加粗等

**参数**:
```python
{
    "target_styles": ["Heading 1"],      # 目标样式
    "target_blocks": [0, 5],             # 或指定block范围
    "expected_font_name": "宋体",         # 期望字体
    "font_name_alternatives": ["Times"], # 备选字体
    "expected_font_size": 228600,        # 期望字号（EMU）
    "font_size_tolerance": 635,          # 容差
    "expected_bold": true,               # 是否加粗
    "expected_italic": false,            # 是否斜体
    "expected_color": "000000",          # 颜色（RGB）
    "check_consistency": true            # 检查一致性
}
```

**适用场景**:
- FONT001-004: 封面、标题、正文字体检查
- 任何需要验证字体格式的场景

---

#### 5. `ParagraphFormatRule` - 段落格式检查

**用途**: 检查行距、对齐、缩进、间距等

**参数**:
```python
{
    "target_styles": ["Normal"],
    "line_spacing": 1.5,                 # 行距
    "line_spacing_tolerance": 0.05,      # 容差
    "alignment": "left|center|right|justify",  # 对齐
    "first_line_indent": 635,            # 首行缩进（twips）
    "left_indent": 0,                    # 左缩进
    "right_indent": 0,                   # 右缩进
    "space_before": 0,                   # 段前间距
    "space_after": 0                     # 段后间距
}
```

**适用场景**:
- PAR001: 行距检查
- 段落缩进检查
- 对齐方式检查

---

#### 6. `TableFormatRule` - 表格格式检查

**用途**: 检查表格尺寸、边框、对齐等

**参数**:
```python
{
    "min_rows": 2,
    "max_rows": 100,
    "min_cols": 2,
    "max_cols": 20,
    "check_header_row": true,            # 检查标题行
    "header_row_bold": true,             # 标题行加粗
    "check_borders": true,               # 检查边框
    "border_style": "single|double|none",
    "cell_alignment": "left|center|right"
}
```

**适用场景**:
- T001: 表格尺寸检查
- 表格样式统一性检查

---

### 三、结构检查类

#### 7. `SequenceRule` - 序列/编号检查

**用途**: 检查编号连续性（标题、图表、公式等）

**参数**:
```python
{
    "target_type": "heading|figure|table|equation",
    "numbering_pattern": "^(\\d+)\\.",   # 编号提取正则
    "numbering_levels": [1, 2, 3],       # 层级
    "check_continuity": true,            # 检查连续性
    "allow_skips": false,                # 允许跳号
    "start_from": 1                      # 起始编号
}
```

**适用场景**:
- HDG001: 标题编号连续性
- 图表编号连续性
- 公式编号连续性

---

#### 8. `OrderingRule` - 顺序检查

**用途**: 检查章节/元素出现顺序

**参数**:
```python
{
    "required_sequence": [               # 必需顺序
        {"title": "摘要", "optional": false},
        {"title": "目录", "optional": true},
        {"title": "正文", "optional": false},
        {"title": "参考文献", "optional": false}
    ],
    "strict_order": true                 # 严格顺序
}
```

**适用场景**:
- 验证文档章节顺序
- 验证图表目录位置

---

#### 9. `RelationRule` - 关系检查

**用途**: 检查元素间的关系（前后、配对等）

**参数**:
```python
{
    "element_a": {
        "type": "table",
        "pattern": null
    },
    "element_b": {
        "type": "paragraph",
        "pattern": "^表\\s*\\d+"          # 表题注
    },
    "relation_type": "before|after|paired",
    "max_distance": 2,                   # 最大距离（blocks）
    "required": true
}
```

**适用场景**:
- FIG002: 图题注在图后
- TBL002: 表题注在表前
- 表格与数据对应关系

---

### 四、内容规范类

#### 10. `PunctuationRule` - 标点符号检查

**用途**: 检查标点符号使用

**参数**:
```python
{
    "target_styles": ["Normal"],
    "check_ending": true,                # 检查结尾
    "required_ending": ["。", "；"],      # 允许的结尾
    "forbidden_chars": [",", "."],       # 禁止字符
    "check_pairing": true,               # 检查配对
    "pairs": [["(", ")"], ["「", "」"]],
    "min_length": 10                     # 最小长度（触发检查）
}
```

**适用场景**:
- PAR003: 段落末尾标点
- PAR006: 引号配对
- 中英文标点混用检查

---

#### 11. `SpacingRule` - 空格/间距检查

**用途**: 检查字符间空格、连续空行等

**参数**:
```python
{
    "check_chinese_spacing": true,       # 中文间不应有空格
    "check_unit_spacing": true,          # 数值单位间应有空格
    "units": ["m", "kg", "℃"],
    "max_consecutive_spaces": 1,         # 最多连续空格
    "max_consecutive_empty_lines": 1,    # 最多连续空行
    "exceptions": ["%"]                  # 例外情况
}
```

**适用场景**:
- PAR004: 中文字符间空格
- PAR007: 连续空行
- UNIT001: 数值单位间空格

---

#### 12. `CitationRule` - 引用检查

**用途**: 检查参考文献引用格式和完整性

**参数**:
```python
{
    "citation_pattern": "\\[\\d+\\]",    # 引用格式
    "citation_style": "superscript|inline",  # 引用样式
    "check_all_cited": true,             # 所有文献被引用
    "check_all_exist": true,             # 所有引用有对应文献
    "reference_section": "参考文献"       # 参考文献章节标题
}
```

**适用场景**:
- REF002: 参考文献引用检查
- 引用格式统一性

---

### 五、特殊检查类

#### 13. `ConsistencyRule` - 一致性检查

**用途**: 检查相同类型元素的一致性

**参数**:
```python
{
    "check_type": "font|style|format",
    "target_elements": ["Heading 1"],
    "properties": ["font_name", "font_size", "bold"],
    "allow_variance": 0.05               # 允许的差异
}
```

**适用场景**:
- 所有一级标题格式一致
- 所有表格样式一致
- 所有图题注格式一致

---

#### 14. `CustomPatternRule` - 自定义模式检查

**用途**: 通过自定义规则灵活检查

**参数**:
```python
{
    "pattern": "custom_regex",
    "extraction_groups": [1, 2],         # 提取组
    "validation_function": "builtin_func_name",  # 内置验证函数
    "validation_params": {},
    "error_template": "错误：{0} 不符合要求 {1}"
}
```

**适用场景**:
- 特殊格式验证
- 复杂逻辑检查
- 扩展点

---

## 配置文件结构

### 基本模板配置

```yaml
# template_name.yaml

description: "模板描述"

# 导入其他配置（可选）
import:
  - "base_common.yaml"

# 规则定义
rules:
  - id: "RULE_ID"
    enabled: true
    rule_class: "RuleClassName"  # 对应上面的通用规则类
    params:
      description: "规则描述"
      # ... 规则特定参数
    severity: "error|warning|info"

# 全局设置
settings:
  strict_mode: false
  ignore_styles: ["Header", "Footer"]
```

### 规则 ID 命名规范

```
[类别][编号]

类别代码:
  COV - 封面 (Cover)
  TOC - 目录 (Table of Contents)
  HDG - 标题 (Heading)
  PAR - 段落 (Paragraph)
  REF - 参考文献 (References)
  FIG - 图 (Figure)
  TBL - 表 (Table)
  EQN - 公式 (Equation)
  FNT - 字体 (Font)
  FMT - 格式 (Format)
  STR - 结构 (Structure)
  ...

示例:
  COV001 - 封面第1条规则
  HDG001 - 标题第1条规则
  PAR003 - 段落第3条规则
```

## 扩展指南

### 何时需要新的通用规则类？

当满足以下条件时，考虑添加新规则类：

1. **新的检查模式**：现有规则类无法覆盖
2. **高复用性**：多个文档模板都需要
3. **清晰的抽象**：能明确定义参数和行为
4. **不可组合**：无法通过组合现有规则实现

### 如何添加新规则类？

1. 在 `script/rules/` 创建新文件
2. 继承 `Rule` 或 `FinalizeRule`
3. 定义清晰的 `__init__` 参数
4. 实现 `check()` 或 `finalize()` 方法
5. 在 `registry.py` 注册规则类
6. 编写单元测试
7. 更新本文档

示例：

```python
# script/rules/custom_rules.py

from script.core.rule import Rule
from script.core.model import Issue, Severity, Location

class MyNewRule(Rule):
    """新的通用规则类：XXX检查"""
    
    def __init__(
        self,
        id: str,
        description: str,
        # 清晰定义所有参数
        param1: str,
        param2: int = 10,
        **kwargs
    ):
        self.id = id
        self.description = description
        self.param1 = param1
        self.param2 = param2
    
    def applies_to(self, block, ctx) -> bool:
        """判断规则是否适用于该block"""
        return True  # 或根据条件返回
    
    def check(self, block, ctx) -> List[Issue]:
        """执行检查"""
        issues = []
        # 检查逻辑
        return issues
```

```python
# script/rules/registry.py

from script.rules.custom_rules import MyNewRule

_RULE_CLASSES = {
    # ... 现有规则
    "MY001": MyNewRule,
}
```

## 最佳实践

### 1. 参数命名规范

- 使用描述性名称：`expected_font_name` 而非 `font`
- 布尔参数用 `check_*` 或 `is_*` 前缀
- 列表参数用复数：`keywords`、`styles`
- 提供合理默认值

### 2. 错误消息模板化

```python
def check(self, block, ctx):
    if error:
        return [Issue(
            code=self.id,
            severity=Severity.ERROR,
            message=f"{self.description}: {具体错误原因}",
            location=Location(...),
            evidence={"expected": xxx, "actual": yyy}
        )]
```

### 3. 性能考虑

- 在 `applies_to()` 中快速过滤
- 缓存重复计算的结果
- 避免在循环中重复编译正则表达式

### 4. 向后兼容

- 新增参数提供默认值
- 不删除已有参数
- 标记废弃参数而非直接删除

## 示例：完整配置

```yaml
# example_template.yaml

description: "示例文档模板"

rules:
  # 使用 PresenceRule 检查封面
  - id: "COV001"
    rule_class: PresenceRule
    params:
      description: "必须包含封面"
      keywords: ["题目", "作者"]
      check_first_n_blocks: 10
  
  # 使用 FontStyleRule 检查标题字体
  - id: "HDG001"
    rule_class: FontStyleRule
    params:
      description: "一级标题必须使用黑体3号"
      target_styles: ["Heading 1"]
      expected_font_name: "黑体"
      expected_font_size: 203200
  
  # 使用 ParagraphFormatRule 检查行距
  - id: "PAR001"
    rule_class: ParagraphFormatRule
    params:
      description: "正文行距必须为1.5倍"
      target_styles: ["Normal"]
      line_spacing: 1.5
      line_spacing_tolerance: 0.05
  
  # 使用 SequenceRule 检查编号
  - id: "SEQ001"
    rule_class: SequenceRule
    params:
      description: "标题编号必须连续"
      target_type: "heading"
      numbering_pattern: "^(\\d+)\\."
      check_continuity: true

settings:
  strict_mode: false
```

## 总结

通过这套通用规则类体系：

- ✅ **14 个通用规则类** 覆盖 90% 的常见检查需求
- ✅ **配置驱动** 无需修改代码即可适配新文档
- ✅ **易于扩展** 清晰的扩展指南和规范
- ✅ **高度复用** 一个规则类服务多个规则 ID

**核心思想**：代码实现检查逻辑，配置定义检查对象。
