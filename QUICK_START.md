# 快速开始指南

## 安装

```bash
# 克隆项目
git clone <repo-url>
cd check-word-doc

# 安装依赖（使用 Poetry）
poetry install
```

## 基本使用

### 检查文档

```bash
# 使用基线配置检查文档
poetry run docx-lint document.docx --config config/base.yaml
```

### 输出选项

```bash
# 输出 Markdown 格式（默认）
poetry run docx-lint document.docx --config config/base.yaml

# 输出 JSON 格式
poetry run docx-lint document.docx --config config/base.yaml --format json

# 保存报告到文件
poetry run docx-lint document.docx --config config/base.yaml --out report.md
```

## 配置文件

### 使用基线配置

项目提供了基线配置 `config/base.yaml`，包含所有基础检查规则：

- 结构检查：封面、目录、插图目录、附表目录
- 标题检查：标题编号连续性
- 段落检查：空行、标点、中文格式、引号等
- 参考文献检查：章节存在性、引用、标题级别

### 自定义配置

创建自己的配置文件：

```yaml
# my_config.yaml

# 导入基线配置
import:
  - "base.yaml"

# 禁用某些规则
rules:
  - id: "PAR003"
    enabled: false  # 不检查段落标点
  
  # 或修改规则参数
  - id: "HDG001"
    enabled: true
    params:
      description: "标题编号必须连续"
      check_heading_numbering: true
      heading_styles: ["Heading 1", "Heading 2"]
```

使用自定义配置：

```bash
poetry run docx-lint document.docx --config my_config.yaml
```

## 支持的检查规则

### 结构规则

| 规则 ID | 说明 | 状态 |
|---------|------|------|
| COV001 | 文档必须包含封面 | ✅ |
| TOC001 | 文档必须包含目录 | ✅ |
| TOC002 | 目录页码必须连续 | ✅ |
| TOC003 | 目录页码必须准确 | ⏳ |
| FIG002 | 插图目录页码连续 | ✅ |
| FIG003 | 插图目录页码准确 | ⏳ |
| TBL003 | 附表目录页码准确 | ⏳ |

### 标题规则

| 规则 ID | 说明 | 状态 |
|---------|------|------|
| HDG001 | 各级标题编号连续 | ✅ |

### 段落规则

| 规则 ID | 说明 | 状态 |
|---------|------|------|
| PAR002 | 连续空段落检查 | ✅ |
| PAR003 | 段落末尾标点检查 | ✅ |
| PAR004 | 中文字符间空格 | ✅ |
| PAR005 | 英文引号包围中文 | ✅ |
| PAR006 | 中文引号配对 | ✅ |
| PAR007 | 连续空行检查 | ✅ |

### 参考文献规则

| 规则 ID | 说明 | 状态 |
|---------|------|------|
| REF001 | 参考文献章节存在 | ✅ |
| REF002 | 参考文献被引用 | ✅ |
| REF003 | 参考文献标题级别 | ✅ |

### 表格规则

| 规则 ID | 说明 | 状态 |
|---------|------|------|
| T001 | 表格尺寸验证 | ✅ |
| T003 | 键值表验证 | ✅ |
| T010 | 表格题注配对 | ✅ |

## 示例输出

### Markdown 格式

```markdown
# Docx Lint Report

## COV001 (error)
- Location: block_index=0, kind=document
- Hint: (document)
- Message: 文档必须包含封面: 未找到封面

## PAR004 (error)
- Location: block_index=25, kind=paragraph
- Hint: 这是一个包含空格的段落...
- Message: 中文字符之间不能有一个或多个空格: 中文字符 '和' 和 '空格' 之间不应有空格
```

### JSON 格式

```json
[
  {
    "code": "COV001",
    "severity": "error",
    "message": "文档必须包含封面: 未找到封面",
    "location": {
      "block_index": 0,
      "kind": "document",
      "hint": "(document)"
    },
    "evidence": null
  }
]
```

## 常见问题

### Q: 如何只检查特定规则？

A: 在配置文件中只启用需要的规则：

```yaml
rules:
  - id: "TOC001"
    enabled: true
  - id: "REF001"
    enabled: true
  # 其他规则不列出或 enabled: false
```

### Q: 如何自定义规则参数？

A: 在配置文件的 `params` 中设置：

```yaml
rules:
  - id: "PAR003"
    params:
      required_punctuation: ["。", "！", "？"]  # 自定义允许的标点
      min_length: 20  # 修改最小长度阈值
```

### Q: 如何添加新规则？

A: 查看 [script/rules/README.md](script/rules/README.md) 的详细说明。

## 更多信息

- 架构设计：[ARCHITECTURE.md](ARCHITECTURE.md)
- 详细文档：[doc/plan.md](doc/plan.md)
- 规则系统：[script/rules/README.md](script/rules/README.md)
