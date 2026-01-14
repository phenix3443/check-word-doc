## docx-lint vNext（planc）最新架构设计（不保留向后兼容）

### 1. 目标与约束

- **目标**：把 `check-word-doc` 重构为可扩展的 docx-lint，引入统一的 Block 遍历（保持 Word 原始顺序），用 Rule 插件化承载全部检查逻辑，统一 Issue 输出，适配本地与 CI。
- **不保留向后兼容**：旧的 `run_xxx_check()`、旧的 result dict 结构全部废弃，统一迁移到新引擎。
- **统一数据源**：默认使用 `python-docx` 的对象模型；必要时允许 Rule 直接读取 `document.xml` 做 XML 级扫描（性能或覆盖性原因），但输出仍必须是 Issue。

### 2. 为什么必须引入 Walker

Word 的正文由一串 Block 组成（段落 `w:p`、表格 `w:tbl`）。如果直接遍历 `doc.paragraphs` / `doc.tables` 会丢失原始顺序，导致：

- 无法稳定判断“某个表格前一个段落是不是题注”
- 无法实现“图片后必须紧跟图题/表题”
- 无法准确给出位置索引（block_index）

因此 vNext 以 **Walker.iter_blocks()** 作为所有规则的数据入口。

### 3. 核心对象模型（统一输出与统一输入）

#### 3.1 Issue 模型

```python
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class Severity(str, Enum):
    INFO = "info"
    WARN = "warn"
    ERROR = "error"


@dataclass
class Location:
    block_index: int
    kind: str
    hint: str


@dataclass
class Issue:
    code: str
    severity: Severity
    message: str
    location: Location
    evidence: Optional[dict] = None
```

#### 3.2 Block 模型（Lint 的基本单位）

```python
from dataclasses import dataclass
from typing import Union
from docx.text.paragraph import Paragraph
from docx.table import Table


@dataclass
class ParagraphBlock:
    index: int
    paragraph: Paragraph


@dataclass
class TableBlock:
    index: int
    table: Table


Block = Union[ParagraphBlock, TableBlock]
```

#### 3.3 Walker（保持原始顺序）

```python
from typing import Iterator
from docx import Document
from docx.oxml.text.paragraph import CT_P
from docx.oxml.table import CT_Tbl
from docx.text.paragraph import Paragraph
from docx.table import Table


class Walker:
    def iter_blocks(self, doc: Document) -> Iterator[Block]:
        body = doc.element.body
        idx = 0
        for child in body.iterchildren():
            if isinstance(child, CT_P):
                yield ParagraphBlock(idx, Paragraph(child, doc))
                idx += 1
            elif isinstance(child, CT_Tbl):
                yield TableBlock(idx, Table(child, doc))
                idx += 1
```

### 4. Context（文档级能力与共享索引）

Context 不仅承载 config，还应缓存常用索引，避免 Rule 重复扫描：

- blocks 列表（顺序 Block）
- 题注判断（style + 文本特征）
- heading 判断
- 可选：段落是否在表格单元格中（对某些规则很重要）

```python
from dataclasses import dataclass
from typing import Any, List
from docx import Document
from docx.text.paragraph import Paragraph


@dataclass
class Context:
    doc: Document
    config: dict
    blocks: List[Block]

    def is_heading(self, p: Paragraph) -> bool:
        name = (p.style.name or "").lower()
        return name.startswith("heading") or name.startswith("标题")

    def is_caption(self, p: Paragraph) -> bool:
        name = (p.style.name or "").lower()
        if name in {"caption", "题注", "图题", "表题"}:
            return True
        if "caption" in name:
            return True
        return False
```

### 5. Rule 接口与两种规则形态

#### 5.1 流式规则（per-block）

```python
from typing import Protocol, List


class Rule(Protocol):
    id: str

    def applies_to(self, block: Block, ctx: Context) -> bool: ...
    def check(self, block: Block, ctx: Context) -> List[Issue]: ...
```

#### 5.2 扫描规则（finalize）

用于需要跨 Block 关联的检查，例如：

- Figure 与 Caption 的配对
- Table 与 Caption 的配对
- 目录项与正文标题映射

约定：扫描规则在 `applies_to` 中只做收集，不立即产生 Issue；在 `finalize(ctx)` 输出 Issue。

### 6. 引擎：DocxLint（唯一入口）

```python
from docx import Document
from typing import List


class DocxLint:
    def __init__(self, rules: List[Rule], config: dict):
        self.rules = rules
        self.config = config

    def run(self, path: str) -> List[Issue]:
        doc = Document(path)
        blocks = list(Walker().iter_blocks(doc))
        ctx = Context(doc=doc, config=self.config, blocks=blocks)

        issues: List[Issue] = []
        for block in blocks:
            for rule in self.rules:
                if rule.applies_to(block, ctx):
                    issues.extend(rule.check(block, ctx))

        for rule in self.rules:
            fin = getattr(rule, "finalize", None)
            if callable(fin):
                issues.extend(fin(ctx))

        return issues
```

### 7. 表格检查设计（与现有脚本的差异点）

现有实现中，很多“表格相关检查”是通过：

- 单独遍历 `doc.tables`
- 或在 XML 层自己维护索引

vNext 要求：

- **所有表格结构检查基于 `TableBlock`**（行/列、首行、键值列、空单元格、合并单元格策略等）
- **所有表格题注配对检查基于 Block 顺序**（Table 前一个/后一个 Paragraph 是否是 caption）

建议的表格规则分层：

- `T001 TableDimensionsRule`：行数/列数/最小值/精确值
- `T002 TableHeaderRule`：首行标题匹配（可配置）
- `T003 KeyValueTableRule`：两列键值表：第一列 key 必须属于集合、第二列必须非空/匹配正则
- `T010 TableCaptionPairRule`（finalize）：表格与表题联动（前/后紧邻策略）
- `T020 TableCellStyleRule`：单元格内部 Paragraph 的字体/字号/对齐/行距等（可复用“设置类”模式）

### 8. Settings 模式（参考 FontSettings/ParagraphSettings）

vNext 推荐把“样式规范”抽象为 Settings 类（类似你在 `数据汇交` 中的 `FontSettings`、`ParagraphSettings`、`TableStyleSettings`），然后让 Rule 组合这些 settings 的 validators：

- `FontSettings`：run 级别字体
- `ParagraphSettings`：段落级格式
- `TableStyleSettings`：表格级（行列、表格对齐）、单元格级（垂直/水平对齐、padding）、单元格内段落样式

Rule 负责：

- 选择适用对象（某些 block、某些 style、某些区域）
- 调用 settings 的 validators
- 生成 Issue（带 location）

### 9. 配置（YAML）迁移原则

现有 `config/*.yaml` 可以继续使用“模块分区”的方式，但 vNext 建议将配置映射到 Ruleset：

- `rules`: 列出启用的规则与其参数
- `selectors`: 用于按 style/文本前缀/结构区段选择 block

示例（仅示意，具体字段以实现为准）：

```yaml
rules:
  - id: T001
    enabled: true
    params:
      min_rows: 2
      min_cols: 2
  - id: T010
    enabled: true
    params:
      caption_direction: before
      max_distance: 1
```

### 10. 目录结构（建议）

```
check-word-doc/
  script/
    core/
      model.py        # Severity/Issue/Location/Block
      walker.py       # Walker
      context.py      # Context
      engine.py       # DocxLint
    rules/
      heading.py
      paragraph.py
      table.py
      figure.py
      references.py
    reporters/
      markdown.py
      json.py
    cli.py            # argparse only, no check logic
  config/
    base.yaml
    example.yaml
  test/
    ...
```

### 11. 迁移策略（不保留兼容）

- **Step 1**：实现 `core/*`（model/walker/context/engine）并通过最小 ruleset 跑通
- **Step 2**：把每个旧检查脚本拆成一个或多个 Rule
- **Step 3**：用 reporter 统一输出 Markdown/JSON；删除旧的 result dict
- **Step 4**：把 `check.py` 替换为 `cli.py` + `engine.run()`，并删除 `functions.py` 的旧入口

### 12. 结论

vNext 的关键改动只有两条：

- **Block 顺序统一遍历（Walker）**
- **规则插件化（Rule + Issue）**

在这两条之上，表格/图片/目录等复杂联动检查都会变得自然且可持续演进。

