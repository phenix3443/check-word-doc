# 硬编码内容审查报告

## 审查时间
2026-01-15

## 审查目的
确保代码不包含与特定文档格式、内容强相关的硬编码，保证系统能够通过配置文件适配各种不同的文档类型。

## 发现的硬编码内容

### 1. 中文字号映射（中等优先级）

**位置：** `script/utils/unit_converter.py:62-71`

**问题：**
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
- 这是中国国家标准（GB/T 9704-2012）的字号体系
- 虽然是标准，但理论上应该可配置以支持其他字号体系
- **影响范围：** 中等（主要影响中文文档）
- **优先级：** 中等（可以保留，但应文档化）

**建议：**
1. **保留当前实现**：这是广泛使用的标准
2. **添加文档说明**：在代码注释中说明这是 GB/T 9704-2012 标准
3. **未来扩展**：如需支持其他字号体系，可以通过配置文件扩展

### 2. 对齐方式映射（低优先级）

**位置：** `script/core/style_checker.py:289-300`

**问题：**
```python
align_map = {
    '居中': WD_ALIGN_PARAGRAPH.CENTER,
    'CENTER': WD_ALIGN_PARAGRAPH.CENTER,
    '左对齐': WD_ALIGN_PARAGRAPH.LEFT,
    'LEFT': WD_ALIGN_PARAGRAPH.LEFT,
    '右对齐': WD_ALIGN_PARAGRAPH.RIGHT,
    'RIGHT': WD_ALIGN_PARAGRAPH.RIGHT,
    '两端对齐': WD_ALIGN_PARAGRAPH.JUSTIFY,
    'JUSTIFY': WD_ALIGN_PARAGRAPH.JUSTIFY,
    '分散对齐': WD_ALIGN_PARAGRAPH.DISTRIBUTE,
    'DISTRIBUTE': WD_ALIGN_PARAGRAPH.DISTRIBUTE,
}
```

**分析：**
- 这是中文和英文对齐方式名称到 `python-docx` 枚举的映射
- 映射本身是必需的（`python-docx` 的 API 要求）
- 支持中英文双语是为了配置文件的易用性
- **影响范围：** 低（这是 Word 的标准对齐方式）
- **优先级：** 低（可以保留）

**建议：**
1. **保留当前实现**：这些是 Word 的标准对齐方式
2. **提取为类常量**：可以将映射表提取为类常量，便于维护
3. **支持扩展**：如果未来需要支持更多语言，可以通过配置文件扩展

### 3. 单位转换常量（低优先级）

**位置：** `script/utils/unit_converter.py:18-30`

**问题：**
```python
EMU_PER_INCH = 914400  # 1英寸 = 914400 EMU
EMU_PER_CM = 360000    # 1厘米 = 360000 EMU
TWIP_PER_PT = 20       # 1点 = 20 twip
PT_PER_INCH = 72       # 1英寸 = 72点

CHAR_WIDTH_RATIO = 1.0  # 字符宽度与字号的比例
LINE_HEIGHT_RATIO = 1.2  # 行高比例
```

**分析：**
- 这些是 `python-docx` 和 Word 的内部单位转换常量
- 大部分是固定的标准（如 EMU、twip）
- `CHAR_WIDTH_RATIO` 和 `LINE_HEIGHT_RATIO` 是估算值
- **影响范围：** 低（这些是技术标准）
- **优先级：** 低（可以保留）

**建议：**
1. **保留标准常量**：EMU、twip 等是固定标准
2. **文档化估算值**：为 `CHAR_WIDTH_RATIO` 和 `LINE_HEIGHT_RATIO` 添加说明
3. **可选配置**：未来可以允许通过配置文件覆盖估算值

## 没有硬编码的内容（✅ 良好）

### 1. 文档内容
- ✅ 没有硬编码具体的文档内容（如"摘要"、"标题"等）
- ✅ 所有内容匹配都通过配置文件的 `pattern` 定义

### 2. 文档结构
- ✅ 没有硬编码文档结构
- ✅ 所有结构定义都在配置文件的 `classifiers` 中

### 3. 样式规则
- ✅ 没有硬编码样式规则
- ✅ 所有样式定义都在配置文件的 `styles` 中

### 4. 字体名称
- ✅ 没有硬编码字体名称
- ✅ 字体名称都在配置文件中定义

### 5. 格式要求
- ✅ 没有硬编码格式要求
- ✅ 所有格式要求都在配置文件中定义

## 改进建议

### 高优先级（必须）
无。当前代码已经很好地将文档相关的内容都放在配置文件中。

### 中优先级（建议）

#### 1. 提取对齐方式映射为类常量

**当前：** 映射表在方法内部

**建议：** 提取为类常量

```python
class StyleChecker:
    # 对齐方式映射（中英文）
    ALIGNMENT_MAP = {
        '居中': WD_ALIGN_PARAGRAPH.CENTER,
        'CENTER': WD_ALIGN_PARAGRAPH.CENTER,
        '左对齐': WD_ALIGN_PARAGRAPH.LEFT,
        'LEFT': WD_ALIGN_PARAGRAPH.LEFT,
        '右对齐': WD_ALIGN_PARAGRAPH.RIGHT,
        'RIGHT': WD_ALIGN_PARAGRAPH.RIGHT,
        '两端对齐': WD_ALIGN_PARAGRAPH.JUSTIFY,
        'JUSTIFY': WD_ALIGN_PARAGRAPH.JUSTIFY,
        '分散对齐': WD_ALIGN_PARAGRAPH.DISTRIBUTE,
        'DISTRIBUTE': WD_ALIGN_PARAGRAPH.DISTRIBUTE,
    }
```

**优点：**
- 便于维护和扩展
- 可以在类初始化时被覆盖（如果需要）
- 代码更清晰

#### 2. 添加文档说明

为所有"硬编码"的常量添加详细的文档说明：

```python
class UnitConverter:
    """单元转换器
    
    中文字号映射基于中国国家标准 GB/T 9704-2012。
    如需支持其他字号体系，可以通过继承此类并覆盖相关方法实现。
    """
    
    # 中文字号映射（GB/T 9704-2012）
    CHINESE_FONT_SIZES = {
        "初号": 42, "小初": 36,
        # ...
    }
```

### 低优先级（可选）

#### 1. 支持自定义字号映射

允许通过配置文件扩展字号映射：

```yaml
# config.yaml
document:
  font_size_aliases:
    "特大号": 48
    "超大号": 36
```

**实现：**
```python
class UnitConverter:
    _custom_sizes = {}
    
    @classmethod
    def register_custom_size(cls, name: str, pt: float):
        """注册自定义字号"""
        cls._custom_sizes[name] = pt
    
    @classmethod
    def parse_font_size(cls, value):
        # 先查找自定义字号
        if value in cls._custom_sizes:
            return int(cls._custom_sizes[value] * 2)
        # 再查找标准字号
        # ...
```

#### 2. 支持多语言对齐方式名称

允许通过配置文件定义其他语言的对齐方式名称：

```yaml
# config.yaml
document:
  alignment_aliases:
    "中央揃え": "CENTER"  # 日语
    "centré": "CENTER"     # 法语
```

## 总结

### 当前状态：✅ 优秀

代码已经很好地实现了配置驱动：
- ✅ 所有文档内容、结构、样式都在配置文件中
- ✅ 核心代码不包含任何文档特定的硬编码
- ✅ 系统可以通过配置文件适配不同的文档类型

### 存在的"硬编码"

仅有的"硬编码"都是**技术标准**或**通用映射**：
1. 中文字号映射（国家标准）
2. 对齐方式映射（Word 标准）
3. 单位转换常量（技术标准）

这些"硬编码"是合理的，因为：
- 它们是广泛使用的标准
- 不是特定文档的要求
- 提供了易用性（支持中文配置）

### 建议行动

**立即行动（必须）：**
- 无。当前代码已经符合要求。

**短期改进（建议）：**
1. 提取对齐方式映射为类常量
2. 为所有常量添加详细的文档说明
3. 在 README 中说明支持的单位和字号

**长期扩展（可选）：**
1. 支持自定义字号映射（如果有需求）
2. 支持多语言对齐方式名称（如果有需求）

## 结论

✅ **代码审查通过**

当前代码已经很好地实现了"配置驱动"的设计理念。所有与特定文档相关的内容都在配置文件中，核心代码只包含必要的技术标准和通用映射。系统可以通过配置文件适配各种不同类型的文档。
