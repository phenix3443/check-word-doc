# 配置文件说明

## 概述

本项目使用 YAML 格式的配置文件来管理文档格式检查规则。配置文件位于 `config/` 目录下，默认配置文件为 `default.yaml`。

## 配置文件结构

### 1. 检查项开关（checks）

控制各个检查项的启用/禁用状态：

```yaml
checks:
  cover: true                    # 封面检查
  table_of_contents: true        # 目录检查
  figure_list: true              # 图目录检查
  table_list: true               # 表目录检查
  body_paragraphs: true          # 正文段落检查
  body_headings: true            # 正文标题检查
  captions: true                 # 图表题注检查
  references: true               # 参考文献检查
  attachments: true              # 附件检查
  headers: true                  # 页眉检查
  footers: true                  # 页脚检查
  page_numbers: true             # 页码检查
  empty_lines: true              # 空行检查
  consecutive_empty_lines: true  # 连续空行检查
```

### 2. 格式要求（format）

每个检查项都包含格式要求配置，主要包括：

- **font**: 字体名称（如："宋体"、"黑体"）
- **size**: 字号（Word中的字号，如：12、14、16）
- **bold**: 是否加粗（true/false）
- **alignment**: 对齐方式（left/center/right/justify）
- **line_spacing**: 行距（数字，如1.5表示1.5倍行距）
- **first_line_indent**: 首行缩进（字符数）
- **hanging_indent**: 悬挂缩进（字符数）
- **space_before**: 段前间距（磅）
- **space_after**: 段后间距（磅）
- **error_message**: 错误提示信息

### 3. 编号检查（numbering）

用于检查编号的连续性和格式：

- **check_continuity**: 是否检查编号连续性
- **check_format**: 是否检查编号格式
- **format_pattern**: 编号格式正则表达式
- **error_message**: 错误提示信息

### 4. 验证规则（validation）

用于验证文档元素之间的关系：

- **check_page_numbers**: 检查页码准确性
- **check_title_match**: 检查标题匹配
- **check_citation_match**: 检查引用匹配
- **error_message**: 错误提示信息

### 5. 一致性检查（consistency）

用于检查格式的一致性：

- **check_consistency**: 是否检查一致性
- **check_format_consistency**: 是否检查格式一致性
- **allow_different_by_section**: 是否允许不同章节使用不同格式
- **error_message**: 错误提示信息

## 主要检查项配置说明

### 封面（cover）

检查封面的必需元素和格式要求。

**必需元素**：
- title（标题）
- author（作者）
- date（日期）

**可选元素**：
- subtitle（副标题）
- institution（机构）

### 目录（table_of_contents）

检查目录的格式和编号连续性。

### 图目录（figure_list）

检查图目录的格式、编号连续性和与正文中图片的对应关系。

### 表目录（table_list）

检查表目录的格式、编号连续性和与正文中表格的对应关系。

### 正文段落（body_paragraphs）

检查正文段落的格式要求，包括字体、字号、行距、首行缩进、对齐方式等。

**排除部分**：
- 封面
- 目录
- 图目录
- 表目录
- 参考文献
- 附件
- 附录

### 正文标题（body_headings）

检查各级标题的格式和编号。

**标题级别**：
- level 1: 一级标题（如：1）
- level 2: 二级标题（如：1.1）
- level 3: 三级标题（如：1.1.1）

### 图表题注（captions）

检查图和表的题注格式。

**格式要求**：
- 字体：宋体
- 字号：5号
- 对齐：居中

### 参考文献（references）

检查参考文献列表格式和正文中的引用格式。

**引用格式**：
- [1]：单个引用
- [1-3]：范围引用
- [1,2,3]：多个引用

### 页眉页脚（headers/footers）

检查页眉页脚的格式和一致性。

### 页码（page_numbers）

检查页码的格式、连续性和与目录的一致性。

## 使用方式

1. 使用默认配置：直接使用 `config/default.yaml`
2. 自定义配置：复制 `default.yaml` 并修改相应配置项
3. 在检查脚本中指定配置文件路径

## 注意事项

1. YAML 文件使用缩进表示层级关系，请保持正确的缩进
2. 字符串值建议使用引号包裹，特别是包含特殊字符时
3. 正则表达式中的特殊字符需要转义（如：`\d` 应写为 `\\d`）
4. 字号使用 Word 中的字号值（5号对应 size: 5）
5. 间距单位：段前/段后间距使用磅（pt），缩进使用字符数

