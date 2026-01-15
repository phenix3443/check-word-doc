# 配置文件格式说明

## 概述

配置文件采用 YAML 格式，包含两个核心部分：
1. **classifiers**：元素识别规则（给元素打标签）
2. **styles**：样式定义（定义每个 class 应有的格式）

## 基本结构

```yaml
document:
  # 全局默认样式（可选）
  defaults:
    font:
      size: 小四
      name_eastasia: 宋体
      name_ascii: "Times New Roman"
    paragraph:
      line_spacing: 1.5倍
  
  # 元素识别规则
  classifiers:
    - class: class-name
      match:
        # 匹配条件
  
  # 样式定义
  styles:
    .class-name:
      font:
        # 字体样式
      paragraph:
        # 段落格式
```

## classifiers 详解

### 基本语法

```yaml
classifiers:
  - class: class-name  # 要添加的 class 名称
    match:
      type: paragraph/table  # 元素类型
      # ... 其他匹配条件
```

### 匹配条件类型

#### 1. 绝对位置匹配 (position)

匹配文档中固定位置的元素。

```yaml
- class: title
  match:
    type: paragraph
    position: 0  # 文档第一个段落（从 0 开始计数）
```

**参数说明：**
- `position: N` - 第 N 个段落（0-based）
- `position: 0` - 第一个段落
- `position: -1` - 最后一个段落

#### 2. 内容模式匹配 (pattern)

根据段落内容匹配。

```yaml
- class: abstract
  match:
    type: paragraph
    pattern: "^摘要[:：]"  # 正则表达式
```

**参数说明：**
- `pattern` - 正则表达式字符串
- 匹配段落的文本内容
- 常用模式：
  - `^摘要[:：]` - 以"摘要："开头
  - `^关键词[:：]` - 以"关键词："开头
  - `^\\d+\\.` - 以数字和点开头（如 "1. xxx"）
  - `^\\*` - 以 * 开头
  - `.*[,，].*` - 包含逗号

#### 3. 相对位置匹配 (after/before)

相对于其他元素定位。

```yaml
- class: author-list
  match:
    type: paragraph
    after:
      class: title  # 在 title 之后
    offset: 0  # 偏移量（可选，默认 0）
```

**参数说明：**
- `after: {class: xxx}` - 在具有 xxx class 的元素之后
- `before: {class: xxx}` - 在具有 xxx class 的元素之前
- `offset: N` - 偏移量（0 表示紧接着，1 表示隔一个）

**示例：**
```yaml
# 紧接在标题后的段落
- class: subtitle
  match:
    type: paragraph
    after: {class: title}
    offset: 0

# 标题后第二个段落
- class: date
  match:
    type: paragraph
    after: {class: title}
    offset: 1
```

#### 4. 范围匹配 (range)

匹配两个锚点之间的所有元素。

```yaml
- class: author-affiliation
  match:
    type: paragraph
    range:
      after: {class: author-list}
      before: {class: abstract}
    pattern: "^\\d+\\."  # 可选：范围内进一步筛选
```

**参数说明：**
- `range.after` - 范围起点（不包含）
- `range.before` - 范围终点（不包含）
- `pattern` - 可选，范围内进一步筛选

**锚点定义方式：**
```yaml
# 1. 通过 class 引用
after: {class: title}

# 2. 通过绝对位置
after: {position: 0}

# 3. 通过内容模式
before: {pattern: "^摘要[:：]"}
```

#### 5. 组合匹配

可以组合多个条件。

```yaml
- class: corresponding-author
  match:
    type: paragraph
    range:
      after: {class: author-list}
      before: {class: abstract}
    pattern: "^\\*"  # 必须以 * 开头
```

#### 6. 复合区域匹配 (children) ⭐

对于复杂的文档结构，可以定义**复合区域**，在父区域内使用**相对定位**匹配子元素。

```yaml
# 作者区域（复合区域）
- class: author-section
  match:
    type: paragraph
    range:
      after: {class: title}
      before: {pattern: "^摘要："}
  # 子元素规则（相对于父区域）
  children:
    # 第一个子元素
    - class: author-list
      match:
        position: first  # 相对位置
        pattern: ".*[,，].*"
    
    # 中间的子元素
    - class: author-affiliation
      match:
        position: middle  # 范围内的中间元素
        pattern: "^\\d+\\."
    
    # 最后一个子元素
    - class: corresponding-author
      match:
        position: last  # 相对位置
        pattern: "^\\*"
```

**相对位置关键字：**
- `first` - 父区域的第一个元素
- `last` - 父区域的最后一个元素
- `middle` - 父区域的中间元素（不包括首尾）
- 数字索引 - 相对于父区域的索引（如 `0`, `1`, `-1`）

**优势：**
- ✅ 灵活适应可变数量的元素（如多个作者单位）
- ✅ 语义清晰，表达文档的层次结构
- ✅ 相对定位，不依赖绝对位置

### 多 class 支持 ⭐

**重要特性**：一个元素可以匹配多个规则，拥有多个 class（类似 HTML）。

```yaml
# 示例：让标题同时拥有多个 class
classifiers:
  - class: title
    match: {position: 0}
  
  - class: important
    match: {position: 0}
  
  - class: first-element
    match: {position: 0}

# 结果：第一个段落会有 3 个 class
# <p class="title important first-element">...</p>
```

**应用场景：**
- 通用样式 + 特定样式组合
- 多个维度的分类（位置 + 内容 + 类型）
- 样式继承和组合

### 匹配顺序

classifiers 按照定义顺序执行：
- 先定义的规则先执行
- 后面的规则可以引用前面规则定义的 class
- 一个元素可以匹配多个规则，拥有多个 class

**示例：**
```yaml
classifiers:
  # 1. 先识别标题
  - class: title
    match:
      position: 0
  
  # 2. 再识别标题后的元素（依赖 title）
  - class: author-list
    match:
      after: {class: title}
      pattern: ".*[,，].*"
  
  # 3. 然后识别作者列表后的元素（依赖 author-list）
  - class: author-affiliation
    match:
      range:
        after: {class: author-list}
        before: {pattern: "^摘要[:：]"}
      pattern: "^\\d+\\."
```

## styles 详解

### 基本语法

```yaml
styles:
  .class-name:
    font:
      # 字体属性
    paragraph:
      # 段落属性
```

### 字体属性 (font)

```yaml
.title:
  font:
    name_eastasia: 黑体      # 中文字体
    name_ascii: "Times New Roman"  # 西文字体
    size: 三号               # 字号
    bold: true              # 是否加粗
    italic: false           # 是否斜体
```

**字号支持的格式：**
- 中文字号：`初号`, `小初`, `一号`, `小一`, `二号`, `小二`, `三号`, `小三`, `四号`, `小四`, `五号`, `小五`, `六号`, `小六`
- 磅数：`16pt`, `12pt` 等
- 数字：`16`, `12` 等（默认为磅）

**字体名称：**
- `name_eastasia` - 中文字体（如：宋体、黑体、楷体）
- `name_ascii` - 西文字体（如：Times New Roman、Arial）

### 段落属性 (paragraph)

```yaml
.title:
  paragraph:
    alignment: 居中          # 对齐方式
    line_spacing: 1.5倍     # 行距
    first_line_indent: 2字符  # 首行缩进
    left_indent: 0字符       # 左缩进
    right_indent: 0字符      # 右缩进
    space_before: 0.5行     # 段前间距
    space_after: 0.5行      # 段后间距
```

**对齐方式：**
- `居中` / `CENTER`
- `左对齐` / `LEFT`
- `右对齐` / `RIGHT`
- `两端对齐` / `JUSTIFY`
- `分散对齐` / `DISTRIBUTE`

**行距：**
- 倍数：`1.5倍`, `2倍`, `单倍`, `双倍`
- 数字：`1.5`, `2` （表示倍数）
- 固定值：`20pt` （固定行高）

**间距和缩进：**
支持多种单位：
- `0.5行` - 相对于字体大小的行高
- `2字符` - 相对于字体大小的字符宽度
- `12pt` - 绝对磅数
- `1cm` - 厘米
- `0.5in` - 英寸

## 完整示例

```yaml
document:
  # 全局默认样式
  defaults:
    font:
      size: 小四
      name_eastasia: 宋体
      name_ascii: "Times New Roman"
    paragraph:
      line_spacing: 1.5倍
      alignment: 两端对齐
  
  # 元素识别规则
  classifiers:
    # 1. 标题（第一段）
    - class: title
      match:
        type: paragraph
        position: 0
    
    # 2. 作者列表（第二段，包含逗号）
    - class: author-list
      match:
        type: paragraph
        position: 1
        pattern: ".*[,，].*"
    
    # 3. 作者单位（标题和摘要之间，以数字开头）
    - class: author-affiliation
      match:
        type: paragraph
        range:
          after: {class: author-list}
          before: {pattern: "^摘要[:：]"}
        pattern: "^\\d+\\."
    
    # 4. 通信作者（标题和摘要之间，以*开头）
    - class: corresponding-author
      match:
        type: paragraph
        range:
          after: {class: author-list}
          before: {pattern: "^摘要[:：]"}
        pattern: "^\\*"
    
    # 5. 摘要
    - class: abstract
      match:
        type: paragraph
        pattern: "^摘要[:：]"
    
    # 6. 关键词
    - class: keywords
      match:
        type: paragraph
        pattern: "^关键词[:：]"
        after: {class: abstract}
  
  # 样式定义
  styles:
    # 标题样式
    .title:
      font:
        name_eastasia: 黑体
        name_ascii: "Times New Roman"
        size: 三号
        bold: false
      paragraph:
        alignment: 居中
        space_before: 0.5行
        space_after: 0.5行
    
    # 作者列表样式
    .author-list:
      font:
        name_eastasia: 楷体
        name_ascii: "Times New Roman"
        size: 小四
      paragraph:
        alignment: 居中
    
    # 作者单位样式
    .author-affiliation:
      font:
        size: 五号
      paragraph:
        alignment: 居中
    
    # 通信作者样式
    .corresponding-author:
      font:
        size: 五号
      paragraph:
        alignment: 居中
    
    # 摘要样式
    .abstract:
      font:
        name_eastasia: 黑体
        size: 小四
        bold: true
      paragraph:
        alignment: 左对齐
        first_line_indent: 0字符
    
    # 关键词样式
    .keywords:
      font:
        size: 小四
      paragraph:
        alignment: 左对齐
        first_line_indent: 0字符
```

## 调试技巧

### 1. 输出文档结构

```bash
poetry run docx-lint document.docx --config config.yaml --debug-structure
```

可以看到每个段落被打上了哪些 class。

### 2. 逐步调试

从简单的规则开始，逐步添加：

```yaml
# 第一步：只识别标题
classifiers:
  - class: title
    match:
      position: 0

# 确认无误后，添加更多规则
```

### 3. 使用注释

```yaml
classifiers:
  # 这是标题识别规则
  # 要求：文档第一段
  - class: title
    match:
      position: 0
  
  # 这是作者列表识别规则
  # 要求：第二段，且包含逗号（多个作者）
  - class: author-list
    match:
      position: 1
      pattern: ".*[,，].*"
```

## 常见问题

### Q: 为什么我的规则没有匹配到？

A: 检查以下几点：
1. 规则顺序是否正确（后面的规则依赖前面的 class）
2. 正则表达式是否正确（注意转义字符）
3. 位置计数是否正确（从 0 开始）

### Q: 一个元素可以有多个 class 吗？

A: **可以！** 这是我们系统的重要特性，完全类似 HTML。

一个元素可以匹配多个规则，拥有多个 class。样式检查会检查所有 class 对应的样式。

```yaml
# 示例：多个规则匹配同一元素
classifiers:
  - class: heading        # 通用：标题类
    match: {pattern: "^\\d+"}
  
  - class: level-1        # 特定：一级标题
    match: {pattern: "^\\d+\\.\\s"}
  
  - class: important      # 特殊标记
    match: {pattern: "^1\\."}

# 结果："1. 引言" 会有 3 个 class: heading, level-1, important
```

**优势：**
- 可以定义通用样式（如 `.heading`）和特殊样式（如 `.important`）
- 类似 CSS 的 class 组合思想
- 灵活的样式复用

### Q: 如何匹配可变数量的元素？

A: 使用**复合区域（children）**配合相对定位：

```yaml
# 定义作者区域（复合区域）
- class: author-section
  match:
    range:
      after: {class: title}
      before: {class: abstract}
  # 子元素使用相对定位
  children:
    - class: author-list
      match:
        position: first  # 第一个
    
    - class: author-affiliation
      match:
        position: middle  # 中间所有元素
        pattern: "^\\d+\\."
    
    - class: corresponding-author
      match:
        position: last  # 最后一个
```

这样无论有多少个作者单位，都能正确识别。

### Q: 如何跳过某些元素不检查？

A: 不给它们定义 class 即可。只有有 class 的元素才会被样式检查。
