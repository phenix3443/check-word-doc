# 重复和未引用文献对照分析脚本使用说明

## 功能概述

`generate_reference_analysis.py` 脚本用于自动分析总报告中的重复文献和未引用文献在各课题报告中的分布情况，并生成详细的对照分析报告。

## 主要功能

1. **分析总报告参考文献**
   - 提取所有参考文献
   - 识别未引用文献
   - 检测重复文献
   - 统计引用格式问题

2. **分析课题报告参考文献**
   - 自动扫描课题报告目录
   - 支持标准参考文献列表格式
   - 支持尾注格式参考文献
   - 提取各课题的参考文献信息

3. **匹配和对照分析**
   - 智能匹配总报告和课题报告中的相同文献
   - 分析重复文献在各课题中的分布
   - 统计未引用文献的使用情况
   - 生成详细的对照表

4. **生成分析报告**
   - Markdown格式的详细报告
   - 包含表格和统计信息
   - 提供处理建议

## 安装要求

```bash
# 确保已安装必要的Python包
pip install python-docx  # 如果使用docx处理
```

## 使用方法

### 基本用法

```bash
python generate_reference_analysis.py \
    --main-report "/path/to/总报告.docx" \
    --subject-reports "/path/to/课题报告目录/"
```

### 完整参数

```bash
python generate_reference_analysis.py \
    --main-report "/Users/user/项目/总报告.docx" \
    --subject-reports "/Users/user/项目/课题报告/" \
    --output "参考文献分析报告.md" \
    --config "custom_config.yaml" \
    --verbose
```

### 参数说明

- `--main-report, -m`: **必需** 主报告文档路径 (.docx格式)
- `--subject-reports, -s`: **必需** 课题报告目录路径
- `--output, -o`: 可选，输出报告文件路径 (默认: `reference_analysis_YYYYMMDD_HHMMSS.md`)
- `--config, -c`: 可选，自定义配置文件路径
- `--verbose, -v`: 可选，显示详细输出信息

## 目录结构要求

### 课题报告目录结构

```
课题报告/
├── 课题1/
│   ├── 课题1-科技报告.docx
│   └── 其他文件...
├── 课题2/
│   ├── 课题2-科技报告.docx
│   └── 其他文件...
├── 课题3/
│   ├── 课题3-科技报告.docx
│   └── 其他文件...
└── ...
```

**注意**: 脚本会自动查找每个课题目录下包含"科技报告"关键词的.docx文件。

## 输出报告格式

生成的Markdown报告包含以下部分：

### 1. 总报告参考文献检查结果
- 总参考文献数量
- 未引用文献数量
- 重复文献组数
- 其他统计信息

### 2. 重复文献在各课题中的分布
- 每组重复文献的详细对照表
- 显示在各课题中的对应编号
- 引用状态分析

### 3. 未引用文献在各课题中的分布
- 按课题分组显示匹配的未引用文献
- 对比总报告和课题报告中的引用状态
- 完全未在任何课题中找到的文献

### 4. 总结和建议
- 重复文献处理建议
- 未引用文献处理建议
- 统计汇总

## 示例用法

### 示例1: 基本分析

```bash
cd /Users/liushangliang/github/phenix3443/check-word-doc

python script/generate_reference_analysis.py \
    --main-report "/Users/liushangliang/github/phenix3443/idea/23年项目/年度报告/2025/项目报告/2025年度-23 年项目-科技报告-202512241156.docx" \
    --subject-reports "/Users/liushangliang/github/phenix3443/idea/23年项目/年度报告/2025/课题报告/"
```

### 示例2: 指定输出文件

```bash
python script/generate_reference_analysis.py \
    --main-report "总报告.docx" \
    --subject-reports "课题报告/" \
    --output "2025年度参考文献分析报告.md"
```

### 示例3: 使用自定义配置

```bash
python script/generate_reference_analysis.py \
    --main-report "总报告.docx" \
    --subject-reports "课题报告/" \
    --config "/path/to/custom_config.yaml" \
    --verbose
```

## 支持的文档格式

### 参考文献格式
- **标准格式**: 文档末尾的参考文献列表，格式为 `[数字] 文献内容`
- **尾注格式**: 使用Word尾注功能的参考文献

### 引用格式
- 文中引用: `[1]`, `[2]` 等数字引用
- 支持上标和非上标格式检测

## 错误处理

脚本包含完善的错误处理机制：

1. **文件不存在**: 检查输入文件和目录是否存在
2. **格式不支持**: 自动检测并处理不同的参考文献格式
3. **解析失败**: 提供详细的错误信息和建议
4. **部分失败**: 即使某些课题分析失败，仍会生成可用的报告

## 性能优化

- 支持大型文档的处理
- 智能文献匹配算法
- 内存优化的XML解析
- 并行处理多个课题报告

## 扩展功能

### 自定义匹配规则

可以通过配置文件自定义文献匹配的规则：

```yaml
# custom_config.yaml
reference_matching:
  similarity_threshold: 0.8  # 相似度阈值
  ignore_case: true          # 忽略大小写
  ignore_punctuation: true   # 忽略标点符号
```

### 输出格式定制

支持自定义输出报告的格式和内容：

```yaml
report_format:
  include_full_content: false  # 是否包含完整文献内容
  max_content_length: 100     # 文献内容最大显示长度
  show_similarity_score: true # 显示相似度分数
```

## 故障排除

### 常见问题

1. **找不到参考文献**
   - 检查文档格式是否正确
   - 确认参考文献部分的标题和格式
   - 尝试使用 `--verbose` 参数查看详细信息

2. **课题报告分析失败**
   - 确认课题目录结构正确
   - 检查文档是否损坏
   - 查看是否使用了特殊格式

3. **匹配结果不准确**
   - 调整相似度阈值
   - 检查文献内容的一致性
   - 手动验证匹配结果

### 调试模式

使用 `--verbose` 参数可以获得详细的调试信息：

```bash
python generate_reference_analysis.py \
    --main-report "总报告.docx" \
    --subject-reports "课题报告/" \
    --verbose
```

## 更新日志

- **v1.0.0**: 初始版本，支持基本的参考文献分析和报告生成
- 支持标准格式和尾注格式的参考文献
- 智能文献匹配和重复检测
- Markdown格式的详细报告输出

## 技术支持

如有问题或建议，请：
1. 检查本文档的故障排除部分
2. 使用 `--verbose` 参数获取详细信息
3. 查看生成的错误日志

---

*最后更新: 2026-01-06*
