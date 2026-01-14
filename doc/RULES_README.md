# 规则系统架构说明

## 设计理念

本项目采用**通用规则类 + 配置驱动**的架构，符合 vNext (plan.md) 的设计目标：
- 规则插件化
- 配置驱动
- 易于扩展
- 统一 Issue 输出

## 核心概念

### 通用规则类（Generic Rule Classes）

每个规则类对应**一类检查逻辑**，通过配置参数控制具体行为：

| 规则类 | 用途 | 服务的规则 ID |
|--------|------|--------------|
| `PresenceRule` | 元素存在性检查 | COV001, TOC001, FIG001, TBL001, REF001 等 |
| `PageContinuityRule` | 页码连续性检查 | TOC002, FIG002 |
| `PageAccuracyRule` | 页码准确性检查 | TOC003, FIG003, TBL003 |
| `HeadingNumberingRule` | 标题编号连续性 | HDG001 |
| `PunctuationRule` | 段落标点检查 | PAR003 |
| `ChineseSpacingRule` | 中文空格检查 | PAR004 |
| `EnglishQuotesRule` | 英文引号检查 | PAR005 |
| `ChineseQuoteMatchingRule` | 中文引号配对 | PAR006 |
| `ConsecutiveEmptyRule` | 连续空行/段落 | PAR002, PAR007 |

### 配置驱动（Configuration-Driven）

规则通过配置文件定义，无需修改代码：

```yaml
# config/base/structure.yaml
rules:
  - id: "COV001"
    enabled: true
    params:
      description: "文档必须包含封面"
      required: true
      keywords: ["题目", "标题", "作者"]
      check_first_n_blocks: 5

  - id: "TOC001"
    enabled: true
    params:
      description: "文档必须包含目录"
      required: true
      title_text: "目录"
      style_prefixes: ["TOC"]
```

### 规则注册（Rule Registry）

`registry.py` 负责：
1. 维护规则 ID 到规则类的映射
2. 从配置文件读取规则定义
3. 动态创建规则实例

```python
# registry.py
_RULE_CLASSES = {
    "COV001": PresenceRule,    # 封面检查
    "TOC001": PresenceRule,    # 目录检查
    "TOC002": PageContinuityRule,  # 目录页码连续性
    "PAR003": PunctuationRule,     # 段落标点检查
    # ...
}

def build_rules(config: dict) -> List[Rule]:
    """根据配置动态创建规则实例"""
    # 读取 config['rules']
    # 创建规则实例
    # 返回规则列表
```

## 文件结构

```
script/rules/
├── README.md              # 本文件
├── registry.py            # 规则注册表和构建器
├── structure_rules.py     # 结构相关规则类
├── paragraph_rules.py     # 段落相关规则类
├── reference_rules.py     # 参考文献规则类
├── table.py               # 表格规则类（已存在）
└── smoke.py               # 测试规则（已存在）
```

## 添加新规则

### 方式 1：使用现有规则类

如果新规则的检查逻辑与现有规则类相似，只需在配置文件中添加：

```yaml
rules:
  - id: "NEW001"
    enabled: true
    params:
      # 根据规则类的参数定义填写
```

然后在 `registry.py` 中注册：

```python
_RULE_CLASSES = {
    # ...
    "NEW001": PresenceRule,  # 使用现有规则类
}
```

### 方式 2：创建新规则类

如果需要全新的检查逻辑，创建新的规则类：

```python
@dataclass
class MyNewRule(Rule):
    id: str
    description: str = ""
    my_param: str = ""  # 自定义参数

    def applies_to(self, block: Block, ctx: Context) -> bool:
        # 判断是否应用到当前 block
        pass

    def check(self, block: Block, ctx: Context) -> List[Issue]:
        # 执行检查，返回 Issue 列表
        pass
```

## 优势

1. **一对多映射**：一个规则类可以服务多个规则 ID
2. **配置灵活**：添加新规则无需修改代码
3. **易于维护**：相似逻辑集中在一个类中
4. **类型安全**：使用 dataclass 和类型注解
5. **符合设计**：完全符合 plan.md 的插件化架构

## 与旧架构的对比

| 方面 | 旧架构 | 新架构 |
|------|--------|--------|
| 规则定义 | 硬编码类 | 通用类 + 配置 |
| 添加规则 | 修改代码 | 修改配置 |
| 代码重复 | 高 | 低 |
| 可维护性 | 低 | 高 |
| 扩展性 | 差 | 优秀 |

## 示例

完整的工作流程：

```python
from rules.registry import build_rules
from config_loader import ConfigLoader

# 1. 加载配置
loader = ConfigLoader('config/base.yaml')
config = loader.load()

# 2. 构建规则
rules = build_rules(config)
# 根据配置创建了 30+ 个规则实例

# 3. 运行引擎
from core.engine import DocxLint
engine = DocxLint(rules=rules, config=config)
issues = engine.run('document.docx')

# 4. 输出报告
from reporters.markdown_reporter import render_markdown
print(render_markdown(issues))
```

## 参考

- [plan.md](../../doc/plan.md) - vNext 架构设计
- [core/](../core/) - 核心模型（Block, Issue, Walker, Engine）
- [table.py](./table.py) - 表格规则示例
