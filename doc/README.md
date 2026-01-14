# docx-lint 文档目录

## 📌 重要概念

### [CONCEPTS.md](CONCEPTS.md) ⭐ 必读
**核心概念说明**

- 通用规则 vs 通用规则类（容易混淆！）
- 三层架构说明
- 配置文件分类和作用
- 概念对比表

---

## 核心设计文档

### 1. [plan.md](plan.md)
**docx-lint vNext 架构设计**

- Walker 设计原理
- Rule 插件化
- Issue 统一输出
- Context 和 Block 模型
- 迁移策略

### 2. [GENERIC_RULES_DESIGN.md](GENERIC_RULES_DESIGN.md)
**通用规则类设计指南**

- 设计目标和核心原则
- 14 个推荐通用规则类详细说明
  - FontStyleRule（字体样式检查）
  - ParagraphFormatRule（段落格式检查）
  - SequenceRule（序列/编号检查）
  - MatchingRule（文本匹配检查）
  - CountingRule（数量统计检查）
  - RelationRule（关系检查）
  - OrderingRule（顺序检查）
  - ConsistencyRule（一致性检查）
  - CustomPatternRule（自定义模式）
  - ... 更多
- 配置文件结构规范
- 扩展指南和最佳实践

### 3. [TEMPLATE_ADAPTATION_EXAMPLE.md](TEMPLATE_ADAPTATION_EXAMPLE.md)
**模板适配实践示例**

- 用同一套规则类适配 3 种不同文档
  - 数据论文
  - 学位论文
  - 技术报告
- 配置继承和复用策略
- 效果对比分析

## 使用指南

### 4. [GENERIC_RULES_USAGE.md](GENERIC_RULES_USAGE.md)
**通用规则类使用指南**

- 已实现的 6 个通用规则类详细用法
  - FontStyleRule
  - ParagraphFormatRule
  - SequenceRule
  - MatchingRule
  - CountingRule
  - RelationRule
- 参数说明和配置示例
- 字号转换表（pt → EMU）
- 常见问题解答

### 5. [RULES_README.md](RULES_README.md)
**规则系统文档**

- 规则系统架构
- 现有规则类列表
- 添加新规则指南
- 规则类开发规范

### 6. [DATA_PAPER_TEMPLATE_README.md](DATA_PAPER_TEMPLATE_README.md)
**数据论文模板规则配置说明**

- 基于"数据论文模板（刘尚亮修正版）"
- 模板特征和格式要求
- 35 条检查规则详细说明
- 使用方法和常见问题

## 文档导航

### 按用途导航

**我想了解架构设计**
- 阅读 [plan.md](plan.md) - vNext 架构设计
- 阅读 [GENERIC_RULES_DESIGN.md](GENERIC_RULES_DESIGN.md) - 通用规则类设计

**我想适配新的文档类型**
- 阅读 [TEMPLATE_ADAPTATION_EXAMPLE.md](TEMPLATE_ADAPTATION_EXAMPLE.md) - 适配示例
- 阅读 [GENERIC_RULES_USAGE.md](GENERIC_RULES_USAGE.md) - 规则使用方法
- 参考 `config/data_paper_template.yaml` - 实际配置示例

**我想添加新的规则类**
- 阅读 [RULES_README.md](RULES_README.md) - 规则系统文档
- 阅读 [GENERIC_RULES_DESIGN.md](GENERIC_RULES_DESIGN.md) - 扩展指南

**我想检查数据论文**
- 阅读 [DATA_PAPER_TEMPLATE_README.md](DATA_PAPER_TEMPLATE_README.md) - 数据论文模板说明
- 使用 `config/data_paper_template.yaml` 配置文件

### 按角色导航

**架构师/开发者**
1. [plan.md](plan.md) - 理解整体架构
2. [GENERIC_RULES_DESIGN.md](GENERIC_RULES_DESIGN.md) - 规则类设计
3. [RULES_README.md](RULES_README.md) - 开发规范

**配置维护者/用户**
1. [GENERIC_RULES_USAGE.md](GENERIC_RULES_USAGE.md) - 使用方法
2. [TEMPLATE_ADAPTATION_EXAMPLE.md](TEMPLATE_ADAPTATION_EXAMPLE.md) - 适配示例
3. [DATA_PAPER_TEMPLATE_README.md](DATA_PAPER_TEMPLATE_README.md) - 模板说明

## 快速链接

### 配置文件
- `../config/base.yaml` - 基础配置
- `../config/data_paper_template.yaml` - 数据论文模板（35条规则）
- `../config/example_with_generic_rules.yaml` - 通用规则类示例

### 代码文件
- `../script/core/` - 核心引擎
- `../script/rules/format_rules.py` - 通用规则类实现
- `../script/rules/registry.py` - 规则注册表

### 项目文档
- `../README.md` - 项目说明
- `../ARCHITECTURE.md` - 架构详细说明
- `../QUICK_START.md` - 快速开始指南

## 更新日志

### 2026-01-14

- ✅ 创建通用规则类设计文档
- ✅ 实现 6 个核心通用规则类
- ✅ 完善模板适配示例
- ✅ 整合所有文档到 doc/ 目录

### 2026-01-13

- ✅ vNext 架构设计
- ✅ Walker 和 Engine 实现
- ✅ 规则系统基础架构

---

**文档总数**: 6 个主要文档  
**覆盖范围**: 设计、开发、使用、示例  
**最后更新**: 2026-01-14
