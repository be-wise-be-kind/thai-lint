"""
Purpose: Configuration file loading for file placement linter

Scope: Handles loading and parsing of JSON/YAML configuration files

Overview: Provides configuration file loading functionality for the file placement linter.
    Supports both JSON and YAML config formats, handles path resolution relative to project
    root, and provides safe defaults when config files are missing or invalid. Isolates
    file I/O concerns from business logic to maintain single responsibility.

Dependencies: pathlib, json, yaml

Exports: ConfigLoader

Interfaces: load_config_file(config_file, project_root) -> dict

Implementation: Uses standard library JSON and PyYAML for parsing, returns empty dict on errors
"""

import json
from pathlib import Path
from typing import Any

import yaml


class ConfigLoader:
    """Loads configuration files for file placement linter."""

    def __init__(self, project_root: Path):
        """Initialize config loader.

        Args:
            project_root: Project root directory
        """
        self.project_root = project_root

    def load_config_file(self, config_file: str) -> dict[str, Any]:
        """Load configuration from file.

        Args:
            config_file: Path to config file

        Returns:
            Loaded configuration dict, or empty dict if file doesn't exist

        Raises:
            ValueError: If config file format is unsupported
        """
        config_path = self._resolve_path(config_file)
        if not config_path.exists():
            return {}
        return self._parse_file(config_path)

    def _resolve_path(self, config_file: str) -> Path:
        """Resolve config file path relative to project root.

        Args:
            config_file: Config file path (relative or absolute)

        Returns:
            Resolved absolute path
        """
        config_path = Path(config_file)
        if not config_path.is_absolute():
            config_path = self.project_root / config_path
        return config_path

    def _parse_file(self, config_path: Path) -> dict[str, Any]:
        """Parse config file based on extension.

        Args:
            config_path: Path to config file

        Returns:
            Parsed configuration dict

        Raises:
            ValueError: If file format is unsupported
        """
        with config_path.open(encoding="utf-8") as f:
            if config_path.suffix in [".yaml", ".yml"]:
                return yaml.safe_load(f) or {}
            if config_path.suffix == ".json":
                return json.load(f)
            raise ValueError(f"Unsupported config format: {config_path.suffix}")
