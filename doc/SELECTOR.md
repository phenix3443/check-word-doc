# Selector 语法规范

## 概述

Selector（选择器）系统允许你使用类似 CSS 的语法来查询和筛选文档中已经被 Classifier 标记的元素。

## 基本语法

### 1. 类选择器 (Class Selector)

选择具有特定 class 的所有元素：

```
.author-list          # 选择所有 author-list 元素
.heading-introduction # 选择所有 heading-introduction 元素
.reference-item       # 选择所有参考文献条目
```

### 2. 后代选择器 (Descendant Selector)

选择某个元素内部的后代元素：

```
.author-section .author-list           # 选择 author-section 内的 author-list
.author-section .author-affiliation    # 选择 author-section 内的 author-affiliation
```

### 3. 子选择器 (Child Selector)

选择某个元素的直接子元素（使用 `>`）：

```
.author-section > .author-list         # 选择 author-section 的直接子元素 author-list
```

### 4. 相邻兄弟选择器 (Adjacent Sibling Selector)

选择紧跟在某个元素后面的兄弟元素（使用 `+`）：

```
.heading-introduction + .body-introduction  # 选择紧跟在引言标题后的引言内容
.keywords-en + .data-info-table-caption     # 选择紧跟在英文关键词后的表题注
```

### 5. 通用兄弟选择器 (General Sibling Selector)

选择某个元素后面的所有兄弟元素（使用 `~`）：

```
.heading-introduction ~ .heading-data-collection  # 选择引言标题后的数据采集标题
```

### 6. 伪类选择器 (Pseudo-class Selector)

#### 位置伪类

```
.reference-item:first        # 第一个参考文献条目
.reference-item:last         # 最后一个参考文献条目
.reference-item:nth(2)       # 第二个参考文献条目（从1开始）
.reference-item:nth(0)       # 第一个参考文献条目（从0开始）
```

#### 类型伪类

```
.author-affiliation:first-of-type   # 第一个作者单位
.author-affiliation:last-of-type    # 最后一个作者单位
.author-affiliation:nth-of-type(2)  # 第二个作者单位
```

### 7. 属性选择器 (Attribute Selector)

选择具有特定属性的元素：

```
[type="table"]           # 选择所有表格类型的元素
[type="paragraph"]       # 选择所有段落类型的元素
```

### 8. 组合选择器 (Multiple Selectors)

使用逗号分隔多个选择器：

```
.heading-1, .heading-2, .heading-3   # 选择所有一级、二级、三级标题
.abstract, .abstract-en              # 选择中英文摘要
```

## 实际应用示例

### 示例1: 查询第二个作者的地址

```python
# 方法1: 使用 nth 伪类
selector = ".author-section .author-affiliation:nth(2)"

# 方法2: 使用 nth-of-type
selector = ".author-section .author-affiliation:nth-of-type(2)"
```

### 示例2: 查询参考文献的第二条

```python
selector = ".reference-item:nth(2)"
# 或
selector = ".reference-item:nth-of-type(2)"
```

### 示例3: 查询所有一级标题

```python
selector = ".heading-1"
# 或使用通用 heading 类（如果定义了）
selector = "[class^='heading-']"  # 以 heading- 开头的所有 class
```

### 示例4: 查询引言标题后的第一段正文

```python
selector = ".heading-introduction + .body-introduction"
```

### 示例5: 查询作者区域内的所有元素

```python
selector = ".author-section > *"  # 所有直接子元素
# 或
selector = ".author-section *"    # 所有后代元素
```

### 示例6: 查询第一个作者和通讯作者

```python
# 第一个作者（作者列表的第一个）
selector = ".author-section .author-list:first"

# 通讯作者（作者区域的最后一个元素）
selector = ".author-section .corresponding-author"
```

### 示例7: 查询数据信息表

```python
# 表题注
selector = ".data-info-table-caption"

# 表格本身
selector = ".data-info-table"

# 表题注和表格
selector = ".data-info-table-caption, .data-info-table"
```

## 高级用法

### 链式查询

```python
# 先选择作者区域，再在其中选择作者单位
results = selector.select(".author-section")
affiliations = results[0].select(".author-affiliation")
```

### 条件过滤

```python
# 选择包含特定文本的元素
selector = ".reference-item"
results = [r for r in selector.select(selector) if "2023" in r.text]
```

### 获取元素内容

```python
# 获取文本内容
text = selector.select_one(".abstract").text

# 获取所有类名
classes = selector.select_one(".author-list").classes

# 获取元素类型
elem_type = selector.select_one(".data-info-table").type  # "table"
```

## API 设计

### Selector 类

```python
class Selector:
    """文档元素选择器"""
    
    def __init__(self, blocks: List[Block]):
        """初始化选择器
        
        Args:
            blocks: 已经被 Classifier 标记的文档元素列表
        """
        pass
    
    def select(self, selector: str) -> List[Block]:
        """选择所有匹配的元素
        
        Args:
            selector: CSS 风格的选择器字符串
            
        Returns:
            匹配的元素列表
        """
        pass
    
    def select_one(self, selector: str) -> Optional[Block]:
        """选择第一个匹配的元素
        
        Args:
            selector: CSS 风格的选择器字符串
            
        Returns:
            第一个匹配的元素，如果没有则返回 None
        """
        pass
    
    def exists(self, selector: str) -> bool:
        """检查是否存在匹配的元素
        
        Args:
            selector: CSS 风格的选择器字符串
            
        Returns:
            是否存在匹配的元素
        """
        pass
    
    def count(self, selector: str) -> int:
        """统计匹配的元素数量
        
        Args:
            selector: CSS 风格的选择器字符串
            
        Returns:
            匹配的元素数量
        """
        pass
```

## 实现优先级

### 第一阶段（基础功能）
- ✅ 类选择器 `.class`
- ✅ 后代选择器 `.parent .child`
- ✅ 子选择器 `.parent > .child`
- ✅ 位置伪类 `:first`, `:last`, `:nth(n)`

### 第二阶段（进阶功能）
- ⏳ 相邻兄弟选择器 `.a + .b`
- ⏳ 通用兄弟选择器 `.a ~ .b`
- ⏳ 类型伪类 `:first-of-type`, `:nth-of-type(n)`
- ⏳ 属性选择器 `[attr="value"]`

### 第三阶段（高级功能）
- ⏳ 组合选择器 `.a, .b`
- ⏳ 通配符选择器 `*`
- ⏳ 否定伪类 `:not(.class)`
- ⏳ 链式查询

## 注意事项

1. **索引从 0 开始**：`:nth(0)` 表示第一个元素，`:nth(1)` 表示第二个元素
2. **类名不需要前缀**：直接使用 `.author-list`，不需要 `.class-author-list`
3. **大小写敏感**：类名区分大小写，`.Author-List` 和 `.author-list` 是不同的
4. **空格有意义**：`.a .b` 是后代选择器，`.a.b` 是同时具有两个类的元素
5. **性能考虑**：复杂的选择器可能会影响性能，建议使用简单直接的选择器

## 与 CSS 的差异

1. **没有 ID 选择器**：文档元素没有唯一 ID 的概念
2. **没有标签选择器**：使用 `[type="table"]` 代替 `table`
3. **伪类有限**：只实现了常用的位置和类型伪类
4. **没有伪元素**：不支持 `::before`、`::after` 等伪元素
5. **没有层叠和继承**：只用于查询，不涉及样式计算
