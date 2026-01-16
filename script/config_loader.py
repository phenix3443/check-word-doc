#!/usr/bin/env python3
"""
Configuration file loading and parsing module.
"""

import yaml
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
import re


class ConfigError(Exception):
    """Configuration error exception."""

    pass


class ConfigLoader:
    """Configuration loader and validator."""

    def __init__(self, config_path: str):
        """
        Initialize config loader.

        Args:
            config_path: Path to configuration file (required).
                         Must be provided when calling load().
        """
        if not config_path:
            raise ConfigError("config_path is required and cannot be None or empty")
        self.config_path = config_path
        self.config: Dict[str, Any] = {}

    def _get_example_config_path(self) -> Path:
        """Get path to example configuration file."""
        script_dir = Path(__file__).parent
        project_root = script_dir.parent
        return project_root / "config" / "example.yaml"

    def _get_basic_config_path(self) -> Path:
        """Get path to basic configuration file."""
        script_dir = Path(__file__).parent
        project_root = script_dir.parent
        return project_root / "config" / "base.yaml"

    def _resolve_import_path(self, import_path: str, current_file: Path) -> Path:
        """
        Resolve import path relative to current file only.

        Args:
            import_path: Import path (e.g., "base.yaml" or "../config/base.yaml")
            current_file: Path to the current YAML file

        Returns:
            Resolved absolute path

        Raises:
            ConfigError: If import file is not found relative to current file
        """
        if Path(import_path).is_absolute():
            resolved = Path(import_path)
            if not resolved.exists():
                raise ConfigError(f"Import file not found: {import_path}")
            return resolved.resolve()

        # Only try relative to current file (strict mode)
        relative_to_file = current_file.parent / import_path
        if relative_to_file.exists():
            return relative_to_file.resolve()

        # If not found, raise error
        raise ConfigError(
            f"Import file not found: {import_path} "
            f"(searched relative to {current_file.parent}). "
            f"Please use a relative path from the current file or an absolute path."
        )

    def _load_yaml_with_imports(
        self, file_path: Path, loaded_files: Optional[set] = None
    ) -> Dict[str, Any]:
        """
        Load YAML file and handle imports.

        Args:
            file_path: Path to YAML file
            loaded_files: Set of already loaded files to prevent circular imports

        Returns:
            Loaded configuration dictionary
        """
        if loaded_files is None:
            loaded_files = set()

        file_path = file_path.resolve()

        # Prevent circular imports
        if str(file_path) in loaded_files:
            raise ConfigError(f"Circular import detected: {file_path}")

        loaded_files.add(str(file_path))

        if not file_path.exists():
            raise ConfigError(f"Configuration file not found: {file_path}")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ConfigError(f"Error parsing YAML file {file_path}: {e}")
        except Exception as e:
            raise ConfigError(f"Error reading configuration file {file_path}: {e}")

        if config is None:
            raise ConfigError(f"Configuration file is empty: {file_path}")

        # Handle imports
        if isinstance(config, dict) and "import" in config:
            import_paths = config["import"]
            if isinstance(import_paths, str):
                import_paths = [import_paths]

            # Load imported files first
            imported_config = {}
            for import_path in import_paths:
                resolved_path = self._resolve_import_path(import_path, file_path)
                imported = self._load_yaml_with_imports(resolved_path, loaded_files)
                imported_config = self._deep_merge(imported_config, imported)

            # Remove import key and merge with imported config
            config_without_import = {k: v for k, v in config.items() if k != "import"}
            config = self._deep_merge(imported_config, config_without_import)

        loaded_files.remove(str(file_path))
        return config

    def _deep_merge(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deep merge two dictionaries, with override taking precedence.

        Args:
            base: Base dictionary
            override: Override dictionary

        Returns:
            Merged dictionary
        """
        result = base.copy()
        for key, value in override.items():
            # 对于列表类型的配置项，进行合并（追加）而不是覆盖
            # 适用于：rules, classifiers, styles（如果是列表）
            if key in ["rules", "classifiers"] and isinstance(result.get(key), list) and isinstance(value, list):
                result[key] = list(result.get(key) or []) + list(value or [])
                continue
            # 对于字典类型，递归合并
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                # 其他情况直接覆盖
                result[key] = value
        return result

    def load(self) -> Dict[str, Any]:
        """
        Load configuration from file.
        Supports YAML import syntax: add "import: base.yaml" at the top of config file.
        Configuration file path must be provided via config_path parameter.

        Returns:
            Configuration dictionary.

        Raises:
            ConfigError: If configuration file path is not provided or file cannot be loaded or is invalid.
        """
        if not self.config_path:
            raise ConfigError(
                "Configuration file path is required. Please specify a config file using --config option."
            )

        config_file = Path(self.config_path)
        if not config_file.exists():
            raise ConfigError(f"Configuration file not found: {config_file}")

        self.config = self._load_yaml_with_imports(config_file)
        self._validate_config()
        self._apply_extensions()
        return self.config
    
    def _apply_extensions(self):
        """应用配置中的扩展设置（自定义字号、对齐方式等）"""
        document_config = self.config.get('document', {})
        
        # 应用自定义字号别名
        if 'font_size_aliases' in document_config:
            from script.utils.unit_converter import UnitConverter
            for alias, pt in document_config['font_size_aliases'].items():
                UnitConverter.register_font_size_alias(alias, pt)
        
        # 应用自定义对齐方式别名
        if 'alignment_aliases' in document_config:
            from script.core.style_checker import StyleChecker
            from docx.enum.text import WD_ALIGN_PARAGRAPH
            
            # 对齐方式枚举映射
            alignment_enums = {
                'CENTER': WD_ALIGN_PARAGRAPH.CENTER,
                'LEFT': WD_ALIGN_PARAGRAPH.LEFT,
                'RIGHT': WD_ALIGN_PARAGRAPH.RIGHT,
                'JUSTIFY': WD_ALIGN_PARAGRAPH.JUSTIFY,
                'DISTRIBUTE': WD_ALIGN_PARAGRAPH.DISTRIBUTE,
            }
            
            for alias, enum_name in document_config['alignment_aliases'].items():
                if enum_name in alignment_enums:
                    StyleChecker.register_alignment_alias(alias, alignment_enums[enum_name])
        
        # 应用字符宽度比例
        if 'char_width_ratio' in document_config:
            from script.utils.unit_converter import UnitConverter
            UnitConverter.set_char_width_ratio(document_config['char_width_ratio'])
        
        # 应用行高比例
        if 'line_height_ratio' in document_config:
            from script.utils.unit_converter import UnitConverter
            UnitConverter.set_line_height_ratio(document_config['line_height_ratio'])

    def _validate_config(self):
        """
        Validate declarative configuration structure.

        Raises:
            ConfigError: If configuration is invalid.
        """
        if not isinstance(self.config, dict):
            raise ConfigError("Configuration must be a dictionary")

        # 必须包含 document 节
        if "document" not in self.config:
            raise ConfigError(
                "配置文件必须使用声明式格式（包含 'document' 节）。\n"
                "请参考 config/data_paper_declarative.yaml 示例。"
            )

        document_config = self.config.get("document", {})
        if not isinstance(document_config, dict):
            raise ConfigError("'document' section must be a dictionary")

        # 验证 classifiers（可选）
        if "classifiers" in document_config:
            self._validate_classifiers(document_config["classifiers"])
        
        # 验证 styles（可选）
        if "styles" in document_config:
            self._validate_styles(document_config["styles"])
        
        # 验证 defaults（可选）
        if "defaults" in document_config:
            if not isinstance(document_config["defaults"], dict):
                raise ConfigError("'document.defaults' must be a dictionary")

        # Optional: validate legacy structure
        if "structure" in document_config:
            structure = document_config["structure"]
            if not isinstance(structure, list):
                raise ConfigError("'document.structure' must be a list")
    
    def _validate_classifiers(self, classifiers: Any):
        """验证 classifiers 配置
        
        Args:
            classifiers: classifiers 配置
            
        Raises:
            ConfigError: 如果格式不正确
        """
        if not isinstance(classifiers, list):
            raise ConfigError("'document.classifiers' must be a list")
        
        for i, rule in enumerate(classifiers):
            if not isinstance(rule, dict):
                raise ConfigError(f"Classifier rule {i} must be a dictionary")
            
            if "class" not in rule:
                raise ConfigError(f"Classifier rule {i} must have a 'class' field")
            
            if "match" not in rule:
                raise ConfigError(f"Classifier rule {i} must have a 'match' field")
            
            if not isinstance(rule["match"], dict):
                raise ConfigError(f"Classifier rule {i}: 'match' must be a dictionary")
            
            # 验证 position 字段（如果存在）
            match_config = rule["match"]
            if "position" in match_config:
                self._validate_position(match_config["position"], f"Classifier rule {i} (class: {rule['class']})")
            
            # 验证 children 规则（如果存在）
            if "children" in rule:
                if not isinstance(rule["children"], list):
                    raise ConfigError(f"Classifier rule {i} (class: {rule['class']}): 'children' must be a list")
                
                for j, child_rule in enumerate(rule["children"]):
                    if not isinstance(child_rule, dict):
                        raise ConfigError(f"Classifier rule {i} (class: {rule['class']}): child rule {j} must be a dictionary")
                    
                    if "class" not in child_rule:
                        raise ConfigError(f"Classifier rule {i} (class: {rule['class']}): child rule {j} must have a 'class' field")
                    
                    if "match" not in child_rule:
                        raise ConfigError(f"Classifier rule {i} (class: {rule['class']}): child rule {j} must have a 'match' field")
                    
                    if not isinstance(child_rule["match"], dict):
                        raise ConfigError(f"Classifier rule {i} (class: {rule['class']}): child rule {j}: 'match' must be a dictionary")
                    
                    # 验证子规则的 position
                    if "position" in child_rule["match"]:
                        self._validate_position(
                            child_rule["match"]["position"],
                            f"Classifier rule {i} (class: {rule['class']}), child rule {j} (class: {child_rule['class']})"
                        )
    
    def _validate_position(self, position: Any, context: str):
        """验证 position 配置
        
        Args:
            position: position 配置
            context: 上下文信息（用于错误消息）
            
        Raises:
            ConfigError: 如果格式不正确
        """
        # 新语法：position 是一个对象 { type, index/class }
        if isinstance(position, dict):
            if "type" not in position:
                raise ConfigError(f"{context}: position 对象必须包含 'type' 字段")
            
            pos_type = position["type"]
            
            # 验证 type 字段
            if pos_type not in ["absolute", "relative", "after", "before"]:
                raise ConfigError(
                    f"{context}: position.type 必须是 'absolute', 'relative', 'after' 或 'before'，"
                    f"当前值为 '{pos_type}'"
                )
            
            # 根据 type 验证必需字段
            if pos_type in ["absolute", "relative"]:
                if "index" not in position:
                    raise ConfigError(f"{context}: position 对象（type={pos_type}）必须包含 'index' 字段")
            elif pos_type in ["after", "before"]:
                if "class" not in position:
                    raise ConfigError(f"{context}: position 对象（type={pos_type}）必须包含 'class' 字段")
            
            # 验证 index 或 class 字段（根据 type）
            if pos_type in ["absolute", "relative"]:
                pos_index = position["index"]
            
            if pos_type == "absolute":
                # 绝对定位：index 应该是数字或 first/last
                if not isinstance(pos_index, (int, str)):
                    raise ConfigError(
                        f"{context}: position.index (absolute) 必须是数字或字符串 (first/last)，"
                        f"当前类型为 {type(pos_index).__name__}"
                    )
                if isinstance(pos_index, str) and pos_index not in ["first", "last"]:
                    # 允许数字字符串
                    try:
                        int(pos_index)
                    except ValueError:
                        raise ConfigError(
                            f"{context}: position.index (absolute) 字符串值必须是 'first', 'last' 或数字，"
                            f"当前值为 '{pos_index}'"
                        )
            
            elif pos_type == "relative":
                # 相对定位：index 可以是 first/last 或区间表达式
                if not isinstance(pos_index, (int, str)):
                    raise ConfigError(
                        f"{context}: position.index (relative) 必须是数字或字符串，"
                        f"当前类型为 {type(pos_index).__name__}"
                    )
                
                if isinstance(pos_index, str):
                    # 检查是否是有效的相对位置或区间表达式
                    if pos_index not in ["first", "last"]:
                        # 检查是否是区间表达式
                        if not any(c in pos_index for c in '()[]'):
                            # 不是区间表达式，尝试作为数字
                            try:
                                int(pos_index)
                            except ValueError:
                                raise ConfigError(
                                    f"{context}: position.index (relative) 字符串值必须是 "
                                    f"'first', 'last', 数字，或区间表达式 (如 '(first, last)')，"
                                    f"当前值为 '{pos_index}'"
                                )
        
        # 旧语法：position 是一个简单值（向后兼容，不验证）
        # 允许任何类型的简单值
    
    def _validate_styles(self, styles: Any):
        """验证 styles 配置
        
        Args:
            styles: styles 配置
            
        Raises:
            ConfigError: 如果格式不正确
        """
        if not isinstance(styles, dict):
            raise ConfigError("'document.styles' must be a dictionary")
        
        for class_selector, style_def in styles.items():
            # 检查 class 选择器格式（应该以 . 开头）
            if not class_selector.startswith('.'):
                raise ConfigError(
                    f"Style selector '{class_selector}' must start with '.' (e.g., '.title')"
                )
            
            if not isinstance(style_def, dict):
                raise ConfigError(f"Style definition for '{class_selector}' must be a dictionary")
            
            # 验证字体和段落配置（如果存在）
            if "font" in style_def and not isinstance(style_def["font"], dict):
                raise ConfigError(f"'{class_selector}.font' must be a dictionary")
            
            if "paragraph" in style_def and not isinstance(style_def["paragraph"], dict):
                raise ConfigError(f"'{class_selector}.paragraph' must be a dictionary")


def load_config(config_path: str) -> Dict[str, Any]:
    """
    Convenience function to load configuration.

    Args:
        config_path: Path to configuration file (required).

    Returns:
        Configuration dictionary.

    Raises:
        ConfigError: If configuration cannot be loaded.
    """
    if not config_path:
        raise ConfigError("config_path is required and cannot be None or empty")
    loader = ConfigLoader(config_path)
    return loader.load()


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python config_loader.py <config_file_path>")
        print("Example: python config_loader.py config/example.yaml")
        sys.exit(1)

    try:
        config_path = sys.argv[1]
        loader = ConfigLoader(config_path)
        config = loader.load()
        print("Configuration loaded successfully!")
        print(f"Enabled checks: {', '.join(loader.get_all_enabled_checks())}")
    except ConfigError as e:
        print(f"Error loading configuration: {e}")
        sys.exit(1)
