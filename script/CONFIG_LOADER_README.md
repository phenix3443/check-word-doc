# 配置加载模块说明

## 概述

`config_loader.py` 模块提供了配置文件加载、解析和验证功能。该模块支持从YAML格式的配置文件中加载检查规则配置。

## 主要功能

1. **配置文件加载**：从YAML文件加载配置
2. **配置验证**：验证配置文件的完整性和正确性
3. **错误处理**：提供详细的错误信息
4. **默认配置**：自动使用默认配置文件
5. **便捷访问**：提供多种方法访问配置数据

## 主要类和函数

### ConfigLoader 类

配置加载器主类，提供配置加载和访问功能。

#### 主要方法

- `load()`: 加载配置文件
- `get_check_enabled(check_name)`: 检查某个检查项是否启用
- `get_check_config(check_name)`: 获取检查项的完整配置
- `get_format_config(check_name, element_name)`: 获取格式配置
- `get_numbering_config(check_name)`: 获取编号配置
- `get_validation_config(check_name)`: 获取验证配置
- `get_consistency_config(check_name)`: 获取一致性配置
- `compile_regex_pattern(pattern)`: 编译正则表达式
- `get_all_enabled_checks()`: 获取所有启用的检查项列表

### 便捷函数

- `load_config(config_path)`: 加载配置文件（便捷函数）
- `get_default_config()`: 获取默认配置（便捷函数）

### 异常类

- `ConfigError`: 配置相关错误异常类

## 使用示例

### 基本使用

```python
from config_loader import ConfigLoader

loader = ConfigLoader()
config = loader.load()
```

### 检查检查项是否启用

```python
loader = ConfigLoader()
config = loader.load()

if loader.get_check_enabled('cover'):
    print("封面检查已启用")
```

### 获取格式配置

```python
loader = ConfigLoader()
config = loader.load()

cover_title_format = loader.get_format_config('cover', 'title')
if cover_title_format:
    font = cover_title_format.get('font')
    size = cover_title_format.get('size')
    print(f"封面标题格式: {font}, {size}号")
```

### 获取编号配置

```python
loader = ConfigLoader()
config = loader.load()

toc_numbering = loader.get_numbering_config('table_of_contents')
if toc_numbering:
    pattern_str = toc_numbering.get('format_pattern')
    pattern = loader.compile_regex_pattern(pattern_str)
    if pattern and pattern.match('1.1'):
        print("编号格式正确")
```

### 使用自定义配置文件

```python
from config_loader import ConfigLoader

custom_config_path = '/path/to/custom_config.yaml'
loader = ConfigLoader(custom_config_path)
config = loader.load()
```

### 使用便捷函数

```python
from config_loader import load_config, get_default_config

config = get_default_config()
# 或
config = load_config('/path/to/config.yaml')
```

## 配置验证

模块会自动验证以下内容：

1. **基本结构**：配置文件必须是有效的字典结构
2. **检查项开关**：`checks` 部分必须存在且为字典
3. **检查项配置**：每个检查项的配置必须是字典
4. **数据类型**：验证配置值的数据类型（如布尔值、字符串等）

## 错误处理

模块使用 `ConfigError` 异常类来处理配置相关错误：

```python
from config_loader import ConfigLoader, ConfigError

try:
    loader = ConfigLoader()
    config = loader.load()
except ConfigError as e:
    print(f"配置错误: {e}")
except Exception as e:
    print(f"其他错误: {e}")
```

## 测试

运行测试脚本验证模块功能：

```bash
python3 script/test_config_loader.py
```

## 依赖

- Python 3.8+
- PyYAML >= 6.0

本项目使用 Poetry 进行依赖管理。安装依赖：

```bash
poetry install
```

或者激活虚拟环境后运行：

```bash
poetry shell
```

更多安装说明请参考项目根目录的 `INSTALL.md` 文件。

