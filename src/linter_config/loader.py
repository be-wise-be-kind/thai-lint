"""
Purpose: Multi-format configuration loader for linter settings and rule configuration

Scope: Linter configuration management supporting YAML and JSON formats

Overview: Loads linter configuration from .thailint.yaml or .thailint.json files with graceful
    fallback to sensible defaults when config files don't exist or cannot be read. Supports both
    YAML and JSON formats to accommodate different user preferences and tooling requirements,
    using format detection based on file extension. Provides unified configuration structure for
    rule settings, ignore patterns, and linter behavior across all deployment modes (CLI, library,
    Docker). Returns empty defaults (empty rules dict, empty ignore list) when config files are
    missing, allowing the linter to function without configuration. Validates file formats and
    raises clear errors with specific exception types for malformed YAML or JSON, helping users
    quickly identify and fix configuration syntax issues.

Dependencies: PyYAML for YAML parsing with safe_load(), json (stdlib) for JSON parsing,
    pathlib for file path handling

Exports: LinterConfigLoader class

Interfaces: load(config_path: Path) -> dict[str, Any] for loading config files,
    get_defaults() -> dict[str, Any] for default configuration structure

Implementation: Extension-based format detection (.yaml/.yml vs .json), yaml.safe_load()
    for security, empty dict handling for null YAML, ValueError for unsupported formats
"""

import json
from pathlib import Path
from typing import Any

import yaml


class LinterConfigLoader:
    """Load linter configuration from YAML or JSON files.

    Supports loading from .thailint.yaml, .thailint.json, or custom paths.
    Provides sensible defaults when config files don't exist.
    """

    def load(self, config_path: Path) -> dict[str, Any]:
        """Load configuration from file.

        Args:
            config_path: Path to YAML or JSON config file.

        Returns:
            Configuration dictionary.

        Raises:
            ValueError: If file format is unsupported.
            yaml.YAMLError: If YAML is malformed.
            json.JSONDecodeError: If JSON is malformed.
        """
        if not config_path.exists():
            return self.get_defaults()

        suffix = config_path.suffix.lower()

        with config_path.open(encoding="utf-8") as f:
            if suffix in [".yaml", ".yml"]:
                return yaml.safe_load(f) or {}
            if suffix == ".json":
                return json.load(f)
            raise ValueError(f"Unsupported config format: {suffix}")

    def get_defaults(self) -> dict[str, Any]:
        """Get default configuration.

        Returns:
            Default configuration with empty rules and ignore lists.
        """
        return {
            "rules": {},
            "ignore": [],
        }
