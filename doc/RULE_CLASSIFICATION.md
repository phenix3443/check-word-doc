# 规则分类体系

## 核心分类：只有两种规则

### 1. 基础规则 (Base Rules)

**定义**: 适用于**所有文档**的基础检查规则

**位置**: `config/base.yaml` + `config/base/*.yaml`

**特点**:
- ✅ 所有文档都必须遵守
- ✅ 与文档类型无关
- ✅ 通用性强

**示例**:
```yaml
# config/base.yaml

import:
  - "base/paragraphs.yaml"    # 段落基础规则
  - "base/references.yaml"    # 参考文献基础规则
  - "base/headings.yaml"      # 标题基础规则
  - "base/structure.yaml"     # 结构基础规则
```

**包含的规则**:
- 段落末尾标点检查（PAR003）
- 中文字符间空格检查（PAR004）
- 中文引号配对检查（PAR006）
- 连续空行检查（PAR007）
- 参考文献存在性检查（REF001）
- 参考文献引用检查（REF002）
- ... 等

---

### 2. 文档自定义规则 (Document-Specific Rules)

**定义**: 针对**特定文档类型或项目**的额外检查规则

**位置**: 
- 模板配置：`config/data_paper_template.yaml`、`config/thesis_template.yaml` 等
- 项目配置：用户自己的 `my_project.yaml`

**特点**:
- ✅ 特定于文档类型（如数据论文、学位论文）
- ✅ 特定于项目需求
- ✅ 导入基础规则 + 添加自定义规则

**示例**:

#### 数据论文模板配置

```yaml
# config/data_paper_template.yaml

description: "数据论文模板"

# 1. 导入基础规则（所有文档共用）
import:
  - "base.yaml"

# 2. 添加数据论文特定的规则
rules:
  # 数据论文特有的格式要求
  - id: "FONT001"
    params:
      description: "封面标题必须使用黑体3号加粗"
      target_blocks: [0]
      expected_font_name: "黑体"
      expected_font_size: 203200
  
  # 数据论文特有的章节要求
  - id: "STRUCT001"
    params:
      description: "必须包含'数据采集和处理方法'章节"
      keywords: ["数据采集", "处理方法"]
  
  - id: "STRUCT002"
    params:
      description: "必须包含'数据样本描述'章节"
      keywords: ["数据样本", "样本描述"]
  
  # ... 更多数据论文特定规则
```

#### 学位论文模板配置

```yaml
# config/thesis_template.yaml

description: "学位论文模板"

# 1. 导入基础规则（所有文档共用）
import:
  - "base.yaml"

# 2. 添加学位论文特定的规则
rules:
  # 学位论文特有的格式要求
  - id: "FONT001"
    params:
      description: "封面标题必须使用宋体2号加粗"
      target_blocks: [0]
      expected_font_name: "宋体"
      expected_font_size: 254000  # 不同于数据论文
  
  # 学位论文特有的章节要求
  - id: "STRUCT001"
    params:
      description: "必须包含'绪论'章节"
      keywords: ["绪论", "第1章"]  # 不同于数据论文
  
  # ... 更多学位论文特定规则
```

#### 用户项目配置

```yaml
# my_project.yaml

description: "我的项目自定义配置"

# 1. 导入文档模板（已包含基础规则）
import:
  - "data_paper_template.yaml"

# 2. 根据项目需求调整
rules:
  # 禁用某个规则
  - id: "FONT001"
    enabled: false  # 我的项目不检查封面字体
  
  # 修改规则参数
  - id: "STRUCT001"
    params:
      keywords: ["数据收集", "处理方法"]  # 使用不同的关键词
  
  # 添加项目特定规则
  - id: "MY_CUSTOM"
    params:
      description: "我的项目特定检查"
      ...
```

---

## 文档模板 = 预设的文档自定义规则

你说得对！**模板配置本质上还是文档自定义规则**，只是我们预先为常见文档类型准备好了。

```
文档自定义规则
    ├── 预设模板（我们提供）
    │     ├── data_paper_template.yaml   ← 数据论文的自定义规则
    │     ├── thesis_template.yaml       ← 学位论文的自定义规则
    │     └── report_template.yaml       ← 技术报告的自定义规则
    │
    └── 用户项目配置（用户编写）
          └── my_project.yaml            ← 用户的自定义规则
```

---

## 配置文件的使用场景

### config/base.yaml
**用途**: 作为所有文档的基础，提供最基本的检查

**使用者**: 
- ✅ 所有模板配置都应该导入它
- ✅ 用户项目可以直接导入它（如果不需要模板）

**示例**:
```bash
# 只用基础规则检查
poetry run docx-lint doc.docx --config config/base.yaml
```

---

### config/data_paper_template.yaml
**用途**: 数据论文的检查规则（基础规则 + 数据论文特定规则）

**使用者**:
- ✅ 检查数据论文时使用
- ✅ 或被用户项目导入后再自定义

**示例**:
```bash
# 用数据论文模板检查
poetry run docx-lint my_data_paper.docx --config config/data_paper_template.yaml
```

---

### my_project.yaml (用户自己创建)
**用途**: 用户项目的自定义规则

**使用者**:
- ✅ 用户根据项目需求编写

**示例**:
```bash
# 用项目配置检查
poetry run docx-lint my_doc.docx --config my_project.yaml
```

---

## 总结

**只有两种规则**:

1. **基础规则** (`config/base.yaml`)
   - 所有文档共用
   - 通用性检查

2. **文档自定义规则** (其他所有配置)
   - 特定于文档类型或项目
   - 包括：
     - 模板配置（我们预设的）
     - 用户配置（用户自己写的）

**文档模板** = 预设的文档自定义规则（为常见文档类型准备的）

**配置继承链**:
```
base.yaml (基础规则)
    ↓ import
data_paper_template.yaml (数据论文模板 = 基础 + 数据论文特定)
    ↓ import
my_project.yaml (用户项目 = 模板 + 项目调整)
```
