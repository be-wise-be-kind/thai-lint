"""
Purpose: Test CLI interface for nesting depth linter

Scope: CLI command execution, output formatting, and exit codes

Overview: Validates CLI interface for the nesting depth linter including command availability and
    help text, violation reporting with text output format, JSON output format support, custom
    configuration file handling, exit code behavior (0 for pass, non-zero for violations), and
    command-line option parsing. Tests verify the thai lint nesting command integrates properly
    with the CLI framework, provides user-friendly output, and follows CLI conventions for success
    and failure indication through exit codes.

Dependencies: pytest for testing framework, click.testing.CliRunner for CLI testing,
    src.cli for CLI commands, pathlib for temporary files

Exports: TestNestingCLI (4 tests) covering command availability, violation reporting, JSON output,
    and custom config

Interfaces: Tests `thai lint nesting [OPTIONS] PATH` CLI command

Implementation: Uses CliRunner to invoke CLI commands in isolated environment, creates temporary
    files with test code, verifies output content and exit codes
"""

import pytest
from click.testing import CliRunner


class TestNestingCLI:
    """Test CLI interface for nesting linter."""

    def test_cli_json_output(self, tmp_path):
        """CLI should support JSON output format."""
        import json

        from src.cli import cli

        # Create temp file with nesting violation
        test_file = tmp_path / "test.py"
        test_file.write_text("""
def nested_func():
    for i in range(5):
        for j in range(5):
            for k in range(5):
                for m in range(5):
                    print(i, j, k, m)
""")

        runner = CliRunner()
        result = runner.invoke(cli, ["nesting", "--format", "json", str(test_file)])

        # Should output valid JSON
        try:
            output_data = json.loads(result.output)
            assert isinstance(output_data, (list, dict)), "JSON output should be list or dict"
        except json.JSONDecodeError:
            pytest.fail(f"Output should be valid JSON. Got: {result.output}")

    def test_cli_custom_config(self, tmp_path):
        """CLI should support --config flag."""
        from src.cli import cli

        # Create custom config file
        config_file = tmp_path / "custom.yaml"
        config_file.write_text("""
nesting:
  max_nesting_depth: 2
""")

        # Create test file with depth 3 (should violate limit 2)
        # Note: Depth counts control structures only - each if/for/while adds 1
        test_file = tmp_path / "test.py"
        test_file.write_text("""
def test_func():
    if True:
        if True:
            if True:
                print("depth 3")
""")

        runner = CliRunner()
        result = runner.invoke(cli, ["nesting", "--config", str(config_file), str(test_file)])

        # Should apply custom config and find violation (depth 3 > limit 2)
        assert result.exit_code != 0, "Should find violation with custom limit 2"
