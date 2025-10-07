"""
Purpose: Test suite for file placement linter configuration loading from YAML and JSON

Scope: Configuration validation for allow/deny patterns, regex validation, and config object handling

Overview: Validates the configuration loading system that reads file placement rules from YAML/JSON
    files or config objects. Tests verify config loading from multiple formats (YAML, JSON),
    validation of regex patterns, error handling for malformed configs, fallback to defaults,
    and direct config object passing. Ensures the linter can parse placement rules correctly
    including allow patterns, deny patterns with reasons, and directory-specific configurations.
    Validates that invalid regex patterns are caught early during config load.

Dependencies: pytest for testing framework, pathlib for file creation, tmp_path fixture

Exports: TestConfigurationLoading test class with 6 tests

Interfaces: Tests FilePlacementLinter(config_file=str) and FilePlacementLinter(config_obj=dict)

Implementation: 6 tests covering JSON/YAML loading, malformed config handling, regex validation,
    defaults fallback, and inline config object support
"""

import pytest


class TestConfigurationLoading:
    """Test loading allow/deny patterns from config."""

    def test_load_json_config(self, tmp_path):
        """Load file placement rules from JSON."""
        config_file = tmp_path / "layout.json"
        config_file.write_text("""{
  "file_placement": {
    "directories": {
      "src/": {
        "allow": ["^src/.*\\\\.py$"]
      }
    }
  }
}""")
        from src.linters.file_placement import FilePlacementLinter

        linter = FilePlacementLinter(config_file=str(config_file))
        assert linter.config is not None

    def test_load_yaml_config(self, tmp_path):
        """Load file placement rules from YAML."""
        config_file = tmp_path / "layout.yaml"
        config_file.write_text("""
file_placement:
  directories:
    src/:
      allow:
        - '^src/.*\\.py$'
""")
        from src.linters.file_placement import FilePlacementLinter

        linter = FilePlacementLinter(config_file=str(config_file))
        assert linter.config is not None

    def test_handle_missing_config_file(self):
        """Missing config file falls back to defaults."""
        from src.linters.file_placement import FilePlacementLinter

        linter = FilePlacementLinter(config_file="nonexistent.yaml")
        # Should not crash, should use defaults
        assert linter is not None

    def test_handle_malformed_json(self, tmp_path):
        """Malformed JSON raises clear error."""
        config_file = tmp_path / "bad.json"
        config_file.write_text("{invalid json}")

        import json

        from src.linters.file_placement import FilePlacementLinter

        with pytest.raises(json.JSONDecodeError):  # Should raise parse error
            FilePlacementLinter(config_file=str(config_file))

    def test_validate_regex_patterns_on_load(self, tmp_path):
        """Invalid regex patterns caught on load."""
        config_file = tmp_path / "layout.yaml"
        config_file.write_text("""
file_placement:
  directories:
    src/:
      allow:
        - "[invalid(regex"
""")
        from src.linters.file_placement import FilePlacementLinter

        with pytest.raises(ValueError):  # Should catch bad regex
            FilePlacementLinter(config_file=str(config_file))

    def test_support_inline_json_object(self):
        """Support passing JSON object directly (not file path)."""
        config_obj = {"file_placement": {"directories": {"src/": {"allow": [r"^src/.*\.py$"]}}}}
        from src.linters.file_placement import FilePlacementLinter

        linter = FilePlacementLinter(config_obj=config_obj)
        assert linter.config == config_obj
