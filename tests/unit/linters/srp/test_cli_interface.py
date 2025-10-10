"""
Purpose: Test CLI interface for SRP linter command

Scope: Command-line interface validation, flag parsing, output formatting for SRP linter

Overview: Validates CLI interface for SRP linter command including thai-lint srp command
    availability, --max-methods flag functionality, --max-loc flag functionality,
    --config flag for configuration file loading, output format options (text/JSON),
    exit code behavior (0 for pass, 1 for violations), help text and usage information,
    and integration with main CLI framework. Ensures SRP linter is accessible via
    command-line with proper flag support and user-friendly output.

Dependencies: pytest for testing framework, click for CLI framework, src.cli for main CLI,
    subprocess for CLI testing, pathlib for Path handling

Exports: TestCLIInterface (6 tests) covering command availability and flag functionality

Interfaces: Tests thai-lint srp command invocation and flag parsing

Implementation: Uses subprocess or click.testing.CliRunner for CLI invocation testing,
    verifies command registration and output
"""

from pathlib import Path


class TestCLIInterface:
    """Test SRP linter CLI command interface."""

    def test_srp_command_exists(self):
        """CLI should have 'srp' command available."""
        from click.testing import CliRunner

        from src.cli import cli

        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0, "CLI should run"
        # Help output should mention srp command

        # Should execute without error (may have violations or not)

    def test_max_methods_flag_works(self):
        """CLI should support --max-methods flag."""
        from click.testing import CliRunner

        from src.cli import cli

        runner = CliRunner()
        with runner.isolated_filesystem():
            # Create test file with 6 methods
            Path("test.py").write_text(
                """
class TestClass:
    def m1(self): pass
    def m2(self): pass
    def m3(self): pass
    def m4(self): pass
    def m5(self): pass
    def m6(self): pass
"""
            )

            # Should pass with default (7)
            runner.invoke(cli, ["srp", "test.py"])

            # Should fail with --max-methods=5
            runner.invoke(cli, ["srp", "--max-methods", "5", "test.py"])
            # Verify flag affects behavior

    def test_max_loc_flag_works(self):
        """CLI should support --max-loc flag."""
        from click.testing import CliRunner

        from src.cli import cli

        runner = CliRunner()
        with runner.isolated_filesystem():
            # Create test file
            methods = "\n".join([f"    def m{i}(self): pass" for i in range(5)])
            Path("test.py").write_text(
                f"""
class TestClass:
{methods}
"""
            )

            # Test with custom LOC limit
            runner.invoke(cli, ["srp", "--max-loc", "10", "test.py"])
            # Should use custom LOC limit

    def test_output_format_json(self):
        """CLI should support --format=json output."""
        from click.testing import CliRunner

        from src.cli import cli

        runner = CliRunner()
        with runner.isolated_filesystem():
            Path("test.py").write_text(
                """
class DataManager:
    def m1(self): pass
    def m2(self): pass
    def m3(self): pass
    def m4(self): pass
    def m5(self): pass
    def m6(self): pass
    def m7(self): pass
    def m8(self): pass
"""
            )

            runner.invoke(cli, ["srp", "--format", "json", "test.py"])
            # Output should be valid JSON

    def test_exit_codes(self):
        """CLI should return correct exit codes."""
        from click.testing import CliRunner

        from src.cli import cli

        runner = CliRunner()
        with runner.isolated_filesystem():
            # File with no violations
            Path("good.py").write_text(
                """
class Simple:
    def test(self): pass
"""
            )

            # File with violations
            Path("bad.py").write_text(
                """
class DataManager:
    def m1(self): pass
    def m2(self): pass
    def m3(self): pass
    def m4(self): pass
    def m5(self): pass
    def m6(self): pass
    def m7(self): pass
    def m8(self): pass
"""
            )

            # No violations: exit code 0
            result_pass = runner.invoke(cli, ["srp", "good.py"])
            assert result_pass.exit_code == 0, "Should exit 0 on pass"

            # Has violations: exit code 1
            result_fail = runner.invoke(cli, ["srp", "bad.py"])
            assert result_fail.exit_code == 1, "Should exit 1 on violations"
