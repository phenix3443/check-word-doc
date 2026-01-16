# docx-lint 架构设计

## 核心理念

基于 **HTML/CSS 分离思想**，将文档检查分为两个独立的阶段：

1. **语义标注阶段**：遍历文档，根据规则给元素添加 class（类似 HTML 的语义标签）
2. **样式检查阶段**：根据 class 定义的样式规则检查元素格式（类似 CSS 样式定义）

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│  Word 文档   │ ──→ │  语义标注     │ ──→ │  样式检查    │
│  (docx)     │      │ (Classifier) │      │  (Checker)  │
└─────────────┘      └──────────────┘      └─────────────┘
     ↓                     ↓                      ↓
  段落、表格           添加 class 属性          比对样式定义
```

## 类比 Web 前端

| Web 开发 | docx-lint | 说明 |
|---------|-----------|------|
| HTML 元素 | Word 段落/表格 | 文档的基本组成单元 |
| class 属性 | 语义标签 | 标识元素的语义角色 |
| CSS 样式 | 格式规则 | 定义元素应有的样式 |
| DOM 遍历 | Walker | 按顺序访问元素 |
| CSS 选择器 | Classifier | 匹配和标注元素 |

### 示例对比

**Web 开发：**

```html
<!-- HTML: 内容 + 语义 -->
<h1 class="title">文章标题</h1>
<div class="author-info">
  <p class="author-list">张三，李四</p>
  <p class="affiliation">北京大学</p>
</div>
```

```css
/* CSS: 样式定义 */
.title {
  font-family: "黑体";
  font-size: 16pt;
  text-align: center;
}

.author-list {
  font-family: "楷体";
  font-size: 12pt;
  text-align: center;
}
```

**docx-lint：**

```yaml
# 配置：语义识别规则
classifiers:
  # 绝对定位：文档第一段
  - class: title
    match:
      # type: paragraph  # 默认值，可省略
      position:
        type: absolute
        index: 0

  # 模式匹配：以"摘要："开头
  - class: abstract
    match:
      # type: paragraph  # 默认值，可省略
      pattern: "^摘要：.*$"

  # 区间定位：标题和摘要之间
  - class: author-section
    match:
      # type: paragraph  # 默认值，可省略
      position:
        type: between
        class: [title, abstract]

# 配置：样式定义
styles:
  .title:
    font:
      name_eastasia: 黑体
      size: 三号
    paragraph:
      alignment: 居中

  .author-section:
    font:
      name_eastasia: 楷体
      size: 小四
    paragraph:
      alignment: 居中
```

## 系统架构

### 整体流程

```
1. 加载配置
   ├── classifiers（元素识别规则）
   ├── styles（样式定义）
   ├── rules（内容规则检查）
   └── defaults（全局默认样式）

2. 遍历文档（Walker）
   └── 顺序访问所有段落和表格

3. 语义标注（Classifier）
   ├── 分析规则依赖关系
   ├── 递归处理规则（确保依赖先被处理）
   ├── 根据 classifiers 规则匹配元素
   ├── 给匹配的元素添加 class 属性
   └── 支持多种匹配方式：
       ├── position 定位（通过 position 字段）
       │   ├── absolute: 绝对位置（index: 0, -1）
       │   ├── between: 区间定位（class: [a, b]）
       │   ├── next: 下一个元素（class: xxx）
       │   └── prev: 上一个元素（class: xxx）
       ├── pattern: 内容模式匹配
       └── class 引用（引用其他已识别的元素）

4. 样式检查（StyleChecker）
   ├── 遍历所有带 class 的元素
   ├── 查找对应的样式定义
   ├── 检查元素的实际格式
   └── 生成 Issue 报告

5. 内容规则检查（RuleChecker）
   ├── 遍历所有带 class 的元素
   ├── 应用对应的内容规则
   ├── 检查逻辑条件、内容格式等
   └── 生成 Issue 报告

6. 输出报告
   └── Markdown 或 JSON 格式
```

### 核心模块

#### 1. Classifier（分类器）

负责元素识别和 class 标注。

**关键特性：递归依赖解析 + 循环依赖检测**

当规则之间存在依赖关系时（例如 `author-section` 依赖 `title` 和 `abstract`），
Classifier 会自动分析依赖并按正确顺序处理：

1. **循环依赖检测**（初始化时）
   - 使用 DFS + 三色标记法检测有向图中的环
   - 如果检测到循环依赖，立即抛出 `ValueError` 并报告循环路径
   - 例如：`A -> B -> C -> A` 会被检测并报错

2. **依赖提取**
   - 提取每条规则的依赖（通过 `_extract_dependencies`）
   - 分析 `position` 中的 `class` 引用（`type: next/before/relative`）

3. **递归处理**
   - 递归处理依赖规则（通过 `_process_rule_with_dependencies`）
   - 使用记忆化避免重复处理

**正确示例（无循环）：**

```yaml
# author-section 引用了 title 和 abstract
- class: author-section
  match:
    type: paragraph
    position:
      type: relative
      index: (title, abstract)  # 依赖 title 和 abstract
```

处理顺序：`title` → `abstract` → `author-section` ✅

**错误示例（循环依赖）：**

```yaml
# ❌ 错误：A 依赖 B，B 依赖 A
- class: section-a
  match:
    position:
      type: next
      class: section-b

- class: section-b
  match:
    position:
      type: next
      class: section-a
```

错误信息：`检测到循环依赖: section-a -> section-b -> section-a`

```python
class Classifier:
    """元素分类器（支持递归依赖解析）"""

    def classify(self, blocks: List[Block]) -> List[Block]:
        """给文档元素添加 class 属性"""
        for block in blocks:
            for rule in self.rules:
                if self._match(block, rule, blocks):
                    block.add_class(rule['class'])
        return blocks

    def _match(self, block: Block, rule: dict, context: List[Block]) -> bool:
        """判断元素是否匹配规则"""
        # 支持多种匹配方式
        # - type: 元素类型（默认 paragraph）
        # - position: {type: absolute} - 绝对位置
        # - position: {type: relative} - 相对位置/区间
        # - position: {type: next} - 紧跟定位
        # - position: {type: prev} - 之前定位
        # - position: {type: between} - 区间定位
        # - pattern: 识别型内容模式（用于识别元素身份，不用于验证格式）
        pass
```

#### 2. StyleChecker（样式检查器）

负责根据 class 检查元素样式。

```python
class StyleChecker:
    """样式检查器"""

    def check(self, blocks: List[Block]) -> List[Issue]:
        """检查所有元素的样式"""
        issues = []
        for block in blocks:
            for class_name in block.classes:
                style_def = self.styles.get(f'.{class_name}')
                if style_def:
                    issues.extend(self._check_style(block, style_def))
        return issues

    def _check_style(self, block: Block, style_def: dict) -> List[Issue]:
        """检查单个元素的样式"""
        # 检查字体、段落格式等
        pass
```

#### 3. Block（文档元素）

扩展后的 Block 模型，支持 class 属性。

```python
@dataclass
class Block:
    """文档元素基类"""
    index: int
    classes: List[str] = field(default_factory=list)

    def add_class(self, class_name: str):
        """添加 class"""
        if class_name not in self.classes:
            self.classes.append(class_name)

    def has_class(self, class_name: str) -> bool:
        """检查是否有指定 class"""
        return class_name in self.classes

@dataclass
class ParagraphBlock(Block):
    """段落元素"""
    paragraph: Paragraph

@dataclass
class TableBlock(Block):
    """表格元素"""
    table: Table
```

## 匹配规则详解

### 元素类型（type）

**默认值**：`paragraph`

所有匹配规则默认匹配段落元素。如果需要匹配表格，需要显式指定：

```yaml
# 默认匹配段落（可省略 type）
- class: title
  match:
    position:
      type: absolute
      index: 0

# 显式指定匹配表格
- class: data-table
  match:
    type: table
    position:
      type: absolute
      index: 5
```

### 1. 绝对位置匹配

```yaml
- class: title
  match:
    type: paragraph
    position:
      type: absolute
      index: 0  # 文档第一个段落
```

### 2. 内容模式匹配

**用途**：用于**识别元素身份**的特征模式

```yaml
- class: abstract
  match:
    # type: paragraph  # 默认值，可省略
    pattern: "^摘要：.*$"  # 识别：以"摘要："开头的是摘要

- class: keywords
  match:
    pattern: "^关键词：.*$"  # 识别：以"关键词："开头的是关键词
```

**重要原则**：

- ✅ **识别型 pattern**：用于识别元素的身份特征（如 `^摘要：`、`^Abstract:`）
- ❌ **验证型 pattern**：用于验证内容格式的 pattern 应该放在 `rules.yaml` 中

**示例对比**：

```yaml
# ✅ 正确：识别型 pattern（放在 classifiers.yaml）
- class: abstract
  match:
    pattern: "^摘要：.*$"  # 识别元素身份

# ❌ 错误：验证型 pattern（应该放在 rules.yaml）
- class: author-list
  match:
    pattern: "^.*[,，、].*$"  # 验证内容格式
```

### 3. 紧跟定位匹配

```yaml
- class: title-en
  match:
    type: paragraph
    position:
      type: next
      class: keywords  # 紧跟在 keywords 之后
```

### 4. 区间定位匹配

```yaml
- class: author-section
  match:
    type: paragraph
    position:
      type: between
      class: [title, abstract]  # 标题和摘要之间
```

### 5. 复合区域匹配 (children) ⭐

对于复杂的文档结构，使用 **复合区域** + **相对定位**：

```yaml
# 父区域：作者信息区域
- class: author-section
  match:
    type: paragraph
    position:
      type: between
      class: [title, abstract]  # 标题和摘要之间

  # 子元素：使用相对定位（相对于父区域）
  children:
    # 第一个：作者列表
    - class: author-list
      match:
        position:
          type: relative
          index: 0  # 父区域的第一个
        pattern: ".*[,，].*"

    # 中间：作者单位（可变数量）
    - class: author-affiliation
      match:
        position:
          type: between
          class: [author-list, corresponding-author]  # 区间定位
        pattern: "^\\d+\\."

    # 最后：通信作者
    - class: corresponding-author
      match:
        position:
          type: relative
          index: -1  # 父区域的最后一个
        pattern: "^\\*"
```

**相对位置索引：**

- `0` - 父区域的第一个元素
- `-1` - 父区域的最后一个元素
- `between` + `class: [class1, class2]` - 父区域内两个元素之间的区间

**优势：**

- ✅ 适应可变数量的元素
- ✅ 语义清晰，体现层次结构
- ✅ 类似 HTML 的 DOM 树结构

## 样式定义详解

### 基本语法

```yaml
styles:
  .class-name:
    font:
      name_eastasia: 字体名
      name_ascii: 西文字体名
      size: 字号
      bold: true/false
      italic: true/false
    paragraph:
      alignment: 对齐方式
      line_spacing: 行距
      first_line_indent: 首行缩进
      space_before: 段前间距
      space_after: 段后间距
```

### 样式继承（未来扩展）

```yaml
styles:
  # 基础样式
  .paragraph:
    font:
      size: 小四
    paragraph:
      line_spacing: 1.5倍

  # 继承基础样式
  .author-info:
    extends: .paragraph
    font:
      name_eastasia: 楷体  # 覆盖字体
```

## 配置文件结构

完整的配置文件包含四部分：

```yaml
document:
  # 1. 元素识别规则
  classifiers:
    - class: title
      match: {...}
    - class: abstract
      match: {...}

  # 2. 样式定义
  styles:
    .title:
      font: {...}
      paragraph: {...}
    .abstract:
      font: {...}

  # 3. 内容规则检查（可选）
  rules:
    - id: author-superscript-check
      class: author-list
      conditions: {...}
      message: "..."

  # 4. 全局默认样式（可选）
  defaults:
    font:
      size: 小四
      name_eastasia: 宋体
    paragraph:
      line_spacing: 1.5倍
```

## 调试支持

### 1. 输出文档结构

可以输出文档的 class 标注结果，方便调试：

```bash
poetry run docx-lint document.docx --config config.yaml --debug-structure

# 输出：
# [0] .title: "数据论文标题"
# [1] .author-list: "张三¹，李四²"
# [2] .author-affiliation: "1. 北京大学，北京·100871"
# [3] .author-affiliation: "2. 清华大学，北京·100084"
# [4] .corresponding-author: "* 通信作者：..."
# [5] .abstract: "摘要：本文介绍..."
```

### 2. 可视化匹配过程

```bash
poetry run docx-lint document.docx --config config.yaml --verbose

# 输出：
# [Classifier] Checking block 0
#   - Rule 'title' (position: {type: absolute, index: 0}): ✓ MATCH
#   - Added class: title
# [Classifier] Checking block 1
#   - Rule 'title-en' (position: {type: next, class: keywords}): ✓ MATCH
#   - Added class: title-en
```

## 优势

1. ✅ **关注点分离**：语义识别 vs 样式检查
2. ✅ **直观易懂**：类似 HTML/CSS，学习曲线低
3. ✅ **灵活强大**：支持多种匹配方式组合
4. ✅ **多 class 支持**：一个元素可以有多个 class（如 HTML）
5. ✅ **易于调试**：可输出 class 标注结果
6. ✅ **可扩展**：未来可支持样式继承、变量等高级特性

## 核心特性

### 1. 多 class 支持

完全类似 HTML，一个元素可以同时拥有多个 class：

```yaml
classifiers:
  # 通用分类
  - class: paragraph
    match: {type: paragraph}

  # 特定分类
  - class: title
    match:
      position:
        type: absolute
        index: 0

  # 特殊标记
  - class: important
    match:
      position:
        type: absolute
        index: 0

# 结果：第一段会有 class="paragraph title important"
```

这使得我们可以：

- 定义通用样式（如 `.paragraph`）
- 定义特定样式（如 `.title`）
- 定义特殊样式（如 `.important`）
- 样式可以叠加和组合
