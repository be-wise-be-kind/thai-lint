"""
Purpose: CLI integration tests for SARIF output format option

Scope: CLI invocation with --format sarif, output validation, exit codes

Overview: Integration tests validating thai-lint CLI properly handles --format sarif option
    across all 5 linters (file-placement, nesting, srp, dry, magic-numbers). Tests CLI
    invocation, SARIF output structure, JSON validity, exit codes (0 for no violations,
    1 for violations), and stderr vs stdout handling. Following TDD methodology - tests
    written BEFORE implementation, all tests MUST FAIL initially.

Dependencies: pytest, click.testing.CliRunner, src.cli (CLI commands)

Exports: 15+ CLI integration test functions

Interfaces: Click testing runner, JSON parsing for output validation

Implementation: TDD approach with CLI testing patterns, expects "sarif" format option in PR3
"""

import json

from click.testing import CliRunner

from src.cli import cli

# === CLI Invocation Tests (5 tests) ===


class TestCliSarifInvocation:
    """Tests for CLI invocation with --format sarif option."""

    def test_file_placement_accepts_sarif_format(self, tmp_path) -> None:
        """file-placement command accepts --format sarif option."""
        test_file = tmp_path / "test.py"
        test_file.write_text("# test file")

        runner = CliRunner()
        result = runner.invoke(cli, ["file-placement", "--format", "sarif", str(tmp_path)])

        # Should not error on invalid option (sarif should be valid)
        assert "Invalid value for '--format'" not in result.output

    def test_nesting_accepts_sarif_format(self, tmp_path) -> None:
        """nesting command accepts --format sarif option."""
        test_file = tmp_path / "test.py"
        test_file.write_text("# test file")

        runner = CliRunner()
        result = runner.invoke(cli, ["nesting", "--format", "sarif", str(tmp_path)])

        assert "Invalid value for '--format'" not in result.output

    def test_srp_accepts_sarif_format(self, tmp_path) -> None:
        """srp command accepts --format sarif option."""
        test_file = tmp_path / "test.py"
        test_file.write_text("# test file")

        runner = CliRunner()
        result = runner.invoke(cli, ["srp", "--format", "sarif", str(tmp_path)])

        assert "Invalid value for '--format'" not in result.output

    def test_dry_accepts_sarif_format(self, tmp_path) -> None:
        """dry command accepts --format sarif option."""
        test_file = tmp_path / "test.py"
        test_file.write_text("# test file")

        config = tmp_path / ".thailint.yaml"
        config.write_text("dry:\n  enabled: true\n  cache_enabled: false")

        runner = CliRunner()
        result = runner.invoke(
            cli, ["dry", "--format", "sarif", str(tmp_path), "--config", str(config)]
        )

        assert "Invalid value for '--format'" not in result.output

    def test_magic_numbers_accepts_sarif_format(self, tmp_path) -> None:
        """magic-numbers command accepts --format sarif option."""
        test_file = tmp_path / "test.py"
        test_file.write_text("# test file")

        runner = CliRunner()
        result = runner.invoke(cli, ["magic-numbers", "--format", "sarif", str(tmp_path)])

        assert "Invalid value for '--format'" not in result.output


# === Output Structure Tests (5 tests) ===


class TestCliSarifOutputStructure:
    """Tests for SARIF output structure from CLI commands."""

    def test_sarif_output_is_valid_json(self, tmp_path) -> None:
        """SARIF output must be valid JSON."""
        test_file = tmp_path / "test.py"
        test_file.write_text("# test file")

        runner = CliRunner()
        result = runner.invoke(cli, ["nesting", "--format", "sarif", str(test_file)])

        # Should be parsable JSON
        output = json.loads(result.output)
        assert isinstance(output, dict)

    def test_sarif_output_has_required_top_level_fields(self, tmp_path) -> None:
        """SARIF output must have version, $schema, runs at top level."""
        test_file = tmp_path / "test.py"
        test_file.write_text("# test")

        runner = CliRunner()
        result = runner.invoke(cli, ["srp", "--format", "sarif", str(test_file)])

        output = json.loads(result.output)
        assert "version" in output
        assert "$schema" in output
        assert "runs" in output

    def test_sarif_output_version_is_2_1_0(self, tmp_path) -> None:
        """SARIF output version must be 2.1.0."""
        test_file = tmp_path / "test.py"
        test_file.write_text("# test")

        runner = CliRunner()
        result = runner.invoke(cli, ["file-placement", "--format", "sarif", str(test_file)])

        output = json.loads(result.output)
        assert output["version"] == "2.1.0"

    def test_sarif_output_has_tool_metadata(self, tmp_path) -> None:
        """SARIF output must include tool metadata."""
        test_file = tmp_path / "test.py"
        test_file.write_text("# test")

        config = tmp_path / ".thailint.yaml"
        config.write_text("dry:\n  enabled: true\n  cache_enabled: false")

        runner = CliRunner()
        result = runner.invoke(
            cli, ["dry", "--format", "sarif", str(tmp_path), "--config", str(config)]
        )

        output = json.loads(result.output)
        driver = output["runs"][0]["tool"]["driver"]
        assert driver["name"] == "thai-lint"
        assert "version" in driver

    def test_sarif_output_has_results_array(self, tmp_path) -> None:
        """SARIF output must have results array."""
        test_file = tmp_path / "test.py"
        test_file.write_text("# test")

        runner = CliRunner()
        result = runner.invoke(cli, ["magic-numbers", "--format", "sarif", str(test_file)])

        output = json.loads(result.output)
        run = output["runs"][0]
        assert "results" in run
        assert isinstance(run["results"], list)


# === Exit Code Tests (3 tests) ===


class TestCliSarifExitCodes:
    """Tests for CLI exit codes with SARIF output."""

    def test_sarif_exit_code_zero_when_no_violations(self, tmp_path) -> None:
        """CLI exits with 0 when no violations found (SARIF format)."""
        # Create valid file (no violations)
        test_file = tmp_path / "valid.py"
        test_file.write_text("# valid Python file\nx = 1")

        runner = CliRunner()
        result = runner.invoke(cli, ["nesting", "--format", "sarif", str(test_file)])

        assert result.exit_code == 0

    def test_sarif_exit_code_one_when_violations_found(self, tmp_path) -> None:
        """CLI exits with 1 when violations found (SARIF format)."""
        # Create file with deeply nested code that will trigger violation
        test_file = tmp_path / "deeply_nested.py"
        test_file.write_text("""
def deeply_nested():
    if True:
        for i in range(10):
            while True:
                if i > 5:
                    for j in range(5):
                        if j > 2:
                            print(i, j)
""")

        runner = CliRunner()
        result = runner.invoke(cli, ["nesting", "--format", "sarif", str(test_file)])

        # Should have violations due to deep nesting
        assert result.exit_code == 1

    def test_sarif_exit_code_consistent_with_json_format(self, tmp_path) -> None:
        """SARIF and JSON formats produce same exit codes for same input."""
        test_file = tmp_path / "test.py"
        test_file.write_text("# simple test file\nx = 1")

        runner = CliRunner()
        json_result = runner.invoke(cli, ["srp", "--format", "json", str(test_file)])
        sarif_result = runner.invoke(cli, ["srp", "--format", "sarif", str(test_file)])

        assert json_result.exit_code == sarif_result.exit_code


# === Output Routing Tests (2 tests) ===


class TestCliSarifOutputRouting:
    """Tests for CLI output routing with SARIF format."""

    def test_sarif_output_goes_to_stdout(self, tmp_path) -> None:
        """SARIF output is written to stdout, not stderr."""
        test_file = tmp_path / "test.py"
        test_file.write_text("# test")

        runner = CliRunner()
        result = runner.invoke(cli, ["nesting", "--format", "sarif", str(test_file)])

        # Output should be in stdout (result.output)
        # and be valid SARIF JSON
        output = json.loads(result.output)
        assert output["version"] == "2.1.0"

    def test_sarif_format_does_not_print_text_violations(self, tmp_path) -> None:
        """SARIF format does not print text-formatted violations."""
        test_file = tmp_path / "test.py"
        test_file.write_text("# test")

        runner = CliRunner()
        result = runner.invoke(cli, ["file-placement", "--format", "sarif", str(test_file)])

        # Output should be JSON, not text like "file.py:1:0 - message"
        # Should start with { (JSON object)
        assert result.output.strip().startswith("{")


# === Additional CLI Tests ===


class TestCliSarifAdditional:
    """Additional CLI tests for SARIF output edge cases."""

    def test_sarif_output_with_recursive_flag(self, tmp_path) -> None:
        """SARIF output works with --recursive flag."""
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        test_file = subdir / "test.py"
        test_file.write_text("# test in subdir")

        runner = CliRunner()
        result = runner.invoke(cli, ["nesting", "--format", "sarif", "--recursive", str(tmp_path)])

        output = json.loads(result.output)
        assert output["version"] == "2.1.0"

    def test_sarif_output_with_no_recursive_flag(self, tmp_path) -> None:
        """SARIF output works with --no-recursive flag."""
        test_file = tmp_path / "test.py"
        test_file.write_text("# test file")

        runner = CliRunner()
        result = runner.invoke(cli, ["srp", "--format", "sarif", "--no-recursive", str(tmp_path)])

        output = json.loads(result.output)
        assert output["version"] == "2.1.0"

    def test_sarif_output_contains_violations_when_present(self, tmp_path) -> None:
        """SARIF output contains results when violations are found."""
        # Create file with magic number that should trigger violation
        test_file = tmp_path / "magic.py"
        test_file.write_text("""
def calculate():
    timeout = 3600  # magic number
    retries = 12345  # magic number
    return timeout * retries
""")

        runner = CliRunner()
        result = runner.invoke(cli, ["magic-numbers", "--format", "sarif", str(test_file)])

        output = json.loads(result.output)
        run = output["runs"][0]
        # Should have violations for magic numbers
        assert "results" in run

    def test_sarif_short_format_option(self, tmp_path) -> None:
        """SARIF output works with short -f option."""
        test_file = tmp_path / "test.py"
        test_file.write_text("# test")

        runner = CliRunner()
        result = runner.invoke(cli, ["nesting", "-f", "sarif", str(test_file)])

        output = json.loads(result.output)
        assert output["version"] == "2.1.0"
