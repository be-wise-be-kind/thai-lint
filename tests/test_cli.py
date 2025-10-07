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

    def test_hello_default(self, runner):
        """Test hello command with default name."""
        result = runner.invoke(cli, ["hello"])
        assert result.exit_code == 0
        assert "Hello, World!" in result.output

    def test_hello_with_name(self, runner):
        """Test hello command with custom name."""
        result = runner.invoke(cli, ["hello", "--name", "Alice"])
        assert result.exit_code == 0
        assert "Hello, Alice!" in result.output

    def test_hello_with_short_name_option(self, runner):
        """Test hello command with short option."""
        result = runner.invoke(cli, ["hello", "-n", "Bob"])
        assert result.exit_code == 0
        assert "Hello, Bob!" in result.output

    def test_hello_uppercase(self, runner):
        """Test hello command with uppercase flag."""
        result = runner.invoke(cli, ["hello", "--name", "Charlie", "--uppercase"])
        assert result.exit_code == 0
        assert "HELLO, CHARLIE!" in result.output

    def test_hello_short_uppercase(self, runner):
        """Test hello command with short uppercase flag."""
        result = runner.invoke(cli, ["hello", "-n", "Dave", "-u"])
        assert result.exit_code == 0
        assert "HELLO, DAVE!" in result.output

    def test_hello_with_custom_config(self, runner, temp_config_yaml):
        """Test hello command with custom greeting from config."""
        result = runner.invoke(cli, ["--config", str(temp_config_yaml), "hello", "--name", "Eve"])
        assert result.exit_code == 0
        assert "Hi, Eve!" in result.output

    def test_hello_help(self, runner):
        """Test hello command help text."""
        result = runner.invoke(cli, ["hello", "--help"])
        assert result.exit_code == 0
        assert "Print a greeting message" in result.output
        assert "--name" in result.output


class TestConfigShow:
    """Test config show command."""

    def test_config_show_default(self, runner):
        """Test showing default configuration."""
        result = runner.invoke(cli, ["config", "show"])
        assert result.exit_code == 0
        assert "log_level" in result.output
        assert "INFO" in result.output

    def test_config_show_text_format(self, runner):
        """Test showing config in text format."""
        result = runner.invoke(cli, ["config", "show", "--format", "text"])
        assert result.exit_code == 0
        assert ":" in result.output  # Text format uses key : value

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

    def test_config_show_with_custom_config(self, runner, temp_config_yaml):
        """Test showing custom configuration."""
        result = runner.invoke(cli, ["--config", str(temp_config_yaml), "config", "show"])
        assert result.exit_code == 0
        assert "DEBUG" in result.output


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

    def test_config_get_with_custom_config(self, runner, temp_config_yaml):
        """Test getting value from custom config."""
        result = runner.invoke(
            cli, ["--config", str(temp_config_yaml), "config", "get", "greeting"]
        )
        assert result.exit_code == 0
        assert "Hi" in result.output


class TestConfigSet:
    """Test config set command."""

    def test_config_set_string_value(self, runner, tmp_path):
        """Test setting string config value."""
        config_file = tmp_path / "config.yaml"

        result = runner.invoke(
            cli, ["--config", str(config_file), "config", "set", "greeting", "Howdy"]
        )
        assert result.exit_code == 0
        assert "Set greeting = Howdy" in result.output

        # Verify value was saved
        result = runner.invoke(cli, ["--config", str(config_file), "config", "get", "greeting"])
        assert "Howdy" in result.output

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

    def test_verbose_flag(self, runner):
        """Test CLI with verbose flag."""
        result = runner.invoke(cli, ["--verbose", "hello"])
        assert result.exit_code == 0
        # Verbose logging should be present (timestamps, etc.)

    def test_short_verbose_flag(self, runner):
        """Test CLI with short verbose flag."""
        result = runner.invoke(cli, ["-v", "hello"])
        assert result.exit_code == 0


class TestErrorHandling:
    """Test error handling."""

    def test_invalid_config_file(self, runner, tmp_path):
        """Test error with invalid config file."""
        invalid_config = tmp_path / "invalid.yaml"
        invalid_config.write_text("invalid: yaml: content: [[[")

        result = runner.invoke(cli, ["--config", str(invalid_config), "hello"])
        assert result.exit_code != 0
        assert "Error" in result.output or "error" in result.output

    def test_nonexistent_config_file(self, runner, tmp_path):
        """Test with nonexistent config file (should use defaults)."""
        nonexistent = tmp_path / "does-not-exist.yaml"

        result = runner.invoke(cli, ["--config", str(nonexistent), "hello"])
        # Should still work with defaults
        assert result.exit_code == 0


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
