# Position 语法统一更新日志

## 更新日期
2026-01-16

## 更新内容

### 1. 语法统一

将所有定位语法统一为 `position` 格式，增强一致性和可读性。

#### 修改前（旧语法）

```yaml
# 旧的 after 语法
after:
  class: keywords-en

# 旧的 before 语法  
before:
  class: references
```

#### 修改后（新语法）

```yaml
# 统一的 position 语法
position:
  type: after
  class: keywords-en

position:
  type: before
  class: references
```

### 2. 支持的 Position 类型

现在 `position` 支持四种类型：

| 类型 | 说明 | 必需字段 | 示例 |
|------|------|----------|------|
| `absolute` | 绝对定位 | `index` | `{type: absolute, index: 0}` |
| `relative` | 相对定位/区间定位 | `index` | `{type: relative, index: (a, b)}` |
| `after` | 紧跟定位 | `class` | `{type: after, class: keywords}` |
| `before` | 之前定位 | `class` | `{type: before, class: references}` |

### 3. 配置文件更新

#### config/template/data_paper/classifiers.yaml

共更新 **11处** `after` 语法：

1. `title-en` - 紧跟在 keywords 之后
2. `heading-introduction` - 紧跟在 keywords-en 之后
3. `heading-data-collection` - 紧跟在 heading-introduction 之后
4. `heading-data-description` - 紧跟在 heading-data-collection 之后
5. `heading-quality-control` - 紧跟在 heading-data-description 之后
6. `heading-data-value` - 紧跟在 heading-quality-control 之后
7. `heading-usage-method` - 紧跟在 heading-data-value 之后
8. `heading-availability` - 紧跟在 heading-usage-method 之后
9. `heading-acknowledgments` - 紧跟在 heading-availability 之后
10. `heading-author-contributions` - 紧跟在 heading-acknowledgments 之后
11. `heading-references` - 紧跟在 heading-author-contributions 之后

### 4. 代码更新

#### script/core/classifier.py

- 新增对 `position: {type: after/before, class: xxx}` 的支持
- 更新依赖提取逻辑，识别新语法中的 class 引用
- 保持向后兼容，旧的 `after/before` 语法仍然支持

#### script/config_loader.py

- 更新配置验证逻辑
- 验证 `type: after/before` 时必须有 `class` 字段
- 验证 `type: absolute/relative` 时必须有 `index` 字段
- 支持的 `type` 值：`absolute`, `relative`, `after`, `before`

### 5. 文档更新

#### doc/POSITION_SYNTAX.md

- 新增 "3. 紧跟定位 (After)" 章节
- 新增 "4. 之前定位 (Before)" 章节
- 新增 "定位类型选择指南" 表格
- 新增 "语法演进" 章节，说明旧语法和新语法的对比
- 更新所有示例代码，使用数字索引（0, -1）而非字符串

#### README.md

- 更新 "支持的定位方式" 章节
- 新增 "4. 紧跟定位 (After)" 说明
- 新增 "5. 之前定位 (Before)" 说明
- 更新模式匹配示例，使用完全匹配格式（`$` 结尾）

### 6. 统计数据

#### 配置统计

```
position: {type: absolute}: 1 个
position: {type: relative}: 2 个  
position: {type: after}: 11 个
旧 after 语法: 0 个
```

#### 总规则数

- **Classifiers**: 23 条规则
  - 通用规则: 5 条
  - 数据论文特定规则: 18 条
- **Styles**: 29 个样式定义

### 7. 优势

1. **语法统一** - 所有定位都使用 `position` 字段
2. **类型明确** - 通过 `type` 字段清楚表达定位方式
3. **易于理解** - 配置结构一致，降低学习成本
4. **易于扩展** - 未来可以轻松添加新的定位类型
5. **向后兼容** - 旧语法仍然支持，平滑迁移

### 8. 迁移指南

如果你的配置使用了旧的 `after/before` 语法，建议迁移到新语法：

```yaml
# 旧语法 → 新语法
after:
  class: xxx
  offset: 0

# 改为
position:
  type: after
  class: xxx
  # offset: 0 是默认值，可以省略
```

### 9. 相关提交

- `3787d44` - refactor: 统一定位语法为 position 格式
- `c805015` - fix: 修正参考文献标题 pattern 为完全匹配
- `468daa6` - fix: 删除重复的 .abstract-en 样式配置
- `9ea60c2` - refactor: 提取通用配置并完善数据论文格式规则

## 测试验证

所有更新已通过以下测试：

```bash
✅ 配置加载成功
✅ Classifier 初始化成功（23 条规则）
✅ 所有定位语法已统一为 position 格式
✅ 无循环依赖
✅ 依赖链完整
```

## 下一步计划

1. ✅ 语法统一完成
2. ✅ 文档更新完成
3. ⏳ 实际文档测试
4. ⏳ 性能优化
5. ⏳ 错误信息优化
