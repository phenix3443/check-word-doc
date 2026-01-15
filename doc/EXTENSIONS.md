# 扩展配置说明

## 概述

虽然系统内置了常用的字号和对齐方式（基于中国国家标准和 Word 标准），但你可以通过配置文件扩展这些功能，而**无需修改任何代码**。

## 支持的扩展

### 1. 自定义字号别名

添加自定义的字号名称，系统会自动识别。

#### 配置格式

```yaml
document:
  font_size_aliases:
    "别名": 磅数
```

#### 示例

```yaml
document:
  font_size_aliases:
    "特大号": 48      # 自定义：特大号 = 48pt
    "超大号": 36      # 自定义：超大号 = 36pt
    "正文": 10.5      # 自定义：正文 = 10.5pt（相当于五号）
    "标题": 16        # 自定义：标题 = 16pt（相当于三号）
```

#### 使用

```yaml
styles:
  .my-title:
    font:
      size: 特大号    # 使用自定义字号
```

#### 说明

- 自定义字号会**优先**于标准字号
- 标准字号（如"三号"、"小四"）仍然可用
- 可以覆盖标准字号（不推荐）

### 2. 自定义对齐方式别名

添加其他语言的对齐方式名称。

#### 配置格式

```yaml
document:
  alignment_aliases:
    "别名": "枚举值"
```

#### 支持的枚举值

| 枚举值 | 含义 |
|--------|------|
| `CENTER` | 居中 |
| `LEFT` | 左对齐 |
| `RIGHT` | 右对齐 |
| `JUSTIFY` | 两端对齐 |
| `DISTRIBUTE` | 分散对齐 |

#### 示例

```yaml
document:
  alignment_aliases:
    # 日语
    "中央揃え": "CENTER"     # 居中
    "左揃え": "LEFT"         # 左对齐
    "右揃え": "RIGHT"        # 右对齐
    "両端揃え": "JUSTIFY"    # 两端对齐
    
    # 法语
    "centré": "CENTER"       # 居中
    "gauche": "LEFT"         # 左对齐
    "droite": "RIGHT"        # 右对齐
    
    # 其他自定义
    "中间": "CENTER"
    "左": "LEFT"
```

#### 使用

```yaml
styles:
  .my-paragraph:
    paragraph:
      alignment: 中央揃え    # 使用日语对齐方式
```

#### 说明

- 标准对齐方式（中英文）仍然可用
- 可以添加任何语言的对齐方式名称

### 3. 字符宽度比例

调整字符宽度与字号的比例。

#### 配置格式

```yaml
document:
  char_width_ratio: 1.0    # 默认值
```

#### 说明

- 默认值：`1.0`（字符宽度 = 字号）
- 用于计算"字符"单位的间距和缩进
- 例如：`first_line_indent: 2字符`
- 如果使用的字体字符宽度与字号不是 1:1，可以在此调整

#### 示例

```yaml
document:
  char_width_ratio: 0.9    # 字符宽度 = 字号 * 0.9
```

### 4. 行高比例

调整行高与字号的比例。

#### 配置格式

```yaml
document:
  line_height_ratio: 1.2   # 默认值
```

#### 说明

- 默认值：`1.2`（Word 的单倍行距）
- 用于计算"行"单位的间距
- 例如：`space_before: 0.5行`

#### 示例

```yaml
document:
  line_height_ratio: 1.5   # 行高 = 字号 * 1.5
```

## 完整示例

```yaml
# my_custom_config.yaml

document:
  # 自定义字号
  font_size_aliases:
    "特大号": 48
    "正文": 10.5
    "标题": 16
  
  # 自定义对齐方式（日语）
  alignment_aliases:
    "中央揃え": "CENTER"
    "左揃え": "LEFT"
  
  # 调整字符宽度比例
  char_width_ratio: 1.0
  
  # 调整行高比例
  line_height_ratio: 1.2
  
  # 元素识别
  classifiers:
    - class: title
      match:
        type: paragraph
        position:
          type: absolute
          index: 0
  
  # 样式定义（使用自定义别名）
  styles:
    .title:
      font:
        size: 特大号        # 使用自定义字号
      paragraph:
        alignment: 中央揃え  # 使用日语对齐方式
```

## 使用场景

### 场景 1：多语言文档

如果你的团队使用日语、法语等其他语言，可以添加对应语言的对齐方式名称：

```yaml
document:
  alignment_aliases:
    "中央揃え": "CENTER"
    "centré": "CENTER"
```

### 场景 2：简化配置

如果你经常使用某些特定的字号，可以定义简短的别名：

```yaml
document:
  font_size_aliases:
    "大": 16
    "中": 12
    "小": 10.5
```

### 场景 3：特殊字体

如果使用的字体字符宽度与标准不同，可以调整比例：

```yaml
document:
  char_width_ratio: 0.9    # 窄字体
  # 或
  char_width_ratio: 1.1    # 宽字体
```

### 场景 4：自定义标准

如果你的组织有自己的字号标准：

```yaml
document:
  font_size_aliases:
    "公司标题": 20
    "公司正文": 11
    "公司注释": 9
```

## 优先级

1. **自定义字号** > 标准字号（GB/T 9704-2012）
2. **自定义对齐方式** 与标准对齐方式共存
3. **自定义比例** 覆盖默认比例

## 注意事项

### ✅ 推荐做法

1. **不要覆盖标准字号**：保持标准字号（如"三号"）不变
2. **使用有意义的名称**：如"标题"、"正文"而不是"a"、"b"
3. **添加注释**：说明自定义别名的含义和用途
4. **保持一致性**：在整个项目中使用相同的自定义别名

### ❌ 不推荐做法

1. **覆盖标准字号**：
   ```yaml
   # 不推荐
   font_size_aliases:
     "三号": 18    # 覆盖标准的三号（16pt）
   ```

2. **使用模糊的名称**：
   ```yaml
   # 不推荐
   font_size_aliases:
     "a": 16
     "b": 12
   ```

3. **过度自定义**：
   ```yaml
   # 不推荐：定义太多别名会让配置难以维护
   font_size_aliases:
     "size1": 16
     "size2": 15
     "size3": 14
     # ... 太多了
   ```

## 测试扩展

创建一个测试配置文件：

```yaml
# test_extensions.yaml
document:
  font_size_aliases:
    "测试": 20
  
  alignment_aliases:
    "测试对齐": "CENTER"
  
  classifiers:
    - class: test
      match:
        type: paragraph
        position:
          type: absolute
          index: 0
  
  styles:
    .test:
      font:
        size: 测试
      paragraph:
        alignment: 测试对齐
```

运行测试：

```bash
poetry run docx-lint document.docx --config test_extensions.yaml
```

如果配置正确，系统会：
- ✅ 识别"测试"字号（20pt）
- ✅ 识别"测试对齐"（居中）
- ✅ 正常进行检查

## 总结

通过扩展配置，你可以：

1. ✅ **无需修改代码**即可添加自定义功能
2. ✅ **支持多语言**团队协作
3. ✅ **适应特殊需求**（特殊字体、自定义标准等）
4. ✅ **保持灵活性**，同时不影响标准功能

这正是**配置驱动设计**的优势！🎉
