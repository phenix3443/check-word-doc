# Selector 使用示例

## 快速开始

### 基本流程

```python
from docx import Document
from script.core.classifier import Classifier
from script.core.selector import Selector
from script.config_loader import ConfigLoader

# 1. 加载配置
loader = ConfigLoader('config/template/data_paper/config.yaml')
config = loader.load()

# 2. 打开文档
doc = Document('your_paper.docx')

# 3. 使用 Classifier 标记文档元素
classifier = Classifier(config['document']['classifiers'])
blocks = classifier.classify(doc)  # 返回已标记的 blocks

# 4. 创建 Selector
selector = Selector(blocks)

# 5. 使用选择器查询元素
result = selector.select_one(".author-affiliation:nth(1)")
print(f"第二个作者地址: {result.paragraph.text}")
```

## 常见查询示例

### 1. 查询作者信息

#### 查询第一个作者
```python
# 方法1: 使用 :first 伪类
author = selector.select_one(".author-list:first")
print(f"第一作者: {author.paragraph.text}")

# 方法2: 使用 :nth(0)
author = selector.select_one(".author-list:nth(0)")
```

#### 查询第二个作者的地址
```python
# 第二个作者单位（索引从0开始，所以第二个是 nth(1)）
affiliation = selector.select_one(".author-affiliation:nth(1)")
print(f"第二个作者地址: {affiliation.paragraph.text}")
```

#### 查询通讯作者
```python
corresponding = selector.select_one(".corresponding-author")
print(f"通讯作者: {corresponding.paragraph.text}")
```

#### 查询所有作者相关信息
```python
author_info = selector.select(".author-section")
print(f"作者区域共 {len(author_info)} 个元素:")
for item in author_info:
    print(f"  - {item.paragraph.text}")
```

### 2. 查询摘要和关键词

#### 查询中文摘要
```python
abstract = selector.select_one(".abstract")
print(f"中文摘要: {abstract.paragraph.text}")
```

#### 查询英文摘要
```python
abstract_en = selector.select_one(".abstract-en")
print(f"英文摘要: {abstract_en.paragraph.text}")
```

#### 查询关键词
```python
keywords = selector.select_one(".keywords")
print(f"关键词: {keywords.paragraph.text}")
```

### 3. 查询标题和章节

#### 查询论文标题
```python
title = selector.select_one(".title")
print(f"论文标题: {title.paragraph.text}")
```

#### 查询引言标题
```python
intro_heading = selector.select_one(".heading-introduction")
print(f"引言标题: {intro_heading.paragraph.text}")
```

#### 查询引言内容
```python
# 方法1: 直接查询
intro_body = selector.select(".body-introduction")

# 方法2: 使用相邻兄弟选择器
intro_body = selector.select(".heading-introduction + .body-introduction")

print(f"引言内容共 {len(intro_body)} 段:")
for para in intro_body:
    print(f"  - {para.paragraph.text[:50]}...")
```

#### 查询所有一级标题
```python
# 查询所有以 heading- 开头的类
headings = []
for block in blocks:
    for cls in block.classes:
        if cls.startswith('heading-'):
            headings.append(block)
            break

print(f"一级标题共 {len(headings)} 个:")
for h in headings:
    print(f"  - {h.paragraph.text}")
```

### 4. 查询参考文献

#### 查询参考文献标题
```python
ref_heading = selector.select_one(".heading-references")
print(f"参考文献标题: {ref_heading.paragraph.text}")
```

#### 查询第一条参考文献
```python
first_ref = selector.select_one(".reference-item:first")
print(f"第一条参考文献: {first_ref.paragraph.text}")
```

#### 查询第二条参考文献
```python
second_ref = selector.select_one(".reference-item:nth(1)")
print(f"第二条参考文献: {second_ref.paragraph.text}")
```

#### 查询最后一条参考文献
```python
last_ref = selector.select_one(".reference-item:last")
print(f"最后一条参考文献: {last_ref.paragraph.text}")
```

#### 查询所有参考文献
```python
refs = selector.select(".reference-item")
print(f"参考文献共 {len(refs)} 条:")
for i, ref in enumerate(refs, 1):
    print(f"  [{i}] {ref.paragraph.text}")
```

### 5. 查询表格

#### 查询数据信息表题注
```python
table_caption = selector.select_one(".data-info-table-caption")
print(f"表题注: {table_caption.paragraph.text}")
```

#### 查询数据信息表
```python
# 使用属性选择器查询表格类型
table = selector.select_one("[type='table']")
# 或使用类选择器
table = selector.select_one(".data-info-table")
```

#### 查询所有表格题注
```python
captions = selector.select(".table-caption")
print(f"表格题注共 {len(captions)} 个:")
for caption in captions:
    print(f"  - {caption.paragraph.text}")
```

### 6. 使用相邻兄弟选择器

#### 查询标题后的第一段正文
```python
# 查询引言标题后的第一段
first_para = selector.select_one(".heading-introduction + .body-introduction")

# 查询数据采集标题后的第一段
first_para = selector.select_one(".heading-data-collection + .body-data-collection")
```

#### 查询关键词后的元素
```python
# 查询英文关键词后的表题注
next_elem = selector.select_one(".keywords-en + .data-info-table-caption")
print(f"关键词后的元素: {next_elem.paragraph.text}")
```

### 7. 统计和检查

#### 检查元素是否存在
```python
# 检查是否有英文摘要
has_abstract_en = selector.exists(".abstract-en")
print(f"是否有英文摘要: {has_abstract_en}")

# 检查是否有致谢
has_acknowledgments = selector.exists(".heading-acknowledgments")
print(f"是否有致谢: {has_acknowledgments}")
```

#### 统计元素数量
```python
# 统计参考文献数量
ref_count = selector.count(".reference-item")
print(f"参考文献数量: {ref_count}")

# 统计作者单位数量
affiliation_count = selector.count(".author-affiliation")
print(f"作者单位数量: {affiliation_count}")

# 统计一级标题数量
heading_count = selector.count(".heading-1")
print(f"一级标题数量: {heading_count}")
```

## 高级用法

### 1. 条件过滤

```python
# 查询包含特定关键词的参考文献
refs = selector.select(".reference-item")
refs_2023 = [r for r in refs if "2023" in r.paragraph.text]
print(f"2023年的文献共 {len(refs_2023)} 条")

# 查询包含特定作者的文献
refs_wang = [r for r in refs if "Wang" in r.paragraph.text or "王" in r.paragraph.text]
print(f"王姓作者的文献共 {len(refs_wang)} 条")
```

### 2. 批量处理

```python
# 提取所有章节标题和内容
sections = [
    ("heading-introduction", "body-introduction"),
    ("heading-data-collection", "body-data-collection"),
    ("heading-data-description", "body-data-description"),
]

for heading_class, body_class in sections:
    heading = selector.select_one(f".{heading_class}")
    body = selector.select(f".{body_class}")
    
    if heading:
        print(f"\n{heading.paragraph.text}")
        print(f"内容段落数: {len(body)}")
        for para in body:
            print(f"  - {para.paragraph.text[:50]}...")
```

### 3. 导出结构化数据

```python
import json

# 提取作者信息
authors = selector.select(".author-list")
affiliations = selector.select(".author-affiliation")
corresponding = selector.select_one(".corresponding-author")

author_data = {
    "authors": [a.paragraph.text for a in authors],
    "affiliations": [a.paragraph.text for a in affiliations],
    "corresponding": corresponding.paragraph.text if corresponding else None
}

print(json.dumps(author_data, ensure_ascii=False, indent=2))
```

### 4. 验证文档结构

```python
# 检查必需的元素是否存在
required_elements = [
    (".title", "论文标题"),
    (".author-list", "作者列表"),
    (".abstract", "中文摘要"),
    (".abstract-en", "英文摘要"),
    (".keywords", "关键词"),
    (".keywords-en", "英文关键词"),
    (".heading-references", "参考文献"),
]

print("文档结构检查:")
for selector_str, name in required_elements:
    exists = selector.exists(selector_str)
    status = "✅" if exists else "❌"
    print(f"{status} {name}: {'存在' if exists else '缺失'}")
```

### 5. 生成文档大纲

```python
# 提取所有标题生成大纲
outline = []

# 一级标题
for block in blocks:
    if any(cls.startswith('heading-') for cls in block.classes):
        outline.append({
            'level': 1,
            'text': block.paragraph.text,
            'classes': block.classes
        })

print("文档大纲:")
for item in outline:
    indent = "  " * (item['level'] - 1)
    print(f"{indent}- {item['text']}")
```

## 性能优化建议

### 1. 缓存选择结果

```python
# 如果需要多次查询同一个选择器，可以缓存结果
class CachedSelector:
    def __init__(self, selector):
        self.selector = selector
        self.cache = {}
    
    def select(self, selector_str):
        if selector_str not in self.cache:
            self.cache[selector_str] = self.selector.select(selector_str)
        return self.cache[selector_str]

cached_selector = CachedSelector(selector)
```

### 2. 使用简单选择器

```python
# 推荐：简单直接
refs = selector.select(".reference-item")

# 不推荐：过于复杂（如果不需要）
refs = selector.select(".heading-references + .reference-item")
```

### 3. 提前过滤

```python
# 如果只需要特定类型的元素，可以提前过滤
from script.core.model import ParagraphBlock

paragraphs = [b for b in blocks if isinstance(b, ParagraphBlock)]
para_selector = Selector(paragraphs)
```

## 错误处理

### 1. 处理不存在的元素

```python
# 使用 select_one 时检查返回值
result = selector.select_one(".non-existent")
if result:
    print(result.paragraph.text)
else:
    print("元素不存在")

# 或使用 exists 先检查
if selector.exists(".author-affiliation"):
    affiliations = selector.select(".author-affiliation")
    # 处理 affiliations
```

### 2. 处理索引越界

```python
# 使用 :nth() 时注意索引范围
refs = selector.select(".reference-item")
if len(refs) >= 2:
    second_ref = selector.select_one(".reference-item:nth(1)")
else:
    print("参考文献少于2条")
```

## 完整示例：提取论文元数据

```python
def extract_paper_metadata(doc_path, config_path):
    """提取论文元数据"""
    # 加载配置和文档
    loader = ConfigLoader(config_path)
    config = loader.load()
    doc = Document(doc_path)
    
    # 标记和选择
    classifier = Classifier(config['document']['classifiers'])
    blocks = classifier.classify(doc)
    selector = Selector(blocks)
    
    # 提取元数据
    metadata = {}
    
    # 标题
    title = selector.select_one(".title")
    metadata['title'] = title.paragraph.text if title else None
    
    # 作者
    authors = selector.select(".author-list")
    metadata['authors'] = [a.paragraph.text for a in authors]
    
    # 作者单位
    affiliations = selector.select(".author-affiliation")
    metadata['affiliations'] = [a.paragraph.text for a in affiliations]
    
    # 通讯作者
    corresponding = selector.select_one(".corresponding-author")
    metadata['corresponding'] = corresponding.paragraph.text if corresponding else None
    
    # 摘要
    abstract = selector.select_one(".abstract")
    metadata['abstract'] = abstract.paragraph.text if abstract else None
    
    # 关键词
    keywords = selector.select_one(".keywords")
    metadata['keywords'] = keywords.paragraph.text if keywords else None
    
    # 参考文献数量
    metadata['reference_count'] = selector.count(".reference-item")
    
    return metadata

# 使用示例
metadata = extract_paper_metadata('paper.docx', 'config/template/data_paper/config.yaml')
print(json.dumps(metadata, ensure_ascii=False, indent=2))
```

## 总结

Selector 系统提供了强大而灵活的文档元素查询能力：

- ✅ **类似 CSS**：熟悉的语法，易于学习
- ✅ **功能丰富**：支持类选择器、伪类、相邻兄弟选择器等
- ✅ **易于使用**：简单的 API，链式调用
- ✅ **高效查询**：快速定位所需元素
- ✅ **可扩展**：支持自定义过滤和处理

通过 Selector，你可以轻松地从已标记的文档中提取任何需要的信息！
