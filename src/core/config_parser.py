"""
Purpose: Shared YAML/JSON configuration file parsing utilities

Scope: Common parsing logic for configuration files across the project

Overview: Provides reusable utilities for parsing YAML and JSON configuration files with
    consistent error handling and format detection. Eliminates duplication between src/config.py
    and src/linter_config/loader.py by centralizing the parsing logic in one place. Supports
    extension-based format detection (.yaml, .yml, .json), safe YAML loading with yaml.safe_load(),
    and proper null handling. Returns empty dictionaries for null YAML content to ensure consistent
    behavior across all config loaders.

Dependencies: PyYAML for YAML parsing, json (stdlib) for JSON parsing, pathlib for file operations

Exports: parse_config_file(), parse_yaml(), parse_json()

Interfaces: parse_config_file(path: Path) -> dict[str, Any] for extension-based parsing,
    parse_yaml(file_obj, path: Path) -> dict[str, Any] for YAML parsing,
    parse_json(file_obj, path: Path) -> dict[str, Any] for JSON parsing

Implementation: yaml.safe_load() for security, json.load() for JSON, ConfigParseError for errors
"""

import json
from pathlib import Path
from typing import Any, TextIO

import yaml


class ConfigParseError(Exception):
    """Configuration file parsing errors."""


def parse_yaml(file_obj: TextIO, path: Path) -> dict[str, Any]:
    """Parse YAML file content.

    Args:
        file_obj: Open file object to read from.
        path: Path to file (for error messages).

    Returns:
        Parsed YAML data as dictionary.

    Raises:
        ConfigParseError: If YAML is malformed.
    """
    try:
        data = yaml.safe_load(file_obj)
        return data if data is not None else {}
    except yaml.YAMLError as e:
        raise ConfigParseError(f"Invalid YAML in {path}: {e}") from e


def parse_json(file_obj: TextIO, path: Path) -> dict[str, Any]:
    """Parse JSON file content.

    Args:
        file_obj: Open file object to read from.
        path: Path to file (for error messages).

    Returns:
        Parsed JSON data as dictionary.

    Raises:
        ConfigParseError: If JSON is malformed.
    """
    try:
        result: dict[str, Any] = json.load(file_obj)
        return result
    except json.JSONDecodeError as e:
        raise ConfigParseError(f"Invalid JSON in {path}: {e}") from e


def _normalize_config_keys(config: dict[str, Any]) -> dict[str, Any]:
    """Normalize configuration keys from hyphens to underscores.

    Converts top-level keys like "magic-numbers" to "magic_numbers" to match
    internal linter expectations while maintaining backward compatibility with
    both formats in config files.

    Args:
        config: Configuration dictionary with potentially hyphenated keys

    Returns:
        Configuration dictionary with normalized (underscored) keys
    """
    normalized = {}
    for key, value in config.items():
        # Replace hyphens with underscores in keys
        normalized_key = key.replace("-", "_")
        normalized[normalized_key] = value
    return normalized


def parse_config_file(path: Path, encoding: str = "utf-8") -> dict[str, Any]:
    """Parse configuration file based on extension.

    Supports .yaml, .yml, and .json formats. Automatically detects format
    from file extension and uses appropriate parser. Normalizes hyphenated
    keys (e.g., "magic-numbers") to underscored keys (e.g., "magic_numbers")
    for internal consistency.

    Args:
        path: Path to configuration file.
        encoding: File encoding (default: utf-8).

    Returns:
        Parsed configuration dictionary with normalized keys.

    Raises:
        ConfigParseError: If file format is unsupported or parsing fails.
    """
    suffix = path.suffix.lower()

    if suffix not in [".yaml", ".yml", ".json"]:
        raise ConfigParseError(f"Unsupported config format: {suffix}")

    with path.open(encoding=encoding) as f:
        if suffix in [".yaml", ".yml"]:
            config = parse_yaml(f, path)
        else:
            config = parse_json(f, path)

    # Normalize keys from hyphens to underscores
    return _normalize_config_keys(config)
