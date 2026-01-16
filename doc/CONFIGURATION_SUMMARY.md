# 配置文件字段快速参考

本文档提供配置文件中各字段的快速参考。详细说明请参阅 [CONFIGURATION_GUIDE.md](./CONFIGURATION_GUIDE.md)。

## 1. classifiers.yaml

### 顶层字段
- `class` - 类名（必填）
- `match` - 匹配条件
- `children` - 子元素数组

### match 字段
- `type` - 元素类型：`paragraph`（默认）, `table`, `image`, `heading`
- `pattern` - 正则表达式（用于识别）
- `position` - 位置定位

### position 字段
- `type` - 定位类型：
  - `absolute` - 绝对定位（+ `index`）
  - `relative` - 相对定位（+ `index`）
  - `between` - 区间定位（+ `class: [start, end]`）
  - `next` - 下一个兄弟（+ `class`）
  - `prev` - 上一个兄弟（+ `class`）
- `index` - 索引：`0`, `1`, `-1` 等
- `class` - 参考类名（字符串或数组）
- `offset` - 偏移量（可选，默认 0）

---

## 2. styles.yaml

### 顶层字段
- `.class-name` - 类选择器

### font 字段
- `name_eastasia` - 中文字体：`宋体`, `黑体`, `楷体`, `华文楷体`, `仿宋`
- `name_ascii` - 西文字体：`Times New Roman`, `Arial`, `Calibri`
- `size` - 字号：
  - 中文：`初号`, `小初`, `一号`, `小一`, `二号`, `小二`, `三号`, `小三`, `四号`, `小四`, `五号`, `小五`, `六号`, `小六`, `七号`, `八号`
  - 磅值：`10.5磅`, `12磅`, `14磅`, `16磅`, `18磅`, `20磅`, `22磅`, `24磅`, `26磅`, `28磅`
- `bold` - 粗体：`true`, `false`
- `italic` - 斜体：`true`, `false`
- `color` - 颜色：十六进制（如 `"000000"`）

### paragraph 字段
- `alignment` - 对齐：`左对齐`, `居中`, `右对齐`, `两端对齐`, `分散对齐`
- `line_spacing` - 行距：`1倍`, `1.15倍`, `1.5倍`, `2倍`, `12磅`, `14磅`
- `space_before` - 段前：`0.5行`, `1行`, `6磅`, `12磅`
- `space_after` - 段后：`0.5行`, `1行`, `6磅`, `12磅`
- `first_line_indent` - 首行缩进：`0字符`, `2字符`, `4字符`
- `left_indent` - 左缩进：`0字符`, `2字符`, `4字符`
- `right_indent` - 右缩进：`0字符`, `2字符`, `4字符`

---

## 3. rules.yaml

### 顶层字段
- `id` - 规则ID（必填）：`r-001`, `r-024`
- `name` - 规则名称（必填）
- `description` - 规则描述（必填）
- `selector` - 选择器（必填）
- `condition` - 条件（可选）
- `check` - 检查类型（必填）
- `severity` - 严重程度（必填）：`error`, `warning`, `info`
- `message` - 错误消息（必填）

### selector 语法
- `.class` - 类选择器
- `.class:first` - 第一个
- `.class:last` - 最后一个
- `.class:nth(n)` - 第 n 个（从 0 开始）
- `.class1 + .class2` - 相邻兄弟
- `[type="table"]` - 属性选择器

### condition 字段
- `selector` - 条件选择器
- `pattern` - 条件模式（正则）
- `count` - 条件数量：`== N`, `>= N`, `<= N`, `> N`, `< N`
- `exists` - 条件存在：`true`, `false`

### check 字段类型

#### pattern - 模式检查
```yaml
check:
  pattern: "^正则表达式$"
```

#### exists - 存在性检查
```yaml
check:
  exists: true
```

#### count - 数量检查
```yaml
check:
  count: ">= 3"
```

#### length - 长度检查
```yaml
check:
  length:
    max: 500
    min: 10
    exclude: "前缀："
```

#### count_equals - 数量相等检查
```yaml
check:
  count_equals:
    reference_selector: ".other-class"
    extract_pattern: "\\d+"
```

#### cross_validate - 交叉验证
```yaml
check:
  cross_validate:
    reference_selector: ".title"
    target_key_column: 0
    target_value_column: 1
    target_key: "键名"
```

#### table_cell_pattern - 表格单元格检查
```yaml
check:
  table_cell_pattern:
    target_key_column: 0
    target_value_column: 1
    target_key: "键名"
    pattern: "^正则表达式$"
```

---

## 快速示例

### classifiers.yaml
```yaml
document:
  classifiers:
    - class: title
      match:
        position:
          type: absolute
          index: 0
    
    - class: abstract
      match:
        pattern: "^摘要[：:].*$"
    
    - class: keywords
      match:
        position:
          type: next
          class: abstract
```

### styles.yaml
```yaml
document:
  styles:
    .title:
      font:
        name_eastasia: 黑体
        name_ascii: "Times New Roman"
        size: 三号
      paragraph:
        alignment: 居中
    
    .abstract:
      font:
        name_eastasia: 宋体
        size: 五号
      paragraph:
        alignment: 左对齐
        line_spacing: 1.15倍
```

### rules.yaml
```yaml
document:
  rules:
    - id: r-001
      name: 摘要长度检查
      description: 摘要限长500字
      selector: ".abstract"
      check:
        length:
          max: 500
          exclude: "摘要："
      severity: error
      message: "摘要长度超过500字"
    
    - id: r-002
      name: 参考文献格式
      selector: ".reference-item"
      check:
        pattern: "^\\[\\d+\\]  [^ ].*$"
      severity: error
      message: "参考文献格式错误"
```

---

详细文档：[CONFIGURATION_GUIDE.md](./CONFIGURATION_GUIDE.md)
