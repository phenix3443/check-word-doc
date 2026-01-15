# 代码清理记录

## 清理时间

2026-01-15

## 清理原因

项目经过多次重构，从最初的 rule-based 架构演进到现在的 class-based 架构（Classifier + StyleChecker）。旧的代码和文档已不再使用，需要清理以保持代码库的整洁。

## 删除的文件

### 1. 旧的规则系统（Rule-based）

**目录：**
- `script/rules/` - 整个目录
  - `format_rules.py` - 字体和格式规则
  - `paragraph_rules.py` - 段落规则
  - `reference_rules.py` - 参考文献规则
  - `registry.py` - 规则注册表
  - `structure_rules.py` - 结构规则
  - `table.py` - 表格规则
  - `smoke.py` - 冒烟测试规则

**说明：** 这些是旧的 rule-based 系统的规则类，现在已被 Classifier + StyleChecker 架构取代。

### 2. 旧的设置系统

**目录：**
- `script/settings/` - 整个目录
  - `font_settings.py`
  - `language_settings.py`
  - `paragraph_settings.py`
  - `table_settings.py`

**说明：** 这些设置类是为旧的 rule-based 系统设计的，现在样式定义直接在 YAML 配置文件中。

### 3. 旧的核心组件

**文件：**
- `script/core/rule_generator.py` - 旧的规则生成器
- `script/core/rule.py` - Rule 和 FinalizeRule 协议定义
- `script/core/context.py` - Context 类（用于 rule-based 系统）
- `script/utils.py` - 旧的工具函数

**说明：** 这些组件是为旧的 rule-based 系统设计的，现在不再需要。

### 4. 旧的文档

**文件：**
- `ARCHITECTURE.md` - 根目录的旧架构文档（已移到 doc/ 目录）
- `QUICK_START.md` - 旧的快速开始文档
- `script_generated_analysis.md` - 自动生成的分析文档
- `doc/CONFIG_FORMAT.md` - 旧的配置格式文档
- `doc/IMPLEMENTATION_PLAN.md` - 旧的实现计划

**说明：** 这些文档描述的是旧的系统架构，已不再适用。

### 5. 旧的测试和配置

**文件：**
- `test/test_declarative_config.py` - 旧的声明式配置测试
- `config/test_class_based.yaml` - 旧的测试配置

**说明：** 这些是为旧系统编写的测试文件。

## 保留的核心文件

### 核心引擎
- `script/core/classifier.py` - 语义分类器
- `script/core/style_checker.py` - 样式检查器
- `script/core/walker.py` - 文档遍历器
- `script/core/model.py` - 数据模型
- `script/core/engine.py` - 主引擎

### 工具和接口
- `script/cli.py` - CLI 入口
- `script/config_loader.py` - 配置加载器
- `script/utils/unit_converter.py` - 单位转换器
- `script/reporters/` - 报告生成器

### 配置文件
- `config/template/data_paper/` - 数据论文模板配置
  - `config.yaml` - 主配置
  - `classifiers.yaml` - 元素识别规则
  - `styles.yaml` - 样式定义
  - `rules.yaml` - 内容规则

### 文档
- `doc/ARCHITECTURE.md` - 架构设计
- `doc/POSITION_SYNTAX.md` - 定位语法
- `doc/RULES.md` - 规则系统设计
- `doc/LIMITATIONS.md` - 系统限制

## 代码修改

### 1. `script/cli.py`

**修改前：**
```python
from script.rules.registry import build_rules

rules = build_rules(config)
issues = DocxLint(rules=rules, config=config).run(str(docx_path))
```

**修改后：**
```python
issues = DocxLint(config=config).run(str(docx_path))
```

**说明：** 移除了对旧的 `build_rules` 的调用。

### 2. `script/core/engine.py`

**修改前：**
- 支持两种模式：class-based 和 rule-based
- 包含 `_run_rule_based` 方法

**修改后：**
- 只支持 class-based 模式
- 移除了 `_run_rule_based` 方法
- 简化了 `__init__` 方法（不再需要 `rules` 参数）

**说明：** 完全移除了对旧 rule-based 系统的支持。

## 新架构优势

### 1. 更清晰的职责分离
- **Classifier**：负责识别元素（"这是什么"）
- **StyleChecker**：负责检查样式（"样式对不对"）

### 2. 更灵活的配置
- 类似 HTML/CSS 的设计理念
- 元素识别和样式定义分离
- 支持复杂的定位规则

### 3. 更好的可维护性
- 配置驱动，无需修改代码
- 递归依赖解析，自动处理依赖关系
- 循环依赖检测，防止配置错误

### 4. 更简洁的代码
- 移除了大量旧的规则类
- 核心代码更加聚焦
- 更容易理解和扩展

## 影响

- ✅ 代码库更加整洁
- ✅ 核心架构更加清晰
- ✅ 维护成本降低
- ✅ 新功能更容易添加
- ⚠️ 旧的配置文件不再兼容（需要迁移到新格式）

## 迁移指南

如果有旧的配置文件，需要迁移到新的 class-based 格式：

### 旧格式（rule-based）
```yaml
document:
  structure:
    - type: paragraph
      name: 标题
      font:
        size: 三号
```

### 新格式（class-based）
```yaml
document:
  classifiers:
    - class: title
      match:
        type: paragraph
        position:
          type: absolute
          index: 0
  
  styles:
    .title:
      font:
        size: 三号
```

详见 [doc/ARCHITECTURE.md](doc/ARCHITECTURE.md) 和 [doc/POSITION_SYNTAX.md](doc/POSITION_SYNTAX.md)。
