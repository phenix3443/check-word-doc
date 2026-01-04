# 配置文件结构说明

## 概述

本文档详细说明了 YAML 配置文件的数据结构和设计原则。

## 配置文件基本结构

配置文件采用分层结构，主要包含以下部分：

1. **检查项开关（checks）**：控制各个检查项的启用/禁用
2. **各检查项配置**：每个检查项的详细配置
3. **格式要求（format）**：字体、字号、对齐等格式规范
4. **编号检查（numbering）**：编号格式和连续性检查
5. **验证规则（validation）**：元素间关系的验证
6. **一致性检查（consistency）**：格式一致性检查

## 数据结构定义

### 1. 检查项开关结构

```yaml
checks:
  <check_name>: <boolean>
```

- `check_name`: 检查项名称（如：cover, table_of_contents等）
- `boolean`: true/false，表示是否启用该检查项

### 2. 格式要求结构（format）

```yaml
format:
  font: <string>              # 字体名称
  size: <integer>             # 字号
  bold: <boolean>             # 是否加粗
  alignment: <string>         # 对齐方式：left/center/right/justify
  line_spacing: <float>       # 行距（倍数）
  first_line_indent: <integer> # 首行缩进（字符数）
  hanging_indent: <integer>   # 悬挂缩进（字符数）
  space_before: <integer>     # 段前间距（磅）
  space_after: <integer>      # 段后间距（磅）
  error_message: <string>      # 错误提示信息
```

### 3. 编号检查结构（numbering）

```yaml
numbering:
  check_continuity: <boolean>  # 是否检查连续性
  check_format: <boolean>      # 是否检查格式
  format_pattern: <string>     # 格式正则表达式
  error_message: <string>      # 错误提示信息
```

### 4. 验证规则结构（validation）

```yaml
validation:
  check_<rule_name>: <boolean> # 各种验证规则开关
  error_message: <string>      # 错误提示信息
```

### 5. 一致性检查结构（consistency）

```yaml
consistency:
  check_consistency: <boolean>        # 是否检查一致性
  check_format_consistency: <boolean> # 是否检查格式一致性
  allow_different_by_section: <boolean> # 是否允许不同章节使用不同格式
  error_message: <string>             # 错误提示信息
```

## 各检查项详细结构

### 封面（cover）

```yaml
cover:
  enabled: <boolean>
  required_elements:
    - <element_name>
  optional_elements:
    - <element_name>
  format:
    <element_name>:
      # 格式要求结构
```

### 目录（table_of_contents）

```yaml
table_of_contents:
  enabled: <boolean>
  required: <boolean>
  format:
    # 格式要求结构
  numbering:
    # 编号检查结构
```

### 图目录（figure_list）

```yaml
figure_list:
  enabled: <boolean>
  required: <boolean>
  format:
    # 格式要求结构
  numbering:
    # 编号检查结构
  validation:
    # 验证规则结构
```

### 表目录（table_list）

```yaml
table_list:
  enabled: <boolean>
  required: <boolean>
  format:
    # 格式要求结构
  numbering:
    # 编号检查结构
  validation:
    # 验证规则结构
```

### 正文段落（body_paragraphs）

```yaml
body_paragraphs:
  enabled: <boolean>
  format:
    # 格式要求结构
  exclude_sections:
    - <section_name>
```

### 正文标题（body_headings）

```yaml
body_headings:
  enabled: <boolean>
  levels:
    - level: <integer>
      # 格式要求结构
      numbering_format: <string>  # 编号格式正则表达式
      space_before: <integer>
      space_after: <integer>
  numbering:
    # 编号检查结构
```

### 图表题注（captions）

```yaml
captions:
  enabled: <boolean>
  figure:
    format:
      # 格式要求结构
    numbering:
      # 编号检查结构
    position:
      check_empty_lines_before: <boolean>
      check_empty_lines_after: <boolean>
  table:
    format:
      # 格式要求结构
    numbering:
      # 编号检查结构
    position:
      check_empty_lines_before: <boolean>
      check_empty_lines_after: <boolean>
  consistency:
    # 一致性检查结构
```

### 参考文献（references）

```yaml
references:
  enabled: <boolean>
  required: <boolean>
  format:
    # 格式要求结构
  numbering:
    # 编号检查结构
  citation:
    check_superscript: <boolean>
    format_pattern: <string>
    error_message: <string>
  validation:
    # 验证规则结构
```

### 附件（attachments）

```yaml
attachments:
  enabled: <boolean>
  required: <boolean>
  format:
    title:
      # 格式要求结构
  numbering:
    # 编号检查结构
```

### 页眉（headers）

```yaml
headers:
  enabled: <boolean>
  format:
    # 格式要求结构
  consistency:
    # 一致性检查结构
```

### 页脚（footers）

```yaml
footers:
  enabled: <boolean>
  format:
    # 格式要求结构
  consistency:
    # 一致性检查结构
```

### 页码（page_numbers）

```yaml
page_numbers:
  enabled: <boolean>
  format:
    font: <string>
    size: <integer>
    position: <string>  # bottom_center/bottom_right/top_right
    style: <string>     # arabic/roman
    error_message: <string>
  numbering:
    check_continuity: <boolean>
    start_from_cover: <boolean>
    start_from_contents: <boolean>
    start_number: <integer>
    error_message: <string>
  validation:
    check_with_toc: <boolean>
    check_with_figure_list: <boolean>
    check_with_table_list: <boolean>
    error_message: <string>
```

### 空行检查（empty_lines）

```yaml
empty_lines:
  enabled: <boolean>
  check_consecutive: <boolean>
  max_consecutive: <integer>
  error_message: <string>
```

## 设计原则

1. **可扩展性**：配置文件结构支持添加新的检查项和规则
2. **灵活性**：每个检查项可以独立启用/禁用
3. **可读性**：使用清晰的层级结构和注释
4. **可维护性**：统一的错误提示信息格式
5. **类型安全**：明确的数据类型定义

## 数据类型说明

- **boolean**: true/false
- **integer**: 整数（如：字号、间距）
- **float**: 浮点数（如：行距）
- **string**: 字符串（如：字体名称、错误提示）
- **list**: 列表（如：必需元素列表）

## 正则表达式说明

配置文件中使用的正则表达式遵循 Python re 模块的语法：

- `\d`: 数字
- `\s`: 空白字符
- `+`: 一个或多个
- `*`: 零个或多个
- `?`: 零个或一个
- `()`: 分组
- `[]`: 字符集
- `^`: 字符串开始
- `$`: 字符串结束

注意：在 YAML 中，正则表达式中的反斜杠需要转义（如：`\\d`）。

