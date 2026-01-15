# docx-lint

Word 文档格式检查工具 - 基于语义分类和样式检查的文档规范检查系统

## 特性

- ✅ **语义分类**：通过 Classifier 系统为文档元素添加语义标签（class）
- ✅ **样式检查**：基于 class 的样式检查，类似 CSS 的设计理念
- ✅ **灵活定位**：支持绝对定位、相对定位、区间定位等多种元素定位方式
- ✅ **自动单元转换**：支持 `三号`、`0.5行`、`2字符` 等人类可读单位
- ✅ **配置驱动**：通过 YAML 配置文件定义文档规范，无需修改代码
- ✅ **可扩展**：支持自定义字号、对齐方式等，无需修改代码
- ✅ **递归依赖解析**：自动处理 classifier 之间的依赖关系
- ✅ **循环依赖检测**：防止配置中出现循环依赖
- ✅ **多格式报告**：支持 Markdown 和 JSON 输出

## 快速开始

### 安装

使用 Poetry 管理依赖：

```bash
# 安装依赖
poetry install
```

### 使用

```bash
# 检查文档
poetry run docx-lint document.docx --config config/template/data_paper/config.yaml

# 输出 JSON 格式
poetry run docx-lint document.docx --config config/template/data_paper/config.yaml --format json

# 保存报告到文件
poetry run docx-lint document.docx --config config/template/data_paper/config.yaml --out report.md
```

## 架构说明

### 核心概念

系统采用类似 HTML/CSS 的设计理念：

1. **Classifier（语义标注）**：为文档元素添加 class 标签
   - 类似 HTML 元素的 class 属性
   - 通过位置、内容模式等规则识别元素
   - 支持复合区域（children）和嵌套结构

2. **StyleChecker（样式检查）**：检查每个 class 的样式是否符合要求
   - 类似 CSS 样式定义
   - 为每个 class 定义期望的字体、段落格式等
   - 比较实际样式与期望样式，生成 Issue

3. **Walker（文档遍历）**：按顺序遍历文档元素
   - 将文档解析为 Block 序列（ParagraphBlock、TableBlock）
   - 保持文档原始顺序

### 工作流程

```
文档 → Walker → Blocks → Classifier → Blocks with Classes → StyleChecker → Issues
```

1. **文档解析**：Walker 将文档解析为 Block 序列
2. **语义标注**：Classifier 为每个 Block 添加 class 标签
3. **样式检查**：StyleChecker 检查每个 class 的样式是否符合要求
4. **生成报告**：输出检查结果（Issues）

## 配置示例

### 基本结构

配置文件分为三个部分：

```yaml
document:
  # 1. 默认样式
  defaults:
    font:
      name_eastasia: 宋体
      name_ascii: "Times New Roman"
      size: 五号

  # 2. 元素识别规则（Classifiers）
  classifiers:
    - class: title
      match:
        type: paragraph
        position:
          type: absolute
          index: 0  # 文档第一段

  # 3. 样式定义（Styles）
  styles:
    .title:
      font:
        name_eastasia: 黑体
        size: 三号
      paragraph:
        alignment: 居中
```

### Classifier 示例

```yaml
# 简单定位：论文标题（第一段）
- class: title
  match:
    type: paragraph
    position:
      type: absolute
      index: 0

# 模式匹配：摘要（以"摘要："开头）
- class: abstract
  match:
    type: paragraph
    pattern: "^摘要："

# 相对定位：作者区域（标题和摘要之间）
- class: author-section
  match:
    type: paragraph
    position:
      type: relative
      index: (title, abstract)  # 开区间
  # 复合区域：子元素
  children:
    - class: author-list
      match:
        position:
          type: relative
          index: 0  # 父区域的第一个
    - class: corresponding-author
      match:
        position:
          type: relative
          index: -1  # 父区域的最后一个
```

### Style 示例

```yaml
# 标题样式
.title:
  font:
    name_eastasia: 黑体
    name_ascii: "Times New Roman"
    size: 三号
  paragraph:
    alignment: 居中
    space_before: 0.5行
    space_after: 0.5行

# 正文样式
.body:
  font:
    size: 五号
  paragraph:
    alignment: 两端对齐
    first_line_indent: 2字符
    line_spacing: 1.5倍
```

## 支持的定位方式

### 1. 绝对定位

相对于整个文档的位置：

```yaml
position:
  type: absolute
  index: 0      # 第一个元素
  index: -1     # 最后一个元素
```

### 2. 相对定位（区间）

两个锚点之间的区域：

```yaml
position:
  type: relative
  index: (title, abstract)    # 开区间：不包含 title 和 abstract
  index: [title, abstract)    # 左闭右开：包含 title，不包含 abstract
```

### 3. 相对定位（父区域内）

用于 children 规则：

```yaml
position:
  type: relative
  index: 0      # 父区域的第一个
  index: -1     # 父区域的最后一个
```

### 4. 模式匹配

基于内容的正则表达式匹配：

```yaml
pattern: "^摘要："           # 以"摘要："开头
pattern: "^\\d+\\s+\\S+"    # 一级标题格式
```

详见 [doc/POSITION_SYNTAX.md](doc/POSITION_SYNTAX.md)

## 扩展功能

系统支持通过配置文件扩展功能，无需修改代码：

### 自定义字号

```yaml
document:
  font_size_aliases:
    "特大号": 48
    "正文": 10.5
```

### 自定义对齐方式（支持多语言）

```yaml
document:
  alignment_aliases:
    "中央揃え": "CENTER"  # 日语
    "centré": "CENTER"     # 法语
```

### 调整字符宽度和行高比例

```yaml
document:
  char_width_ratio: 1.0    # 字符宽度与字号的比例
  line_height_ratio: 1.2   # 行高与字号的比例
```

详见 [doc/EXTENSIONS.md](doc/EXTENSIONS.md)

## 项目结构

```
.
├── config/                      # 配置文件
│   └── template/
│       └── data_paper/          # 数据论文模板
│           ├── config.yaml      # 主配置（导入其他配置）
│           ├── classifiers.yaml # 元素识别规则
│           ├── styles.yaml      # 样式定义
│           └── rules.yaml       # 内容规则（待实现）
├── script/                      # 源代码
│   ├── core/                    # 核心引擎
│   │   ├── classifier.py        # 语义分类器
│   │   ├── style_checker.py     # 样式检查器
│   │   ├── walker.py            # 文档遍历器
│   │   ├── model.py             # 数据模型
│   │   └── engine.py            # 主引擎
│   ├── reporters/               # 报告生成器
│   │   ├── markdown_reporter.py
│   │   └── json_reporter.py
│   ├── utils/                   # 工具函数
│   │   └── unit_converter.py   # 单位转换
│   ├── cli.py                   # CLI 入口
│   └── config_loader.py         # 配置加载器
├── doc/                         # 文档
│   ├── ARCHITECTURE.md          # 架构设计
│   ├── POSITION_SYNTAX.md       # 定位语法说明
│   ├── RULES.md                 # 规则系统设计
│   └── LIMITATIONS.md           # 系统限制
├── test/                        # 测试用例
├── pyproject.toml               # Poetry 配置
└── README.md                    # 本文件
```

## 核心组件

### Classifier

负责为文档元素添加语义标签：

- **PositionMatcher**：绝对位置匹配
- **PatternMatcher**：正则表达式匹配
- **RelativeMatcher**：相对位置匹配（区间）
- **RelativePositionInRangeMatcher**：父区域内相对位置匹配
- **递归依赖解析**：自动处理 classifier 之间的依赖关系
- **循环依赖检测**：防止配置错误

### StyleChecker

负责检查元素样式：

- 字体检查：名称、大小、加粗、斜体
- 段落格式检查：对齐、行距、缩进、间距
- 自动单位转换：pt、行、字符等

### Walker

负责文档遍历：

- 将文档解析为 Block 序列
- 支持 ParagraphBlock 和 TableBlock
- 保持文档原始顺序

## 依赖

- Python >= 3.8.1
- pyyaml >= 6.0
- python-docx >= 1.1.0

## 许可

MIT License

## 相关文档

- [doc/ARCHITECTURE.md](doc/ARCHITECTURE.md) - 详细架构说明
- [doc/POSITION_SYNTAX.md](doc/POSITION_SYNTAX.md) - 定位语法文档
- [doc/RULES.md](doc/RULES.md) - 规则系统设计
- [doc/LIMITATIONS.md](doc/LIMITATIONS.md) - 系统限制说明
