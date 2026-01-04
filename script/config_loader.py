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

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize config loader.

        Args:
            config_path: Path to configuration file. If None, uses default config.
        """
        self.config_path = config_path
        self.config: Dict[str, Any] = {}
        self.default_config_path = self._get_default_config_path()

    def _get_default_config_path(self) -> Path:
        """Get path to default configuration file."""
        script_dir = Path(__file__).parent
        project_root = script_dir.parent
        return project_root / "config" / "default.yaml"

    def load(self) -> Dict[str, Any]:
        """
        Load configuration from file.

        Returns:
            Configuration dictionary.

        Raises:
            ConfigError: If configuration file cannot be loaded or is invalid.
        """
        config_file = self.config_path if self.config_path else self.default_config_path

        if not config_file.exists():
            raise ConfigError(f"Configuration file not found: {config_file}")

        try:
            with open(config_file, "r", encoding="utf-8") as f:
                self.config = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ConfigError(f"Error parsing YAML file: {e}")
        except Exception as e:
            raise ConfigError(f"Error reading configuration file: {e}")

        if self.config is None:
            raise ConfigError("Configuration file is empty")

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

        if "checks" not in self.config:
            raise ConfigError("Configuration must contain 'checks' section")

        if not isinstance(self.config["checks"], dict):
            raise ConfigError("'checks' section must be a dictionary")

        self._validate_checks_section()
        self._validate_check_items()

    def _validate_checks_section(self):
        """Validate checks section."""
        checks = self.config["checks"]
        valid_check_names = [
            "cover",
            "table_of_contents",
            "figure_list",
            "table_list",
            "body_paragraphs",
            "body_headings",
            "captions",
            "references",
            "attachments",
            "headers",
            "footers",
            "page_numbers",
            "empty_lines",
            "consecutive_empty_lines",
        ]

        for check_name, enabled in checks.items():
            if not isinstance(enabled, bool):
                raise ConfigError(f"Check '{check_name}' must be a boolean value")

    def _validate_check_items(self):
        """Validate individual check item configurations."""
        check_items = [
            "cover",
            "table_of_contents",
            "figure_list",
            "table_list",
            "body_paragraphs",
            "body_headings",
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
        return self.config["checks"].get(check_name, False)

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

        return [name for name, enabled in self.config["checks"].items() if enabled]


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Convenience function to load configuration.

    Args:
        config_path: Path to configuration file. If None, uses default config.

    Returns:
        Configuration dictionary.

    Raises:
        ConfigError: If configuration cannot be loaded.
    """
    loader = ConfigLoader(config_path)
    return loader.load()


def get_default_config() -> Dict[str, Any]:
    """
    Get default configuration.

    Returns:
        Default configuration dictionary.

    Raises:
        ConfigError: If default configuration cannot be loaded.
    """
    loader = ConfigLoader()
    return loader.load()


if __name__ == "__main__":
    try:
        config = load_config()
        print("Configuration loaded successfully!")
        print(f"Enabled checks: {', '.join(ConfigLoader().get_all_enabled_checks())}")
    except ConfigError as e:
        print(f"Error loading configuration: {e}")
