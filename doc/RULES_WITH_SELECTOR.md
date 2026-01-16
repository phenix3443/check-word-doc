# Rules 配置 - 使用 Selector 语法

## 概述

使用 Selector 语法可以让 rules.yaml 更加简洁和强大，规则定义更加灵活。

## 新语法设计

### 基本结构

```yaml
document:
  rules:
    - id: rule-id
      name: 规则名称
      description: 规则描述
      selector: ".class-name"  # 使用选择器语法
      condition:                # 可选：条件判断
        selector: ".other-class"
        pattern: "regex"
      check:
        pattern: "regex"        # 内容检查
        # 或其他检查类型
      severity: error|warning
      message: 错误消息
```

### 对比：旧语法 vs 新语法

#### 示例1: 简单规则

**旧语法**：
```yaml
- id: r-001
  name: 作者单位编号规则
  applies_to: author-affiliation
  check:
    pattern: "^\\d+\\."
  severity: error
  message: "作者单位必须以数字编号开头"
```

**新语法**：
```yaml
- id: r-001
  name: 作者单位编号规则
  selector: ".author-affiliation"  # 使用选择器
  check:
    pattern: "^\\d+\\."
  severity: error
  message: "作者单位必须以数字编号开头"
```

#### 示例2: 带条件的规则

**旧语法**：
```yaml
- id: r-002
  name: 多作者时的编号规则
  applies_to: author-affiliation
  condition:
    class: author-list
    pattern: ".*[,，、].*"
  check:
    pattern: "^\\d+\\."
  severity: error
  message: "多个作者时，作者单位必须以数字编号开头"
```

**新语法**：
```yaml
- id: r-002
  name: 多作者时的编号规则
  selector: ".author-affiliation"
  condition:
    selector: ".author-list"  # 使用选择器
    pattern: ".*[,，、].*"
  check:
    pattern: "^\\d+\\."
  severity: error
  message: "多个作者时，作者单位必须以数字编号开头"
```

#### 示例3: 使用伪类选择器

**新语法特有功能**：
```yaml
# 检查第一个作者单位
- id: r-010
  name: 第一个作者单位格式
  selector: ".author-affiliation:first"  # 使用伪类
  check:
    pattern: "^1\\."
  severity: error
  message: "第一个作者单位必须以 '1.' 开头"

# 检查第二条参考文献
- id: r-020
  name: 第二条参考文献格式
  selector: ".reference-item:nth(1)"  # 使用 nth 伪类
  check:
    pattern: "^\\[2\\]"
  severity: error
  message: "第二条参考文献必须以 '[2]' 开头"
```

#### 示例4: 使用相邻兄弟选择器

**新语法特有功能**：
```yaml
# 检查引言标题后的第一段正文
- id: r-030
  name: 引言第一段格式
  selector: ".heading-introduction + .body-introduction"  # 相邻兄弟
  check:
    pattern: "^\\s{2}"  # 检查首行缩进
  severity: warning
  message: "引言第一段应该首行缩进2字符"
```

#### 示例5: 复杂条件

**新语法**：
```yaml
# 检查：如果有多个作者单位，每个单位都要有编号
- id: r-040
  name: 多作者单位编号检查
  selector: ".author-affiliation"
  condition:
    # 条件：作者单位数量 > 1
    selector: ".author-affiliation"
    count: "> 1"  # 新增：数量判断
  check:
    pattern: "^\\d+\\."
  severity: error
  message: "多个作者单位时，每个单位必须有编号"
```

## 完整示例：数据论文规则

```yaml
document:
  rules:
    # ========== 作者信息规则 ==========
    
    # 作者列表分隔符
    - id: r-001
      name: 作者列表分隔符规则
      selector: ".author-list"
      check:
        pattern: "^[^,;；、]+\\d+[*]?(，[^,;；、]+\\d+[*]?)*$"
      severity: error
      message: "多个作者之间必须使用中文逗号（，）分隔"
    
    # 作者编号规则
    - id: r-002
      name: 作者编号规则
      selector: ".author-list"
      check:
        pattern: "\\d+"
      severity: error
      message: "每个作者后面必须有数字编号"
    
    # 通讯作者标记
    - id: r-003
      name: 通讯作者标记规则
      selector: ".corresponding-author"
      check:
        pattern: "^\\*"
      severity: error
      message: "通讯作者信息必须以星号开头"
    
    # 第一个作者单位编号
    - id: r-004
      name: 第一个作者单位编号
      selector: ".author-affiliation:first"
      check:
        pattern: "^1\\."
      severity: error
      message: "第一个作者单位必须以 '1.' 开头"
    
    # 第二个作者单位编号
    - id: r-005
      name: 第二个作者单位编号
      selector: ".author-affiliation:nth(1)"
      check:
        pattern: "^2\\."
      severity: error
      message: "第二个作者单位必须以 '2.' 开头"
    
    # 作者单位格式（多作者）
    - id: r-006
      name: 作者单位格式（多作者）
      selector: ".author-affiliation"
      condition:
        selector: ".author-list"
        pattern: ".*[,，、].*"
      check:
        pattern: "^\\d+\\.\\s+.+，.+\\s{2,}\\d{6}$"
      severity: error
      message: "作者单位格式：编号. 单位/机构，城市  邮编"
    
    # ========== 参考文献规则 ==========
    
    # 第一条参考文献
    - id: r-010
      name: 第一条参考文献编号
      selector: ".reference-item:first"
      check:
        pattern: "^\\[1\\]"
      severity: error
      message: "第一条参考文献必须以 '[1]' 开头"
    
    # 参考文献编号连续性
    - id: r-011
      name: 参考文献编号连续性
      selector: ".reference-item"
      check:
        type: sequence  # 新增：序列检查
        pattern: "^\\[(\\d+)\\]"
        start: 1
        step: 1
      severity: error
      message: "参考文献编号必须从 [1] 开始连续递增"
    
    # ========== 章节规则 ==========
    
    # 引言后必须有内容
    - id: r-020
      name: 引言内容检查
      selector: ".heading-introduction + .body-introduction"
      check:
        exists: true  # 新增：存在性检查
      severity: error
      message: "引言标题后必须有引言内容"
    
    # 每个一级标题后必须有正文
    - id: r-021
      name: 标题后必须有正文
      selector: ".heading-data-collection, .heading-data-description"
      check:
        has_next: ".body-*"  # 新增：检查后续元素
      severity: warning
      message: "一级标题后必须有正文内容"
```

## 新增的检查类型

### 1. 存在性检查 (exists)

```yaml
check:
  exists: true  # 检查元素是否存在
```

### 2. 数量检查 (count)

```yaml
condition:
  selector: ".reference-item"
  count: "> 10"  # 检查数量
```

### 3. 序列检查 (sequence)

```yaml
check:
  type: sequence
  pattern: "^\\[(\\d+)\\]"
  start: 1
  step: 1
```

### 4. 相邻元素检查 (has_next/has_prev)

```yaml
check:
  has_next: ".body-introduction"  # 检查后续元素
  has_prev: ".heading-introduction"  # 检查前置元素
```

### 5. 内容长度检查 (length)

```yaml
check:
  length:
    min: 10
    max: 1000
```

## 选择器语法优势

### 1. 更简洁

**旧语法**：
```yaml
applies_to: author-affiliation
condition:
  class: author-list
```

**新语法**：
```yaml
selector: ".author-affiliation"
condition:
  selector: ".author-list"
```

### 2. 更强大

```yaml
# 可以使用伪类
selector: ".reference-item:first"
selector: ".reference-item:nth(1)"
selector: ".reference-item:last"

# 可以使用相邻兄弟选择器
selector: ".heading-introduction + .body-introduction"

# 可以使用属性选择器
selector: "[type='table']"
```

### 3. 更灵活

```yaml
# 可以组合多个选择器
selector: ".author-affiliation, .author-affiliation-en"

# 可以使用复杂的选择器
selector: ".author-section .author-affiliation:first"
```

### 4. 与 Classifier 一致

使用相同的选择器语法，降低学习成本：

```yaml
# Classifier
- class: author-affiliation
  match:
    position:
      type: next
      class: author-list

# Rule (使用相同的概念)
- id: r-001
  selector: ".author-list + .author-affiliation"
```

## 实现方案

### 1. RuleChecker 类

```python
class RuleChecker:
    """规则检查器（支持 Selector 语法）"""
    
    def __init__(self, rules: List[dict], blocks: List[Block]):
        self.rules = rules
        self.selector = Selector(blocks)
        self.blocks = blocks
    
    def check(self) -> List[Issue]:
        """执行所有规则检查"""
        issues = []
        
        for rule in self.rules:
            # 使用选择器选择目标元素
            selector_str = rule.get('selector')
            targets = self.selector.select(selector_str)
            
            # 检查条件
            if not self._check_condition(rule):
                continue
            
            # 对每个目标元素执行检查
            for target in targets:
                if not self._check_rule(rule, target):
                    issues.append(self._create_issue(rule, target))
        
        return issues
    
    def _check_condition(self, rule: dict) -> bool:
        """检查规则条件"""
        condition = rule.get('condition')
        if not condition:
            return True
        
        # 使用选择器检查条件
        selector_str = condition.get('selector')
        elements = self.selector.select(selector_str)
        
        # 检查数量条件
        if 'count' in condition:
            return self._check_count(elements, condition['count'])
        
        # 检查模式条件
        if 'pattern' in condition:
            return any(re.search(condition['pattern'], e.text) for e in elements)
        
        return True
    
    def _check_rule(self, rule: dict, target: Block) -> bool:
        """检查单个元素是否符合规则"""
        check = rule.get('check', {})
        
        # 模式检查
        if 'pattern' in check:
            return bool(re.search(check['pattern'], target.text))
        
        # 存在性检查
        if 'exists' in check:
            return check['exists']
        
        # 序列检查
        if check.get('type') == 'sequence':
            return self._check_sequence(rule, target)
        
        # 相邻元素检查
        if 'has_next' in check:
            return self._check_has_next(target, check['has_next'])
        
        return True
```

### 2. 配置验证

```python
def _validate_rule(self, rule: dict):
    """验证规则配置"""
    # 必需字段
    required = ['id', 'name', 'selector', 'check', 'severity', 'message']
    for field in required:
        if field not in rule:
            raise ConfigError(f"Rule {rule.get('id')} 缺少必需字段: {field}")
    
    # 验证选择器语法
    try:
        selector = Selector([])
        selector.parse(rule['selector'])
    except Exception as e:
        raise ConfigError(f"Rule {rule['id']} 选择器语法错误: {e}")
```

## 迁移指南

### 从旧语法迁移到新语法

1. **替换 applies_to**：
   ```yaml
   # 旧
   applies_to: author-affiliation
   
   # 新
   selector: ".author-affiliation"
   ```

2. **替换 condition.class**：
   ```yaml
   # 旧
   condition:
     class: author-list
   
   # 新
   condition:
     selector: ".author-list"
   ```

3. **使用新功能**：
   ```yaml
   # 添加伪类
   selector: ".author-affiliation:first"
   
   # 添加相邻兄弟选择器
   selector: ".heading-introduction + .body-introduction"
   ```

## 总结

使用 Selector 语法的优势：

- ✅ **更简洁**：语法更简单，配置更清晰
- ✅ **更强大**：支持伪类、相邻兄弟选择器等高级功能
- ✅ **更灵活**：可以组合多个选择器，表达复杂的规则
- ✅ **更一致**：与 Classifier 使用相同的选择器语法
- ✅ **更易学**：类似 CSS，降低学习成本

通过 Selector 语法，rules.yaml 可以更加简洁和强大！
