"""
Purpose: Tests for stringly-typed linter CLI command interface

Scope: Command-line interface for stringly-typed linter including commands, options, and output

Overview: Test suite for CLI command interface covering basic stringly-typed command,
    custom config file option, recursive mode, and output formats. Validates proper command
    execution, option handling, exit codes, and output formatting.

Dependencies: pytest, click.testing.CliRunner, src.cli, tmp_path fixture

Exports: Test functions for CLI interface scenarios

Interfaces: Uses Click CLI framework via CliRunner

Implementation: TDD approach with isolated temp directory fixtures
"""

from click.testing import CliRunner

from src.cli import cli


class TestStringlyTypedCommandRegistration:
    """Tests for stringly-typed command registration."""

    def test_stringly_typed_command_exists(self):
        """Test that stringly-typed command is registered."""
        runner = CliRunner()
        result = runner.invoke(cli, ["stringly-typed", "--help"])

        assert result.exit_code == 0
        assert "stringly-typed" in result.output.lower()

    def test_stringly_typed_help_shows_options(self):
        """Test that help shows expected options."""
        runner = CliRunner()
        result = runner.invoke(cli, ["stringly-typed", "--help"])

        assert "--format" in result.output
        assert "--recursive" in result.output
        assert "--config" in result.output


class TestStringlyTypedCommandExecution:
    """Tests for stringly-typed command execution."""

    def test_stringly_typed_cli_no_violations(self, tmp_path):
        """Test CLI returns 0 when no violations found."""
        file1 = tmp_path / "file1.py"
        file1.write_text("""
def process():
    return 42
""")

        runner = CliRunner()
        result = runner.invoke(cli, ["stringly-typed", str(tmp_path)])

        assert result.exit_code == 0

    def test_stringly_typed_cli_with_violations(self, tmp_path):
        """Test CLI returns 1 when violations found (cross-file pattern)."""
        file1 = tmp_path / "file1.py"
        file1.write_text("""
def validate_env(env):
    if env in ("staging", "production"):
        return True
    return False
""")

        file2 = tmp_path / "file2.py"
        file2.write_text("""
def check_environment(env):
    if env in ("staging", "production"):
        return True
    raise ValueError("Invalid environment")
""")

        runner = CliRunner()
        result = runner.invoke(cli, ["stringly-typed", str(tmp_path)])

        assert result.exit_code == 1
        assert "stringly" in result.output.lower() or "staging" in result.output.lower()

    def test_stringly_typed_cli_default_path(self, tmp_path, monkeypatch):
        """Test CLI uses current directory when no path provided."""
        file1 = tmp_path / "file1.py"
        file1.write_text("def foo(): pass")

        monkeypatch.chdir(tmp_path)

        runner = CliRunner()
        result = runner.invoke(cli, ["stringly-typed"])

        assert result.exit_code == 0


class TestStringlyTypedConfigOption:
    """Tests for stringly-typed config option."""

    def test_stringly_typed_with_custom_config(self, tmp_path):
        """Test CLI with custom config file."""
        file1 = tmp_path / "file1.py"
        file1.write_text("""
def validate(status):
    if status in ("active", "inactive"):
        return True
""")

        file2 = tmp_path / "file2.py"
        file2.write_text("""
def check(status):
    if status in ("active", "inactive"):
        return True
""")

        config = tmp_path / "custom.yaml"
        config.write_text("""
stringly_typed:
  enabled: true
  min_occurrences: 2
  min_values_for_enum: 2
  max_values_for_enum: 6
""")

        runner = CliRunner()
        result = runner.invoke(cli, ["stringly-typed", str(tmp_path), "--config", str(config)])

        assert result.exit_code in [0, 1]
        assert result.output is not None

    def test_stringly_typed_disabled_via_config(self, tmp_path):
        """Test CLI respects enabled=false in config."""
        file1 = tmp_path / "file1.py"
        file1.write_text("""
def validate(env):
    if env in ("staging", "production"):
        return True
""")

        file2 = tmp_path / "file2.py"
        file2.write_text("""
def check(env):
    if env in ("staging", "production"):
        return True
""")

        config = tmp_path / ".thailint.yaml"
        config.write_text("""
stringly_typed:
  enabled: false
""")

        runner = CliRunner()
        result = runner.invoke(cli, ["stringly-typed", str(tmp_path), "--config", str(config)])

        assert result.exit_code == 0


class TestStringlyTypedRecursiveOption:
    """Tests for stringly-typed recursive option."""

    def test_stringly_typed_recursive_default(self, tmp_path):
        """Test CLI scans recursively by default."""
        subdir = tmp_path / "subdir"
        subdir.mkdir()

        file1 = subdir / "file1.py"
        file1.write_text("""
def validate(env):
    if env in ("staging", "production"):
        return True
""")

        file2 = tmp_path / "file2.py"
        file2.write_text("""
def check(env):
    if env in ("staging", "production"):
        return True
""")

        runner = CliRunner()
        result = runner.invoke(cli, ["stringly-typed", str(tmp_path)])

        assert result.exit_code == 1

    def test_stringly_typed_no_recursive(self, tmp_path):
        """Test CLI with --no-recursive option."""
        subdir = tmp_path / "subdir"
        subdir.mkdir()

        file1 = subdir / "file1.py"
        file1.write_text("""
def validate(env):
    if env in ("staging", "production"):
        return True
""")

        file2 = tmp_path / "file2.py"
        file2.write_text("def foo(): pass")

        runner = CliRunner()
        result = runner.invoke(cli, ["stringly-typed", str(tmp_path), "--no-recursive"])

        assert result.exit_code == 0
