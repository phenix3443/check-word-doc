# 项目结构

## 概述

`check-word-doc` 是一个基于配置驱动的 Word 文档格式检查工具，采用类似 HTML/CSS 的设计理念。

## 目录结构

```
check-word-doc/
├── config/                          # 配置文件
│   ├── common/                      # 通用配置（可复用）
│   │   ├── classifiers.yaml         # 通用元素识别规则
│   │   └── styles.yaml              # 通用样式定义
│   ├── template/                    # 模板配置
│   │   └── data_paper/              # 数据论文模板
│   │       ├── config.yaml          # 主配置文件
│   │       ├── classifiers.yaml     # 元素识别规则
│   │       ├── styles.yaml          # 样式定义
│   │       └── rules.yaml           # 内容验证规则
│   └── extensions_example.yaml      # 扩展配置示例
│
├── script/                          # 源代码
│   ├── cli.py                       # 命令行接口
│   ├── config_loader.py             # 配置加载器
│   ├── core/                        # 核心模块
│   │   ├── classifier.py            # 元素分类器（语义标记）
│   │   ├── selector.py              # CSS 风格选择器
│   │   ├── style_checker.py         # 样式检查器
│   │   ├── walker.py                # 文档遍历器
│   │   ├── model.py                 # 数据模型
│   │   └── engine.py                # 检查引擎
│   ├── reporters/                   # 报告生成器
│   │   ├── json_reporter.py         # JSON 格式报告
│   │   └── markdown_reporter.py     # Markdown 格式报告
│   └── utils/                       # 工具类
│       ├── __init__.py
│       └── unit_converter.py        # 单位转换器
│
├── doc/                             # 文档
│   ├── ARCHITECTURE.md              # 架构设计文档
│   ├── POSITION_SYNTAX.md           # 定位语法说明
│   ├── SELECTOR.md                  # Selector 语法规范
│   ├── SELECTOR_EXAMPLES.md         # Selector 使用示例
│   ├── RULES_WITH_SELECTOR.md       # Rules 使用 Selector 语法
│   └── CONFIG_ALIGNMENT.md          # 配置对齐说明
│
├── examples/                        # 示例代码
│   └── selector_demo.py             # Selector 演示脚本
│
├── test/                            # 测试代码
│   ├── __init__.py
│   ├── config/                      # 配置加载测试
│   ├── selector/                    # Selector 测试
│   ├── paragraphs/                  # 段落测试
│   ├── reference/                   # 参考文献测试
│   └── struct/                      # 结构测试
│
├── README.md                        # 项目说明
├── INSTALL.md                       # 安装指南
├── pyproject.toml                   # 项目配置（Poetry）
├── .gitignore                       # Git 忽略文件
└── cspell.config.yaml               # 拼写检查配置
```

## 核心概念

### 1. 配置驱动架构

项目采用配置驱动的设计，所有检查规则都通过 YAML 配置文件定义，代码不包含任何硬编码的格式要求。

### 2. HTML/CSS 设计理念

借鉴 Web 前端的设计思想：

| Web 概念 | 本项目对应 | 说明 |
|---------|-----------|------|
| HTML 元素 | Word 文档元素 | 段落、表格、图片等 |
| CSS Class | Classifier | 语义标记（如 `.title`, `.author-list`） |
| CSS 样式 | Style | 字体、段落格式等 |
| CSS 选择器 | Selector | 查询和筛选元素 |

### 3. 三层配置体系

#### Layer 1: Classifiers（元素识别）

定义如何识别和标记文档元素：

```yaml
# 示例：识别论文标题
- class: title
  match:
    position:
      type: absolute
      index: 0
```

#### Layer 2: Styles（样式定义）

定义每个 class 的期望样式：

```yaml
# 示例：标题样式
.title:
  font:
    name_eastasia: 黑体
    name_ascii: "Times New Roman"
    size: 三号
  paragraph:
    alignment: 居中
```

#### Layer 3: Rules（内容验证）

定义内容级别的验证规则：

```yaml
# 示例：作者列表分隔符规则
- id: r-001
  name: 作者列表分隔符规则
  selector: ".author-list"
  check:
    pattern: "^[^,;；、]+\\d+[*]?(，[^,;；、]+\\d+[*]?)*$"
  severity: error
  message: "多个作者之间必须使用中文逗号（，）分隔"
```

## 工作流程

```
1. 加载配置
   ↓
2. 遍历文档（Walker）
   ↓
3. 元素分类（Classifier）
   ↓
4. 样式检查（StyleChecker）
   ↓
5. 内容验证（RuleChecker）
   ↓
6. 生成报告（Reporter）
```

## 配置文件说明

### config.yaml（主配置）

```yaml
# 导入其他配置文件
import:
  - ../../common/classifiers.yaml
  - ../../common/styles.yaml
  - classifiers.yaml
  - styles.yaml
  - rules.yaml

# 扩展配置（可选）
extensions:
  font_sizes:
    特大号: 36
  alignments:
    居中: center
```

### classifiers.yaml（元素识别）

定义文档元素的识别规则，支持：
- 绝对定位（`absolute`）
- 相对定位（`next`, `prev`, `between`）
- 模式匹配（`pattern`）
- 嵌套结构（`children`）

### styles.yaml（样式定义）

定义每个 class 的期望样式：
- 字体属性（中文字体、西文字体、字号、粗体等）
- 段落属性（对齐、缩进、行距、段前段后距等）

### rules.yaml（内容验证）

定义内容级别的验证规则：
- 使用 Selector 语法选择元素
- 支持模式匹配、存在性检查、数量检查等
- 支持条件规则

## 核心模块说明

### Classifier（分类器）

**功能**：识别和标记文档元素

**特性**：
- 递归依赖解析
- 循环依赖检测
- 支持复合区域（`children`）
- 支持多种定位方式

### Selector（选择器）

**功能**：查询和筛选已标记的元素

**特性**：
- CSS 风格的选择器语法
- 支持伪类（`:first`, `:last`, `:nth(n)`）
- 支持相邻兄弟选择器（`+`）
- 支持属性选择器（`[type="table"]`）

### StyleChecker（样式检查器）

**功能**：检查元素样式是否符合要求

**特性**：
- 字体检查（字体名称、字号、粗体、斜体等）
- 段落检查（对齐、缩进、行距、段间距等）
- 单位自动转换（pt、字符、行等）

### Walker（遍历器）

**功能**：遍历 Word 文档的所有元素

**特性**：
- 支持段落、表格、图片等
- 提供统一的元素访问接口

### ConfigLoader（配置加载器）

**功能**：加载和验证配置文件

**特性**：
- 支持配置文件导入（`import`）
- 配置合并和覆盖
- 配置验证
- 扩展配置支持

## 测试

### 测试结构

```
test/
├── config/          # 配置加载测试
├── selector/        # Selector 功能测试
├── paragraphs/      # 段落格式测试
├── reference/       # 参考文献测试
└── struct/          # 文档结构测试
```

### 运行测试

```bash
# 运行所有测试
poetry run pytest

# 运行特定测试
poetry run pytest test/selector/

# 运行 Selector 演示
poetry run python3 examples/selector_demo.py
```

## 扩展性

### 添加新的文档模板

1. 在 `config/template/` 下创建新目录
2. 创建 `config.yaml`, `classifiers.yaml`, `styles.yaml`, `rules.yaml`
3. 根据模板特点定义规则

### 添加新的检查规则

1. 在 `classifiers.yaml` 中添加元素识别规则
2. 在 `styles.yaml` 中添加样式定义
3. 在 `rules.yaml` 中添加内容验证规则

### 自定义扩展

在 `config.yaml` 中添加 `extensions` 配置：

```yaml
extensions:
  font_sizes:
    自定义字号: 24
  alignments:
    自定义对齐: custom
  character_width_ratio: 2.0
  line_height_ratio: 1.2
```

## 依赖管理

项目使用 Poetry 进行依赖管理：

```bash
# 安装依赖
poetry install

# 添加新依赖
poetry add package-name

# 更新依赖
poetry update
```

## 文档说明

| 文档 | 说明 |
|------|------|
| `README.md` | 项目概述、快速开始 |
| `INSTALL.md` | 安装指南 |
| `doc/ARCHITECTURE.md` | 架构设计详解 |
| `doc/POSITION_SYNTAX.md` | 定位语法详解 |
| `doc/SELECTOR.md` | Selector 语法规范 |
| `doc/SELECTOR_EXAMPLES.md` | Selector 使用示例 |
| `doc/RULES_WITH_SELECTOR.md` | Rules 使用 Selector |
| `doc/CONFIG_ALIGNMENT.md` | 配置对齐说明 |

## 配置对齐

为了便于维护，三个配置文件（classifiers.yaml、styles.yaml、rules.yaml）的内容顺序完全对齐，按照文档的自然顺序排列。

详见：`doc/CONFIG_ALIGNMENT.md`

## 开发指南

### 代码风格

- 遵循 PEP 8 规范
- 使用类型注解
- 编写清晰的文档字符串

### 提交规范

- 使用清晰的提交信息
- 一次提交只做一件事
- 更新相关文档

### 配置管理

- 保持三个配置文件的顺序一致
- 添加清晰的注释
- 使用完整匹配的正则表达式

## 总结

这是一个干净、现代、可扩展的 Word 文档格式检查工具，采用配置驱动的设计理念，借鉴 Web 前端的成熟思想，提供强大而灵活的文档格式检查能力。
