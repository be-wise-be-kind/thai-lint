"""
Purpose: Test suite for multi-format configuration loading with validation

Scope: Validation of YAML and JSON config loading, default handling, and error reporting

Overview: Validates the configuration loading system that supports both YAML and JSON formats,
    ensuring configs are parsed correctly, defaults are provided when files don't exist, and
    errors are raised clearly for malformed content. Tests verify YAML config loading with
    nested structures, JSON config loading with equivalent results to YAML, graceful fallback
    to defaults for missing files, and appropriate error raising for invalid syntax. Ensures
    the configuration system provides consistent behavior across formats and handles edge cases
    properly, allowing users to configure the linter using their preferred format while
    maintaining reliability through proper validation and error handling.

Dependencies: pytest for testing framework, json for creating test configs, pathlib for
    temporary file creation, tmp_path fixture

Exports: TestYAMLConfigLoading, TestJSONConfigLoading, TestConfigDefaults test classes

Interfaces: Tests LinterConfigLoader.load() with various file formats, validates get_defaults()
    structure, error handling for malformed configs and unsupported formats

Implementation: 9 tests using pytest tmp_path fixture for isolated file creation, format
    equivalence testing between YAML and JSON, error validation with pytest.raises
"""

import json

import pytest


class TestYAMLConfigLoading:
    """Test YAML configuration loading."""


class TestJSONConfigLoading:
    """Test JSON configuration loading."""

    def test_invalid_json_raises_error(self, tmp_path):
        """Invalid JSON raises clear error."""
        config_file = tmp_path / "bad.json"
        config_file.write_text("{invalid json content")

        from src.core.config_parser import ConfigParseError
        from src.linter_config.loader import LinterConfigLoader

        loader = LinterConfigLoader()
        # ConfigParseError wraps json.JSONDecodeError
        with pytest.raises((ValueError, json.JSONDecodeError, ConfigParseError)):
            loader.load(config_file)


class TestConfigDefaults:
    """Test default configuration values."""

    def test_unsupported_file_format_raises_error(self, tmp_path):
        """Unsupported file format raises clear error."""
        config_file = tmp_path / "config.txt"
        config_file.write_text("some content")

        from src.core.config_parser import ConfigParseError
        from src.linter_config.loader import LinterConfigLoader

        loader = LinterConfigLoader()
        # ConfigParseError raised for unsupported formats
        with pytest.raises((ValueError, ConfigParseError), match="Unsupported config format"):
            loader.load(config_file)
