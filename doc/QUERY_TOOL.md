# 文档查询工具使用指南

`query.py` 是一个命令行工具，用于使用 CSS 风格的选择器查询 Word 文档中的特定元素。

## 功能特点

- 🔍 使用 CSS 风格的选择器语法
- 📊 支持多种查询模式（列表、单个、统计）
- 🎯 精确定位文档元素
- 📝 清晰的输出格式

## 安装

确保已安装项目依赖：

```bash
poetry install
```

## 基本用法

```bash
poetry run python3 script/query.py <文档路径> --config <配置文件> --selector <选择器>
```

### 必需参数

- `<文档路径>`: Word 文档的路径（.docx 文件）
- `--config, -c`: 配置文件路径（如 `config/template/data_paper/config.yaml`）
- `--selector, -s`: CSS 风格的选择器字符串

### 可选参数

- `--count`: 只显示匹配元素的数量
- `--first`: 只显示第一个匹配的元素
- `--no-classes`: 不显示元素的类名
- `--no-index`: 不显示元素的索引
- `--full`: 显示完整内容（不截断）

## 选择器语法

### 1. 类选择器 (Class Selector)

使用 `.classname` 选择具有指定类的元素。

```bash
# 查询所有标题
poetry run python3 script/query.py doc.docx -c config.yaml -s ".heading"

# 查询所有参考文献
poetry run python3 script/query.py doc.docx -c config.yaml -s ".reference-item"

# 查询作者列表
poetry run python3 script/query.py doc.docx -c config.yaml -s ".author-list"
```

### 2. 伪类选择器 (Pseudo-class Selector)

#### `:first` - 第一个元素

```bash
# 查询第一个作者
poetry run python3 script/query.py doc.docx -c config.yaml -s ".author-list:first"

# 查询第一个标题
poetry run python3 script/query.py doc.docx -c config.yaml -s ".heading:first"
```

#### `:last` - 最后一个元素

```bash
# 查询最后一个参考文献
poetry run python3 script/query.py doc.docx -c config.yaml -s ".reference-item:last"
```

#### `:nth(n)` - 第 n 个元素（索引从 0 开始）

```bash
# 查询第一个作者（索引 0）
poetry run python3 script/query.py doc.docx -c config.yaml -s ".author-list:nth(0)"

# 查询第二个作者（索引 1）
poetry run python3 script/query.py doc.docx -c config.yaml -s ".author-list:nth(1)"

# 查询第三个参考文献（索引 2）
poetry run python3 script/query.py doc.docx -c config.yaml -s ".reference-item:nth(2)"
```

### 3. 属性选择器 (Attribute Selector)

使用 `[attribute="value"]` 选择具有指定属性的元素。

```bash
# 查询所有表格
poetry run python3 script/query.py doc.docx -c config.yaml -s "[type='table']"

# 查询所有段落
poetry run python3 script/query.py doc.docx -c config.yaml -s "[type='paragraph']"
```

### 4. 相邻兄弟选择器 (Adjacent Sibling Selector)

使用 `+` 选择紧邻的下一个兄弟元素。

```bash
# 查询标题后面的第一个段落
poetry run python3 script/query.py doc.docx -c config.yaml -s ".heading + .body"
```

## 实用示例

### 示例 1: 查找第二个作者

```bash
poetry run python3 script/query.py test/query_test.docx \
  --config config/template/data_paper/config.yaml \
  --selector ".author-list:nth(1)"
```

输出：
```
📋 加载配置: config/template/data_paper/config.yaml
📄 分析文档: test/query_test.docx
✅ 文档共有 19 个元素

🔍 查询选择器: .author-list:nth(1)

✅ 找到 1 个匹配的元素:

[1] (author-section, author-list, author-affiliation, corresponding-author) 1. 北京大学/计算机学院，北京  100871
```

### 示例 2: 统计参考文献数量

```bash
poetry run python3 script/query.py test/query_test.docx \
  --config config/template/data_paper/config.yaml \
  --selector ".reference-item" \
  --count
```

输出：
```
📋 加载配置: config/template/data_paper/config.yaml
📄 分析文档: test/query_test.docx
✅ 文档共有 19 个元素

🔍 查询选择器: .reference-item

✅ 匹配元素数量: 3
```

### 示例 3: 查询所有参考文献

```bash
poetry run python3 script/query.py test/query_test.docx \
  --config config/template/data_paper/config.yaml \
  --selector ".reference-item"
```

输出：
```
📋 加载配置: config/template/data_paper/config.yaml
📄 分析文档: test/query_test.docx
✅ 文档共有 19 个元素

🔍 查询选择器: .reference-item

✅ 找到 3 个匹配的元素:

[1] (reference-item) [1]  张三, 李四. 文档处理技术研究[J]. 计算机学报, 2023, 46(1): 1-10.

[2] (reference-item) [2]  Wang W, Li S. Document Analysis System[C]//Proceedings of ACL, 2023: 100-110.

[3] (reference-item) [3]  Smith J. CSS Selectors Guide[M]. O'Reilly Media, 2022.
```

### 示例 4: 查询文档标题

```bash
poetry run python3 script/query.py test/query_test.docx \
  --config config/template/data_paper/config.yaml \
  --selector ".title" \
  --first
```

输出：
```
📋 加载配置: config/template/data_paper/config.yaml
📄 分析文档: test/query_test.docx
✅ 文档共有 19 个元素

🔍 查询选择器: .title

✅ 找到 1 个匹配的元素:

[1] (title) 数据库（集）基本信息简介
```

### 示例 5: 查询第一个和最后一个参考文献

```bash
# 第一个
poetry run python3 script/query.py test/query_test.docx \
  --config config/template/data_paper/config.yaml \
  --selector ".reference-item:first"

# 最后一个
poetry run python3 script/query.py test/query_test.docx \
  --config config/template/data_paper/config.yaml \
  --selector ".reference-item:last"
```

## 常见查询场景

### 文档结构分析

```bash
# 统计一级标题数量
poetry run python3 script/query.py doc.docx -c config.yaml -s ".heading-a1" --count

# 查看所有一级标题
poetry run python3 script/query.py doc.docx -c config.yaml -s ".heading-a1"

# 查看文档标题
poetry run python3 script/query.py doc.docx -c config.yaml -s ".title" --first
```

### 作者信息提取

```bash
# 查看所有作者信息
poetry run python3 script/query.py doc.docx -c config.yaml -s ".author-list"

# 查看第一作者
poetry run python3 script/query.py doc.docx -c config.yaml -s ".author-list:first"

# 查看通讯作者
poetry run python3 script/query.py doc.docx -c config.yaml -s ".corresponding-author"
```

### 参考文献管理

```bash
# 统计参考文献数量
poetry run python3 script/query.py doc.docx -c config.yaml -s ".reference-item" --count

# 查看所有参考文献
poetry run python3 script/query.py doc.docx -c config.yaml -s ".reference-item"

# 查看第一条参考文献
poetry run python3 script/query.py doc.docx -c config.yaml -s ".reference-item:first"
```

### 摘要和关键词

```bash
# 查看中文摘要
poetry run python3 script/query.py doc.docx -c config.yaml -s ".abstract"

# 查看英文摘要
poetry run python3 script/query.py doc.docx -c config.yaml -s ".abstract-en"

# 查看中文关键词
poetry run python3 script/query.py doc.docx -c config.yaml -s ".keywords"

# 查看英文关键词
poetry run python3 script/query.py doc.docx -c config.yaml -s ".keywords-en"
```

## 输出格式

默认输出格式：

```
[索引] (类名列表) 内容
```

- **索引**: 匹配元素的序号（从 1 开始）
- **类名列表**: 元素的所有类名，用逗号分隔
- **内容**: 元素的文本内容（段落）或描述（表格）

### 自定义输出

```bash
# 不显示类名
poetry run python3 script/query.py doc.docx -c config.yaml -s ".heading" --no-classes

# 不显示索引
poetry run python3 script/query.py doc.docx -c config.yaml -s ".heading" --no-index

# 显示完整内容（不截断）
poetry run python3 script/query.py doc.docx -c config.yaml -s ".abstract" --full
```

## 支持的选择器

| 选择器类型 | 语法 | 示例 | 说明 |
|-----------|------|------|------|
| 类选择器 | `.class` | `.heading` | 选择具有指定类的元素 |
| 伪类 `:first` | `.class:first` | `.author-list:first` | 选择第一个匹配的元素 |
| 伪类 `:last` | `.class:last` | `.reference-item:last` | 选择最后一个匹配的元素 |
| 伪类 `:nth(n)` | `.class:nth(n)` | `.author-list:nth(1)` | 选择第 n 个元素（从 0 开始） |
| 属性选择器 | `[attr="value"]` | `[type="table"]` | 选择具有指定属性的元素 |
| 相邻兄弟 | `.a + .b` | `.heading + .body` | 选择紧邻的下一个兄弟元素 |

## 注意事项

1. **索引从 0 开始**: `:nth(0)` 表示第一个元素，`:nth(1)` 表示第二个元素
2. **类名区分大小写**: `.Author` 和 `.author` 是不同的类
3. **配置文件必需**: 必须提供配置文件才能进行元素分类
4. **文档格式**: 仅支持 `.docx` 格式的 Word 文档

## 故障排除

### 问题 1: 未找到匹配的元素

**原因**: 
- 选择器语法错误
- 配置文件中没有定义该类
- 文档中确实没有该类型的元素

**解决方法**:
1. 检查选择器语法是否正确
2. 查看配置文件中的 `classifiers` 部分
3. 使用更通用的选择器（如 `paragraph`）测试

### 问题 2: 配置加载失败

**原因**: 配置文件路径错误或格式不正确

**解决方法**:
1. 检查配置文件路径是否正确
2. 验证 YAML 格式是否正确
3. 查看错误信息中的具体提示

### 问题 3: 文档分析失败

**原因**: 文档格式不正确或损坏

**解决方法**:
1. 确认文档是 `.docx` 格式
2. 尝试用 Word 打开并重新保存
3. 检查文档是否损坏

## 相关文档

- [配置指南](CONFIGURATION_GUIDE.md) - 详细的配置文件编写指南
- [Selector 语法](SELECTOR_SYNTAX.md) - 完整的选择器语法参考
- [架构文档](ARCHITECTURE.md) - 系统架构说明

## 版本信息

- **版本**: 1.0
- **最后更新**: 2026-01-17
