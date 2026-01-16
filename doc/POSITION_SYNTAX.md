# Position 定位语法说明

## 概述

`position` 字段用于定位文档元素，支持四种定位类型：
1. **绝对定位** (`absolute`)：相对于整个文档的绝对位置
2. **相对定位** (`relative`)：相对于其他元素或父区域的相对位置
3. **下一个元素** (`next`)：紧跟在指定元素之后的下一个同级元素
4. **上一个元素** (`prev`)：位于指定元素之前的上一个同级元素

## 1. 绝对定位 (Absolute)

相对于整个文档的绝对位置。

### 语法

```yaml
position:
  type: absolute
  index: <位置>
```

### 支持的位置值

| 值 | 说明 | 示例 |
|----|------|------|
| `0`, `1`, `2`... | 数字索引（从 0 开始） | 第 0 个段落 |
| `-1`, `-2`... | 负数索引（从末尾开始） | 最后一个段落 |

**注意**：只支持数字形式，不支持字符串形式（如 `"first"`, `"last"`）。使用 `0` 表示第一个，`-1` 表示最后一个。

### 示例

```yaml
# 论文标题（文档的第一个段落）
- class: title
  match:
    type: paragraph
    position:
      type: absolute
      index: 0  # 第一个段落
```

## 2. 相对定位 (Relative)

相对于其他元素或父区域的位置。

### 语法

```yaml
position:
  type: relative
  index: <相对位置或区间表达式>
```

### 2.1 相对于其他元素（区间定位）

使用数学区间符号表示两个锚点之间的区域。

#### 区间符号

| 符号 | 说明 | 包含关系 |
|------|------|----------|
| `(a, b)` | 开区间 | 不包含 a 和 b |
| `[a, b)` | 左闭右开 | 包含 a，不包含 b |
| `(a, b]` | 左开右闭 | 不包含 a，包含 b |
| `[a, b]` | 闭区间 | 包含 a 和 b |

#### 锚点类型

锚点可以是：
- **class 名称**：引用其他已识别的元素（如 `title`、`abstract`）
- **pattern**：使用正则表达式匹配（如 `"^摘要："`）
- **position**：绝对位置（如 `0`、`first`、`last`）

#### 示例

```yaml
# 作者区域：标题和摘要之间（不包含标题和摘要本身）
- class: author-section
  match:
    type: paragraph
    position:
      type: relative
      index: (title, abstract)  # 开区间

# 正文区域：摘要之后到参考文献之前（包含摘要，不包含参考文献）
- class: body-section
  match:
    type: paragraph
    position:
      type: relative
      index: [abstract, references-title)  # 左闭右开
```

### 2.2 相对于父区域

用于 `children` 规则中，相对于父区域的位置。

#### 支持的位置值

| 值 | 说明 |
|----|------|
| `0`, `1`, `2`... | 相对于父区域的索引（0表示第一个） |
| `-1`, `-2`... | 相对于父区域的负数索引（-1表示最后一个） |

**注意**：只支持数字形式，不支持字符串形式（如 `"first"`, `"last"`, `"middle"`）。使用 `0` 表示第一个，`-1` 表示最后一个。

#### 示例

```yaml
# 作者区域（父区域）
- class: author-section
  match:
    type: paragraph
    position:
      type: relative
      index: (title, abstract)
  
  # 子元素（相对于父区域）
  children:
    # 第一个元素：作者列表
    - class: author-list
      match:
        position:
          type: relative
          index: 0  # 父区域的第一个（0-based）
        pattern: ".*[,，、].*"
    
    # 中间元素：作者单位（使用区间表达式）
    - class: author-affiliation
      match:
        position:
          type: relative
          index: (author-list, corresponding-author)  # 开区间
    
    # 最后一个元素：通信作者
    - class: corresponding-author
      match:
        position:
          type: relative
          index: -1  # 父区域的最后一个
        pattern: "^\\*"
```

## 3. 下一个元素 (Next)

紧跟在指定元素之后的下一个同级元素。

### 语法

```yaml
position:
  type: next
  class: <元素类名>
  offset: <偏移量>  # 可选，默认为 0
```

### 参数说明

| 参数 | 说明 | 必需 | 默认值 |
|------|------|------|--------|
| `class` | 锚点元素的类名 | 是 | - |
| `offset` | 偏移量（0 表示紧跟的下一个） | 否 | 0 |

### 示例

```yaml
# 英文标题：紧跟在关键词之后
- class: title-en
  match:
    type: paragraph
    position:
      type: next
      class: keywords

# 引言：紧跟在英文关键词之后
- class: heading-introduction
  match:
    type: paragraph
    pattern: "^(引\\s+言|概\\s+述)$"
    position:
      type: next
      class: keywords-en

# 数据采集和处理方法：紧跟在引言之后
- class: heading-data-collection
  match:
    type: paragraph
    pattern: "^1\\s+数据采集和处理方法$"
    position:
      type: next
      class: heading-introduction
```

### 适用场景

- **顺序依赖**：元素按固定顺序出现
- **一对一关系**：每个锚点后只有一个目标元素
- **清晰的文档结构**：如标题的依赖链

### 类比 CSS

类似 CSS 的相邻兄弟选择器 `+`：
```css
h1 + p {  /* 选择紧跟在 h1 后的 p 元素 */
    color: red;
}
```

## 4. 上一个元素 (Prev)

位于指定元素之前的上一个同级元素。

### 语法

```yaml
position:
  type: prev
  class: <元素类名>
  offset: <偏移量>  # 可选，默认为 0
```

### 参数说明

| 参数 | 说明 | 必需 | 默认值 |
|------|------|------|--------|
| `class` | 锚点元素的类名 | 是 | - |
| `offset` | 偏移量（0 表示紧邻的上一个） | 否 | 0 |

### 示例

```yaml
# 某元素：位于参考文献之前
- class: some-element
  match:
    type: paragraph
    position:
      type: prev
      class: references
```

## 完整示例

```yaml
document:
  classifiers:
    # 1. 绝对定位：论文标题
    - class: title
      match:
        type: paragraph
        position:
          type: absolute
          index: 0
    
    # 2. 相对定位（区间）：作者区域
    - class: author-section
      match:
        type: paragraph
        position:
          type: relative
          index: (title, abstract)
      
      # 3. 相对定位（父区域）：作者区域内的子元素
      children:
        - class: author-list
          match:
            position:
              type: relative
              index: 0  # 第一个
            pattern: ".*,.*"
        
        - class: corresponding-author
          match:
            position:
              type: relative
              index: -1  # 最后一个
            pattern: "^\\*"
    
    # 4. 模式匹配：摘要（不需要 position）
    - class: abstract
      match:
        type: paragraph
        pattern: "^摘要："
    
    # 5. 下一个元素：英文标题紧跟在关键词之后
    - class: title-en
      match:
        type: paragraph
        position:
          type: next
          class: keywords
    
    # 6. 下一个元素：引言紧跟在英文关键词之后
    - class: heading-introduction
      match:
        type: paragraph
        pattern: "^(引\\s+言|概\\s+述)$"
        position:
          type: next
          class: keywords-en
```

## 定位类型选择指南

| 场景 | 推荐类型 | 示例 |
|------|----------|------|
| 文档第一个/最后一个元素 | `absolute` | 标题（第0个段落） |
| 两个元素之间的区域 | `relative` (区间) | 作者区域（标题和摘要之间） |
| 父区域内的子元素 | `relative` (索引) | 作者列表（父区域第一个） |
| 元素按固定顺序出现 | `next` | 一级标题依赖链 |
| 元素在某元素之前 | `prev` | 某元素在参考文献之前 |
| 内容特征明显 | 无需 `position` | 摘要（以"摘要："开头） |

## 设计原则

1. **语义清晰**：`type` 字段明确表达定位类型
2. **标准符号**：使用数学区间符号表示包含关系
3. **统一格式**：所有定位都使用 `position: { type, ... }` 结构
4. **灵活组合**：可以与 `pattern`、`type` 等其他匹配条件组合使用
5. **类型明确**：通过 `type` 字段区分不同的定位方式

## 注意事项

1. **依赖顺序**：使用 class 引用时，确保被引用的 class 已定义（系统会自动处理依赖）
2. **循环依赖**：避免 A 依赖 B，B 依赖 A 的情况（系统会检测并报错）
3. **父区域范围**：`children` 中的 `relative` 定位相对于父区域
4. **区间边界**：开区间 `(a, b)` 不包含锚点本身，闭区间 `[a, b]` 包含锚点
5. **数字索引**：只支持数字形式（`0`, `-1`），不支持字符串形式（`"first"`, `"last"`）
6. **类型验证**：
   - `type: absolute/relative` 必须有 `index` 字段
   - `type: next/prev` 必须有 `class` 字段

## 语法演进

### 旧语法（已弃用）

```yaml
# 旧的 after 语法（不推荐）
after:
  class: keywords

# 旧的 before 语法（不推荐）
before:
  class: references
```

### 新语法（推荐）

```yaml
# 新的统一 position 语法
position:
  type: next     # 下一个元素（原 after）
  class: keywords

position:
  type: prev     # 上一个元素（原 before）
  class: references
```

**迁移说明**：
- 旧语法 `after: {class: xxx}` → 新语法 `position: {type: next, class: xxx}`
- 旧语法 `before: {class: xxx}` → 新语法 `position: {type: prev, class: xxx}`

**命名变更说明**：
- `after` → `next`：更明确表示"下一个同级元素"
- `before` → `prev`：更明确表示"上一个同级元素"
- 类似编程中的 `next`/`previous` 概念，语义更清晰