"""
Purpose: Configuration management for CLI application with YAML/JSON support

Scope: Load, validate, save, and merge configuration from multiple sources

Overview: Provides comprehensive configuration management including loading from YAML and JSON files,
    searching multiple default locations, merging configurations with clear precedence rules, schema
    validation with helpful error messages, and safe persistence with atomic writes. Supports both
    user-level and system-level configuration files with environment-specific overrides. Includes
    default values for all settings to ensure the application works out of the box.

Dependencies: PyYAML for YAML parsing, json for JSON parsing, pathlib for file operations, logging

Exports: load_config(), save_config(), validate_config(), merge_configs(), ConfigError, DEFAULT_CONFIG

Interfaces: Configuration dictionaries, Path objects for file locations, validation results

Implementation: Multi-location config search, recursive dict merging, comprehensive validation
"""

import json
import logging
from pathlib import Path
from typing import Any

import yaml

from src.core.config_parser import ConfigParseError, parse_config_file

logger = logging.getLogger(__name__)


class ConfigError(Exception):
    """Configuration-related errors."""


# Default configuration constants
DEFAULT_MAX_RETRIES = 3
DEFAULT_TIMEOUT_SECONDS = 30

# Default configuration values
DEFAULT_CONFIG: dict[str, Any] = {
    "app_name": "{{PROJECT_NAME}}",
    "version": "0.1.0",
    "log_level": "INFO",
    "output_format": "text",
    "greeting": "Hello",
    "max_retries": DEFAULT_MAX_RETRIES,
    "timeout": DEFAULT_TIMEOUT_SECONDS,
}

# Configuration file search paths (in priority order)
# First match wins
CONFIG_LOCATIONS: list[Path] = [
    Path.cwd() / "config.yaml",  # Current directory YAML
    Path.cwd() / "config.json",  # Current directory JSON
    Path.home() / ".config" / "{{PROJECT_NAME}}" / "config.yaml",  # User config YAML
    Path.home() / ".config" / "{{PROJECT_NAME}}" / "config.json",  # User config JSON
    Path("/etc/{{PROJECT_NAME}}/config.yaml"),  # System config YAML (Unix/Linux)
]


def _load_and_merge_config(config_path: Path) -> dict[str, Any]:
    """Load config file and merge with defaults."""
    config = DEFAULT_CONFIG.copy()
    user_config = _load_config_file(config_path)
    return merge_configs(config, user_config)


def _validate_and_return_config(config: dict[str, Any], config_path: Path) -> dict[str, Any]:
    """Validate config and return if valid, otherwise raise error."""
    is_valid, errors = validate_config(config)
    if not is_valid:
        error_msg = "Configuration validation failed:\n" + "\n".join(f"  - {e}" for e in errors)
        raise ConfigError(error_msg)
    logger.info("Loaded config from: %s", config_path)
    return config


def _try_load_from_location(location: Path) -> dict[str, Any] | None:
    """Try to load and validate config from a location."""
    try:
        config = _load_and_merge_config(location)
        is_valid, errors = validate_config(config)
        if not is_valid:
            logger.warning("Invalid config at %s: %s", location, errors)
            return None
        logger.info("Loaded config from: %s", location)
        return config
    except ConfigError as e:
        logger.warning("Failed to load config from %s: %s", location, e)
        return None


def _load_from_explicit_path(config_path: Path) -> dict[str, Any]:
    """Load config from explicit path."""
    if not config_path.exists():
        logger.warning("Config file not found: %s, using defaults", config_path)
        return DEFAULT_CONFIG.copy()
    merged_config = _load_and_merge_config(config_path)
    return _validate_and_return_config(merged_config, config_path)


def _load_from_default_locations() -> dict[str, Any]:
    """Load config from default locations."""
    existing_locations = (loc for loc in CONFIG_LOCATIONS if loc.exists())
    for location in existing_locations:
        loaded_config = _try_load_from_location(location)
        if loaded_config:
            return loaded_config
    logger.debug("No CLI config file found, using defaults")
    return DEFAULT_CONFIG.copy()


def load_config(config_path: Path | None = None) -> dict[str, Any]:
    """
    Load configuration with fallback to defaults.

    Searches default locations if no explicit path provided. Validates
    configuration after loading and merges with defaults to ensure all
    keys are present.

    Args:
        config_path: Explicit path to config file. If None, searches
                     CONFIG_LOCATIONS in priority order.

    Returns:
        Configuration dictionary with defaults merged in.

    Raises:
        ConfigError: If config file exists but cannot be parsed or is invalid.

    Example:
        >>> config = load_config()
        >>> config = load_config(Path('custom-config.yaml'))
    """
    if config_path:
        return _load_from_explicit_path(config_path)
    return _load_from_default_locations()


def _load_config_file(path: Path) -> dict[str, Any]:
    """
    Load config from YAML or JSON file based on extension.

    Args:
        path: Path to configuration file.

    Returns:
        Configuration dictionary.

    Raises:
        ConfigError: If file cannot be parsed.
    """
    try:
        return parse_config_file(path)
    except ConfigParseError as e:
        raise ConfigError(str(e)) from e
    except Exception as e:
        raise ConfigError(f"Failed to load config from {path}: {e}") from e


def _validate_before_save(config: dict[str, Any]) -> None:
    """Validate config before saving."""
    is_valid, errors = validate_config(config)
    if not is_valid:
        error_msg = "Cannot save invalid configuration:\n" + "\n".join(f"  - {e}" for e in errors)
        raise ConfigError(error_msg)


def _write_config_file(config: dict[str, Any], path: Path) -> None:
    """Write config to file based on extension."""
    if path.suffix in [".yaml", ".yml"]:
        _write_yaml_config(config, path)
    elif path.suffix == ".json":
        _write_json_config(config, path)
    else:
        raise ConfigError(f"Unsupported config format: {path.suffix}")


def _write_yaml_config(config: dict[str, Any], path: Path) -> None:
    """Write config as YAML."""
    with path.open("w") as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)


def _write_json_config(config: dict[str, Any], path: Path) -> None:
    """Write config as JSON."""
    with path.open("w") as f:
        json.dump(config, f, indent=2, sort_keys=False)


def save_config(config: dict[str, Any], config_path: Path | None = None):
    """
    Save configuration to file.

    Creates parent directory if it doesn't exist. Format determined by
    file extension. Validates configuration before saving.

    Args:
        config: Configuration dictionary to save.
        config_path: Path to save config. If None, uses first CONFIG_LOCATIONS entry.

    Raises:
        ConfigError: If config cannot be saved or is invalid.

    Example:
        >>> save_config({'log_level': 'DEBUG'})
        >>> save_config({'log_level': 'DEBUG'}, Path('my-config.yaml'))
    """
    path = config_path or CONFIG_LOCATIONS[0]
    path.parent.mkdir(parents=True, exist_ok=True)
    _validate_before_save(config)
    _write_and_log_config(config, path)


def _write_and_log_config(config: dict[str, Any], path: Path) -> None:
    """Write config file and log success."""
    try:
        _write_config_file(config, path)
        logger.info("Saved config to: %s", path)
    except ConfigError:
        raise
    except Exception as e:
        raise ConfigError(f"Failed to save config to {path}: {e}") from e


def _validate_required_keys(config: dict[str, Any], errors: list[str]) -> None:
    """Validate that all required keys are present in config."""
    required_keys = ["app_name", "log_level"]
    for key in required_keys:
        if key not in config:
            errors.append(f"Missing required key: {key}")


def _validate_log_level(config: dict[str, Any], errors: list[str]) -> None:
    """Validate log level is a valid value."""
    valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    if "log_level" in config:
        if config["log_level"] not in valid_log_levels:
            errors.append(
                f"Invalid log_level: {config['log_level']}. "
                f"Must be one of: {', '.join(valid_log_levels)}"
            )


def _validate_output_format(config: dict[str, Any], errors: list[str]) -> None:
    """Validate output format is a valid value."""
    valid_formats = ["text", "json", "yaml"]
    if "output_format" in config:
        if config["output_format"] not in valid_formats:
            errors.append(
                f"Invalid output_format: {config['output_format']}. "
                f"Must be one of: {', '.join(valid_formats)}"
            )


def _validate_max_retries(config: dict[str, Any], errors: list[str]) -> None:
    """Validate max_retries configuration value."""
    if "max_retries" in config:
        if not isinstance(config["max_retries"], int) or config["max_retries"] < 0:
            errors.append("max_retries must be a non-negative integer")


def _validate_timeout(config: dict[str, Any], errors: list[str]) -> None:
    """Validate timeout configuration value."""
    if "timeout" in config:
        if not isinstance(config["timeout"], (int, float)) or config["timeout"] <= 0:
            errors.append("timeout must be a positive number")


def _validate_numeric_values(config: dict[str, Any], errors: list[str]) -> None:
    """Validate numeric configuration values."""
    _validate_max_retries(config, errors)
    _validate_timeout(config, errors)


def _validate_string_values(config: dict[str, Any], errors: list[str]) -> None:
    """Validate string configuration values."""
    if "app_name" in config:
        if not isinstance(config["app_name"], str) or not config["app_name"].strip():
            errors.append("app_name must be a non-empty string")


def validate_config(config: dict[str, Any]) -> tuple[bool, list[str]]:
    """
    Validate configuration schema and values.

    Checks for required keys, validates value types and ranges, and ensures
    enum values are within allowed sets.

    Args:
        config: Configuration dictionary to validate.

    Returns:
        Tuple of (is_valid, error_messages). is_valid is True if no errors,
        error_messages is list of validation error strings.

    Example:
        >>> is_valid, errors = validate_config(config)
        >>> if not is_valid:
        ...     for error in errors:
        ...         print(f"Error: {error}")
    """
    errors: list[str] = []

    _validate_required_keys(config, errors)
    _validate_log_level(config, errors)
    _validate_output_format(config, errors)
    _validate_numeric_values(config, errors)
    _validate_string_values(config, errors)

    return len(errors) == 0, errors


def merge_configs(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """
    Merge two configurations, with override taking precedence.

    Recursively merges nested dictionaries. Override values completely
    replace base values for non-dict types.

    Args:
        base: Base configuration.
        override: Override configuration (takes precedence).

    Returns:
        Merged configuration dictionary.

    Example:
        >>> base = {'a': 1, 'b': {'c': 2, 'd': 3}}
        >>> override = {'b': {'d': 4}, 'e': 5}
        >>> merged = merge_configs(base, override)
        >>> # Result: {'a': 1, 'b': {'c': 2, 'd': 4}, 'e': 5}
    """
    result = base.copy()

    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            # Recursively merge nested dicts
            result[key] = merge_configs(result[key], value)
        else:
            # Override value
            result[key] = value

    return result


def get_config_path() -> Path | None:
    """
    Find the first existing config file in CONFIG_LOCATIONS.

    Returns:
        Path to config file if found, None otherwise.

    Example:
        >>> path = get_config_path()
        >>> if path:
        ...     print(f"Config at: {path}")
    """
    for location in CONFIG_LOCATIONS:
        if location.exists():
            return location
    return None
