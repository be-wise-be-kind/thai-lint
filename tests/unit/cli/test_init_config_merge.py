"""
Purpose: Unit tests for init-config merge functionality

Scope: Tests for merging missing linter sections into existing config files

Overview: Comprehensive test suite for the init-config merge feature that adds missing
    linter configuration sections to existing .thailint.yaml files without overwriting
    user customizations. Tests cover section detection, merge behavior, comment preservation,
    and edge cases like empty files and malformed configs.

Dependencies: pytest, click.testing for CLI runner, yaml for config parsing

Exports: Test classes for merge functionality

Interfaces: Standard pytest test interface

Implementation: Uses pytest fixtures and Click's CliRunner for integration testing
"""

import yaml


class TestExtractLinterSections:
    """Tests for extracting linter sections from template."""

    def test_extracts_magic_numbers_section(self):
        """Should extract magic-numbers section with comments."""
        from src.cli.config_merge import extract_linter_sections as _extract_linter_sections

        template = """# Header comment
magic-numbers:
  enabled: true
  allowed_numbers: [1, 2, 3]

# Another section
nesting:
  enabled: true
"""
        sections = _extract_linter_sections(template)

        assert "magic-numbers" in sections
        assert "enabled: true" in sections["magic-numbers"]
        assert "allowed_numbers" in sections["magic-numbers"]

    def test_extracts_all_linter_sections(self):
        """Should extract all linter sections from template."""
        from src.cli.config_merge import extract_linter_sections as _extract_linter_sections

        template = """magic-numbers:
  enabled: true

nesting:
  enabled: true

srp:
  enabled: true
"""
        sections = _extract_linter_sections(template)

        assert len(sections) >= 3
        assert "magic-numbers" in sections
        assert "nesting" in sections
        assert "srp" in sections


class TestIdentifyMissingSections:
    """Tests for identifying which sections are missing from existing config."""

    def test_identifies_missing_sections(self):
        """Should identify linter sections missing from existing config."""
        from src.cli.config_merge import identify_missing_sections as _identify_missing_sections

        existing_config = {"magic-numbers": {"enabled": True}, "nesting": {"enabled": True}}
        all_sections = ["magic-numbers", "nesting", "srp", "dry", "file-header"]

        missing = _identify_missing_sections(existing_config, all_sections)

        assert "srp" in missing
        assert "dry" in missing
        assert "file-header" in missing
        assert "magic-numbers" not in missing
        assert "nesting" not in missing

    def test_returns_empty_when_all_present(self):
        """Should return empty list when all sections exist."""
        from src.cli.config_merge import identify_missing_sections as _identify_missing_sections

        existing_config = {"magic-numbers": {}, "nesting": {}, "srp": {}}
        all_sections = ["magic-numbers", "nesting", "srp"]

        missing = _identify_missing_sections(existing_config, all_sections)

        assert len(missing) == 0

    def test_returns_all_when_config_empty(self):
        """Should return all sections when config is empty."""
        from src.cli.config_merge import identify_missing_sections as _identify_missing_sections

        existing_config = {}
        all_sections = ["magic-numbers", "nesting", "srp"]

        missing = _identify_missing_sections(existing_config, all_sections)

        assert len(missing) == 3


class TestMergeConfigs:
    """Tests for merging missing sections into existing config."""

    def test_appends_missing_sections(self):
        """Should append missing linter sections to existing config."""
        from src.cli.config_merge import merge_config_sections as _merge_config_sections

        existing_content = """# My config
magic-numbers:
  enabled: true
  allowed_numbers: [-1, 0, 1, 2, 3]
"""
        missing_sections = {
            "nesting": """# ============================================================================
# NESTING LINTER
# ============================================================================
nesting:
  enabled: true
  max_nesting_depth: 4
"""
        }

        merged = _merge_config_sections(existing_content, missing_sections)

        assert "magic-numbers:" in merged
        assert "allowed_numbers: [-1, 0, 1, 2, 3]" in merged  # User value preserved
        assert "nesting:" in merged
        assert "max_nesting_depth: 4" in merged

    def test_preserves_existing_comments(self):
        """Should preserve comments in existing config."""
        from src.cli.config_merge import merge_config_sections as _merge_config_sections

        existing_content = """# My custom header comment
# Another comment
magic-numbers:
  enabled: true
  # My inline comment
  allowed_numbers: [1, 2, 3]
"""
        missing_sections = {"nesting": "nesting:\n  enabled: true\n"}

        merged = _merge_config_sections(existing_content, missing_sections)

        assert "# My custom header comment" in merged
        assert "# Another comment" in merged
        assert "# My inline comment" in merged

    def test_preserves_user_customizations(self):
        """Should not overwrite user's customized values."""
        from src.cli.config_merge import merge_config_sections as _merge_config_sections

        existing_content = """magic-numbers:
  enabled: false  # User disabled this
  allowed_numbers: [0, 1, 42, 100]  # Custom list
"""
        missing_sections = {"nesting": "nesting:\n  enabled: true\n"}

        merged = _merge_config_sections(existing_content, missing_sections)

        # Parse to verify values
        config = yaml.safe_load(merged)
        assert config["magic-numbers"]["enabled"] is False
        assert 42 in config["magic-numbers"]["allowed_numbers"]


class TestInitConfigMergeMode:
    """Integration tests for init-config with merge behavior."""

    def test_merges_when_file_exists(self, tmp_path):
        """Should merge missing sections when config file exists."""
        from click.testing import CliRunner

        from src.cli_main import cli

        # Create existing config with only magic-numbers
        config_path = tmp_path / ".thailint.yaml"
        config_path.write_text(
            """magic-numbers:
  enabled: true
  allowed_numbers: [0, 1, 42]
"""
        )

        runner = CliRunner()
        result = runner.invoke(cli, ["init-config", "--non-interactive", "-o", str(config_path)])

        assert result.exit_code == 0

        # Verify merge happened
        content = config_path.read_text()
        config = yaml.safe_load(content)

        # User's customization preserved
        assert 42 in config.get("magic-numbers", {}).get("allowed_numbers", [])
        # New sections added
        assert "nesting" in config
        assert "srp" in config
        assert "file-header" in config

    def test_force_overwrites_completely(self, tmp_path):
        """Should completely overwrite when --force is used."""
        from click.testing import CliRunner

        from src.cli_main import cli

        # Create existing config with custom value
        config_path = tmp_path / ".thailint.yaml"
        config_path.write_text(
            """magic-numbers:
  enabled: true
  allowed_numbers: [42, 999]  # Will be lost with --force
"""
        )

        runner = CliRunner()
        result = runner.invoke(
            cli, ["init-config", "--non-interactive", "--force", "-o", str(config_path)]
        )

        assert result.exit_code == 0

        # Verify overwrite happened
        content = config_path.read_text()
        config = yaml.safe_load(content)

        # User's customization lost (replaced with defaults)
        assert 42 not in config.get("magic-numbers", {}).get("allowed_numbers", [])
        assert 999 not in config.get("magic-numbers", {}).get("allowed_numbers", [])

    def test_creates_new_file_when_not_exists(self, tmp_path):
        """Should create new file with all sections when config doesn't exist."""
        from click.testing import CliRunner

        from src.cli_main import cli

        config_path = tmp_path / ".thailint.yaml"
        assert not config_path.exists()

        runner = CliRunner()
        result = runner.invoke(cli, ["init-config", "--non-interactive", "-o", str(config_path)])

        assert result.exit_code == 0
        assert config_path.exists()

        config = yaml.safe_load(config_path.read_text())
        assert "magic-numbers" in config
        assert "nesting" in config
        assert "srp" in config

    def test_shows_merge_message_when_merging(self, tmp_path):
        """Should show message about merged sections."""
        from click.testing import CliRunner

        from src.cli_main import cli

        config_path = tmp_path / ".thailint.yaml"
        config_path.write_text("magic-numbers:\n  enabled: true\n")

        runner = CliRunner()
        result = runner.invoke(cli, ["init-config", "--non-interactive", "-o", str(config_path)])

        assert result.exit_code == 0
        assert "Added" in result.output or "merged" in result.output.lower()


class TestEdgeCases:
    """Tests for edge cases in merge functionality."""

    def test_handles_empty_existing_file(self, tmp_path):
        """Should handle empty existing config file."""
        from click.testing import CliRunner

        from src.cli_main import cli

        config_path = tmp_path / ".thailint.yaml"
        config_path.write_text("")

        runner = CliRunner()
        result = runner.invoke(cli, ["init-config", "--non-interactive", "-o", str(config_path)])

        assert result.exit_code == 0
        config = yaml.safe_load(config_path.read_text())
        assert "magic-numbers" in config

    def test_handles_malformed_yaml(self, tmp_path):
        """Should handle malformed YAML gracefully."""
        from click.testing import CliRunner

        from src.cli_main import cli

        config_path = tmp_path / ".thailint.yaml"
        config_path.write_text("invalid: yaml: content: [")

        runner = CliRunner()
        result = runner.invoke(cli, ["init-config", "--non-interactive", "-o", str(config_path)])

        # Should either error gracefully or use --force behavior
        assert result.exit_code in (0, 1)

    def test_handles_config_with_only_global_settings(self, tmp_path):
        """Should add all linter sections when only global settings exist."""
        from click.testing import CliRunner

        from src.cli_main import cli

        config_path = tmp_path / ".thailint.yaml"
        config_path.write_text(
            """exclude:
  - "node_modules/"
  - ".git/"
output_format: json
"""
        )

        runner = CliRunner()
        result = runner.invoke(cli, ["init-config", "--non-interactive", "-o", str(config_path)])

        assert result.exit_code == 0
        config = yaml.safe_load(config_path.read_text())

        # Global settings preserved
        assert "node_modules/" in config.get("exclude", [])
        assert config.get("output_format") == "json"
        # Linter sections added
        assert "magic-numbers" in config
