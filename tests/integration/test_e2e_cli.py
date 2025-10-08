"""
Purpose: End-to-end CLI workflow tests validating complete command execution paths

Scope: Full CLI command testing including help, lint commands, exit codes, and output formats

Overview: Comprehensive E2E test suite for CLI functionality that validates complete user
    workflows from command invocation to output. Tests verify help text display, version
    information, lint command execution with various options, exit codes (0 for pass, 1 for
    violations, 2 for errors), output format options (text/JSON), configuration loading,
    and error handling. Uses Click CliRunner for isolated command execution with controlled
    input/output capture and file system mocking.

Dependencies: pytest for testing, Click CliRunner for CLI testing, tempfile for test fixtures

Exports: TestCLIHelp, TestCLILinting, TestCLIExitCodes, TestCLIOutputFormats test classes

Interfaces: Click CliRunner invocation, subprocess-free CLI testing

Implementation: Uses CliRunner for isolated command testing, temporary files for test
    configurations, comprehensive assertions on stdout/stderr/exit codes
"""

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from src.cli import cli


class TestCLIHelp:
    """Test CLI help text and version information."""

    def test_cli_help_shows_usage(self) -> None:
        """Test that --help flag shows usage information."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])

        assert result.exit_code == 0
        assert "thai-lint" in result.output
        assert "Usage:" in result.output
        assert "Options:" in result.output
        assert "Commands:" in result.output

    def test_cli_version_shows_version(self) -> None:
        """Test that --version flag shows version number."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--version"])

        assert result.exit_code == 0
        assert "version" in result.output.lower()

    def test_file_placement_command_exists(self) -> None:
        """Test that file-placement command is available."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])

        assert result.exit_code == 0
        assert "file-placement" in result.output
        assert "Commands:" in result.output

    def test_file_placement_help_shows_options(self) -> None:
        """Test that file-placement --help shows all options."""
        runner = CliRunner()
        result = runner.invoke(cli, ["file-placement", "--help"])

        assert result.exit_code == 0
        assert "--config" in result.output
        assert "--rules" in result.output
        assert "--format" in result.output
        assert "--recursive" in result.output


class TestCLILinting:
    """Test CLI linting commands with various configurations."""

    def test_lint_file_with_violations(self) -> None:
        """Test linting a file that has violations."""
        runner = CliRunner()

        with runner.isolated_filesystem():
            # Create test file
            Path("test.py").write_text("print('test')")

            # Create .git marker so project root detection works
            Path(".git").mkdir()

            # Create .artifacts directory and generated config
            Path(".artifacts").mkdir()
            Path(".artifacts/generated-config.yaml").write_text(
                "file-placement:\n  global_deny:\n    - pattern: '.*\\.py$'\n      reason: 'No Python files'\n"
            )

            # Run linter
            result = runner.invoke(cli, ["file-placement", "test.py"])

            # Should exit with code 1 (violations found)
            assert result.exit_code == 1
            assert "test.py" in result.output
            assert "violation" in result.output.lower() or "not allowed" in result.output.lower()

    def test_lint_file_without_violations(self) -> None:
        """Test linting a file that passes all rules."""
        runner = CliRunner()

        with runner.isolated_filesystem():
            # Create test file
            Path("test.py").write_text("print('test')")

            # Create config with allow pattern
            Path(".thailint.yaml").write_text(
                "file-placement:\n  global_patterns:\n    allow:\n      - pattern: '.*\\.py$'\n"
            )

            # Run linter
            result = runner.invoke(cli, ["file-placement", "test.py"])

            # Should exit with code 0 (no violations)
            assert result.exit_code == 0

    def test_lint_with_inline_rules(self) -> None:
        """Test linting with inline JSON rules via --rules flag."""
        runner = CliRunner()

        with runner.isolated_filesystem():
            # Create test file
            Path("test.py").write_text("print('test')")

            # Create .git marker so project root detection works
            Path(".git").mkdir()

            # Run with inline rules (using proper file-placement structure)
            rules = '{"global_deny": [{"pattern": ".*\\\\.py$", "reason": "No Python files"}]}'
            result = runner.invoke(cli, ["file-placement", "--rules", rules, "test.py"])

            # Should find violations
            assert result.exit_code == 1

    def test_lint_with_external_config(self) -> None:
        """Test linting with external config file via --config flag."""
        runner = CliRunner()

        with runner.isolated_filesystem():
            # Create test file
            Path("test.py").write_text("print('test')")

            # Create .git marker so project root detection works
            Path(".git").mkdir()

            # Create external config
            Path("custom.yaml").write_text(
                "file-placement:\n  global_deny:\n    - pattern: '.*\\.py$'\n      reason: 'No Python files'\n"
            )

            # Run with external config (CLI will copy it to .artifacts/generated-config.yaml)
            result = runner.invoke(cli, ["file-placement", "--config", "custom.yaml", "test.py"])

            # Should find violations
            assert result.exit_code == 1


class TestCLIExitCodes:
    """Test CLI exit codes follow conventions."""

    def test_exit_code_0_on_success(self) -> None:
        """Test exit code 0 when no violations found."""
        runner = CliRunner()

        with runner.isolated_filesystem():
            Path("test.py").write_text("print('test')")
            Path(".thailint.yaml").write_text(
                "rules:\n  file-placement:\n    allow:\n      - '.*\\.py$'\n"
            )

            result = runner.invoke(cli, ["file-placement", "test.py"])
            assert result.exit_code == 0

    def test_exit_code_1_on_violations(self) -> None:
        """Test exit code 1 when violations found."""
        runner = CliRunner()

        with runner.isolated_filesystem():
            Path("test.py").write_text("print('test')")

            # Create .git marker so project root detection works
            Path(".git").mkdir()

            # Create .artifacts directory and generated config
            Path(".artifacts").mkdir()
            Path(".artifacts/generated-config.yaml").write_text(
                "file-placement:\n  global_deny:\n    - pattern: '.*\\.py$'\n      reason: 'No Python files'\n"
            )

            result = runner.invoke(cli, ["file-placement", "test.py"])
            assert result.exit_code == 1

    def test_exit_code_2_on_error(self) -> None:
        """Test exit code 2 on configuration or runtime errors."""
        runner = CliRunner()

        with runner.isolated_filesystem():
            # Run on non-existent file
            result = runner.invoke(cli, ["file-placement", "nonexistent.py"])

            # Should exit with error code
            assert result.exit_code == 2


class TestCLIOutputFormats:
    """Test CLI output format options."""

    def test_text_output_format(self) -> None:
        """Test default text output format."""
        runner = CliRunner()

        with runner.isolated_filesystem():
            Path("test.py").write_text("print('test')")

            # Create .git marker so project root detection works
            Path(".git").mkdir()

            # Create .artifacts directory and generated config
            Path(".artifacts").mkdir()
            Path(".artifacts/generated-config.yaml").write_text(
                "file-placement:\n  global_deny:\n    - pattern: '.*\\.py$'\n      reason: 'No Python files'\n"
            )

            result = runner.invoke(cli, ["file-placement", "test.py"])

            # Text format should be human-readable
            assert result.exit_code == 1
            assert "test.py" in result.output

    def _setup_json_test_files(self):
        """Set up test files for JSON output test."""
        Path("test.py").write_text("print('test')")

        # Create .git marker so project root detection works
        Path(".git").mkdir()

        # Create .artifacts directory and generated config
        Path(".artifacts").mkdir()
        Path(".artifacts/generated-config.yaml").write_text(
            "file-placement:\n  global_deny:\n    - pattern: '.*\\.py$'\n      reason: 'No Python files'\n"
        )

    def _verify_json_parseable(self, result):
        """Verify output is parseable JSON.

        Args:
            result: CLI runner result object
        """
        try:
            data = json.loads(result.output)
            assert isinstance(data, (list, dict))
        except json.JSONDecodeError:
            pytest.fail("Output is not valid JSON")

    def test_json_output_format(self) -> None:
        """Test JSON output format."""
        runner = CliRunner()

        with runner.isolated_filesystem():
            # Set up test files
            self._setup_json_test_files()

            result = runner.invoke(cli, ["file-placement", "--format", "json", "test.py"])

            # JSON format should be parseable
            assert result.exit_code == 1
            self._verify_json_parseable(result)


class TestCLIRecursive:
    """Test CLI recursive directory scanning."""

    def test_recursive_directory_scan(self) -> None:
        """Test linting recursively scans subdirectories."""
        runner = CliRunner()

        with runner.isolated_filesystem():
            # Create nested structure
            Path("src").mkdir()
            Path("src/test.py").write_text("print('test')")
            Path("src/nested").mkdir()
            Path("src/nested/deep.py").write_text("print('deep')")

            # Create .git marker so project root detection works
            Path(".git").mkdir()

            # Create .artifacts directory and generated config
            Path(".artifacts").mkdir()
            Path(".artifacts/generated-config.yaml").write_text(
                "file-placement:\n  global_deny:\n    - pattern: '.*\\.py$'\n      reason: 'No Python files'\n"
            )

            # Run recursive scan
            result = runner.invoke(cli, ["file-placement", "--recursive", "src"])

            # Should find violations in nested files
            assert result.exit_code == 1
            assert "test.py" in result.output or "deep.py" in result.output

    def test_non_recursive_scan(self) -> None:
        """Test non-recursive scan only checks direct files."""
        runner = CliRunner()

        with runner.isolated_filesystem():
            # Create nested structure
            Path("src").mkdir()
            Path("src/test.py").write_text("print('test')")
            Path("src/nested").mkdir()
            Path("src/nested/deep.py").write_text("print('deep')")

            Path(".thailint.yaml").write_text(
                "rules:\n  file-placement:\n    allow:\n      - '.*\\.py$'\n"
            )

            # Run non-recursive scan
            result = runner.invoke(cli, ["file-placement", "src/test.py"])

            # Should only check specified file
            assert result.exit_code == 0
