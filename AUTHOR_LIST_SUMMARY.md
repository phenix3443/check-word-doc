# 作者列表配置总结

## 问题

如何配置作者列表的格式要求：
1. **样式**：居中，小4号，中文字体华文楷体，西文字体Times New Roman
2. **内容**：多个作者时，使用中文逗号分割，每个作者名字后面有数字

## 解决方案

通过配置文件和正则表达式完美实现！

### 1. 样式配置（styles.yaml）

```yaml
.author-list:
  font:
    name_eastasia: 华文楷体
    name_ascii: "Times New Roman"
    size: 小四
  paragraph:
    alignment: 居中
```

### 2. 内容规则（rules.yaml）

#### r-001: 多作者格式规则

```yaml
- id: r-001
  name: 作者列表格式规则（多作者）
  selector: ".author-list"
  condition:
    selector: ".author-list"
    pattern: "，"  # 包含中文逗号 = 多作者
  check:
    pattern: "^[^,;；、，]+\\d+[*]?(，[^,;；、，]+\\d+[*]?)*$"
  severity: error
  message: "多个作者时，必须使用中文逗号（，）分隔，每个作者名后必须有数字编号（如：王嘉平1*，汪浩2）"
```

#### r-002: 单作者格式规则

```yaml
- id: r-002
  name: 作者列表格式规则（单作者）
  selector: ".author-list"
  condition:
    selector: ".author-list"
    pattern: "^[^，]*$"  # 不包含中文逗号 = 单作者
  check:
    pattern: "^[^,;；、，]+\\d+[*]?$"
  severity: error
  message: "作者名后必须有数字编号（如：王嘉平1*）"
```

#### r-003: 通讯作者标记规则

```yaml
- id: r-003
  name: 通讯作者标记规则
  selector: ".author-list"
  check:
    pattern: "\\d+\\*"
  severity: error
  message: "通讯作者的编号后必须有星号（如：王嘉平1*）"
```

## 正则表达式详解

### 多作者格式

```regex
^[^,;；、，]+\d+[*]?(，[^,;；、，]+\d+[*]?)*$
```

**含义**：
- `^` - 开始
- `[^,;；、，]+` - 作者名（不能包含分隔符）
- `\d+` - 数字编号（必须）
- `[*]?` - 星号（可选，表示通讯作者）
- `，` - 中文逗号
- `(，[^,;；、，]+\d+[*]?)*` - 后续作者（重复）
- `$` - 结束

**示例**：
- ✅ `王嘉平1*，汪浩2`
- ✅ `张三1*，李四2，王五3`
- ❌ `王嘉平1,汪浩2`（英文逗号）
- ❌ `王嘉平，汪浩2`（第一个作者缺数字）

### 单作者格式

```regex
^[^,;；、，]+\d+[*]?$
```

**含义**：
- `^` - 开始
- `[^,;；、，]+` - 作者名（不能包含分隔符）
- `\d+` - 数字编号（必须）
- `[*]?` - 星号（可选）
- `$` - 结束

**示例**：
- ✅ `王嘉平1*`
- ✅ `汪浩1`
- ❌ `王嘉平`（缺数字）

## 工作原理

### 1. 条件判断

系统通过检查是否包含中文逗号来判断单/多作者：

```yaml
condition:
  selector: ".author-list"
  pattern: "，"  # 有逗号 = 多作者
```

### 2. 格式检查

根据判断结果应用不同的正则表达式：
- 多作者：检查所有作者都有数字，使用中文逗号分隔
- 单作者：检查作者有数字

### 3. 错误提示

格式不符时显示清晰的错误消息，帮助用户修正。

## 测试验证

运行测试：

```bash
poetry run python3 test/author_list_test.py
```

测试结果：

```
================================================================================
作者列表格式测试
================================================================================

✅ [PASS] (单作者) 单作者，有星号（通讯作者）
✅ [PASS] (单作者) 单作者，无星号
✅ [PASS] (多作者) 两个作者，第一作者是通讯作者
✅ [PASS] (多作者) 两个作者，第二作者是通讯作者
✅ [PASS] (多作者) 三个作者，第一作者是通讯作者
✅ [PASS] (多作者) 三个作者，两个通讯作者
✅ [PASS] (单作者) ❌ 缺少数字编号
✅ [PASS] (单作者) ❌ 缺少数字编号（只有星号）
✅ [PASS] (单作者) ❌ 使用英文逗号
✅ [PASS] (单作者) ❌ 使用分号
✅ [PASS] (单作者) ❌ 使用顿号
✅ [PASS] (多作者) ❌ 第二个作者缺少数字
✅ [PASS] (多作者) ❌ 第一个作者缺少数字

测试结果: 13 通过, 0 失败
🎉 所有测试通过！
```

## 配置验证

```bash
poetry run python3 << 'EOF'
from script.config_loader import ConfigLoader

loader = ConfigLoader('config/template/data_paper/config.yaml')
config = loader.load()

# 检查样式
styles = config['document']['styles']
print("样式配置:")
print(f"  字体: {styles['.author-list']['font']}")
print(f"  段落: {styles['.author-list']['paragraph']}")

# 检查规则
rules = config['document']['rules']
author_rules = [r for r in rules if '.author-list' in r.get('selector', '')]
print(f"\n规则数量: {len(author_rules)} 条")
for rule in author_rules:
    print(f"  [{rule['id']}] {rule['name']}")
EOF
```

输出：

```
样式配置:
  字体: {'name_eastasia': '华文楷体', 'name_ascii': 'Times New Roman', 'size': '小四'}
  段落: {'alignment': '居中'}

规则数量: 3 条
  [r-001] 作者列表格式规则（多作者）
  [r-002] 作者列表格式规则（单作者）
  [r-003] 通讯作者标记规则
```

## 优势

### 1. 完全配置驱动

✅ 所有规则都在配置文件中定义
✅ 代码中没有任何硬编码
✅ 易于修改和扩展

### 2. 正则表达式强大

✅ 精确匹配格式要求
✅ 自动区分单/多作者
✅ 支持复杂的验证逻辑

### 3. 清晰的错误提示

✅ 明确指出错误类型
✅ 提供正确示例
✅ 帮助用户快速修正

### 4. 完整的测试覆盖

✅ 13 个测试用例
✅ 覆盖正常和异常情况
✅ 所有测试通过

## 总结

通过配置文件和正则表达式，我们完美实现了作者列表的格式检查：

| 检查项 | 实现方式 | 状态 |
|--------|---------|------|
| 字体样式 | styles.yaml | ✅ |
| 对齐方式 | styles.yaml | ✅ |
| 分隔符 | 正则表达式 | ✅ |
| 数字编号 | 正则表达式 | ✅ |
| 通讯作者标记 | 正则表达式 | ✅ |
| 单/多作者区分 | 条件规则 | ✅ |

**答案**：是的，完全可以通过正则表达式实现！🎉

详细文档请参考：`doc/AUTHOR_LIST_CONFIG.md`
