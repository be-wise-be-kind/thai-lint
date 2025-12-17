"""
Purpose: Test CLI interface for stateless-class linter command

Scope: Command-line interface validation, flag parsing, output formatting for stateless-class linter

Overview: Validates CLI interface for stateless-class linter command including thai-lint
    stateless-class command availability, output format options (text/JSON/SARIF),
    exit code behavior (0 for pass, 1 for violations), help text and usage information,
    configuration file support, and integration with main CLI framework. Ensures
    stateless-class linter is accessible via command-line with proper flag support
    and user-friendly output.

Dependencies: pytest for testing framework, click for CLI framework, src.cli for main CLI,
    click.testing.CliRunner for CLI testing, pathlib for Path handling

Exports: TestCLIInterface (6 tests) covering command availability and behavior

Interfaces: Tests thai-lint stateless-class command invocation and flag parsing

Implementation: Uses click.testing.CliRunner for CLI invocation testing,
    verifies command registration, output format, and exit codes
"""

from pathlib import Path


class TestCLIInterface:
    """Test stateless-class linter CLI command interface."""

    def test_stateless_class_command_exists(self):
        """CLI should have 'stateless-class' command available."""
        from click.testing import CliRunner

        from src.cli import cli

        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0, "CLI should run"
        # Help output should mention stateless-class command
        assert "stateless-class" in result.output, "stateless-class command should be listed"

    def test_exits_zero_when_no_violations(self):
        """CLI should exit 0 when file has no violations."""
        from click.testing import CliRunner

        from src.cli import cli

        runner = CliRunner()
        with runner.isolated_filesystem():
            # Create file with proper init and state - no violation
            Path("clean.py").write_text(
                '''
class WithInit:
    """Class with proper initialization."""

    def __init__(self):
        self.data = []

    def get_data(self):
        return self.data
'''
            )

            result = runner.invoke(cli, ["stateless-class", "clean.py"])
            assert result.exit_code == 0, f"Should exit 0 when no violations: {result.output}"

    def test_exits_one_when_violations_found(self):
        """CLI should exit 1 when file has violations."""
        from click.testing import CliRunner

        from src.cli import cli

        runner = CliRunner()
        with runner.isolated_filesystem():
            # Create file with stateless class - should violate
            Path("bad.py").write_text(
                '''
class StatelessHelper:
    """Stateless class that should be module functions."""

    def method1(self, x):
        return x * 2

    def method2(self, y):
        return y + 1
'''
            )

            result = runner.invoke(cli, ["stateless-class", "bad.py"])
            assert result.exit_code == 1, f"Should exit 1 when violations found: {result.output}"

    def test_outputs_violation_details(self):
        """CLI should output violation details with class name and suggestion."""
        from click.testing import CliRunner

        from src.cli import cli

        runner = CliRunner()
        with runner.isolated_filesystem():
            Path("violation.py").write_text(
                '''
class TokenHasher:
    """Stateless token hasher class."""

    def hash_token(self, token):
        return hash(token)

    def verify_hash(self, token, expected):
        return self.hash_token(token) == expected
'''
            )

            result = runner.invoke(cli, ["stateless-class", "violation.py"])
            assert result.exit_code == 1, "Should have violation"
            # Output should contain class name
            assert "TokenHasher" in result.output, "Should mention violating class name"
            # Output should contain suggestion to use module functions
            assert "module" in result.output.lower() or "function" in result.output.lower(), (
                f"Should suggest module functions: {result.output}"
            )

    def test_output_format_json(self):
        """CLI should support --format=json output."""
        import json

        from click.testing import CliRunner

        from src.cli import cli

        runner = CliRunner()
        with runner.isolated_filesystem():
            Path("test.py").write_text(
                '''
class StatelessClass:
    """Stateless class."""

    def method1(self, x):
        return x * 2

    def method2(self, y):
        return y + 1
'''
            )

            result = runner.invoke(cli, ["stateless-class", "--format", "json", "test.py"])
            assert result.exit_code == 1, "Should have violation"
            # Output should be valid JSON
            try:
                data = json.loads(result.output)
                assert isinstance(data, dict), "JSON output should be a dict"
                assert "violations" in data, "Should have violations key"
                assert len(data["violations"]) > 0, "Should have at least one violation"
            except json.JSONDecodeError as e:
                raise AssertionError(f"Output should be valid JSON: {result.output}") from e

    def test_output_format_sarif(self):
        """CLI should support --format=sarif output."""
        import json

        from click.testing import CliRunner

        from src.cli import cli

        runner = CliRunner()
        with runner.isolated_filesystem():
            Path("test.py").write_text(
                '''
class StatelessClass:
    """Stateless class."""

    def method1(self, x):
        return x * 2

    def method2(self, y):
        return y + 1
'''
            )

            result = runner.invoke(cli, ["stateless-class", "--format", "sarif", "test.py"])
            assert result.exit_code == 1, "Should have violation"
            # Output should be valid SARIF JSON
            try:
                data = json.loads(result.output)
                assert "$schema" in data, "SARIF should have $schema"
                assert data.get("version") == "2.1.0", "SARIF should be version 2.1.0"
            except json.JSONDecodeError as e:
                raise AssertionError(f"Output should be valid SARIF JSON: {result.output}") from e

    def test_config_file_support(self):
        """CLI should support --config flag for configuration file."""
        from click.testing import CliRunner

        from src.cli import cli

        runner = CliRunner()
        with runner.isolated_filesystem():
            Path("test.py").write_text(
                '''
class StatelessClass:
    """Stateless class."""

    def method1(self, x):
        return x * 2

    def method2(self, y):
        return y + 1
'''
            )
            # Create config file
            Path(".thailint.yaml").write_text(
                """
stateless-class:
  enabled: true
"""
            )

            # Should work with config file
            result = runner.invoke(
                cli, ["stateless-class", "--config", ".thailint.yaml", "test.py"]
            )
            # Command should execute (may have violations or not based on config)
            assert result.exit_code in (0, 1), f"Command should execute: {result.output}"

    def test_recursive_directory_scan(self):
        """CLI should recursively scan directories by default."""
        from click.testing import CliRunner

        from src.cli import cli

        runner = CliRunner()
        with runner.isolated_filesystem():
            # Create nested directory structure
            Path("src").mkdir()
            Path("src/utils").mkdir()
            Path("src/utils/helpers.py").write_text(
                '''
class StatelessHelper:
    """Stateless helper class."""

    def helper1(self, x):
        return x * 2

    def helper2(self, y):
        return y + 1
'''
            )

            result = runner.invoke(cli, ["stateless-class", "."])
            assert result.exit_code == 1, f"Should find violation in nested file: {result.output}"
            assert "StatelessHelper" in result.output, "Should report nested file violation"

    def test_help_text(self):
        """CLI should show helpful usage information."""
        from click.testing import CliRunner

        from src.cli import cli

        runner = CliRunner()
        result = runner.invoke(cli, ["stateless-class", "--help"])
        assert result.exit_code == 0, "Help should work"
        # Help should explain the command
        assert "stateless" in result.output.lower(), (
            "Help should describe stateless class detection"
        )


class TestCLIEdgeCases:
    """Test edge cases for stateless-class CLI command."""

    def test_handles_empty_file(self):
        """CLI should handle empty files gracefully."""
        from click.testing import CliRunner

        from src.cli import cli

        runner = CliRunner()
        with runner.isolated_filesystem():
            Path("empty.py").write_text("")

            result = runner.invoke(cli, ["stateless-class", "empty.py"])
            assert result.exit_code == 0, f"Should exit 0 for empty file: {result.output}"

    def test_handles_no_classes(self):
        """CLI should handle files with no classes."""
        from click.testing import CliRunner

        from src.cli import cli

        runner = CliRunner()
        with runner.isolated_filesystem():
            Path("functions.py").write_text(
                """
def helper1(x):
    return x * 2

def helper2(y):
    return y + 1
"""
            )

            result = runner.invoke(cli, ["stateless-class", "functions.py"])
            assert result.exit_code == 0, f"Should exit 0 for file with no classes: {result.output}"

    def test_handles_nonexistent_file(self):
        """CLI should handle nonexistent file gracefully."""
        from click.testing import CliRunner

        from src.cli import cli

        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(cli, ["stateless-class", "nonexistent.py"])
            # Should exit with error code (typically 2 for file not found)
            assert result.exit_code != 0, "Should exit non-zero for nonexistent file"

    def test_multiple_files_argument(self):
        """CLI should accept multiple file arguments."""
        from click.testing import CliRunner

        from src.cli import cli

        runner = CliRunner()
        with runner.isolated_filesystem():
            Path("file1.py").write_text(
                """
class Good:
    def __init__(self):
        self.data = []
"""
            )
            Path("file2.py").write_text(
                """
class Bad:
    def method1(self): pass
    def method2(self): pass
"""
            )

            result = runner.invoke(cli, ["stateless-class", "file1.py", "file2.py"])
            assert result.exit_code == 1, f"Should find violation in file2: {result.output}"
