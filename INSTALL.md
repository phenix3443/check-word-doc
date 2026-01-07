# 安装说明

## 前置要求

本项目使用 Poetry 进行依赖管理。请先安装 Poetry：

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

或者使用 pip：

```bash
pip install poetry
```

更多安装方法请参考 [Poetry 官方文档](https://python-poetry.org/docs/#installation)。

## 依赖安装

### 方法1：使用 Poetry 安装（推荐）

```bash
poetry install
```

这将安装所有依赖项，包括开发依赖。

### 方法2：仅安装生产依赖

```bash
poetry install --no-dev
```

### 方法3：使用 Poetry 虚拟环境

Poetry 会自动创建和管理虚拟环境。激活虚拟环境：

```bash
poetry shell
```

或者在不激活虚拟环境的情况下运行命令：

```bash
poetry run python test/config_loader.py
```

## 项目依赖

项目依赖定义在 `pyproject.toml` 文件中：

- **PyYAML >= 6.0** - YAML 配置文件解析

### 添加新依赖

```bash
poetry add <package-name>
```

### 添加开发依赖

```bash
poetry add --group dev <package-name>
```

### 更新依赖

```bash
poetry update
```

## 验证安装

运行测试脚本验证配置加载模块：

```bash
poetry run python test/config_loader.py
```

或者先激活虚拟环境：

```bash
poetry shell
python test/config_loader.py
```

如果所有测试通过，说明安装成功。

## 其他 Poetry 命令

### 查看依赖树

```bash
poetry show --tree
```

### 导出依赖（如果需要）

```bash
poetry export -f requirements.txt --output requirements.txt --without-hashes
```

### 锁定依赖版本

```bash
poetry lock
```
