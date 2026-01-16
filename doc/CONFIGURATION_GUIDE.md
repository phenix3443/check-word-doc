# 配置文件编写指南

本文档详细说明如何编写 `classifiers.yaml`、`styles.yaml` 和 `rules.yaml` 配置文件。

## 目录

- [1. classifiers.yaml - 分类器配置](#1-classifiersyaml---分类器配置)
- [2. styles.yaml - 样式配置](#2-stylesyaml---样式配置)
- [3. rules.yaml - 规则配置](#3-rulesyaml---规则配置)
- [4. 完整示例](#4-完整示例)

---

## 1. classifiers.yaml - 分类器配置

分类器用于识别和标记文档中的不同元素，为每个元素分配语义类（class）。

### 1.1 基本结构

```yaml
document:
  classifiers:
    - class: "类名"
      match:
        type: "元素类型"
        pattern: "匹配模式"
        position:
          type: "定位类型"
          # ... 定位参数
      children:
        - class: "子元素类名"
          # ... 子元素配置
```

### 1.2 字段说明

#### 1.2.1 `class` - 类名

- **类型**: 字符串
- **必填**: 是
- **说明**: 为匹配的元素分配的语义类名
- **命名规范**: 
  - 使用小写字母和连字符
  - 语义化命名，描述元素的作用
  - 示例: `title`, `author-list`, `abstract`, `heading-introduction`

#### 1.2.2 `match` - 匹配条件

##### `match.type` - 元素类型

- **类型**: 字符串
- **必填**: 否（默认为 `paragraph`）
- **可选值**:
  - `paragraph` - 段落（默认值）
  - `table` - 表格
  - `image` - 图片
  - `heading` - 标题
- **示例**:
  ```yaml
  match:
    type: paragraph  # 匹配段落
  ```

##### `match.pattern` - 匹配模式

- **类型**: 字符串（正则表达式）
- **必填**: 否
- **说明**: 用于匹配元素内容的正则表达式
- **注意**: 
  - 用于**识别**元素，不是用于**验证**内容
  - 应该使用 `^` 和 `$` 进行完整匹配
  - 验证规则应该放在 `rules.yaml` 中
- **示例**:
  ```yaml
  match:
    pattern: "^摘要[：:].*$"  # 匹配以"摘要："或"摘要:"开头的段落
  ```

##### `match.position` - 位置定位

用于指定元素在文档中的位置。

###### `position.type` - 定位类型

- **类型**: 字符串
- **必填**: 是
- **可选值**:
  - `absolute` - 绝对定位（相对于整个文档）
  - `relative` - 相对定位（相对于父元素的子元素）
  - `between` - 区间定位（在两个元素之间）
  - `next` - 下一个相邻兄弟元素
  - `prev` - 上一个相邻兄弟元素

**1) `absolute` - 绝对定位**

相对于整个文档的位置。

- **参数**:
  - `index`: 位置索引
    - 数字: `0`（第一个）、`1`（第二个）、`-1`（最后一个）
- **示例**:
  ```yaml
  position:
    type: absolute
    index: 0  # 文档的第一个段落
  ```

**2) `relative` - 相对定位**

相对于父元素的子元素位置（用于 `children` 中）。

- **参数**:
  - `index`: 位置索引
    - 数字: `0`（第一个子元素）、`1`（第二个子元素）、`-1`（最后一个子元素）
- **示例**:
  ```yaml
  children:
    - class: first-child
      match:
        position:
          type: relative
          index: 0  # 父元素的第一个子元素
  ```

**3) `between` - 区间定位**

在两个指定元素之间的所有元素。

- **参数**:
  - `class`: 两个边界元素的类名数组 `[起始类, 结束类]`
- **示例**:
  ```yaml
  position:
    type: between
    class: [title, abstract]  # 在标题和摘要之间的所有元素
  ```

**4) `next` - 下一个相邻兄弟**

紧跟在指定元素后面的下一个同级元素。

- **参数**:
  - `class`: 参考元素的类名
  - `offset`: 偏移量（可选，默认为 0）
- **示例**:
  ```yaml
  position:
    type: next
    class: title  # 紧跟在 title 后面的元素
  ```

**5) `prev` - 上一个相邻兄弟**

紧挨在指定元素前面的上一个同级元素。

- **参数**:
  - `class`: 参考元素的类名
  - `offset`: 偏移量（可选，默认为 0）
- **示例**:
  ```yaml
  position:
    type: prev
    class: abstract  # 紧挨在 abstract 前面的元素
  ```

#### 1.2.3 `children` - 子元素

用于定义复合区域内的子元素。

- **类型**: 数组
- **必填**: 否
- **说明**: 子元素通常使用 `relative`、`next` 或 `prev` 定位
- **示例**:
  ```yaml
  - class: author-section
    match:
      position:
        type: between
        class: [title, abstract]
    children:
      - class: author-list
        match:
          position:
            type: relative
            index: 0  # 第一个子元素
      - class: author-affiliation
        match:
          position:
            type: next
            class: author-list  # 紧跟在 author-list 后面
  ```

### 1.3 完整示例

```yaml
document:
  classifiers:
    # 1. 文档标题（第一个段落）
    - class: title
      match:
        type: paragraph
        position:
          type: absolute
          index: 0

    # 2. 摘要（以"摘要："开头）
    - class: abstract
      match:
        type: paragraph
        pattern: "^摘要[：:].*$"

    # 3. 作者信息区域（在标题和摘要之间）
    - class: author-section
      match:
        position:
          type: between
          class: [title, abstract]
      children:
        # 3.1 作者列表（第一个子元素）
        - class: author-list
          match:
            position:
              type: relative
              index: 0
        
        # 3.2 作者单位（紧跟作者列表）
        - class: author-affiliation
          match:
            position:
              type: next
              class: author-list
        
        # 3.3 通讯作者（最后一个子元素）
        - class: corresponding-author
          match:
            position:
              type: relative
              index: -1

    # 4. 引言标题（内容为"引  言"）
    - class: heading-introduction
      match:
        type: paragraph
        pattern: "^引\\s+言$"

    # 5. 引言内容（紧跟引言标题）
    - class: body-introduction
      match:
        position:
          type: next
          class: heading-introduction

    # 6. 表格题注
    - class: data-info-table-caption
      match:
        type: paragraph
        pattern: "^表\\s*\\d+\\s*[：:].*$"

    # 7. 数据信息表（紧跟表格题注）
    - class: data-info-table
      match:
        type: table
        position:
          type: next
          class: data-info-table-caption

    # 8. 参考文献标题
    - class: heading-references
      match:
        type: paragraph
        pattern: "^参考文献$"

    # 9. 参考文献列表（紧跟参考文献标题）
    - class: reference-item
      match:
        position:
          type: next
          class: heading-references
```

---

## 2. styles.yaml - 样式配置

样式配置定义每个类（class）应该具有的格式要求。

### 2.1 基本结构

```yaml
document:
  styles:
    .类名:
      font:
        # 字体设置
      paragraph:
        # 段落设置
```

### 2.2 字段说明

#### 2.2.1 类选择器

- **格式**: `.类名`
- **说明**: 以点号 `.` 开头，后跟 `classifiers.yaml` 中定义的类名
- **示例**: `.title`, `.abstract`, `.heading-introduction`

#### 2.2.2 `font` - 字体设置

##### `font.name_eastasia` - 中文字体

- **类型**: 字符串
- **必填**: 否
- **可选值**:
  - `宋体`
  - `黑体`
  - `楷体`
  - `华文楷体`
  - `仿宋`
  - 其他中文字体名称
- **示例**:
  ```yaml
  font:
    name_eastasia: 宋体
  ```

##### `font.name_ascii` - 西文字体

- **类型**: 字符串
- **必填**: 否
- **可选值**:
  - `Times New Roman`
  - `Arial`
  - `Calibri`
  - 其他西文字体名称
- **示例**:
  ```yaml
  font:
    name_ascii: "Times New Roman"
  ```

##### `font.size` - 字号

- **类型**: 字符串
- **必填**: 否
- **可选值**:
  - 中文字号: `初号`, `小初`, `一号`, `小一`, `二号`, `小二`, `三号`, `小三`, `四号`, `小四`, `五号`, `小五`, `六号`, `小六`, `七号`, `八号`
  - 磅值: `10.5磅`, `12磅`, `14磅`, `16磅`, `18磅`, `20磅`, `22磅`, `24磅`, `26磅`, `28磅` 等
  - 简写: `三号`, `小四`, `五号` 等
- **对应关系**:
  - 初号 = 42磅
  - 小初 = 36磅
  - 一号 = 26磅
  - 小一 = 24磅
  - 二号 = 22磅
  - 小二 = 18磅
  - 三号 = 16磅
  - 小三 = 15磅
  - 四号 = 14磅
  - 小四 = 12磅
  - 五号 = 10.5磅
  - 小五 = 9磅
  - 六号 = 7.5磅
  - 小六 = 6.5磅
  - 七号 = 5.5磅
  - 八号 = 5磅
- **示例**:
  ```yaml
  font:
    size: 五号  # 或 10.5磅
  ```

##### `font.bold` - 粗体

- **类型**: 布尔值
- **必填**: 否
- **可选值**: `true`, `false`
- **默认值**: `false`
- **示例**:
  ```yaml
  font:
    bold: true
  ```

##### `font.italic` - 斜体

- **类型**: 布尔值
- **必填**: 否
- **可选值**: `true`, `false`
- **默认值**: `false`
- **示例**:
  ```yaml
  font:
    italic: true
  ```

##### `font.color` - 字体颜色

- **类型**: 字符串
- **必填**: 否
- **可选值**: 十六进制颜色代码
- **示例**:
  ```yaml
  font:
    color: "000000"  # 黑色
  ```

#### 2.2.3 `paragraph` - 段落设置

##### `paragraph.alignment` - 对齐方式

- **类型**: 字符串
- **必填**: 否
- **可选值**:
  - `左对齐` / `left`
  - `居中` / `center`
  - `右对齐` / `right`
  - `两端对齐` / `justify`
  - `分散对齐` / `distribute`
- **示例**:
  ```yaml
  paragraph:
    alignment: 居中
  ```

##### `paragraph.line_spacing` - 行距

- **类型**: 字符串
- **必填**: 否
- **可选值**:
  - 倍数行距: `1倍`, `1.15倍`, `1.5倍`, `2倍`, `2.5倍`, `3倍`
  - 固定值: `12磅`, `14磅`, `16磅` 等
  - 最小值: `最小12磅`, `最小14磅` 等
- **示例**:
  ```yaml
  paragraph:
    line_spacing: 1.15倍
  ```

##### `paragraph.space_before` - 段前间距

- **类型**: 字符串
- **必填**: 否
- **可选值**:
  - 行数: `0.5行`, `1行`, `1.5行`, `2行`
  - 磅值: `6磅`, `12磅`, `18磅`, `24磅`
- **示例**:
  ```yaml
  paragraph:
    space_before: 0.5行
  ```

##### `paragraph.space_after` - 段后间距

- **类型**: 字符串
- **必填**: 否
- **可选值**:
  - 行数: `0.5行`, `1行`, `1.5行`, `2行`
  - 磅值: `6磅`, `12磅`, `18磅`, `24磅`
- **示例**:
  ```yaml
  paragraph:
    space_after: 0.5行
  ```

##### `paragraph.first_line_indent` - 首行缩进

- **类型**: 字符串
- **必填**: 否
- **可选值**:
  - 字符数: `0字符`, `2字符`, `4字符`
  - 磅值: `0磅`, `21磅`, `42磅`
  - 厘米: `0厘米`, `0.74厘米`, `1.48厘米`
- **说明**: `0字符` 表示顶格排，`2字符` 是常见的首行缩进
- **示例**:
  ```yaml
  paragraph:
    first_line_indent: 2字符
  ```

##### `paragraph.left_indent` - 左缩进

- **类型**: 字符串
- **必填**: 否
- **可选值**:
  - 字符数: `0字符`, `2字符`, `4字符`
  - 磅值: `0磅`, `21磅`, `42磅`
  - 厘米: `0厘米`, `0.74厘米`, `1.48厘米`
- **示例**:
  ```yaml
  paragraph:
    left_indent: 2字符
  ```

##### `paragraph.right_indent` - 右缩进

- **类型**: 字符串
- **必填**: 否
- **可选值**: 同 `left_indent`
- **示例**:
  ```yaml
  paragraph:
    right_indent: 0字符
  ```

### 2.3 完整示例

```yaml
document:
  styles:
    # 1. 文档标题样式
    .title:
      font:
        name_eastasia: 黑体
        name_ascii: "Times New Roman"
        size: 三号
      paragraph:
        alignment: 居中
        space_before: 0.5行
        space_after: 0.5行

    # 2. 作者列表样式
    .author-list:
      font:
        name_eastasia: 华文楷体
        name_ascii: "Times New Roman"
        size: 小四
      paragraph:
        alignment: 居中

    # 3. 作者单位样式
    .author-affiliation:
      font:
        name_eastasia: 华文楷体
        name_ascii: "Times New Roman"
        size: 五号
      paragraph:
        alignment: 居中

    # 4. 摘要样式
    .abstract:
      font:
        name_eastasia: 华文楷体
        name_ascii: "Times New Roman"
        size: 五号
      paragraph:
        alignment: 左对齐
        line_spacing: 1.15倍

    # 5. 关键词样式
    .keywords:
      font:
        name_eastasia: 华文楷体
        size: 五号
      paragraph:
        alignment: 两端对齐
        line_spacing: 1.15倍

    # 6. 一级标题样式
    .heading-introduction:
      font:
        name_eastasia: 宋体
        name_ascii: "Times New Roman"
        size: 四号
      paragraph:
        alignment: 左对齐
        space_before: 0.5行
        space_after: 0.5行

    # 7. 正文样式
    .body-introduction:
      font:
        name_eastasia: 宋体
        name_ascii: "Times New Roman"
        size: 五号
      paragraph:
        alignment: 两端对齐
        first_line_indent: 2字符
        line_spacing: 1.15倍

    # 8. 图片题注样式
    .figure-caption:
      font:
        name_eastasia: 宋体
        name_ascii: "Times New Roman"
        size: 小五
        bold: true
      paragraph:
        alignment: 居中
        line_spacing: 1.15倍
        space_before: 0.5行
        space_after: 0.5行

    # 9. 表格题注样式
    .data-info-table-caption:
      font:
        name_eastasia: 宋体
        name_ascii: "Times New Roman"
        size: 小五
        bold: true
      paragraph:
        alignment: 居中
        line_spacing: 1.15倍
        space_before: 0.5行
        space_after: 0.5行

    # 10. 表格内容样式
    .data-info-table:
      font:
        name_eastasia: 宋体
        name_ascii: "Times New Roman"
        size: 小五
      paragraph:
        line_spacing: 1.15倍

    # 11. 参考文献列表样式
    .reference-item:
      font:
        name_eastasia: 宋体
        name_ascii: "Times New Roman"
        size: 五号
      paragraph:
        alignment: 左对齐
        line_spacing: 1.15倍
```

---

## 3. rules.yaml - 规则配置

规则配置定义内容验证规则，用于检查文档内容是否符合要求。

### 3.1 基本结构

```yaml
document:
  rules:
    - id: "规则ID"
      name: "规则名称"
      description: "规则描述"
      selector: "选择器"
      condition:
        # 条件（可选）
      check:
        # 检查类型
      severity: "严重程度"
      message: "错误消息"
```

### 3.2 字段说明

#### 3.2.1 `id` - 规则ID

- **类型**: 字符串
- **必填**: 是
- **格式**: `r-XXX`（r- 前缀 + 三位数字）
- **说明**: 规则的唯一标识符
- **示例**: `r-001`, `r-024`, `r-100`

#### 3.2.2 `name` - 规则名称

- **类型**: 字符串
- **必填**: 是
- **说明**: 规则的简短名称
- **示例**: `作者列表格式规则`, `摘要长度检查`

#### 3.2.3 `description` - 规则描述

- **类型**: 字符串
- **必填**: 是
- **说明**: 规则的详细描述
- **示例**: `多个作者时，作者之间应该使用中文逗号分割，而且每个作者后面应该有数字`

#### 3.2.4 `selector` - 选择器

使用 CSS 风格的选择器语法选择要检查的元素。

- **类型**: 字符串
- **必填**: 是
- **语法**:
  - 类选择器: `.class-name`
  - 伪类选择器:
    - `:first` - 第一个元素
    - `:last` - 最后一个元素
    - `:nth(n)` - 第 n 个元素（从 0 开始）
  - 相邻兄弟选择器: `.class1 + .class2`
  - 属性选择器: `[type="table"]`
- **示例**:
  ```yaml
  selector: ".author-list"                    # 所有 author-list 元素
  selector: ".author-list:first"              # 第一个 author-list 元素
  selector: ".reference-item:nth(1)"          # 第二个 reference-item 元素
  selector: ".heading-introduction + .body"   # 紧跟在 heading-introduction 后的 body 元素
  ```

#### 3.2.5 `condition` - 条件

定义规则生效的条件（可选）。

##### `condition.selector` - 条件选择器

- **类型**: 字符串
- **必填**: 否
- **说明**: 选择用于判断条件的元素
- **示例**:
  ```yaml
  condition:
    selector: ".author-list"
  ```

##### `condition.pattern` - 条件模式

- **类型**: 字符串（正则表达式）
- **必填**: 否
- **说明**: 条件元素必须匹配的模式
- **示例**:
  ```yaml
  condition:
    selector: ".author-list"
    pattern: ".*,.*"  # 包含逗号（多作者）
  ```

##### `condition.count` - 条件数量

- **类型**: 字符串
- **必填**: 否
- **可选值**:
  - `== N` - 等于 N 个
  - `>= N` - 大于等于 N 个
  - `<= N` - 小于等于 N 个
  - `> N` - 大于 N 个
  - `< N` - 小于 N 个
- **示例**:
  ```yaml
  condition:
    selector: ".reference-item"
    count: ">= 2"  # 至少有 2 条参考文献
  ```

##### `condition.exists` - 条件存在性

- **类型**: 布尔值
- **必填**: 否
- **可选值**: `true`, `false`
- **说明**: 检查元素是否存在
- **示例**:
  ```yaml
  condition:
    selector: ".corresponding-author"
    exists: true  # 通讯作者存在时
  ```

#### 3.2.6 `check` - 检查类型

定义具体的检查内容。

##### `check.pattern` - 模式检查

使用正则表达式检查内容格式。

- **类型**: 字符串（正则表达式）
- **说明**: 元素内容必须匹配的正则表达式
- **示例**:
  ```yaml
  check:
    pattern: "^[^,，]+,[^,，]+$"  # 包含一个逗号
  ```

##### `check.exists` - 存在性检查

检查元素是否存在。

- **类型**: 布尔值
- **可选值**: `true`, `false`
- **示例**:
  ```yaml
  check:
    exists: true  # 元素必须存在
  ```

##### `check.count` - 数量检查

检查元素数量。

- **类型**: 字符串
- **可选值**:
  - `== N` - 等于 N 个
  - `>= N` - 大于等于 N 个
  - `<= N` - 小于等于 N 个
  - `> N` - 大于 N 个
  - `< N` - 小于 N 个
- **示例**:
  ```yaml
  check:
    count: ">= 3"  # 至少 3 个
  ```

##### `check.length` - 长度检查

检查文本长度。

- **类型**: 对象
- **参数**:
  - `max`: 最大长度
  - `min`: 最小长度
  - `exclude`: 排除的前缀（可选）
- **示例**:
  ```yaml
  check:
    length:
      max: 500
      exclude: "摘要："  # 不计算"摘要："的长度
  ```

##### `check.count_equals` - 数量相等检查

比较两个选择器选中的元素数量。

- **类型**: 对象
- **参数**:
  - `reference_selector`: 参考选择器
  - `extract_pattern`: 提取模式（可选）
- **说明**: 用于检查两组元素数量是否一致
- **示例**:
  ```yaml
  check:
    count_equals:
      reference_selector: ".author-list"
      extract_pattern: "\\d+"  # 提取作者列表中的数字
  ```

##### `check.cross_validate` - 交叉验证

比较不同元素之间的内容。

- **类型**: 对象
- **参数**:
  - `reference_selector`: 参考元素选择器
  - `target_key_column`: 目标表格的键列索引
  - `target_value_column`: 目标表格的值列索引
  - `target_key`: 要查找的键
- **说明**: 用于表格 Key-Value 查找和内容比较
- **示例**:
  ```yaml
  check:
    cross_validate:
      reference_selector: ".title"
      target_key_column: 0
      target_value_column: 1
      target_key: "数据库（集）名称"
  ```

##### `check.table_cell_pattern` - 表格单元格模式检查

检查表格中特定单元格的内容格式。

- **类型**: 对象
- **参数**:
  - `target_key_column`: 键列索引（默认 0）
  - `target_value_column`: 值列索引（默认 1）
  - `target_key`: 要查找的键
  - `pattern`: 值必须匹配的正则表达式
- **说明**: 用于 Key-Value 表格的内容验证
- **示例**:
  ```yaml
  check:
    table_cell_pattern:
      target_key_column: 0
      target_value_column: 1
      target_key: "数据作者"
      pattern: "^[^,，;；、]+([、][^,，;；、]+)*$"
  ```

#### 3.2.7 `severity` - 严重程度

- **类型**: 字符串
- **必填**: 是
- **可选值**:
  - `error` - 错误（必须修复）
  - `warning` - 警告（建议修复）
  - `info` - 信息（提示）
- **示例**:
  ```yaml
  severity: error
  ```

#### 3.2.8 `message` - 错误消息

- **类型**: 字符串
- **必填**: 是
- **说明**: 规则不通过时显示的错误消息
- **示例**:
  ```yaml
  message: "作者列表格式错误，多个作者之间应使用中文逗号分隔"
  ```

### 3.3 完整示例

```yaml
document:
  rules:
    # ========== 作者规则 ==========

    # r-001: 作者列表格式规则（多作者）
    - id: r-001
      name: 作者列表格式规则（多作者）
      description: 多个作者时，作者之间应该使用中文逗号分割，而且每个作者后面应该有数字
      selector: ".author-list"
      condition:
        selector: ".author-list"
        pattern: ".*[,，].*"  # 包含逗号（多作者）
      check:
        pattern: "^[^,，]+\\d+[,，][^,，]+\\d+.*$"
      severity: error
      message: "作者列表格式错误，多个作者之间应使用中文逗号分隔，每个作者后面应有数字编号"

    # r-007: 作者单位格式
    - id: r-007
      name: 作者单位格式
      description: 作者单位格式必须为"单位/机构，城市  邮编"
      selector: ".author-affiliation"
      check:
        pattern: "^.+/.+，[^\\s]+\\s{2}\\d{6}$"
      severity: error
      message: "作者单位格式错误，应为：单位/机构，城市  邮编（注意：单位和机构之间用/分隔，城市和邮编之间有恰好两个空格）"

    # r-009: 作者单位数量检查
    - id: r-009
      name: 作者单位数量检查
      description: 作者单位数量应该与作者数量一致
      selector: ".author-affiliation"
      check:
        count_equals:
          reference_selector: ".author-list"
          extract_pattern: "\\d+"  # 从作者列表中提取最大数字
      severity: error
      message: "作者单位数量与作者数量不一致"

    # ========== 摘要和关键词规则 ==========

    # r-015: 摘要长度检查
    - id: r-015
      name: 摘要长度检查
      description: 摘要限长500字（不包括"摘要："）
      selector: ".abstract"
      check:
        length:
          max: 500
          exclude: "摘要："
      severity: error
      message: "摘要长度超过500字（不包括'摘要：'）"

    # r-016: 摘要无引用检查
    - id: r-016
      name: 摘要无引用检查
      description: 摘要中不应包含引用
      selector: ".abstract"
      check:
        pattern: "^(?!.*\\[\\d+\\]).*$"
      severity: error
      message: "摘要中不应包含引用（如 [1]）"

    # r-018: 关键词数量检查
    - id: r-018
      name: 关键词数量检查
      description: 关键词不低于3个
      selector: ".keywords"
      check:
        count:
          min: 3
          separator: "；"
          exclude: "关键词："
      severity: error
      message: "关键词数量不足3个"

    # ========== 参考文献规则 ==========

    # r-024: 参考文献格式
    - id: r-024
      name: 参考文献格式
      description: 参考文献必须按照"[数字]  内容"格式，序号后空2格
      selector: ".reference-item"
      check:
        pattern: "^\\[\\d+\\]  [^ ].*$"
      severity: error
      message: "参考文献格式错误，应为：[数字]  内容（注意：序号后恰好2个空格）"

    # r-025: 第一条参考文献编号
    - id: r-025
      name: 第一条参考文献编号
      description: 第一条参考文献必须以 '[1]' 开头
      selector: ".reference-item:first"
      check:
        pattern: "^\\[1\\]  "
      severity: error
      message: "第一条参考文献必须以 '[1]' 开头"

    # r-026: 参考文献编号连续性
    - id: r-026
      name: 参考文献编号连续性
      description: 参考文献编号应该连续（如果有第2条，应该是[2]）
      selector: ".reference-item:nth(1)"
      condition:
        selector: ".reference-item"
        count: ">= 2"
      check:
        pattern: "^\\[2\\]  "
      severity: error
      message: "第二条参考文献必须以 '[2]' 开头，编号应该连续"

    # ========== 表格规则 ==========

    # r-040: 数据信息表题注格式
    - id: r-040
      name: 数据信息表题注格式
      description: 数据信息表题注必须为"表 1： 数据库（集）基本信息简介"
      selector: ".data-info-table-caption"
      check:
        pattern: "^表\\s*1\\s*[：:]\\s*数据库（集）基本信息简介$"
      severity: error
      message: "数据信息表题注格式错误，应为'表 1： 数据库（集）基本信息简介'（注意空格和标点）"

    # r-042: 数据库名称与论文标题一致性
    - id: r-042
      name: 数据库名称与论文标题一致性
      description: 数据信息表中的"数据库（集）名称"应与论文标题一致
      selector: ".data-info-table"
      check:
        cross_validate:
          reference_selector: ".title"
          target_key_column: 0
          target_value_column: 1
          target_key: "数据库（集）名称"
      severity: error
      message: "数据信息表中的'数据库（集）名称'与论文标题不一致"

    # r-043: 数据作者分隔符检查
    - id: r-043
      name: 数据作者分隔符检查
      description: 数据信息表中的"数据作者"之间应使用中文顿号分隔
      selector: ".data-info-table"
      check:
        table_cell_pattern:
          target_key_column: 0
          target_value_column: 1
          target_key: "数据作者"
          pattern: "^[^,，;；、]+([、][^,，;；、]+)*$"
      severity: error
      message: "数据作者之间应使用中文顿号（、）分隔"

    # r-044: 数据量格式检查
    - id: r-044
      name: 数据量格式检查
      description: 数据信息表中的"数据量"必须是文件大小格式
      selector: ".data-info-table"
      check:
        table_cell_pattern:
          target_key_column: 0
          target_value_column: 1
          target_key: "数据量"
          pattern: "^\\d+(\\.\\d+)?\\s*(B|KB|MB|GB|TB|PB|EB)$"
      severity: error
      message: "数据量格式错误，应为文件大小格式（如：100KB、1.5GB）"

    # r-045: 数据格式检查
    - id: r-045
      name: 数据格式检查
      description: 数据信息表中的"数据格式"必须是文件扩展名格式
      selector: ".data-info-table"
      check:
        table_cell_pattern:
          target_key_column: 0
          target_value_column: 1
          target_key: "数据格式"
          pattern: "^\\.[a-zA-Z0-9]+(\\s*[、，,;；]\\s*\\.[a-zA-Z0-9]+)*$"
      severity: error
      message: "数据格式错误，应为文件扩展名格式（如：.txt、.csv、.json）"

    # ========== 章节规则 ==========

    # r-030: 引言内容存在性
    - id: r-030
      name: 引言内容检查
      description: 引言标题后必须有内容
      selector: ".heading-introduction + .body-introduction"
      check:
        exists: true
      severity: error
      message: "引言标题后必须有内容"

    # r-054: 参考文献存在性
    - id: r-054
      name: 参考文献存在性
      selector: ".heading-references"
      check:
        exists: true
      severity: error
      message: "文档必须包含参考文献"

    # r-055: 参考文献数量
    - id: r-055
      name: 参考文献数量
      selector: ".reference-item"
      check:
        count: ">= 1"
      severity: error
      message: "至少应有1条参考文献"
```

---

## 4. 完整示例

### 4.1 项目结构

```
config/
  template/
    data_paper/
      config.yaml          # 主配置文件（引用其他配置）
      classifiers.yaml     # 分类器配置
      styles.yaml          # 样式配置
      rules.yaml           # 规则配置
```

### 4.2 config.yaml

```yaml
# 主配置文件
imports:
  - classifiers.yaml
  - styles.yaml
  - rules.yaml
```

### 4.3 使用流程

1. **定义分类器** (`classifiers.yaml`)
   - 识别文档中的各种元素
   - 为每个元素分配语义类

2. **定义样式** (`styles.yaml`)
   - 为每个类定义格式要求
   - 指定字体、段落等样式

3. **定义规则** (`rules.yaml`)
   - 定义内容验证规则
   - 使用选择器选择元素
   - 定义检查条件和错误消息

4. **运行检查**
   ```bash
   poetry run python script/cli.py check document.docx --config config/template/data_paper/config.yaml
   ```

---

## 5. 常见模式和最佳实践

### 5.1 分类器模式

#### 模式1: 绝对位置定位
```yaml
# 文档第一个段落
- class: title
  match:
    position:
      type: absolute
      index: 0
```

#### 模式2: 内容模式匹配
```yaml
# 以特定文字开头的段落
- class: abstract
  match:
    pattern: "^摘要[：:].*$"
```

#### 模式3: 相对位置定位
```yaml
# 紧跟在某个元素后面
- class: keywords
  match:
    position:
      type: next
      class: abstract
```

#### 模式4: 区间定位
```yaml
# 在两个元素之间的所有元素
- class: author-section
  match:
    position:
      type: between
      class: [title, abstract]
```

#### 模式5: 复合区域
```yaml
# 包含子元素的区域
- class: author-section
  match:
    position:
      type: between
      class: [title, abstract]
  children:
    - class: author-list
      match:
        position:
          type: relative
          index: 0
    - class: author-affiliation
      match:
        position:
          type: next
          class: author-list
```

### 5.2 样式模式

#### 模式1: 标题样式
```yaml
.heading-level1:
  font:
    name_eastasia: 宋体
    name_ascii: "Times New Roman"
    size: 四号
  paragraph:
    alignment: 左对齐
    space_before: 0.5行
    space_after: 0.5行
```

#### 模式2: 正文样式
```yaml
.body-text:
  font:
    name_eastasia: 宋体
    name_ascii: "Times New Roman"
    size: 五号
  paragraph:
    alignment: 两端对齐
    first_line_indent: 2字符
    line_spacing: 1.15倍
```

#### 模式3: 题注样式
```yaml
.caption:
  font:
    name_eastasia: 宋体
    name_ascii: "Times New Roman"
    size: 小五
    bold: true
  paragraph:
    alignment: 居中
    line_spacing: 1.15倍
    space_before: 0.5行
    space_after: 0.5行
```

### 5.3 规则模式

#### 模式1: 格式检查
```yaml
- id: r-001
  name: 格式检查
  selector: ".element"
  check:
    pattern: "^正则表达式$"
  severity: error
  message: "格式错误"
```

#### 模式2: 条件规则
```yaml
- id: r-002
  name: 条件规则
  selector: ".element"
  condition:
    selector: ".other-element"
    pattern: ".*条件.*"
  check:
    pattern: "^正则表达式$"
  severity: error
  message: "条件满足时格式错误"
```

#### 模式3: 数量检查
```yaml
- id: r-003
  name: 数量检查
  selector: ".element"
  check:
    count: ">= 3"
  severity: error
  message: "数量不足"
```

#### 模式4: 长度检查
```yaml
- id: r-004
  name: 长度检查
  selector: ".element"
  check:
    length:
      max: 500
      exclude: "前缀："
  severity: error
  message: "长度超限"
```

#### 模式5: 交叉验证
```yaml
- id: r-005
  name: 交叉验证
  selector: ".table"
  check:
    cross_validate:
      reference_selector: ".title"
      target_key_column: 0
      target_value_column: 1
      target_key: "键名"
  severity: error
  message: "内容不一致"
```

---

## 6. 调试技巧

### 6.1 验证配置文件

```bash
# 加载配置文件检查语法
poetry run python -c "
from script.config_loader import ConfigLoader
loader = ConfigLoader('config/template/data_paper/config.yaml')
config = loader.load()
print('配置加载成功')
"
```

### 6.2 测试正则表达式

```python
import re

pattern = r"^摘要[：:].*$"
text = "摘要：这是摘要内容"

if re.match(pattern, text):
    print("匹配成功")
else:
    print("匹配失败")
```

### 6.3 测试选择器

```python
from script.core.selector import Selector

# 假设已经分类完成
selector = Selector(classified_blocks)

# 测试选择器
results = selector.select(".author-list")
print(f"找到 {len(results)} 个元素")
```

---

## 7. 附录

### 7.1 字号对照表

| 中文字号 | 磅值 | 英文名称 |
|---------|------|---------|
| 初号 | 42磅 | 42pt |
| 小初 | 36磅 | 36pt |
| 一号 | 26磅 | 26pt |
| 小一 | 24磅 | 24pt |
| 二号 | 22磅 | 22pt |
| 小二 | 18磅 | 18pt |
| 三号 | 16磅 | 16pt |
| 小三 | 15磅 | 15pt |
| 四号 | 14磅 | 14pt |
| 小四 | 12磅 | 12pt |
| 五号 | 10.5磅 | 10.5pt |
| 小五 | 9磅 | 9pt |
| 六号 | 7.5磅 | 7.5pt |
| 小六 | 6.5磅 | 6.5pt |
| 七号 | 5.5磅 | 5.5pt |
| 八号 | 5磅 | 5pt |

### 7.2 常用正则表达式

```yaml
# 中文逗号分隔
pattern: ".*[,，].*"

# 包含数字
pattern: ".*\\d+.*"

# 以方括号数字开头
pattern: "^\\[\\d+\\].*$"

# 邮编（6位数字）
pattern: "\\d{6}"

# 文件大小格式
pattern: "^\\d+(\\.\\d+)?\\s*(B|KB|MB|GB|TB)$"

# 文件扩展名
pattern: "^\\.[a-zA-Z0-9]+$"

# 邮箱地址
pattern: "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"

# 完全匹配（不包含某些字符）
pattern: "^[^,，;；]+$"
```

### 7.3 常用选择器

```yaml
# 类选择器
selector: ".class-name"

# 第一个元素
selector: ".class-name:first"

# 最后一个元素
selector: ".class-name:last"

# 第 n 个元素（从 0 开始）
selector: ".class-name:nth(2)"

# 相邻兄弟
selector: ".class1 + .class2"

# 属性选择器
selector: "[type='table']"
```

---

## 8. 参考资源

- [YAML 语法指南](https://yaml.org/spec/1.2/spec.html)
- [正则表达式教程](https://regexr.com/)
- [CSS 选择器参考](https://developer.mozilla.org/zh-CN/docs/Web/CSS/CSS_Selectors)
- [Word 文档格式规范](https://support.microsoft.com/zh-cn/office)

---

**版本**: 1.0  
**最后更新**: 2026-01-16
