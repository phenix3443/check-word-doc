# 系统限制和未来改进

## 当前限制

### 1. Run 级别样式检查不支持

**限制说明：**

当前系统只能检查**段落级别**的样式（字体、对齐、行距等），无法检查段落内部不同文本片段（run）的样式差异。

**影响的场景：**

#### 作者列表上标

数据论文中，作者名后的数字和星号应为上标格式：

```
王嘉平1*，汪浩2
```

其中：
- `1`、`*`、`2` 应该是上标（`superscript: True`）
- 第一作者的数字后必须有星号

**当前行为：**
- ✅ 可以检查：段落的字体、对齐方式
- ❌ 无法检查：上标数字和星号的格式

#### 摘要和关键词标签

段落开头的"摘要："、"关键词："应为黑体加粗：

```
摘要：本数据集包含...
```

其中：
- `摘要：` 应该是黑体加粗
- 后面的内容是正常字体

**当前行为：**
- ✅ 可以检查：段落的行距、对齐方式
- ❌ 无法检查："摘要："三字的加粗格式

### 2. 表格内容样式检查

**限制说明：**

当前系统可以识别表格（`TableBlock`），但没有实现表格内容的样式检查。

**影响的场景：**
- 表格标题格式
- 表格单元格字体和对齐
- 表格边框样式

### 3. 图片和图注检查

**限制说明：**

当前系统不检查图片和图注的格式。

**影响的场景：**
- 图片分辨率
- 图注位置和格式
- 图片编号

## 未来改进方向

### 优先级 1：Run 级别样式检查

**目标：**
支持检查段落内部不同文本片段的样式。

**设计方案：**

#### 方案 A：扩展 StyleChecker

```yaml
# 配置示例
.author-list:
  paragraph:
    alignment: 居中
  
  # 新增：run 级别样式规则
  runs:
    - pattern: "\\d+\\*?"  # 匹配数字和可选的星号
      style:
        superscript: true
    
    - pattern: "^.+(?=\\d)"  # 作者名（数字前的内容）
      style:
        superscript: false
```

**实现要点：**
1. 扩展 `Block` 模型，包含 runs 信息
2. 扩展 `StyleChecker`，支持 run 级别检查
3. 使用正则表达式匹配特定文本片段
4. 检查匹配片段的样式（上标、加粗、斜体等）

**优势：**
- ✅ 可以精确检查上标格式
- ✅ 可以检查"摘要："等标签的加粗
- ✅ 灵活的模式匹配

**挑战：**
- 需要较大的代码改动
- 配置复杂度增加
- 性能影响（需要遍历所有 runs）

#### 方案 B：专门的 Run 检查器

创建独立的 `RunStyleChecker`，专门处理 run 级别的检查。

```python
class RunStyleChecker:
    """Run 级别样式检查器"""
    
    def check_superscript(self, paragraph, pattern, expected=True):
        """检查匹配 pattern 的文本是否为上标"""
        for run in paragraph.runs:
            if re.match(pattern, run.text):
                if run.font.superscript != expected:
                    return Issue(...)
```

**优势：**
- ✅ 关注点分离
- ✅ 不影响现有代码
- ✅ 可以逐步添加功能

### 优先级 2：表格样式检查

**目标：**
支持检查表格内容的格式。

**设计方案：**

```yaml
.data-table:
  table:
    # 表格整体样式
    border_style: single
    alignment: 居中
  
  # 表头样式
  header:
    font:
      bold: true
      size: 小四
    cell:
      background: lightgray
  
  # 单元格样式
  cell:
    font:
      size: 五号
    alignment: 左对齐
```

### 优先级 3：图片和图注检查

**目标：**
检查图片分辨率和图注格式。

**设计方案：**

```yaml
.figure:
  image:
    min_width: 800px
    min_height: 600px
    format: [png, jpg]
  
  caption:
    pattern: "^图\\d+[：:]"
    font:
      size: 五号
    alignment: 居中
```

## 临时解决方案

在实现完整的 run 级别检查之前，可以采用以下方法：

### 1. 手动检查清单

创建一个检查清单，列出需要手动检查的项目：

```markdown
## 手动检查项

- [ ] 作者列表：数字和星号是否为上标
- [ ] 第一作者：数字后是否有星号
- [ ] 摘要标签："摘要："是否为黑体加粗
- [ ] 关键词标签："关键词："是否为黑体加粗
```

### 2. 警告信息

在检查报告中添加警告信息，提醒用户手动检查：

```
⚠️  注意：以下项目需要手动检查：
   - 作者列表中的上标数字和星号
   - "摘要："和"关键词："的加粗格式
```

### 3. 部分自动化

可以检查文本内容是否符合预期格式（如是否包含数字和星号），但不检查样式：

```python
# 检查作者列表是否包含上标标记
if not re.search(r'\d+\*', author_text):
    issues.append(Issue(
        severity="warning",
        message="作者列表可能缺少上标标记（数字和星号）"
    ))
```

## 贡献指南

如果您想帮助实现这些改进，请参考：
1. [ARCHITECTURE.md](ARCHITECTURE.md) - 系统架构说明
2. [CONTRIBUTING.md](CONTRIBUTING.md) - 贡献指南
3. GitHub Issues - 查看相关的功能请求

## 相关讨论

- Issue #XX: Run 级别样式检查
- Issue #XX: 表格样式检查
- Issue #XX: 图片和图注检查
