"""
Purpose: Multi-format configuration loader for linter settings and rule configuration

Scope: Linter configuration management supporting YAML, JSON, and pyproject.toml formats

Overview: Loads linter configuration from .thailint.yaml, .thailint.json, or pyproject.toml
    [tool.thailint] section with graceful fallback to sensible defaults when config files don't
    exist or cannot be read. Supports YAML, JSON, and TOML formats to accommodate different user
    preferences and tooling requirements, using format detection based on file extension. Provides
    unified configuration structure for rule settings, ignore patterns, and linter behavior across
    all deployment modes (CLI, library, Docker). Returns empty defaults (empty rules dict, empty
    ignore list) when config files are missing, allowing the linter to function without
    configuration. Validates file formats and raises clear errors with specific exception types
    for malformed YAML, JSON, or TOML, helping users quickly identify and fix configuration
    syntax issues.

Dependencies: PyYAML for YAML parsing with safe_load(), json (stdlib) for JSON parsing,
    tomllib (stdlib) for TOML parsing via config_parser, pathlib for file path handling

Exports: load_config function, get_defaults function, LinterConfigLoader class (compat)

Interfaces: load_config(config_path: Path) -> dict[str, Any] for loading config files,
    get_defaults() -> dict[str, Any] for default configuration structure

Implementation: Extension-based format detection (.yaml/.yml vs .json), yaml.safe_load()
    for security, empty dict handling for null YAML, pyproject.toml fallback via
    parse_pyproject_toml(), ValueError for unsupported formats
"""

from pathlib import Path
from typing import Any

from src.core.config_parser import ConfigParseError, parse_config_file, parse_pyproject_toml


def get_defaults() -> dict[str, Any]:
    """Get default configuration.

    Returns:
        Default configuration with empty rules and ignore lists.
    """
    return {
        "rules": {},
        "ignore": [],
    }


def load_config(config_path: Path) -> dict[str, Any]:
    """Load configuration from file.

    Falls back to pyproject.toml [tool.thailint] in the same directory
    if the given config_path does not exist.

    Args:
        config_path: Path to YAML or JSON config file.

    Returns:
        Configuration dictionary.

    Raises:
        ConfigParseError: If file format is unsupported or parsing fails.
    """
    if not config_path.exists():
        pyproject_path = config_path.parent / "pyproject.toml"
        try:
            config = parse_pyproject_toml(pyproject_path)
        except ConfigParseError:
            return get_defaults()
        return config if config else get_defaults()

    return parse_config_file(config_path)


# Legacy class wrapper for backward compatibility
class LinterConfigLoader:
    """Load linter configuration from YAML or JSON files.

    Supports loading from .thailint.yaml, .thailint.json, or custom paths.
    Provides sensible defaults when config files don't exist.

    Note: This class is a thin wrapper around module-level functions
    for backward compatibility.
    """

    def __init__(self) -> None:
        """Initialize the loader."""
        pass  # No state needed

    def load(self, config_path: Path) -> dict[str, Any]:
        """Load configuration from file.

        Args:
            config_path: Path to YAML or JSON config file.

        Returns:
            Configuration dictionary.

        Raises:
            ConfigParseError: If file format is unsupported or parsing fails.
        """
        return load_config(config_path)

    @property
    def defaults(self) -> dict[str, Any]:
        """Default configuration.

        Returns:
            Default configuration with empty rules and ignore lists.
        """
        return get_defaults()
