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
            if key == "rules" and isinstance(result.get(key), list) and isinstance(value, list):
                result[key] = list(result.get(key) or []) + list(value or [])
                continue
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
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
        return self.config

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
