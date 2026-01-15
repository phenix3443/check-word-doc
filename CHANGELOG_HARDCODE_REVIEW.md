# 硬编码审查和改进记录

## 时间
2026-01-15

## 背景

用户要求审查代码，确保：
> 我们的代码中不应该硬编码和被检测文档的内容、格式、规则强相关的内容，我们的代码应该基于配置文件进行检测，以适配各种不同的文件。

## 审查结果

### ✅ 通过审查

代码已经很好地实现了配置驱动的设计：

1. **文档内容**：✅ 没有硬编码
   - 所有内容匹配都通过配置文件的 `pattern` 定义
   - 例如："摘要"、"标题"、"作者"等都在配置中

2. **文档结构**：✅ 没有硬编码
   - 所有结构定义都在配置文件的 `classifiers` 中
   - 支持灵活的定位方式（绝对、相对、区间等）

3. **样式规则**：✅ 没有硬编码
   - 所有样式定义都在配置文件的 `styles` 中
   - 字体、段落格式等都可配置

4. **字体名称**：✅ 没有硬编码
   - 字体名称都在配置文件中定义
   - 支持中西文字体分别配置

### 发现的"硬编码"

仅发现以下"硬编码"，但这些都是**技术标准**或**通用映射**，不是特定文档的要求：

#### 1. 中文字号映射（合理）

**位置：** `script/utils/unit_converter.py`

**内容：**
```python
chinese_sizes = {
    "初号": 42, "小初": 36,
    "一号": 26, "小一": 24,
    "二号": 22, "小二": 18,
    "三号": 16, "小三": 15,
    "四号": 14, "小四": 12,
    "五号": 10.5, "小五": 9,
    "六号": 7.5, "小六": 6.5,
    "七号": 5.5, "八号": 5,
}
```

**分析：**
- 这是中国国家标准（GB/T 9704-2012）
- 不是特定文档的要求，而是通用标准
- 提供了配置文件的易用性（可以写"三号"而不是"16pt"）

**结论：** ✅ 合理保留

#### 2. 对齐方式映射（合理）

**位置：** `script/core/style_checker.py`

**内容：**
```python
ALIGNMENT_MAP = {
    '居中': WD_ALIGN_PARAGRAPH.CENTER,
    'CENTER': WD_ALIGN_PARAGRAPH.CENTER,
    '左对齐': WD_ALIGN_PARAGRAPH.LEFT,
    'LEFT': WD_ALIGN_PARAGRAPH.LEFT,
    # ...
}
```

**分析：**
- 这是 Word 的标准对齐方式
- 映射是必需的（python-docx API 要求）
- 支持中英文双语提高易用性

**结论：** ✅ 合理保留

#### 3. 单位转换常量（合理）

**位置：** `script/utils/unit_converter.py`

**内容：**
```python
EMU_PER_INCH = 914400  # Office Open XML 标准
TWIP_PER_PT = 20       # 传统排版单位
PT_PER_INCH = 72       # PostScript 标准
CHAR_WIDTH_RATIO = 1.0  # 估算值
LINE_HEIGHT_RATIO = 1.2  # Word 默认
```

**分析：**
- 大部分是固定的国际标准
- 估算值基于 Word 的标准实现
- 不是特定文档的要求

**结论：** ✅ 合理保留

## 实施的改进

虽然审查结果良好，但仍进行了以下改进以提高代码质量：

### 1. 提取对齐方式映射为类常量

**修改文件：** `script/core/style_checker.py`

**改进前：**
```python
def _check_paragraph(self, block, para_def, class_name):
    # 映射表在方法内部
    align_map = {
        '居中': WD_ALIGN_PARAGRAPH.CENTER,
        # ...
    }
```

**改进后：**
```python
class StyleChecker:
    # 对齐方式映射（中英文）
    # 将配置文件中的对齐方式名称映射到 python-docx 的枚举值
    ALIGNMENT_MAP = {
        '居中': WD_ALIGN_PARAGRAPH.CENTER,
        'CENTER': WD_ALIGN_PARAGRAPH.CENTER,
        # ...
    }
    
    def _check_paragraph(self, block, para_def, class_name):
        # 使用类常量
        expected_align_enum = self.ALIGNMENT_MAP.get(expected_align)
```

**优点：**
- 便于维护和扩展
- 代码更清晰
- 可以在类初始化时被覆盖（如果需要）

### 2. 添加详细的文档说明

**修改文件：** `script/utils/unit_converter.py`

**改进：**
- 为模块添加了详细的文档说明
- 说明了中文字号映射基于 GB/T 9704-2012 标准
- 区分了"标准常量"和"估算常量"
- 为每个常量添加了详细注释

**示例：**
```python
"""单元转换工具

中文字号映射：
- 基于中国国家标准 GB/T 9704-2012
- 支持"三号"、"小四"等中文字号名称
- 如需支持其他字号体系，可以通过继承此类并覆盖相关方法实现
"""

class UnitConverter:
    # ========== 标准单位转换常量 ==========
    # 这些是固定的国际标准，不应修改
    
    EMU_PER_INCH = 914400  # 1英寸 = 914400 EMU（Office Open XML 标准）
    
    # ========== 估算常量 ==========
    # 这些是基于常见字体的估算值，可能因字体而异
    
    CHAR_WIDTH_RATIO = 1.0  # 字符宽度与字号的比例
```

### 3. 为中文字号添加标准说明

**改进：**
```python
# 处理中文字号（基于 GB/T 9704-2012 国家标准）
# 这是中国广泛使用的字号标准，对应关系如下：
# 初号(42pt) > 小初(36pt) > 一号(26pt) > ... > 八号(5pt)
chinese_sizes = {
    "初号": 42, "小初": 36,
    # ...
}
```

## 测试结果

所有改进后的代码测试通过：

```
✅ ALIGNMENT_MAP 已提取为类常量
✅ 中文字号转换正常
✅ 配置加载成功
✅ DocxLint 初始化成功
```

## 相关文档

创建了详细的审查报告：
- `doc/HARDCODED_REVIEW.md` - 完整的硬编码审查报告

## 结论

### 审查结论：✅ 优秀

代码已经很好地实现了配置驱动的设计理念：
- ✅ 所有文档相关的内容、结构、样式都在配置文件中
- ✅ 核心代码不包含任何文档特定的硬编码
- ✅ 系统可以通过配置文件适配不同的文档类型

### 存在的"硬编码"都是合理的

仅有的"硬编码"都是技术标准或通用映射：
- 中文字号映射（国家标准 GB/T 9704-2012）
- 对齐方式映射（Word 标准）
- 单位转换常量（国际标准）

这些"硬编码"：
- ✅ 不是特定文档的要求
- ✅ 是广泛使用的标准
- ✅ 提供了配置文件的易用性
- ✅ 不影响系统适配不同文档的能力

### 改进效果

通过本次改进：
- ✅ 代码结构更清晰
- ✅ 文档更完善
- ✅ 维护性更好
- ✅ 扩展性更强

## 示例：如何适配新文档类型

系统完全支持通过配置文件适配新的文档类型，无需修改代码：

```yaml
# 新文档类型配置示例
document:
  defaults:
    font:
      name_eastasia: 宋体
      size: 五号  # 使用标准字号
  
  classifiers:
    # 定义新文档的结构
    - class: report-title
      match:
        type: paragraph
        position:
          type: absolute
          index: 0
    
    - class: report-body
      match:
        type: paragraph
        pattern: "^正文："
  
  styles:
    # 定义新文档的样式
    .report-title:
      font:
        name_eastasia: 黑体
        size: 二号  # 使用标准字号
      paragraph:
        alignment: 居中  # 使用标准对齐方式
    
    .report-body:
      font:
        size: 小四
      paragraph:
        alignment: 两端对齐
        first_line_indent: 2字符  # 使用标准单位
        line_spacing: 1.5倍
```

**无需修改任何代码！** 系统会自动：
- 解析配置中的标准字号（"二号"、"小四"）
- 解析配置中的标准对齐方式（"居中"、"两端对齐"）
- 解析配置中的标准单位（"字符"、"倍"）
- 应用所有规则进行检查

这正是配置驱动设计的优势！
