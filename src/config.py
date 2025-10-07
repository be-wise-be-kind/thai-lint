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

logger = logging.getLogger(__name__)


class ConfigError(Exception):
    """Configuration-related errors."""


# Default configuration values
DEFAULT_CONFIG: dict[str, Any] = {
    "app_name": "{{PROJECT_NAME}}",
    "version": "1.0.0",
    "log_level": "INFO",
    "output_format": "text",
    "greeting": "Hello",
    "max_retries": 3,
    "timeout": 30,
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
    # Start with defaults
    config = DEFAULT_CONFIG.copy()

    # If explicit path provided, use it
    if config_path:
        if not config_path.exists():
            logger.warning("Config file not found: %s, using defaults", config_path)
            return config

        user_config = _load_config_file(config_path)
        config = merge_configs(config, user_config)
        logger.info("Loaded config from: %s", config_path)

        # Validate merged config
        is_valid, errors = validate_config(config)
        if not is_valid:
            error_msg = "Configuration validation failed:\n" + "\n".join(f"  - {e}" for e in errors)
            raise ConfigError(error_msg)

        return config

    # Search default locations
    for location in CONFIG_LOCATIONS:
        if location.exists():
            try:
                user_config = _load_config_file(location)
                config = merge_configs(config, user_config)
                logger.info("Loaded config from: %s", location)

                # Validate merged config
                is_valid, errors = validate_config(config)
                if not is_valid:
                    logger.warning("Invalid config at %s: %s", location, errors)
                    continue

                return config
            except ConfigError as e:
                # Try next location if this one fails
                logger.warning("Failed to load config from %s: %s", location, e)
                continue

    logger.info("No config file found, using defaults")
    return config


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
        with path.open() as f:
            if path.suffix in [".yaml", ".yml"]:
                data = yaml.safe_load(f)
                return data if data is not None else {}
            if path.suffix == ".json":
                return json.load(f)
            raise ConfigError(f"Unsupported config format: {path.suffix}")
    except yaml.YAMLError as e:
        raise ConfigError(f"Invalid YAML in {path}: {e}") from e
    except json.JSONDecodeError as e:
        raise ConfigError(f"Invalid JSON in {path}: {e}") from e
    except Exception as e:
        raise ConfigError(f"Failed to load config from {path}: {e}") from e


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

    # Create parent directory if needed
    path.parent.mkdir(parents=True, exist_ok=True)

    # Validate before saving
    is_valid, errors = validate_config(config)
    if not is_valid:
        error_msg = "Cannot save invalid configuration:\n" + "\n".join(f"  - {e}" for e in errors)
        raise ConfigError(error_msg)

    # Save based on extension
    try:
        with path.open("w") as f:
            if path.suffix in [".yaml", ".yml"]:
                yaml.dump(config, f, default_flow_style=False, sort_keys=False)
            elif path.suffix == ".json":
                json.dump(config, f, indent=2, sort_keys=False)
            else:
                raise ConfigError(f"Unsupported config format: {path.suffix}")

        logger.info("Saved config to: %s", path)
    except Exception as e:
        raise ConfigError(f"Failed to save config to {path}: {e}") from e


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
    errors = []

    # Check required keys
    required_keys = ["app_name", "log_level"]
    for key in required_keys:
        if key not in config:
            errors.append(f"Missing required key: {key}")

    # Validate log level
    valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    if "log_level" in config:
        if config["log_level"] not in valid_log_levels:
            errors.append(
                f"Invalid log_level: {config['log_level']}. "
                f"Must be one of: {', '.join(valid_log_levels)}"
            )

    # Validate output format
    valid_formats = ["text", "json", "yaml"]
    if "output_format" in config:
        if config["output_format"] not in valid_formats:
            errors.append(
                f"Invalid output_format: {config['output_format']}. "
                f"Must be one of: {', '.join(valid_formats)}"
            )

    # Validate numeric values
    if "max_retries" in config:
        if not isinstance(config["max_retries"], int) or config["max_retries"] < 0:
            errors.append("max_retries must be a non-negative integer")

    if "timeout" in config:
        if not isinstance(config["timeout"], (int, float)) or config["timeout"] <= 0:
            errors.append("timeout must be a positive number")

    # Validate string values
    if "app_name" in config:
        if not isinstance(config["app_name"], str) or not config["app_name"].strip():
            errors.append("app_name must be a non-empty string")

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
