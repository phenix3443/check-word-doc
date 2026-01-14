# 通用规则类使用指南

## 已实现的通用规则类

### 1. FontStyleRule - 字体样式检查

**用途**: 检查字体名称、字号、加粗、斜体等

**配置示例**:

```yaml
# 检查封面标题字体
- id: "FONT001"
  enabled: true
  params:
    description: "封面标题必须使用黑体3号加粗"
    target_blocks: [0]  # 只检查第一个block
    expected_font_name: "黑体"
    expected_font_size: 203200  # 3号 = 16pt = 203200 EMU
    expected_bold: true

# 检查一级标题字体
- id: "HDG002"
  enabled: true
  params:
    description: "一级标题必须使用宋体4号"
    target_styles: ["Heading 1", "Heading 2"]  # 注意：Heading 2 在模板中是一级标题
    expected_font_name: "宋体"
    expected_font_size: 177800  # 4号 = 14pt
    font_name_alternatives: ["Times New Roman"]  # 西文字体允许
```

**参数说明**:
- `target_styles`: 目标段落样式列表
- `target_blocks`: 或指定block索引（如 [0] 或 [0, 5] 表示索引范围）
- `expected_font_name`: 期望字体名称
- `font_name_alternatives`: 备选字体（如西文字体）
- `expected_font_size`: 期望字号（EMU单位，1pt = 12700 EMU）
- `expected_bold`: 是否加粗
- `expected_italic`: 是否斜体

**字号转换表**:
- 初号 = 42pt = 533400 EMU
- 小初号 = 36pt = 457200 EMU
- 一号 = 26pt = 330200 EMU
- 二号 = 22pt = 279400 EMU
- 小二号 = 18pt = 228600 EMU
- 三号 = 16pt = 203200 EMU
- 四号 = 14pt = 177800 EMU
- 小四号 = 12pt = 152400 EMU
- 五号 = 10.5pt = 133350 EMU

---

### 2. ParagraphFormatRule - 段落格式检查

**用途**: 检查行距、对齐、缩进等

**配置示例**:

```yaml
# 检查正文行距
- id: "PAR001"
  enabled: true
  params:
    description: "正文行距必须为1.5倍"
    target_styles: ["Normal", "Body Text"]
    line_spacing: 1.5
    line_spacing_rule: "multiple"
    line_spacing_tolerance: 0.05

# 检查标题对齐
- id: "HDG_ALIGN"
  enabled: true
  params:
    description: "一级标题必须左对齐"
    target_styles: ["Heading 1"]
    alignment: "left"
```

**参数说明**:
- `target_styles`: 目标段落样式
- `line_spacing`: 行距（倍数）
- `line_spacing_rule`: 行距规则（"multiple", "exactly", "atLeast"）
- `line_spacing_tolerance`: 行距容差
- `alignment`: 对齐方式（"left", "center", "right", "justify"）
- `first_line_indent`: 首行缩进（twips，1 inch = 1440 twips）
- `space_before/after`: 段前/段后间距

---

### 3. SequenceRule - 序列/编号检查

**用途**: 检查标题、图表编号连续性

**配置示例**:

```yaml
# 检查标题编号
- id: "HDG001"
  enabled: true
  params:
    description: "标题编号必须连续"
    target_type: "heading"
    numbering_pattern: "^(\\d+)"  # 提取数字编号
    numbering_levels: [1, 2, 3]
    check_continuity: true
    start_from: 1
    heading_styles: ["Heading 1", "Heading 2", "Heading 3"]

# 检查图编号
- id: "FIG_SEQ"
  enabled: true
  params:
    description: "图编号必须连续"
    target_type: "figure"
    numbering_pattern: "^图\\s*(\\d+)"
    check_continuity: true
    start_from: 1
```

**参数说明**:
- `target_type`: 类型（"heading", "figure", "table", "equation"）
- `numbering_pattern`: 编号提取正则（用括号标记提取组）
- `numbering_levels`: 检查的层级
- `check_continuity`: 是否检查连续性
- `start_from`: 起始编号

---

### 4. MatchingRule - 文本匹配检查

**用途**: 检查文本是否符合特定模式

**配置示例**:

```yaml
# 检查数值单位间空格
- id: "UNIT001"
  enabled: true
  params:
    description: "数值和单位间应有空格"
    pattern: "\\d+\\s+[a-zA-Z]+"  # 匹配"10 kg"等
    match_type: "contains"
    case_sensitive: false

# 检查不应包含的内容
- id: "NO_TODO"
  enabled: true
  params:
    description: "文档中不应包含TODO标记"
    pattern: "TODO|FIXME"
    match_type: "contains"
    negate: true  # 反向匹配
```

**参数说明**:
- `pattern`: 正则表达式
- `match_type`: 匹配类型（"contains", "full", "starts", "ends"）
- `target_styles`: 目标样式（可选）
- `case_sensitive`: 大小写敏感
- `negate`: 反向匹配（不应包含）

---

### 5. CountingRule - 数量统计检查

**用途**: 统计元素数量并验证

**配置示例**:

```yaml
# 检查标题数量
- id: "HDG_COUNT"
  enabled: true
  params:
    description: "一级标题应该有5-8个"
    target_type: "heading"
    target_styles: ["Heading 1"]
    min_count: 5
    max_count: 8

# 检查表格数量
- id: "TABLE_COUNT"
  enabled: true
  params:
    description: "文档至少包含3个表格"
    target_type: "table"
    min_count: 3
```

**参数说明**:
- `target_type`: 类型（"paragraph", "table", "heading"）
- `target_styles`: 目标样式（用于筛选）
- `pattern`: 文本筛选模式（可选）
- `min_count`: 最小数量
- `max_count`: 最大数量
- `exact_count`: 精确数量

---

### 6. RelationRule - 关系检查

**用途**: 检查元素间的关系

**配置示例**:

```yaml
# 检查表格题注在表格前
- id: "TBL002"
  enabled: true
  params:
    description: "表题注必须在表格前"
    element_a_type: "table"
    element_b_type: "paragraph"
    element_b_pattern: "^表\\s*\\d+"
    relation_type: "before"
    max_distance: 2
```

**参数说明**:
- `element_a_type`: 元素A类型
- `element_b_type`: 元素B类型
- `element_b_pattern`: 元素B的文本模式
- `relation_type`: 关系类型（"before", "after", "paired"）
- `max_distance`: 最大距离（blocks数）

---

## 配置文件完整示例

```yaml
# data_paper_with_generic_rules.yaml

description: "使用通用规则类的数据论文模板"

rules:
  # === 封面检查 ===
  - id: "FONT001"
    enabled: true
    params:
      description: "封面标题使用黑体3号加粗"
      target_blocks: [0]
      expected_font_name: "黑体"
      expected_font_size: 203200
      expected_bold: true
  
  - id: "FONT002"
    enabled: true
    params:
      description: "封面作者信息使用华文楷体小4号"
      target_blocks: [1, 2, 3, 4]
      expected_font_name: "华文楷体"
      expected_font_size: 152400
      font_name_alternatives: ["Times New Roman"]
  
  # === 标题格式 ===
  - id: "HDG001"
    enabled: true
    params:
      description: "标题编号必须连续"
      target_type: "heading"
      numbering_pattern: "^(\\d+)"
      check_continuity: true
  
  - id: "HDG002"
    enabled: true
    params:
      description: "一级标题使用宋体4号"
      target_styles: ["Heading 2"]
      expected_font_name: "宋体"
      expected_font_size: 177800
  
  # === 段落格式 ===
  - id: "PAR001"
    enabled: true
    params:
      description: "正文行距1.5倍"
      target_styles: ["Normal"]
      line_spacing: 1.5
      line_spacing_tolerance: 0.05
  
  # === 结构检查 ===
  - id: "COV001"
    enabled: true
    params:
      description: "必须包含封面"
      keywords: ["数据集", "作者", "单位", "摘要"]
      check_first_n_blocks: 10
  
  - id: "STRUCT001"
    enabled: true
    params:
      description: "必须包含引言章节"
      keywords: ["引言", "概述"]
      style_prefixes: ["Heading"]
```

---

## 使用通用规则类的优势

### 1. 代码复用

同一个 `FontStyleRule` 可以检查：
- 封面标题字体（FONT001）
- 封面作者字体（FONT002）
- 一级标题字体（HDG002）
- 二级标题字体（HDG003）
- ...

只需改变配置参数！

### 2. 易于扩展

添加新文档类型只需编写配置文件，无需修改代码。

### 3. 配置驱动

用户可以自定义规则参数，无需懂Python。

### 4. 灵活组合

通过组合多个简单规则实现复杂检查。

---

## 从配置到规则实例的流程

```
1. 配置文件 (data_paper_template.yaml)
   ↓
2. ConfigLoader 加载和合并配置
   ↓
3. build_rules() 读取 rules 列表
   ↓
4. 根据 rule_id 查找 _RULE_CLASSES
   ↓
5. 使用 params 创建规则实例
   ↓
6. 过滤参数（只保留类接受的参数）
   ↓
7. 规则实例列表
   ↓
8. DocxLint 引擎运行规则
```

---

## 常见问题

### Q1: 如何知道某个参数对应哪个规则类？

A: 查看 `registry.py` 中的 `_RULE_CLASSES` 映射，或查看 `format_rules.py` 中规则类的文档字符串。

### Q2: 能否在配置中直接指定规则类而非规则ID？

A: 目前需要通过 rule_id 映射，但可以在配置中使用通用名称如 "SequenceRule"。

### Q3: 参数名称必须完全匹配吗？

A: 是的，参数名称必须与规则类的 `__init__` 方法参数匹配。多余的参数会被自动过滤。

### Q4: 如何调试规则？

A: 检查以下几点：
1. 规则是否在 `_RULE_CLASSES` 中注册
2. 参数名称是否正确
3. 使用 `poetry run python -c "..."` 测试规则创建

---

## 下一步

1. 实现更多通用规则类（OrderingRule, ConsistencyRule等）
2. 为每个规则类编写单元测试
3. 创建更多模板配置示例
4. 完善文档和使用指南
