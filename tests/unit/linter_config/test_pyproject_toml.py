"""
Purpose: Test suite for pyproject.toml [tool.thailint] configuration loading

Scope: Validation of TOML config parsing, fallback behavior, and precedence rules

Overview: Validates that linter configuration can be loaded from pyproject.toml under the
    [tool.thailint] section as a fallback when .thailint.yaml or .thailint.json files are not
    present. Tests cover parsing valid TOML config, handling missing [tool.thailint] sections,
    verifying that .thailint.yaml takes precedence over pyproject.toml, and ensuring key
    normalization (hyphens to underscores) works for TOML-sourced config. Also tests error
    handling for malformed TOML files.

Dependencies: pytest for testing framework, pathlib for temporary file creation, tmp_path fixture

Exports: TestPyprojectTomlParsing, TestPyprojectTomlFallback test classes

Interfaces: Tests parse_pyproject_toml() directly and load_config() fallback behavior

Implementation: Uses pytest tmp_path fixture for isolated file creation, validates precedence
    of .thailint.yaml over pyproject.toml, tests key normalization for hyphenated TOML keys
"""

import pytest

from src.core.config_parser import ConfigParseError, parse_pyproject_toml
from src.linter_config.loader import get_defaults, load_config


class TestPyprojectTomlParsing:
    """Test direct parsing of pyproject.toml [tool.thailint] section."""

    def test_parses_thailint_section(self, tmp_path):
        """Valid [tool.thailint] section is parsed correctly."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text(
            "[tool.thailint]\n"
            "dry = {enabled = true, min_duplicate_lines = 4}\n"
            "nesting = {enabled = true, max_nesting_depth = 3}\n"
        )

        result = parse_pyproject_toml(pyproject)

        assert result["dry"] == {"enabled": True, "min_duplicate_lines": 4}
        assert result["nesting"] == {"enabled": True, "max_nesting_depth": 3}

    def test_missing_thailint_section_returns_empty(self, tmp_path):
        """pyproject.toml without [tool.thailint] returns empty dict."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text('[project]\nname = "myproject"\nversion = "1.0.0"\n')

        result = parse_pyproject_toml(pyproject)

        assert result == {}

    def test_missing_tool_section_returns_empty(self, tmp_path):
        """pyproject.toml without [tool] section returns empty dict."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text('[project]\nname = "myproject"\n')

        result = parse_pyproject_toml(pyproject)

        assert result == {}

    def test_normalizes_hyphenated_keys(self, tmp_path):
        """Hyphenated top-level keys are normalized to underscores.

        Note: Only top-level keys are normalized (consistent with YAML/JSON).
        Nested keys like allowed-numbers remain unchanged.
        """
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text(
            "[tool.thailint]\nmagic-numbers = {enabled = true, allowed-numbers = [-1, 0, 1]}\n"
        )

        result = parse_pyproject_toml(pyproject)

        assert "magic_numbers" in result
        assert "magic-numbers" not in result
        # Nested keys are NOT normalized (consistent with YAML/JSON behavior)
        assert "allowed-numbers" in result["magic_numbers"]

    def test_malformed_toml_raises_error(self, tmp_path):
        """Malformed TOML raises ConfigParseError."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("[invalid toml content = =")

        with pytest.raises(ConfigParseError, match="Invalid TOML"):
            parse_pyproject_toml(pyproject)

    def test_unreadable_file_raises_error(self, tmp_path):
        """Unreadable pyproject.toml raises ConfigParseError."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("[tool.thailint]\n")
        pyproject.chmod(0o000)

        try:
            with pytest.raises(ConfigParseError, match="Cannot read"):
                parse_pyproject_toml(pyproject)
        finally:
            pyproject.chmod(0o644)


class TestPyprojectTomlFallback:
    """Test pyproject.toml fallback behavior in load_config."""

    def test_falls_back_to_pyproject_toml(self, tmp_path):
        """load_config falls back to pyproject.toml when yaml doesn't exist."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("[tool.thailint]\ndry = {enabled = true}\n")

        # Point at a non-existent .thailint.yaml in the same directory
        config_path = tmp_path / ".thailint.yaml"
        result = load_config(config_path)

        assert result["dry"] == {"enabled": True}

    def test_yaml_takes_precedence_over_pyproject(self, tmp_path):
        """Existing .thailint.yaml takes precedence over pyproject.toml."""
        yaml_config = tmp_path / ".thailint.yaml"
        yaml_config.write_text("dry:\n  enabled: false\n")

        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("[tool.thailint]\ndry = {enabled = true}\n")

        result = load_config(yaml_config)

        assert result["dry"] == {"enabled": False}

    def test_returns_defaults_when_no_config_exists(self, tmp_path):
        """Returns defaults when neither yaml nor pyproject.toml exist."""
        config_path = tmp_path / ".thailint.yaml"
        result = load_config(config_path)

        assert result == get_defaults()

    def test_returns_defaults_when_pyproject_has_no_thailint(self, tmp_path):
        """Returns defaults when pyproject.toml exists but has no thailint section."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text('[project]\nname = "myproject"\n')

        config_path = tmp_path / ".thailint.yaml"
        result = load_config(config_path)

        assert result == get_defaults()
