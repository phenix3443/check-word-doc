# 文档索引

本目录包含 `check-word-doc` 项目的所有文档。

## 📚 文档列表

### 核心文档

1. **[CONFIGURATION_GUIDE.md](./CONFIGURATION_GUIDE.md)** ⭐ **推荐首读**
   - **内容**: 配置文件编写完整指南
   - **包含**: 
     - `classifiers.yaml` 所有字段说明和取值
     - `styles.yaml` 所有字段说明和取值
     - `rules.yaml` 所有字段说明和取值
     - 完整示例和最佳实践
   - **适合**: 编写配置文件的用户
   - **大小**: 33KB, 1459行

2. **[CONFIGURATION_SUMMARY.md](./CONFIGURATION_SUMMARY.md)** ⭐ **快速参考**
   - **内容**: 配置文件字段快速参考
   - **包含**: 所有字段的简洁列表和取值
   - **适合**: 快速查询字段取值
   - **大小**: 4.9KB

### 架构文档

3. **[ARCHITECTURE.md](./ARCHITECTURE.md)**
   - **内容**: 系统架构设计
   - **包含**: 
     - 整体架构
     - 核心组件说明
     - 工作流程
   - **适合**: 了解系统设计的开发者
   - **大小**: 14KB

### 功能文档

4. **[SELECTOR.md](./SELECTOR.md)**
   - **内容**: Selector 选择器语法
   - **包含**: 
     - CSS 风格选择器语法
     - 选择器类型和用法
   - **适合**: 编写 `rules.yaml` 的用户
   - **大小**: 7.2KB

5. **[SELECTOR_EXAMPLES.md](./SELECTOR_EXAMPLES.md)**
   - **内容**: Selector 使用示例
   - **包含**: 各种选择器的实际应用示例
   - **适合**: 学习选择器用法
   - **大小**: 12KB

6. **[POSITION_SYNTAX.md](./POSITION_SYNTAX.md)**
   - **内容**: Position 定位语法详解
   - **包含**: 
     - 绝对定位、相对定位
     - 区间定位、相邻定位
   - **适合**: 编写 `classifiers.yaml` 的用户
   - **大小**: 9.8KB

### 专题文档

7. **[RULES_WITH_SELECTOR.md](./RULES_WITH_SELECTOR.md)**
   - **内容**: 规则配置与选择器集成
   - **包含**: 如何在规则中使用选择器
   - **适合**: 编写复杂规则的用户
   - **大小**: 11KB

8. **[AUTHOR_LIST_CONFIG.md](./AUTHOR_LIST_CONFIG.md)**
   - **内容**: 作者列表配置专题
   - **包含**: 作者信息的分类和样式配置
   - **适合**: 处理作者信息的用户
   - **大小**: 6.6KB

9. **[CONFIG_ALIGNMENT.md](./CONFIG_ALIGNMENT.md)**
   - **内容**: 配置文件对齐和组织
   - **包含**: 配置文件的组织结构建议
   - **适合**: 维护大型配置的用户
   - **大小**: 6.3KB

## 🚀 快速开始

### 新手入门路径

1. **第一步**: 阅读 [CONFIGURATION_SUMMARY.md](./CONFIGURATION_SUMMARY.md)
   - 快速了解所有字段和取值

2. **第二步**: 阅读 [CONFIGURATION_GUIDE.md](./CONFIGURATION_GUIDE.md)
   - 深入学习配置文件编写

3. **第三步**: 查看实际配置文件
   - `config/template/data_paper/classifiers.yaml`
   - `config/template/data_paper/styles.yaml`
   - `config/template/data_paper/rules.yaml`

### 进阶学习路径

1. **了解架构**: [ARCHITECTURE.md](./ARCHITECTURE.md)
2. **学习定位**: [POSITION_SYNTAX.md](./POSITION_SYNTAX.md)
3. **掌握选择器**: [SELECTOR.md](./SELECTOR.md) + [SELECTOR_EXAMPLES.md](./SELECTOR_EXAMPLES.md)
4. **编写规则**: [RULES_WITH_SELECTOR.md](./RULES_WITH_SELECTOR.md)

## 📖 按主题查找

### 编写 classifiers.yaml
- [CONFIGURATION_GUIDE.md - 第1章](./CONFIGURATION_GUIDE.md#1-classifiersyaml---分类器配置)
- [POSITION_SYNTAX.md](./POSITION_SYNTAX.md)
- [AUTHOR_LIST_CONFIG.md](./AUTHOR_LIST_CONFIG.md)

### 编写 styles.yaml
- [CONFIGURATION_GUIDE.md - 第2章](./CONFIGURATION_GUIDE.md#2-stylesyaml---样式配置)
- [CONFIGURATION_SUMMARY.md - 第2节](./CONFIGURATION_SUMMARY.md#2-stylesyaml)

### 编写 rules.yaml
- [CONFIGURATION_GUIDE.md - 第3章](./CONFIGURATION_GUIDE.md#3-rulesyaml---规则配置)
- [SELECTOR.md](./SELECTOR.md)
- [SELECTOR_EXAMPLES.md](./SELECTOR_EXAMPLES.md)
- [RULES_WITH_SELECTOR.md](./RULES_WITH_SELECTOR.md)

### 字段取值查询
- [CONFIGURATION_SUMMARY.md](./CONFIGURATION_SUMMARY.md) - 所有字段快速参考
- [CONFIGURATION_GUIDE.md](./CONFIGURATION_GUIDE.md) - 详细说明

### 示例和模式
- [CONFIGURATION_GUIDE.md - 第5章](./CONFIGURATION_GUIDE.md#5-常见模式和最佳实践)
- [SELECTOR_EXAMPLES.md](./SELECTOR_EXAMPLES.md)

## 🔍 常见问题

### Q1: 如何定位文档中的元素？
**A**: 参阅 [POSITION_SYNTAX.md](./POSITION_SYNTAX.md)，了解 5 种定位方式：
- `absolute` - 绝对定位
- `relative` - 相对定位
- `between` - 区间定位
- `next` - 下一个兄弟
- `prev` - 上一个兄弟

### Q2: 如何选择已分类的元素？
**A**: 参阅 [SELECTOR.md](./SELECTOR.md)，了解选择器语法：
- `.class` - 类选择器
- `:first`, `:last`, `:nth(n)` - 伪类选择器
- `.class1 + .class2` - 相邻兄弟选择器

### Q3: 字号如何配置？
**A**: 参阅 [CONFIGURATION_GUIDE.md - 字号对照表](./CONFIGURATION_GUIDE.md#71-字号对照表)
- 中文字号: `五号`, `小四`, `三号` 等
- 磅值: `10.5磅`, `12磅`, `16磅` 等

### Q4: 如何检查内容格式？
**A**: 参阅 [CONFIGURATION_GUIDE.md - 规则配置](./CONFIGURATION_GUIDE.md#3-rulesyaml---规则配置)
- 使用 `check.pattern` 进行正则表达式匹配
- 使用 `check.length` 进行长度检查
- 使用 `check.count` 进行数量检查

### Q5: 如何验证表格内容？
**A**: 参阅 [CONFIGURATION_GUIDE.md - check 字段类型](./CONFIGURATION_GUIDE.md#326-check---检查类型)
- 使用 `check.cross_validate` 进行交叉验证
- 使用 `check.table_cell_pattern` 进行单元格检查

## 📝 文档更新记录

- **2026-01-16**: 创建 `CONFIGURATION_GUIDE.md` 和 `CONFIGURATION_SUMMARY.md`
- **2026-01-17**: 创建文档索引 `README.md`

## 🤝 贡献

如果您发现文档中有错误或需要补充的内容，欢迎提交 Issue 或 Pull Request。

## 📄 许可

本文档与项目代码使用相同的许可证。
