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

    def _deep_merge(
        self, base: Dict[str, Any], override: Dict[str, Any]
    ) -> Dict[str, Any]:
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
            if (
                key in result
                and isinstance(result[key], dict)
                and isinstance(value, dict)
            ):
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
        Validate configuration structure.

        Raises:
            ConfigError: If configuration is invalid.
        """
        if not isinstance(self.config, dict):
            raise ConfigError("Configuration must be a dictionary")

        if "rules" not in self.config and "checks" not in self.config:
            raise ConfigError("Configuration must contain 'rules' section")

        if "rules" in self.config and not isinstance(self.config["rules"], list):
            raise ConfigError("'rules' section must be a list")

        if "checks" in self.config and not isinstance(self.config["checks"], (list, dict)):
            raise ConfigError("'checks' section must be a list or dictionary")

        if "checks" in self.config:
            self._validate_checks_section()
            self._validate_check_items()

    def _validate_checks_section(self):
        """Validate checks section."""
        checks = self.config["checks"]
        valid_check_names = [
            "structure",
            "cover",
            "table_of_contents",
            "figure_list",
            "table_list",
            "paragraphs",
            "headings",
            "captions",
            "references",
            "attachments",
            "headers",
            "footers",
            "page_numbers",
        ]

        if not isinstance(checks, list):
            raise ConfigError("'checks' section must be a list")

        for check_name in checks:
            if not isinstance(check_name, str):
                raise ConfigError(
                    f"Check item must be a string, got {type(check_name)}"
                )
            if check_name not in valid_check_names:
                raise ConfigError(
                    f"Invalid check name: '{check_name}'. Valid names: {', '.join(valid_check_names)}"
                )

    def _validate_check_items(self):
        """Validate individual check item configurations."""
        check_items = [
            "structure",
            "cover",
            "table_of_contents",
            "figure_list",
            "table_list",
            "paragraphs",
            "headings",
            "captions",
            "references",
            "attachments",
            "headers",
            "footers",
            "page_numbers",
            "empty_lines",
        ]

        for item_name in check_items:
            if item_name in self.config:
                item_config = self.config[item_name]
                if not isinstance(item_config, dict):
                    raise ConfigError(f"Check item '{item_name}' must be a dictionary")

                if "enabled" in item_config:
                    if not isinstance(item_config["enabled"], bool):
                        raise ConfigError(f"'{item_name}.enabled' must be a boolean")

    def get_check_enabled(self, check_name: str) -> bool:
        """
        Check if a specific check is enabled.

        Args:
            check_name: Name of the check.

        Returns:
            True if check is enabled, False otherwise.
        """
        if "checks" not in self.config:
            return False
        checks = self.config["checks"]
        # Support both list and dict formats for backward compatibility
        if isinstance(checks, list):
            return check_name in checks
        elif isinstance(checks, dict):
            return checks.get(check_name, False)
        else:
            return False

    def get_check_config(self, check_name: str) -> Optional[Dict[str, Any]]:
        """
        Get configuration for a specific check.

        Args:
            check_name: Name of the check.

        Returns:
            Configuration dictionary for the check, or None if not found.
        """
        return self.config.get(check_name)

    def get_format_config(
        self, check_name: str, element_name: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get format configuration for a check item.

        Args:
            check_name: Name of the check item.
            element_name: Optional element name (e.g., 'title' for cover).

        Returns:
            Format configuration dictionary, or None if not found.
        """
        check_config = self.get_check_config(check_name)
        if not check_config:
            return None

        format_config = check_config.get("format")
        if not format_config:
            return None

        if element_name:
            return format_config.get(element_name)

        return format_config

    def get_numbering_config(self, check_name: str) -> Optional[Dict[str, Any]]:
        """
        Get numbering configuration for a check item.

        Args:
            check_name: Name of the check item.

        Returns:
            Numbering configuration dictionary, or None if not found.
        """
        check_config = self.get_check_config(check_name)
        if not check_config:
            return None

        return check_config.get("numbering")

    def get_validation_config(self, check_name: str) -> Optional[Dict[str, Any]]:
        """
        Get validation configuration for a check item.

        Args:
            check_name: Name of the check item.

        Returns:
            Validation configuration dictionary, or None if not found.
        """
        check_config = self.get_check_config(check_name)
        if not check_config:
            return None

        return check_config.get("validation")

    def get_consistency_config(self, check_name: str) -> Optional[Dict[str, Any]]:
        """
        Get consistency configuration for a check item.

        Args:
            check_name: Name of the check item.

        Returns:
            Consistency configuration dictionary, or None if not found.
        """
        check_config = self.get_check_config(check_name)
        if not check_config:
            return None

        return check_config.get("consistency")

    def compile_regex_pattern(self, pattern: str) -> Optional[re.Pattern]:
        """
        Compile a regex pattern from configuration.

        Args:
            pattern: Regular expression pattern string.

        Returns:
            Compiled regex pattern, or None if pattern is invalid.
        """
        try:
            return re.compile(pattern)
        except re.error:
            return None

    def get_all_enabled_checks(self) -> List[str]:
        """
        Get list of all enabled check names.

        Returns:
            List of enabled check names.
        """
        if "checks" not in self.config:
            return []

        checks = self.config["checks"]
        # Support both list and dict formats for backward compatibility
        if isinstance(checks, list):
            return list(checks)
        elif isinstance(checks, dict):
            return [name for name, enabled in checks.items() if enabled]
        else:
            return []


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
