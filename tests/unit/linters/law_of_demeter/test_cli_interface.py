"""
Purpose: Test CLI interface for law-of-demeter linter command

Scope: CLI command execution, output formatting, exit codes, and option handling

Overview: Validates CLI interface for the law-of-demeter linter including command availability
    and help text, violation reporting with text output, JSON output format support, SARIF
    output format support, custom configuration file handling, --min-depth option handling,
    --check-test-files flag, --recursive flag, exit code behavior (0 for pass, non-zero for
    violations), and command-line option parsing. Tests verify the thai-lint law-of-demeter
    command integrates properly with the CLI framework.

Dependencies: pytest, click.testing.CliRunner, json, src.cli

Exports: TestLawOfDemeterCLI test class

Interfaces: Tests `thai-lint law-of-demeter [OPTIONS] PATH` CLI command

Implementation: Uses CliRunner to invoke CLI commands in isolated environment, creates temporary
    files with test code, verifies output content and exit codes
"""

import json

from click.testing import CliRunner

from src.cli import cli


class TestLawOfDemeterCLI:
    """Test CLI interface for law-of-demeter linter."""

    def test_command_in_help(self) -> None:
        """law-of-demeter command should appear in main CLI help."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert "law-of-demeter" in result.output

    def test_cli_help(self) -> None:
        """CLI should show help for law-of-demeter command."""
        runner = CliRunner()
        result = runner.invoke(cli, ["law-of-demeter", "--help"])

        assert result.exit_code == 0
        assert "law of demeter" in result.output.lower()
        assert "--min-depth" in result.output

    def test_exits_0_for_clean_file(self, tmp_path) -> None:
        """CLI should exit 0 for file without violations."""
        test_file = tmp_path / "clean.py"
        test_file.write_text("""
def greet(name):
    return f"Hello {name}"
""")

        runner = CliRunner()
        result = runner.invoke(cli, ["law-of-demeter", str(test_file)])
        assert result.exit_code == 0

    def test_exits_1_for_violations(self, tmp_path) -> None:
        """CLI should exit 1 for file with violations."""
        test_file = tmp_path / "bad.py"
        test_file.write_text("""
def process(order):
    city = order.customer.address.city
""")

        runner = CliRunner()
        result = runner.invoke(cli, ["law-of-demeter", str(test_file)])
        assert result.exit_code == 1
        assert "law-of-demeter" in result.output

    def test_min_depth_flag(self, tmp_path) -> None:
        """--min-depth flag should override config."""
        test_file = tmp_path / "test.py"
        # This is depth 2 (2 dots), should be caught with min_depth=2 but not min_depth=3
        test_file.write_text("""
def f():
    x = a.b.c
""")

        runner = CliRunner()

        # With default min_depth=3, depth-2 chain should NOT be caught
        result1 = runner.invoke(cli, ["law-of-demeter", str(test_file)])
        assert result1.exit_code == 0

        # With min_depth=2, should be caught
        result2 = runner.invoke(cli, ["law-of-demeter", "--min-depth", "2", str(test_file)])
        assert result2.exit_code == 1

    def test_check_test_files_flag(self, tmp_path) -> None:
        """--check-test-files flag should control test file checking."""
        test_file = tmp_path / "test_app.py"
        test_file.write_text("""
def test_something():
    x = a.b.c.d
""")

        runner = CliRunner()

        # Default: test files NOT checked
        result1 = runner.invoke(cli, ["law-of-demeter", str(test_file)])
        assert result1.exit_code == 0

        # With flag: test files checked
        result2 = runner.invoke(cli, ["law-of-demeter", "--check-test-files", str(test_file)])
        assert result2.exit_code == 1

    def test_json_output(self, tmp_path) -> None:
        """--format json should produce valid JSON output."""
        test_file = tmp_path / "bad.py"
        test_file.write_text("""
def process(order):
    city = order.customer.address.city
""")

        runner = CliRunner()
        result = runner.invoke(cli, ["law-of-demeter", "--format", "json", str(test_file)])

        output_data = json.loads(result.output)
        assert isinstance(output_data, dict)
        assert "violations" in output_data
        assert len(output_data["violations"]) >= 1
        assert output_data["violations"][0]["rule_id"] == "law-of-demeter.chain-depth"

    def test_sarif_output(self, tmp_path) -> None:
        """--format sarif should produce valid SARIF v2.1.0 output."""
        test_file = tmp_path / "bad.py"
        test_file.write_text("""
def process(order):
    city = order.customer.address.city
""")

        runner = CliRunner()
        result = runner.invoke(cli, ["law-of-demeter", "--format", "sarif", str(test_file)])

        output_data = json.loads(result.output)
        assert output_data["version"] == "2.1.0"
        assert "runs" in output_data
        assert len(output_data["runs"][0]["results"]) >= 1

    def test_config_flag(self, tmp_path) -> None:
        """--config flag should load config file."""
        config_file = tmp_path / "custom.yaml"
        config_file.write_text("""
law_of_demeter:
  min_chain_depth: 5
""")

        test_file = tmp_path / "test.py"
        # depth-3 chain should pass with min_chain_depth=5
        test_file.write_text("""
def f():
    x = a.b.c.d
""")

        runner = CliRunner()
        result = runner.invoke(
            cli, ["law-of-demeter", "--config", str(config_file), str(test_file)]
        )
        assert result.exit_code == 0

    def test_recursive_scan(self, tmp_path) -> None:
        """--recursive should scan subdirectories."""
        subdir = tmp_path / "subdir"
        subdir.mkdir()

        test_file = subdir / "test.py"
        test_file.write_text("""
def process(order):
    city = order.customer.address.city
""")

        runner = CliRunner()
        result = runner.invoke(cli, ["law-of-demeter", str(tmp_path)])
        assert result.exit_code == 1

    def test_no_recursive_scan(self, tmp_path) -> None:
        """--no-recursive should not scan subdirectories."""
        subdir = tmp_path / "subdir"
        subdir.mkdir()

        test_file = subdir / "test.py"
        test_file.write_text("""
def process(order):
    city = order.customer.address.city
""")

        runner = CliRunner()
        result = runner.invoke(cli, ["law-of-demeter", "--no-recursive", str(tmp_path)])
        assert result.exit_code == 0
