# docx-lint

Word 文档格式检查工具 - 基于插件化规则引擎的 vNext 架构

## 特性

- ✅ **配置驱动**：通过 YAML 配置文件定义检查规则
- ✅ **插件化架构**：规则插件化，易于扩展
- ✅ **通用规则类**：一个规则类可服务多个规则 ID，减少代码重复 90%
- ✅ **顺序保证**：通过 Walker 保持文档原始顺序，确保题注配对等检查准确
- ✅ **统一输出**：所有规则输出统一的 Issue 格式
- ✅ **多格式报告**：支持 Markdown 和 JSON 输出

## 快速开始

### 安装

使用 Poetry 管理依赖：

```bash
# 安装依赖
poetry install

# 或者只安装运行时依赖
poetry install --only main
```

### 使用

```bash
# 检查文档
poetry run python script/cli.py document.docx --config config/base.yaml

# 输出 JSON 格式
poetry run python script/cli.py document.docx --config config/base.yaml --format json

# 保存报告到文件
poetry run python script/cli.py document.docx --config config/base.yaml --out report.md
```

### 使用脚本命令

安装后可以直接使用 `docx-lint` 命令：

```bash
# 安装
poetry install

# 使用
poetry run docx-lint document.docx --config config/base.yaml
```

## 架构说明

详见 [ARCHITECTURE.md](ARCHITECTURE.md)

### 核心概念

1. **Block 统一遍历**：`Walker.iter_blocks()` 保持文档原始顺序
2. **规则插件化**：所有检查封装为 `Rule`，输出统一 `Issue`
3. **配置驱动**：规则通过 YAML 定义，动态创建实例
4. **通用规则类**：一个类服务多个规则 ID

### 通用规则类示例

```python
# 一个 PresenceRule 类，服务 4 个规则 ID
_RULE_CLASSES = {
    "COV001": PresenceRule,  # 封面检查
    "TOC001": PresenceRule,  # 目录检查
    "FIG001": PresenceRule,  # 插图目录检查
    "TBL001": PresenceRule,  # 附表目录检查
}
```

配置示例：

```yaml
rules:
  - id: "COV001"
    params:
      keywords: ["题目", "作者"]  # 封面特定参数
  
  - id: "TOC001"
    params:
      title_text: "目录"         # 目录特定参数
```

## 已支持的检查规则

### 结构规则（7 个）

- **COV001**: 文档必须包含封面
- **TOC001**: 文档必须包含目录
- **TOC002**: 目录页码必须连续
- **TOC003**: 目录页码必须与实际一致（待完善）
- **FIG002**: 插图目录页码必须连续
- **FIG003**: 插图目录页码必须与实际一致（待完善）
- **TBL003**: 附表目录页码必须与实际一致（待完善）

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
