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
import yaml


class TestYAMLConfigLoading:
    """Test YAML configuration loading."""

    def test_load_valid_yaml_config(self, tmp_path):
        """Load valid YAML configuration from .thailint.yaml."""
        config_file = tmp_path / ".thailint.yaml"
        config_file.write_text("""
rules:
  file-placement:
    enabled: true
    config:
      layout_file: .ai/layout.yaml
""")
        from src.linter_config.loader import LinterConfigLoader

        loader = LinterConfigLoader()
        config = loader.load(config_file)

        assert config["rules"]["file-placement"]["enabled"] is True
        assert config["rules"]["file-placement"]["config"]["layout_file"] == ".ai/layout.yaml"

    def test_load_invalid_yaml_raises_error(self, tmp_path):
        """Invalid YAML raises clear error."""
        config_file = tmp_path / "bad.yaml"
        config_file.write_text("invalid: yaml: content: [")

        from src.core.config_parser import ConfigParseError
        from src.linter_config.loader import LinterConfigLoader

        loader = LinterConfigLoader()
        # ConfigParseError wraps yaml.YAMLError
        with pytest.raises((ValueError, yaml.YAMLError, ConfigParseError)):
            loader.load(config_file)

    def test_load_nonexistent_file_returns_defaults(self, tmp_path):
        """Nonexistent config file returns default configuration."""
        from src.linter_config.loader import LinterConfigLoader

        loader = LinterConfigLoader()
        config = loader.load(tmp_path / "nonexistent.yaml")

        # Should return defaults, not crash
        assert isinstance(config, dict)
        assert "rules" in config
        assert "ignore" in config

    def test_load_config_with_nested_structures(self, tmp_path):
        """Load config with deeply nested structures."""
        config_file = tmp_path / "nested.yaml"
        config_file.write_text("""
rules:
  file-placement:
    enabled: true
    config:
      directories:
        src/:
          allow:
            - "^src/.*\\\\.py$"
          deny:
            - pattern: ".*test.*"
              reason: "Tests go in tests/"
""")
        from src.linter_config.loader import LinterConfigLoader

        loader = LinterConfigLoader()
        config = loader.load(config_file)

        assert (
            config["rules"]["file-placement"]["config"]["directories"]["src/"]["allow"][0]
            == "^src/.*\\.py$"
        )
        assert (
            config["rules"]["file-placement"]["config"]["directories"]["src/"]["deny"][0]["pattern"]
            == ".*test.*"
        )


class TestJSONConfigLoading:
    """Test JSON configuration loading."""

    def test_load_valid_json_config(self, tmp_path):
        """Load valid JSON configuration from .thailint.json."""
        config_file = tmp_path / ".thailint.json"
        config_data = {
            "rules": {
                "file-placement": {"enabled": True, "config": {"layout_file": ".ai/layout.json"}}
            }
        }
        config_file.write_text(json.dumps(config_data, indent=2))

        from src.linter_config.loader import LinterConfigLoader

        loader = LinterConfigLoader()
        config = loader.load(config_file)

        assert config["rules"]["file-placement"]["enabled"] is True
        assert config["rules"]["file-placement"]["config"]["layout_file"] == ".ai/layout.json"

    def test_json_and_yaml_produce_same_result(self, tmp_path):
        """Equivalent YAML and JSON produce identical config."""
        # Create YAML version
        yaml_file = tmp_path / "config.yaml"
        yaml_file.write_text("""
rules:
  test-rule:
    enabled: false
    priority: 10
""")

        # Create JSON version
        json_file = tmp_path / "config.json"
        json_data = {"rules": {"test-rule": {"enabled": False, "priority": 10}}}
        json_file.write_text(json.dumps(json_data))

        from src.linter_config.loader import LinterConfigLoader

        loader = LinterConfigLoader()
        yaml_config = loader.load(yaml_file)
        json_config = loader.load(json_file)

        assert yaml_config == json_config

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

    def test_get_defaults_returns_valid_structure(self):
        """Default config has expected structure."""
        from src.linter_config.loader import LinterConfigLoader

        loader = LinterConfigLoader()
        defaults = loader.get_defaults()

        assert isinstance(defaults, dict)
        assert "rules" in defaults
        assert "ignore" in defaults
        assert isinstance(defaults["rules"], dict)
        assert isinstance(defaults["ignore"], list)

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
