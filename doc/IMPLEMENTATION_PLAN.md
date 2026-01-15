# 实现计划

## 概述

基于 class-based 架构重构 docx-lint，分为 6 个主要任务。

## 任务拆分

### 任务 1：扩展 Block 模型 ✅

**目标**：扩展现有的 Block 类，添加 class 属性支持。

**文件**：`script/core/model.py`

**工作内容**：
1. 为 `Block` 基类添加 `classes` 属性
2. 添加 `add_class()` 方法
3. 添加 `has_class()` 方法
4. 添加 `get_classes()` 方法

**接口设计**：
```python
@dataclass
class Block:
    """文档元素基类"""
    index: int
    classes: List[str] = field(default_factory=list)
    
    def add_class(self, class_name: str) -> None:
        """添加 class"""
        if class_name not in self.classes:
            self.classes.append(class_name)
    
    def has_class(self, class_name: str) -> bool:
        """检查是否有指定 class"""
        return class_name in self.classes
    
    def get_classes(self) -> List[str]:
        """获取所有 class"""
        return self.classes.copy()
```

**验收标准**：
- [ ] Block 类支持 class 属性
- [ ] 单元测试通过

---

### 任务 2：实现 Classifier 系统 🔥

**目标**：实现元素识别和分类系统。

**文件**：`script/core/classifier.py`

**工作内容**：
1. 创建 `Classifier` 类
2. 实现各种匹配器（Matcher）：
   - `PositionMatcher` - 绝对位置匹配
   - `PatternMatcher` - 内容模式匹配
   - `RelativeMatcher` - 相对位置匹配
   - `RangeMatcher` - 范围匹配
3. 实现锚点解析（AnchorResolver）
4. 实现分类逻辑

**接口设计**：
```python
class Classifier:
    """文档元素分类器"""
    
    def __init__(self, rules: List[Dict[str, Any]]):
        """
        Args:
            rules: classifiers 配置
        """
        self.rules = rules
    
    def classify(self, blocks: List[Block]) -> List[Block]:
        """给所有元素添加 class 属性
        
        Args:
            blocks: 文档元素列表
            
        Returns:
            添加了 class 的元素列表（原地修改）
        """
        for rule in self.rules:
            self._apply_rule(rule, blocks)
        return blocks
    
    def _apply_rule(self, rule: dict, blocks: List[Block]) -> None:
        """应用单条规则"""
        class_name = rule['class']
        match_config = rule['match']
        
        for block in blocks:
            if self._match(block, match_config, blocks):
                block.add_class(class_name)
    
    def _match(self, block: Block, config: dict, context: List[Block]) -> bool:
        """判断元素是否匹配规则"""
        # 根据 config 类型选择不同的匹配器
        pass
```

**Matcher 接口**：
```python
class Matcher(ABC):
    """匹配器基类"""
    
    @abstractmethod
    def match(self, block: Block, context: List[Block]) -> bool:
        """判断是否匹配"""
        pass

class PositionMatcher(Matcher):
    """绝对位置匹配"""
    
    def __init__(self, position: int):
        self.position = position
    
    def match(self, block: Block, context: List[Block]) -> bool:
        return block.index == self.position

class PatternMatcher(Matcher):
    """内容模式匹配"""
    
    def __init__(self, pattern: str):
        self.pattern = re.compile(pattern)
    
    def match(self, block: Block, context: List[Block]) -> bool:
        if not isinstance(block, ParagraphBlock):
            return False
        text = block.paragraph.text or ""
        return bool(self.pattern.match(text))
```

**验收标准**：
- [ ] 支持 position 匹配
- [ ] 支持 pattern 匹配
- [ ] 支持 after/before 相对匹配
- [ ] 支持 range 范围匹配
- [ ] 单元测试通过

---

### 任务 3：实现 StyleChecker 系统 🔥

**目标**：实现基于 class 的样式检查。

**文件**：`script/core/style_checker.py`

**工作内容**：
1. 创建 `StyleChecker` 类
2. 解析 styles 配置
3. 实现字体检查
4. 实现段落格式检查
5. 生成 Issue 报告

**接口设计**：
```python
class StyleChecker:
    """样式检查器"""
    
    def __init__(self, styles: Dict[str, Any], defaults: Optional[Dict[str, Any]] = None):
        """
        Args:
            styles: styles 配置（如 {'.title': {font: {...}, paragraph: {...}}}）
            defaults: 全局默认样式（可选）
        """
        self.styles = styles
        self.defaults = defaults or {}
    
    def check(self, blocks: List[Block]) -> List[Issue]:
        """检查所有元素的样式
        
        Args:
            blocks: 已标注 class 的元素列表
            
        Returns:
            Issue 列表
        """
        issues = []
        for block in blocks:
            issues.extend(self._check_block(block))
        return issues
    
    def _check_block(self, block: Block) -> List[Issue]:
        """检查单个元素"""
        issues = []
        for class_name in block.classes:
            style_def = self.styles.get(f'.{class_name}')
            if style_def:
                issues.extend(self._check_style(block, style_def, class_name))
        return issues
    
    def _check_style(self, block: Block, style_def: dict, class_name: str) -> List[Issue]:
        """根据样式定义检查元素"""
        issues = []
        
        # 检查字体
        if 'font' in style_def:
            issues.extend(self._check_font(block, style_def['font'], class_name))
        
        # 检查段落格式
        if 'paragraph' in style_def:
            issues.extend(self._check_paragraph(block, style_def['paragraph'], class_name))
        
        return issues
```

**验收标准**：
- [ ] 支持字体检查（名称、大小、加粗、斜体）
- [ ] 支持段落格式检查（对齐、行距、缩进、间距）
- [ ] 生成正确的 Issue 报告
- [ ] 单元测试通过

---

### 任务 4：修改配置加载器

**目标**：支持新的配置格式（classifiers + styles）。

**文件**：`script/config_loader.py`

**工作内容**：
1. 更新配置验证逻辑
2. 支持 `classifiers` 节
3. 支持 `styles` 节
4. 支持 `defaults` 节

**验收标准**：
- [ ] 能加载新格式的配置文件
- [ ] 配置验证正确
- [ ] 单元测试通过

---

### 任务 5：集成到 Engine

**目标**：将 Classifier 和 StyleChecker 集成到检查引擎。

**文件**：`script/core/engine.py`

**工作内容**：
1. 修改 `DocxLint.lint()` 方法
2. 添加分类阶段
3. 添加样式检查阶段
4. 保持向后兼容（如果需要）

**流程**：
```python
def lint(self, doc_path: str) -> List[Issue]:
    # 1. 加载文档
    doc = Document(doc_path)
    
    # 2. 遍历文档，构建 Block 列表
    walker = Walker(doc)
    blocks = list(walker.iter_blocks())
    
    # 3. 分类阶段：给元素添加 class
    classifier = Classifier(self.config['classifiers'])
    blocks = classifier.classify(blocks)
    
    # 4. 样式检查阶段
    style_checker = StyleChecker(
        self.config['styles'],
        self.config.get('defaults')
    )
    issues = style_checker.check(blocks)
    
    return issues
```

**验收标准**：
- [ ] 完整的检查流程工作正常
- [ ] 生成正确的报告
- [ ] 集成测试通过

---

### 任务 6：创建新配置文件和测试

**目标**：创建数据论文的 class-based 配置文件并测试。

**文件**：`config/data_paper_class_based.yaml`

**工作内容**：
1. 根据数据论文模板创建配置
2. 定义所有 classifiers
3. 定义所有 styles
4. 测试实际文档

**配置示例**：
```yaml
document:
  defaults:
    font:
      size: 小四
      name_eastasia: 宋体
  
  classifiers:
    - class: title
      match:
        type: paragraph
        position: 0
    
    - class: author-list
      match:
        type: paragraph
        position: 1
        pattern: ".*[,，].*"
    
    # ... 更多规则
  
  styles:
    .title:
      font:
        name_eastasia: 黑体
        size: 三号
      paragraph:
        alignment: 居中
    
    # ... 更多样式
```

**验收标准**：
- [ ] 配置文件完整
- [ ] 能正确识别数据论文的各个部分
- [ ] 样式检查准确
- [ ] 通过实际文档测试

---

## 实现顺序

按以下顺序实现，确保每个任务完成后再进行下一个：

1. **任务 1**：扩展 Block 模型（基础设施） ✅
2. **任务 2**：实现 Classifier（核心功能）
3. **任务 3**：实现 StyleChecker（核心功能）
4. **任务 4**：修改配置加载器（支持新格式）
5. **任务 5**：集成到 Engine（串联整个流程）
6. **任务 6**：创建配置和测试（验证功能）

## 时间估计

- 任务 1：1 小时
- 任务 2：3-4 小时
- 任务 3：2-3 小时
- 任务 4：1 小时
- 任务 5：1-2 小时
- 任务 6：2 小时

**总计**：10-13 小时

## 测试策略

每个任务都需要：
1. 单元测试（pytest）
2. 集成测试（实际文档）
3. 边界情况测试

## 调试工具

实现过程中需要的调试功能：
1. `--debug-structure` - 输出文档的 class 标注结果
2. `--verbose` - 输出详细的匹配过程
3. 日志系统 - 记录分类和检查过程

## 文档

需要更新的文档：
- [x] ARCHITECTURE.md - 架构设计
- [x] CONFIG_FORMAT.md - 配置格式说明
- [x] IMPLEMENTATION_PLAN.md - 实现计划（本文件）
- [ ] README.md - 使用说明（实现完成后更新）
- [ ] EXAMPLES.md - 配置示例（实现完成后添加）
