# 声明式配置指南

## 概述

声明式配置是 docx-lint 的全新配置方式，它允许你直接描述"文档应该是什么样子"，而不需要了解具体的规则类和检查逻辑。系统会自动根据你的描述生成相应的检查规则。

## 配置格式对比

### 传统格式（命令式）

```yaml
rules:
  - id: "FONT-001"
    params:
      description: "标题字体检查"
      target_blocks: [0]
      expected_font_name: "黑体"
      expected_font_size: 203200  # EMU 单位，需要手动计算
      expected_bold: false
```

**问题**：
- 需要了解规则 ID 和规则类
- 需要手动计算单位（EMU、twip 等）
- 配置冗长，不直观

### 声明式格式

```yaml
document:
  structure:
    - type: paragraph
      name: 论文标题
      font:
        name_eastasia: 黑体
        size: 三号  # 直接使用人类可读的单位
      paragraph:
        alignment: 居中
        space_before: 0.5行
        space_after: 0.5行
```

**优势**：
- ✅ 直观易读，描述文档结构
- ✅ 自动单元转换（16pt、三号、0.5行 等）
- ✅ 无需了解规则类实现
- ✅ 配置更简洁

## 配置结构

### 1. 文档默认设置

```yaml
document:
  defaults:
    font_size: 10.5pt  # 默认字体大小（五号）
    font_name_eastasia: 宋体  # 默认中文字体
    font_name_ascii: "Times New Roman"  # 默认西文字体
```

### 2. 文档结构定义

按照文档从上到下的顺序，描述每个重要元素：

```yaml
document:
  structure:
    # 第一个元素（block 0）
    - type: paragraph
      name: 论文标题
      content:
        required: true  # 必须存在
        min_length: 5  # 最少5个字符
      font:
        name_eastasia: 黑体
        name_ascii: "Times New Roman"
        size: 三号  # 支持：三号、小四、16pt 等
        bold: false
      paragraph:
        alignment: 居中  # 支持：居中、左对齐、右对齐、两端对齐
        space_before: 0.5行  # 支持：0.5行、12pt、2字符 等
        space_after: 0.5行
    
    # 第二个元素（block 1）
    - type: paragraph
      name: 作者信息
      content:
        required: true
        min_length: 2
      font:
        size: 小四
      paragraph:
        alignment: 居中
```

### 3. 标题规则配置

```yaml
document:
  headings:
    # 标题样式名称
    styles:
      - "Heading 1"
      - "Heading 2"
      - "Heading 3"
      - "标题 1"
      - "标题 2"
      - "标题 3"
    
    # 检查选项
    check_sequence: true  # 检查编号连续性
    check_hierarchy: true  # 检查层级一致性（如 2.3.1 必须在 2.3 之下）
    
    # 各级标题格式
    formats:
      - level: 1
        font:
          name_eastasia: 黑体
          size: 小二
          bold: true
        paragraph:
          alignment: 左对齐
          line_spacing: 1.5倍
      
      - level: 2
        font:
          name_eastasia: 黑体
          size: 小三
          bold: true
        paragraph:
          alignment: 左对齐
          line_spacing: 1.5倍
```

### 4. 参考文献配置

```yaml
document:
  references:
    heading: 参考文献  # 参考文献章节标题
    check_citations: true  # 检查正文引用
    check_citation_validity: true  # 检查引用有效性
    
    format:
      font:
        size: 小四
      paragraph:
        alignment: 两端对齐
        line_spacing: 1.5倍
```

## 单元转换

声明式配置支持自动单元转换，你可以使用人类可读的单位：

### 字体大小

```yaml
font:
  size: 三号      # 中文字号
  size: 小四      # 中文字号
  size: 16pt      # 磅数
  size: 16        # 数字默认为磅数
```

支持的中文字号：
- 初号(42pt)、小初(36pt)
- 一号(26pt)、小一(24pt)
- 二号(22pt)、小二(18pt)
- 三号(16pt)、小三(15pt)
- 四号(14pt)、小四(12pt)
- 五号(10.5pt)、小五(9pt)
- 六号(7.5pt)、小六(6.5pt)

### 间距和缩进

```yaml
paragraph:
  space_before: 0.5行    # 相对单位：行
  space_after: 12pt      # 绝对单位：磅
  first_line_indent: 2字符  # 相对单位：字符
  left_indent: 2字符
  right_indent: 0pt
```

支持的单位：
- **行**: `0.5行`、`1行`（相对于字体大小）
- **字符**: `2字符`、`1字`（相对于字体大小）
- **磅**: `12pt`、`12磅`
- **厘米**: `1cm`、`1厘米`
- **英寸**: `1in`、`1英寸`

### 行距

```yaml
paragraph:
  line_spacing: 1.5倍    # 倍数
  line_spacing: 单倍      # 预设值
  line_spacing: 20pt     # 固定值
```

支持的格式：
- **倍数**: `1.5`、`1.5倍`、`2倍`、`双倍`
- **预设**: `单倍`、`1.5倍`、`2倍`
- **固定值**: `20pt`（固定行高）

## 完整示例

参见 `config/data_paper_declarative.yaml`，这是一个完整的数据论文模板配置示例。

## 与传统格式混用

声明式配置可以与传统规则配置混用：

```yaml
# 导入基础规则（传统格式）
import:
  - base/paragraphs.yaml
  - base/headings.yaml

# 声明式配置
document:
  structure:
    - type: paragraph
      name: 标题
      font:
        size: 三号

# 额外的传统格式规则（可选）
rules:
  - id: "CUSTOM-001"
    params:
      description: "自定义规则"
```

## 自动生成的规则

系统会根据声明式配置自动生成以下类型的规则：

1. **内容检查规则** (`ParagraphContentRule`)
   - 检查段落是否存在
   - 检查最小/最大长度

2. **字体检查规则** (`FontStyleRule`)
   - 检查字体名称（中文、西文）
   - 检查字体大小
   - 检查加粗、斜体

3. **段落格式规则** (`ParagraphFormatRule`)
   - 检查对齐方式
   - 检查行距
   - 检查缩进和间距

4. **标题规则** (`HeadingNumberingRule`, `HeadingHierarchyRule`)
   - 检查标题编号连续性
   - 检查标题层级一致性

5. **参考文献规则** (`ReferencesCitationRule`, `CitationValidationRule`)
   - 检查引用完整性
   - 检查引用有效性

## 测试

运行测试以验证声明式配置：

```bash
poetry run python test/test_declarative_config.py
```

## 迁移指南

如果你有现有的传统格式配置，可以按照以下步骤迁移：

1. **保留基础规则导入**
   ```yaml
   import:
     - base/paragraphs.yaml
     - base/headings.yaml
     - base/references.yaml
   ```

2. **识别文档结构元素**
   - 标题在第几段？
   - 作者信息在第几段？
   - 摘要在第几段？

3. **为每个元素创建配置**
   ```yaml
   document:
     structure:
       - type: paragraph
         name: 元素名称
         content: {...}
         font: {...}
         paragraph: {...}
   ```

4. **测试配置**
   ```bash
   poetry run docx-lint --config your_config.yaml your_document.docx
   ```

## 优势总结

1. **更直观** - 配置就是文档规范的自然语言描述
2. **更简洁** - 无需了解规则类的实现细节
3. **更易维护** - 修改格式要求只需修改配置，无需改代码
4. **自动转换** - 自动处理单位转换，避免手动计算
5. **向后兼容** - 可以与传统规则配置混用

## 未来扩展

声明式配置系统还可以扩展到：
- 图表格式配置
- 页眉页脚配置
- 目录格式配置
- 更多自定义元素

---

**提示**: 声明式配置是推荐的配置方式，它让配置文件成为文档规范的一部分，而不仅仅是检查规则的列表。
