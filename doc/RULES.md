# 规则检查系统 (Rules)

## 概述

规则检查系统用于验证文档**内容**是否符合特定的业务规则，区别于：
- **Classifiers**：识别文档元素（这是什么）
- **Styles**：检查格式样式（字体、对齐、行距等）
- **Rules**：检查内容规则（逻辑、条件、依赖关系等）

## 配置文件

```
config/template/data_paper/
├── classifiers.yaml     # 元素识别
├── styles.yaml          # 样式检查
└── rules.yaml           # 规则检查（新增）
```

## 规则配置格式

### 基本结构

```yaml
document:
  rules:
    - id: r-001                    # 规则 ID（必需）
      name: 规则名称                # 规则名称（必需）
      description: 规则描述         # 详细说明（可选）
      applies_to: class-name       # 应用到哪个 class（必需）
      condition:                   # 条件（可选）
        class: other-class
        pattern: "..."
      check:                       # 检查内容（必需）
        pattern: "..."
      severity: error              # 严重程度（必需）
      message: 错误消息             # 错误提示（必需）
```

### 字段说明

#### 1. id（必需）
规则的唯一标识符。

**格式：** `r-XXX`（r 表示 rule，XXX 是三位数字）

**示例：**
```yaml
id: r-001
id: r-002
```

#### 2. name（必需）
规则的简短名称。

**示例：**
```yaml
name: 作者单位编号规则
name: 通讯作者标记规则
```

#### 3. description（可选）
规则的详细说明。

**示例：**
```yaml
description: 多个作者时，作者单位必须以数字编号开头
```

#### 4. applies_to（必需）
规则应用到哪个 class。

**示例：**
```yaml
applies_to: author-affiliation
applies_to: author-list
```

#### 5. condition（可选）
规则生效的条件。如果指定了条件，只有当条件满足时才会执行检查。

**格式：**
```yaml
condition:
  class: class-name    # 检查哪个 class
  pattern: "regex"     # 匹配模式
```

**示例：**
```yaml
# 条件：author-list 中包含多个作者
condition:
  class: author-list
  pattern: ".*[,，、].*"
```

#### 6. check（必需）
要执行的检查。

**格式：**
```yaml
check:
  pattern: "regex"     # 内容必须匹配的正则表达式
```

**示例：**
```yaml
# 检查：必须以数字开头
check:
  pattern: "^\\d+\\."

# 检查：必须包含星号
check:
  pattern: "\\d+\\*"
```

#### 7. severity（必需）
问题的严重程度。

**可选值：**
- `error`：错误（必须修复）
- `warning`：警告（建议修复）
- `info`：提示（可选修复）

**示例：**
```yaml
severity: error
severity: warning
```

#### 8. message（必需）
检查失败时显示的错误消息。

**示例：**
```yaml
message: "多个作者时，作者单位必须以数字编号开头（如：1. 单位名称）"
message: "通讯作者的编号后必须有星号（如：王嘉平1*），星号表示该作者为通讯作者"
```

## 规则类型

### 1. 简单规则

直接检查某个 class 的内容。

**示例：**
```yaml
- id: r-003
  name: 通信作者标记规则
  applies_to: corresponding-author
  check:
    pattern: "^\\*"
  severity: error
  message: "通信作者信息必须以星号开头"
```

### 2. 条件规则

只有当条件满足时才执行检查。

**示例：**
```yaml
- id: r-001
  name: 作者单位编号规则
  applies_to: author-affiliation
  condition:
    # 条件：有多个作者
    class: author-list
    pattern: ".*[,，、].*"
  check:
    # 检查：单位必须有编号
    pattern: "^\\d+\\."
  severity: error
  message: "多个作者时，作者单位必须以数字编号开头"
```

**逻辑：**
1. 检查 `author-list` 是否包含逗号或顿号（多个作者）
2. 如果是，则检查 `author-affiliation` 是否以数字开头
3. 如果不是，则跳过检查

## 学术论文作者标注规范

### 星号的含义

在学术论文中，**星号 `*` 用于标记通讯作者（Corresponding Author）**，而不是第一作者。

**标准规范：**
- **第一作者（First Author）**：排在作者列表最前面，无需特殊标记
- **通讯作者（Corresponding Author）**：用星号 `*` 标记，负责与期刊和读者联络

**示例：**
```
王嘉平1*，汪浩2
```
- `王嘉平` 是第一作者（排在最前面）
- `1*` 表示王嘉平同时也是通讯作者（有星号）
- `汪浩` 是第二作者
- `2` 表示汪浩的单位编号

**注意：**
- 第一作者可能是通讯作者（如上例）
- 通讯作者也可能不是第一作者（如最后一位导师）
- 星号永远表示通讯作者，不表示第一作者

### 数据论文模板规范

根据数据论文模板：
1. 作者列表：`第一作者1*，第二作者2`
2. 通讯作者信息：`* 论文通信作者：作者名（author@mail.cn）`

## 完整示例

```yaml
document:
  rules:
    # 作者单位编号规则
    - id: r-001
      name: 作者单位编号规则
      description: 多个作者时，作者单位必须以数字编号开头
      applies_to: author-affiliation
      condition:
        class: author-list
        pattern: ".*[,，、].*"
      check:
        pattern: "^\\d+\\."
      severity: error
      message: "多个作者时，作者单位必须以数字编号开头（如：1. 单位名称）"
    
    # 通讯作者标记规则（作者列表中）
    - id: r-002
      name: 通讯作者标记规则（作者列表中）
      description: 通讯作者的编号后必须有星号（星号表示通讯作者，不是第一作者）
      applies_to: author-list
      check:
        pattern: "\\d+\\*"
      severity: error
      message: "通讯作者的编号后必须有星号（如：王嘉平1*），星号表示该作者为通讯作者"
    
    # 通信作者标记规则
    - id: r-003
      name: 通信作者标记规则
      applies_to: corresponding-author
      check:
        pattern: "^\\*"
      severity: error
      message: "通信作者信息必须以星号开头"
```

## 实现状态

### 当前状态
🚧 **规则检查系统正在设计中**

已完成：
- ✅ 规则配置格式设计
- ✅ 示例规则定义
- ✅ 文档说明

待实现：
- ⏳ RuleChecker 类
- ⏳ 条件评估逻辑
- ⏳ 规则执行引擎
- ⏳ 与 Engine 集成

### 未来功能

1. **更多条件类型**
   - `exists`: 检查某个 class 是否存在
   - `count`: 检查某个 class 的数量
   - `and`/`or`: 复合条件

2. **更多检查类型**
   - `length`: 检查文本长度
   - `format`: 检查特定格式
   - `reference`: 检查引用关系

3. **自定义规则函数**
   - 支持 Python 函数
   - 复杂逻辑检查

## 与其他系统的关系

```
文档 → Walker → Blocks
                  ↓
              Classifier → 添加 class 标签
                  ↓
              StyleChecker → 检查格式样式
                  ↓
              RuleChecker → 检查内容规则（新增）
                  ↓
              Reporter → 生成报告
```

## 设计原则

1. **关注点分离**
   - Classifiers：识别"是什么"
   - Styles：检查"怎么显示"
   - Rules：检查"内容对不对"

2. **声明式配置**
   - 规则用 YAML 配置，不写代码
   - 易于维护和扩展

3. **灵活的条件**
   - 支持简单规则和条件规则
   - 可以引用其他 class 的状态

4. **清晰的错误消息**
   - 每条规则都有明确的错误提示
   - 帮助用户快速定位问题

## 相关文档

- [ARCHITECTURE.md](ARCHITECTURE.md) - 系统架构
- [POSITION_SYNTAX.md](POSITION_SYNTAX.md) - Position 语法
- [CONFIG_FORMAT.md](CONFIG_FORMAT.md) - 配置格式
