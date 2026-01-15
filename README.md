# docx-lint

Word 文档格式检查工具 - 声明式配置驱动的文档规范检查系统

## 特性

- ✅ **声明式配置**：直观描述文档结构，无需了解规则类实现
- ✅ **自动单元转换**：支持 `三号`、`0.5行`、`2字符` 等人类可读单位
- ✅ **自动规则生成**：从配置自动生成检查规则，无需修改代码
- ✅ **高度抽象**：配置即文档规范，新增文档类型只需添加配置文件
- ✅ **插件化架构**：规则插件化，易于扩展
- ✅ **统一输出**：所有规则输出统一的 Issue 格式
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
# 检查文档（使用声明式配置）
poetry run docx-lint document.docx --config config/data_paper_declarative.yaml

# 输出 JSON 格式
poetry run docx-lint document.docx --config config/data_paper_declarative.yaml --format json

# 保存报告到文件
poetry run docx-lint document.docx --config config/data_paper_declarative.yaml --out report.md
```

## 配置示例

声明式配置直观描述文档结构：

```yaml
document:
  # 默认设置
  defaults:
    font_size: 10.5pt
    font_name_eastasia: 宋体
    font_name_ascii: "Times New Roman"

  # 文档结构定义
  structure:
    # 标题（第一段）
    - type: paragraph
      name: 论文标题
      content:
        required: true
        min_length: 5
      font:
        name_eastasia: 黑体
        size: 三号  # 自动转换！
      paragraph:
        alignment: 居中
        space_before: 0.5行  # 自动转换！
        space_after: 0.5行

    # 作者信息（第二段）
    - type: paragraph
      name: 作者信息
      content:
        required: true
      font:
        size: 小四
      paragraph:
        alignment: 居中

  # 标题规则
  headings:
    styles: ["Heading 1", "Heading 2", "Heading 3"]
    check_sequence: true
    check_hierarchy: true

  # 参考文献规则
  references:
    heading: 参考文献
    check_citations: true
```

系统会自动生成所有必要的检查规则！

## 架构说明

详见 [doc/DECLARATIVE_CONFIG.md](doc/DECLARATIVE_CONFIG.md)

### 核心概念

1. **声明式配置**：描述"文档应该是什么样子"，而不是"用什么规则检查"
2. **自动规则生成**：`RuleGenerator` 根据配置自动创建规则实例
3. **自动单元转换**：`UnitConverter` 自动处理单位转换（pt、行、字符等）
4. **规则插件化**：所有检查封装为通用 `Rule` 类
5. **Block 统一遍历**：`Walker.iter_blocks()` 保持文档原始顺序

## 支持的检查类型

系统根据声明式配置自动生成以下类型的规则：

### 内容检查

- 段落存在性检查
- 最小/最大长度检查
- 内容必填检查

### 字体检查

- 字体名称检查（中文、西文）
- 字体大小检查
- 加粗、斜体检查

### 段落格式检查

- 对齐方式检查
- 行距检查
- 缩进和间距检查

### 标题检查

- 标题编号连续性检查
- 标题层级一致性检查
- 标题格式检查

### 参考文献检查

- 引用完整性检查（双向检查）
- 引用格式检查

### 标题规则（1 个）

- **HDG001**: 各级标题的编号应该连续

### 段落规则（6 个）

- **PAR002**: 检查连续空段落
- **PAR003**: 正文段落末尾必须使用句号或冒号
- **PAR004**: 中文字符之间不能有空格
- **PAR005**: 中文不能被英文引号包围
- **PAR006**: 中文引号应该左右匹配
- **PAR007**: 段落之间不要存在连续空行

### 参考文献规则（3 个）

- **REF001**: 文档必须包含参考文献章节
- **REF002**: 参考文献必须在正文中被引用
- **REF003**: 参考文献必须是一级标题

### 表格规则（3 个）

- **T001**: 表格尺寸验证（行数/列数）
- **T003**: 键值表验证（必需字段、值格式等）
- **T010**: 表格题注配对检查

**总计：20 个规则，12 个规则类**

## 配置文件

### 基线配置

- `config/base.yaml` - 主配置文件，导入所有基线规则
- `config/base/structure.yaml` - 结构规则
- `config/base/headings.yaml` - 标题规则
- `config/base/paragraphs.yaml` - 段落规则
- `config/base/references.yaml` - 参考文献规则

### 自定义配置

创建自己的配置文件：

```yaml
# my_config.yaml
import:
  - "base.yaml"  # 导入基线规则

# 覆盖或添加规则
rules:
  - id: "PAR003"
    enabled: false  # 禁用某个规则

  - id: "T001"
    params:
      min_rows: 3
      min_cols: 2
```

## 开发

### 运行测试

```bash
poetry run pytest
```

### 代码格式化

```bash
# 使用 black
poetry run black script/

# 使用 ruff 检查
poetry run ruff check script/
```

### 添加新规则

参见 [script/rules/README.md](script/rules/README.md)

## 项目结构

```
.
├── config/                  # 配置文件
│   ├── base.yaml
│   └── base/
│       ├── structure.yaml
│       ├── headings.yaml
│       ├── paragraphs.yaml
│       └── references.yaml
├── script/                  # 源代码
│   ├── core/               # 核心引擎
│   ├── rules/              # 规则系统
│   ├── reporters/          # 报告生成器
│   ├── settings/           # 可复用验证器
│   ├── cli.py              # CLI 入口
│   └── config_loader.py    # 配置加载
├── test/                    # 测试用例
├── doc/                     # 文档
│   └── plan.md             # vNext 架构设计
├── pyproject.toml          # Poetry 配置
├── ARCHITECTURE.md         # 架构说明
└── README.md               # 本文件
```

## 依赖

- Python >= 3.8.1
- pyyaml >= 6.0
- python-docx >= 1.1.0

## 许可

MIT License

## 相关文档

- [ARCHITECTURE.md](ARCHITECTURE.md) - 详细架构说明
- [doc/plan.md](doc/plan.md) - vNext 设计文档
- [script/rules/README.md](script/rules/README.md) - 规则系统文档
