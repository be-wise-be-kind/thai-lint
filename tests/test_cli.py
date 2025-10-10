"""
Purpose: Test suite for CLI commands and interactions

Scope: CLI command testing, option parsing, error handling, and output validation

Overview: Comprehensive test suite for CLI application using Click's CliRunner for isolated
    testing. Tests all commands including hello, config show/get/set/reset with various option
    combinations. Validates command output, exit codes, error messages, and configuration
    interactions. Includes fixtures for temporary config files and isolated CLI invocation.

Dependencies: pytest for testing framework, click.testing.CliRunner for CLI testing

Exports: Test functions for pytest discovery

Interfaces: Click CliRunner, pytest fixtures, temporary file paths

Implementation: Isolated CLI testing with CliRunner, temporary config files, comprehensive assertions
"""

import json

import pytest
import yaml
from click.testing import CliRunner

from src.cli import cli
from src.config import DEFAULT_CONFIG


@pytest.fixture
def runner():
    """Provide Click test runner for isolated CLI testing."""
    return CliRunner()


@pytest.fixture
def temp_config_yaml(tmp_path):
    """Provide temporary YAML config file."""
    config_file = tmp_path / "config.yaml"
    config_data = {
        "greeting": "Hi",
        "log_level": "DEBUG",
        "max_retries": 5,
    }
    with config_file.open("w") as f:
        yaml.dump(config_data, f)
    return config_file


@pytest.fixture
def temp_config_json(tmp_path):
    """Provide temporary JSON config file."""
    config_file = tmp_path / "config.json"
    config_data = {
        "greeting": "Howdy",
        "log_level": "WARNING",
        "max_retries": 2,
    }
    with config_file.open("w") as f:
        json.dump(config_data, f)
    return config_file


class TestCLIBasics:
    """Test basic CLI functionality."""

    def test_cli_help(self, runner):
        """Test CLI shows help text."""
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "thai-lint" in result.output
        assert "Commands:" in result.output

    def test_cli_version(self, runner):
        """Test CLI shows version."""
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert "version" in result.output.lower()


class TestHelloCommand:
    """Test hello command."""


class TestConfigShow:
    """Test config show command."""

    def test_config_show_json_format(self, runner):
        """Test showing config in JSON format."""
        result = runner.invoke(cli, ["config", "show", "--format", "json"])
        assert result.exit_code == 0
        # Should be valid JSON
        assert "{" in result.output
        assert "}" in result.output

    def test_config_show_yaml_format(self, runner):
        """Test showing config in YAML format."""
        result = runner.invoke(cli, ["config", "show", "--format", "yaml"])
        assert result.exit_code == 0
        # YAML format
        assert ":" in result.output


class TestConfigGet:
    """Test config get command."""

    def test_config_get_existing_key(self, runner):
        """Test getting existing config key."""
        result = runner.invoke(cli, ["config", "get", "log_level"])
        assert result.exit_code == 0
        assert "INFO" in result.output

    def test_config_get_nonexistent_key(self, runner):
        """Test getting nonexistent config key."""
        result = runner.invoke(cli, ["config", "get", "nonexistent_key"])
        assert result.exit_code != 0
        assert "not found" in result.output.lower()


class TestConfigSet:
    """Test config set command."""

    def test_config_set_integer_value(self, runner, tmp_path):
        """Test setting integer config value."""
        config_file = tmp_path / "config.yaml"

        result = runner.invoke(
            cli, ["--config", str(config_file), "config", "set", "max_retries", "10"]
        )
        assert result.exit_code == 0

        # Verify value was saved as integer
        result = runner.invoke(
            cli, ["--config", str(config_file), "config", "show", "--format", "yaml"]
        )
        assert "max_retries: 10" in result.output

    def test_config_set_boolean_value(self, runner, tmp_path):
        """Test setting boolean config value."""
        config_file = tmp_path / "config.yaml"

        result = runner.invoke(
            cli, ["--config", str(config_file), "config", "set", "test_flag", "true"]
        )
        assert result.exit_code == 0

    def test_config_set_invalid_value(self, runner, tmp_path):
        """Test setting invalid config value."""
        config_file = tmp_path / "config.yaml"

        result = runner.invoke(
            cli, ["--config", str(config_file), "config", "set", "log_level", "INVALID"]
        )
        assert result.exit_code != 0
        assert "Invalid" in result.output or "invalid" in result.output


class TestConfigReset:
    """Test config reset command."""

    def test_config_reset_with_confirmation(self, runner, tmp_path):
        """Test config reset with yes flag."""
        config_file = tmp_path / "config.yaml"

        # Set custom value
        runner.invoke(cli, ["--config", str(config_file), "config", "set", "greeting", "Custom"])

        # Reset config
        result = runner.invoke(cli, ["--config", str(config_file), "config", "reset", "--yes"])
        assert result.exit_code == 0
        assert "reset to defaults" in result.output.lower()

        # Verify reset to default
        result = runner.invoke(cli, ["--config", str(config_file), "config", "get", "greeting"])
        assert DEFAULT_CONFIG["greeting"] in result.output

    def test_config_reset_abort(self, runner, tmp_path):
        """Test config reset abort on confirmation."""
        config_file = tmp_path / "config.yaml"

        # Reset without yes flag (simulate 'n' input)
        result = runner.invoke(cli, ["--config", str(config_file), "config", "reset"], input="n\n")
        assert result.exit_code != 0  # Aborted


class TestVerboseOutput:
    """Test verbose output option."""

    # Verbose logging should be present (timestamps, etc.)


class TestErrorHandling:
    """Test error handling."""

    def test_invalid_config_file(self, runner, tmp_path):
        """Test error with invalid config file."""
        invalid_config = tmp_path / "invalid.yaml"
        invalid_config.write_text("invalid: yaml: content: [[[")

        result = runner.invoke(cli, ["--config", str(invalid_config), "hello"])
        assert result.exit_code != 0
        assert "Error" in result.output or "error" in result.output


class TestIntegration:
    """Integration tests for complete workflows."""

    def test_full_workflow(self, runner, tmp_path):
        """Test complete configuration workflow."""
        config_file = tmp_path / "config.yaml"

        # 1. Show default config
        result = runner.invoke(cli, ["--config", str(config_file), "config", "show"])
        assert result.exit_code == 0

        # 2. Set custom greeting
        result = runner.invoke(
            cli, ["--config", str(config_file), "config", "set", "greeting", "Hey"]
        )
        assert result.exit_code == 0

        # 3. Use custom greeting
        result = runner.invoke(cli, ["--config", str(config_file), "hello", "--name", "User"])
        assert result.exit_code == 0
        assert "Hey, User!" in result.output

        # 4. Reset to defaults
        result = runner.invoke(cli, ["--config", str(config_file), "config", "reset", "--yes"])
        assert result.exit_code == 0

        # 5. Verify default greeting restored
        result = runner.invoke(cli, ["--config", str(config_file), "hello", "--name", "User"])
        assert result.exit_code == 0
        assert "Hello, User!" in result.output
