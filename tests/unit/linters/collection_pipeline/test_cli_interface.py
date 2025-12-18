"""
Purpose: Test CLI interface for collection-pipeline linter

Scope: CLI command execution, output formatting, and exit codes

Overview: Validates CLI interface for the collection-pipeline linter including command availability
    and help text, violation reporting with text output format, JSON output format support, SARIF
    output format support, custom configuration file handling, --min-continues option handling,
    exit code behavior (0 for pass, non-zero for violations), and command-line option parsing.
    Tests verify the thai-lint pipeline command integrates properly with the CLI framework.

Dependencies: pytest for testing framework, click.testing.CliRunner for CLI testing,
    src.cli for CLI commands, pathlib for temporary files

Exports: TestPipelineCLI test class covering command interface

Interfaces: Tests `thai-lint pipeline [OPTIONS] PATH` CLI command

Implementation: Uses CliRunner to invoke CLI commands in isolated environment, creates temporary
    files with test code, verifies output content and exit codes
"""

import json

from click.testing import CliRunner

from src.cli import cli


class TestPipelineCLI:
    """Test CLI interface for collection-pipeline linter."""

    def test_cli_help(self) -> None:
        """CLI should show help for pipeline command."""
        runner = CliRunner()
        result = runner.invoke(cli, ["pipeline", "--help"])

        assert result.exit_code == 0
        assert "collection pipeline" in result.output.lower()
        assert "--min-continues" in result.output

    def test_cli_detects_violation(self, tmp_path) -> None:
        """CLI should detect embedded filtering patterns."""
        test_file = tmp_path / "test.py"
        test_file.write_text("""
for item in items:
    if not item.is_valid():
        continue
    process(item)
""")

        runner = CliRunner()
        result = runner.invoke(cli, ["pipeline", str(test_file)])

        assert result.exit_code != 0
        assert "collection-pipeline" in result.output

    def test_cli_no_violation_for_clean_code(self, tmp_path) -> None:
        """CLI should exit 0 for clean code."""
        test_file = tmp_path / "test.py"
        test_file.write_text("""
for item in items:
    process(item)
""")

        runner = CliRunner()
        result = runner.invoke(cli, ["pipeline", str(test_file)])

        assert result.exit_code == 0

    def test_cli_json_output(self, tmp_path) -> None:
        """CLI should support JSON output format."""
        test_file = tmp_path / "test.py"
        test_file.write_text("""
for item in items:
    if not item.is_valid():
        continue
    process(item)
""")

        runner = CliRunner()
        result = runner.invoke(cli, ["pipeline", "--format", "json", str(test_file)])

        # Should output valid JSON
        output_data = json.loads(result.output)
        assert isinstance(output_data, dict)
        assert "violations" in output_data
        assert len(output_data["violations"]) == 1
        assert output_data["violations"][0]["rule_id"] == "collection-pipeline.embedded-filter"

    def test_cli_sarif_output(self, tmp_path) -> None:
        """CLI should support SARIF output format."""
        test_file = tmp_path / "test.py"
        test_file.write_text("""
for item in items:
    if not item.is_valid():
        continue
    process(item)
""")

        runner = CliRunner()
        result = runner.invoke(cli, ["pipeline", "--format", "sarif", str(test_file)])

        # Should output valid SARIF JSON
        output_data = json.loads(result.output)
        assert output_data["version"] == "2.1.0"
        assert "runs" in output_data
        assert len(output_data["runs"][0]["results"]) == 1

    def test_cli_min_continues_option(self, tmp_path) -> None:
        """CLI should respect --min-continues option."""
        test_file = tmp_path / "test.py"
        test_file.write_text("""
for item in items:
    if not item.is_valid():
        continue
    process(item)
""")

        runner = CliRunner()

        # With min_continues=1 (default), should find violation
        result1 = runner.invoke(cli, ["pipeline", str(test_file)])
        assert result1.exit_code != 0

        # With min_continues=2, should NOT find violation (only 1 continue guard)
        result2 = runner.invoke(cli, ["pipeline", "--min-continues", "2", str(test_file)])
        assert result2.exit_code == 0

    def test_cli_custom_config(self, tmp_path) -> None:
        """CLI should support --config flag."""
        config_file = tmp_path / "custom.yaml"
        config_file.write_text("""
collection_pipeline:
  min_continues: 2
""")

        test_file = tmp_path / "test.py"
        test_file.write_text("""
for item in items:
    if not item.is_valid():
        continue
    process(item)
""")

        runner = CliRunner()
        result = runner.invoke(cli, ["pipeline", "--config", str(config_file), str(test_file)])

        # Should apply custom config and NOT find violation (only 1 continue, min is 2)
        assert result.exit_code == 0

    def test_cli_multiple_violations(self, tmp_path) -> None:
        """CLI should report multiple violations."""
        test_file = tmp_path / "test.py"
        test_file.write_text("""
for item in items:
    if not item.valid:
        continue
    process1(item)

for other in others:
    if other.skip:
        continue
    process2(other)
""")

        runner = CliRunner()
        result = runner.invoke(cli, ["pipeline", "--format", "json", str(test_file)])

        output_data = json.loads(result.output)
        assert output_data["total"] == 2

    def test_cli_directory_recursive(self, tmp_path) -> None:
        """CLI should scan directories recursively by default."""
        subdir = tmp_path / "subdir"
        subdir.mkdir()

        test_file = subdir / "test.py"
        test_file.write_text("""
for item in items:
    if not item.valid:
        continue
    process(item)
""")

        runner = CliRunner()
        result = runner.invoke(cli, ["pipeline", str(tmp_path)])

        assert result.exit_code != 0
        assert "collection-pipeline" in result.output
