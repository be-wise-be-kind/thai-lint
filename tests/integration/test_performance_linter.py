"""
Purpose: End-to-end integration tests for performance linter CLI commands

Scope: perf, string-concat-loop, and regex-in-loop commands with all output formats

Overview: Comprehensive integration tests validating the performance linter CLI commands work
    correctly end-to-end. Tests cover: CLI help text, basic linting with violations, exit codes,
    output formats (text, JSON, SARIF), --rule filtering, config file loading, and recursive
    directory scanning. Uses Click CliRunner for isolated command execution.

Dependencies: pytest for testing, Click CliRunner for CLI testing, json for output parsing

Exports: TestPerfCLIHelp, TestPerfCLILinting, TestPerfCLIExitCodes, TestPerfCLIOutputFormats,
    TestPerfCLIRuleFiltering, TestStringConcatLoopCLI, TestRegexInLoopCLI test classes

Interfaces: Click CliRunner invocation, subprocess-free CLI testing

Implementation: Uses CliRunner for isolated command testing, temporary files with known
    performance violations, comprehensive assertions on stdout/stderr/exit codes
"""

import json

from click.testing import CliRunner

from src.cli import cli

# =============================================================================
# Test Fixtures - Code samples with known violations
# =============================================================================

PYTHON_STRING_CONCAT_VIOLATION = """
def build_message(items):
    result = ""
    for item in items:
        result += str(item)
    return result
"""

PYTHON_REGEX_VIOLATION = """
import re

def find_matches(lines, pattern):
    matches = []
    for line in lines:
        if re.match(pattern, line):
            matches.append(line)
    return matches
"""

PYTHON_BOTH_VIOLATIONS = """
import re

def process_data(items, pattern):
    result = ""
    for item in items:
        result += str(item)
        if re.search(pattern, str(item)):
            result += " (matched)"
    return result
"""

PYTHON_NO_VIOLATIONS = """
def build_message(items):
    return "".join(str(item) for item in items)

import re

def find_matches(lines, pattern):
    compiled = re.compile(pattern)
    return [line for line in lines if compiled.match(line)]
"""

TYPESCRIPT_STRING_CONCAT_VIOLATION = """
function buildMessage(items: string[]): string {
    let result = "";
    for (const item of items) {
        result += item;
    }
    return result;
}
"""


# =============================================================================
# Perf Command Tests
# =============================================================================


class TestPerfCLIHelp:
    """Test perf command help text and availability."""

    def test_perf_command_exists(self) -> None:
        """Test that perf command is available in CLI."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])

        assert result.exit_code == 0
        assert "perf" in result.output

    def test_perf_help_shows_usage(self) -> None:
        """Test that perf --help shows usage information."""
        runner = CliRunner()
        result = runner.invoke(cli, ["perf", "--help"])

        assert result.exit_code == 0
        assert "Usage:" in result.output
        assert "performance" in result.output.lower()
        assert "--rule" in result.output
        assert "--format" in result.output

    def test_perf_help_shows_rule_options(self) -> None:
        """Test that perf --help shows available rule options."""
        runner = CliRunner()
        result = runner.invoke(cli, ["perf", "--help"])

        assert result.exit_code == 0
        assert "string-concat" in result.output
        assert "regex-loop" in result.output


class TestPerfCLILinting:
    """Test perf command linting functionality."""

    def test_perf_detects_string_concat_violation(self, tmp_path) -> None:
        """Test perf command detects string concatenation in loop."""
        test_file = tmp_path / "concat.py"
        test_file.write_text(PYTHON_STRING_CONCAT_VIOLATION)

        runner = CliRunner()
        result = runner.invoke(cli, ["perf", str(test_file)])

        assert result.exit_code == 1
        assert "string-concat-loop" in result.output

    def test_perf_detects_regex_violation(self, tmp_path) -> None:
        """Test perf command detects regex compilation in loop."""
        test_file = tmp_path / "regex.py"
        test_file.write_text(PYTHON_REGEX_VIOLATION)

        runner = CliRunner()
        result = runner.invoke(cli, ["perf", str(test_file)])

        assert result.exit_code == 1
        assert "regex-in-loop" in result.output

    def test_perf_detects_both_violations(self, tmp_path) -> None:
        """Test perf command detects both types of violations."""
        test_file = tmp_path / "both.py"
        test_file.write_text(PYTHON_BOTH_VIOLATIONS)

        runner = CliRunner()
        result = runner.invoke(cli, ["perf", str(test_file)])

        assert result.exit_code == 1
        assert "string-concat-loop" in result.output
        assert "regex-in-loop" in result.output

    def test_perf_passes_clean_code(self, tmp_path) -> None:
        """Test perf command passes code without violations."""
        test_file = tmp_path / "clean.py"
        test_file.write_text(PYTHON_NO_VIOLATIONS)

        runner = CliRunner()
        result = runner.invoke(cli, ["perf", str(test_file)])

        assert result.exit_code == 0


class TestPerfCLIExitCodes:
    """Test perf command exit codes follow conventions."""

    def test_exit_code_0_no_violations(self, tmp_path) -> None:
        """Test exit code 0 when no violations found."""
        test_file = tmp_path / "clean.py"
        test_file.write_text(PYTHON_NO_VIOLATIONS)

        runner = CliRunner()
        result = runner.invoke(cli, ["perf", str(test_file)])

        assert result.exit_code == 0

    def test_exit_code_1_with_violations(self, tmp_path) -> None:
        """Test exit code 1 when violations found."""
        test_file = tmp_path / "violation.py"
        test_file.write_text(PYTHON_STRING_CONCAT_VIOLATION)

        runner = CliRunner()
        result = runner.invoke(cli, ["perf", str(test_file)])

        assert result.exit_code == 1

    def test_exit_code_2_on_error(self) -> None:
        """Test exit code 2 on file not found error."""
        runner = CliRunner()
        result = runner.invoke(cli, ["perf", "nonexistent_file.py"])

        assert result.exit_code == 2


class TestPerfCLIOutputFormats:
    """Test perf command output format options."""

    def test_json_output_format(self, tmp_path) -> None:
        """Test perf command with JSON output format."""
        test_file = tmp_path / "violation.py"
        test_file.write_text(PYTHON_STRING_CONCAT_VIOLATION)

        runner = CliRunner()
        result = runner.invoke(cli, ["perf", "--format", "json", str(test_file)])

        assert result.exit_code == 1
        data = json.loads(result.output)
        assert "violations" in data
        assert data["total"] > 0
        assert any("string-concat-loop" in v["rule_id"] for v in data["violations"])

    def test_sarif_output_format(self, tmp_path) -> None:
        """Test perf command with SARIF output format."""
        test_file = tmp_path / "violation.py"
        test_file.write_text(PYTHON_STRING_CONCAT_VIOLATION)

        runner = CliRunner()
        result = runner.invoke(cli, ["perf", "--format", "sarif", str(test_file)])

        assert result.exit_code == 1
        data = json.loads(result.output)
        assert data["version"] == "2.1.0"
        assert data["runs"][0]["tool"]["driver"]["name"] == "thai-lint"
        assert len(data["runs"][0]["results"]) > 0

    def test_sarif_contains_performance_rule_ids(self, tmp_path) -> None:
        """Test SARIF output contains performance rule IDs."""
        test_file = tmp_path / "both.py"
        test_file.write_text(PYTHON_BOTH_VIOLATIONS)

        runner = CliRunner()
        result = runner.invoke(cli, ["perf", "--format", "sarif", str(test_file)])

        data = json.loads(result.output)
        rule_ids = [r["ruleId"] for r in data["runs"][0]["results"]]
        assert any("performance.string-concat-loop" in rid for rid in rule_ids)
        assert any("performance.regex-in-loop" in rid for rid in rule_ids)


class TestPerfCLIRuleFiltering:
    """Test perf command --rule filtering option."""

    def test_rule_filter_string_concat_only(self, tmp_path) -> None:
        """Test --rule string-concat filters to string concat violations only."""
        test_file = tmp_path / "both.py"
        test_file.write_text(PYTHON_BOTH_VIOLATIONS)

        runner = CliRunner()
        result = runner.invoke(cli, ["perf", "--rule", "string-concat", str(test_file)])

        assert result.exit_code == 1
        assert "string-concat-loop" in result.output
        assert "regex-in-loop" not in result.output

    def test_rule_filter_regex_loop_only(self, tmp_path) -> None:
        """Test --rule regex-loop filters to regex violations only."""
        test_file = tmp_path / "both.py"
        test_file.write_text(PYTHON_BOTH_VIOLATIONS)

        runner = CliRunner()
        result = runner.invoke(cli, ["perf", "--rule", "regex-loop", str(test_file)])

        assert result.exit_code == 1
        assert "regex-in-loop" in result.output
        assert "string-concat-loop" not in result.output

    def test_rule_filter_with_no_matching_violations(self, tmp_path) -> None:
        """Test --rule filter with no matching violations passes."""
        test_file = tmp_path / "concat_only.py"
        test_file.write_text(PYTHON_STRING_CONCAT_VIOLATION)

        runner = CliRunner()
        result = runner.invoke(cli, ["perf", "--rule", "regex-loop", str(test_file)])

        # No regex violations in string concat file
        assert result.exit_code == 0


class TestPerfCLIRecursive:
    """Test perf command recursive directory scanning."""

    def test_recursive_scan_finds_nested_violations(self, tmp_path) -> None:
        """Test perf command recursively scans subdirectories."""
        # Create nested structure
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        nested_dir = src_dir / "nested"
        nested_dir.mkdir()

        (src_dir / "concat.py").write_text(PYTHON_STRING_CONCAT_VIOLATION)
        (nested_dir / "regex.py").write_text(PYTHON_REGEX_VIOLATION)

        runner = CliRunner()
        result = runner.invoke(cli, ["perf", "--recursive", str(src_dir)])

        assert result.exit_code == 1
        # Should find violations in both files
        assert "string-concat-loop" in result.output
        assert "regex-in-loop" in result.output


# =============================================================================
# String Concat Loop Command Tests
# =============================================================================


class TestStringConcatLoopCLI:
    """Test string-concat-loop individual command."""

    def test_command_exists(self) -> None:
        """Test that string-concat-loop command is available."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])

        assert result.exit_code == 0
        assert "string-concat-loop" in result.output

    def test_detects_violation(self, tmp_path) -> None:
        """Test string-concat-loop detects concatenation in loop."""
        test_file = tmp_path / "concat.py"
        test_file.write_text(PYTHON_STRING_CONCAT_VIOLATION)

        runner = CliRunner()
        result = runner.invoke(cli, ["string-concat-loop", str(test_file)])

        assert result.exit_code == 1
        assert "string-concat-loop" in result.output

    def test_ignores_regex_violations(self, tmp_path) -> None:
        """Test string-concat-loop ignores regex violations."""
        test_file = tmp_path / "regex.py"
        test_file.write_text(PYTHON_REGEX_VIOLATION)

        runner = CliRunner()
        result = runner.invoke(cli, ["string-concat-loop", str(test_file)])

        # Should pass - no string concat violations
        assert result.exit_code == 0

    def test_typescript_support(self, tmp_path) -> None:
        """Test string-concat-loop works with TypeScript."""
        test_file = tmp_path / "concat.ts"
        test_file.write_text(TYPESCRIPT_STRING_CONCAT_VIOLATION)

        runner = CliRunner()
        result = runner.invoke(cli, ["string-concat-loop", str(test_file)])

        assert result.exit_code == 1
        assert "string-concat-loop" in result.output

    def test_json_output(self, tmp_path) -> None:
        """Test string-concat-loop with JSON output."""
        test_file = tmp_path / "concat.py"
        test_file.write_text(PYTHON_STRING_CONCAT_VIOLATION)

        runner = CliRunner()
        result = runner.invoke(cli, ["string-concat-loop", "--format", "json", str(test_file)])

        assert result.exit_code == 1
        data = json.loads(result.output)
        assert data["total"] > 0


# =============================================================================
# Regex In Loop Command Tests
# =============================================================================


class TestRegexInLoopCLI:
    """Test regex-in-loop individual command."""

    def test_command_exists(self) -> None:
        """Test that regex-in-loop command is available."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])

        assert result.exit_code == 0
        assert "regex-in-loop" in result.output

    def test_detects_violation(self, tmp_path) -> None:
        """Test regex-in-loop detects regex compilation in loop."""
        test_file = tmp_path / "regex.py"
        test_file.write_text(PYTHON_REGEX_VIOLATION)

        runner = CliRunner()
        result = runner.invoke(cli, ["regex-in-loop", str(test_file)])

        assert result.exit_code == 1
        assert "regex-in-loop" in result.output

    def test_ignores_string_concat_violations(self, tmp_path) -> None:
        """Test regex-in-loop ignores string concat violations."""
        test_file = tmp_path / "concat.py"
        test_file.write_text(PYTHON_STRING_CONCAT_VIOLATION)

        runner = CliRunner()
        result = runner.invoke(cli, ["regex-in-loop", str(test_file)])

        # Should pass - no regex violations
        assert result.exit_code == 0

    def test_json_output(self, tmp_path) -> None:
        """Test regex-in-loop with JSON output."""
        test_file = tmp_path / "regex.py"
        test_file.write_text(PYTHON_REGEX_VIOLATION)

        runner = CliRunner()
        result = runner.invoke(cli, ["regex-in-loop", "--format", "json", str(test_file)])

        assert result.exit_code == 1
        data = json.loads(result.output)
        assert data["total"] > 0

    def test_sarif_output(self, tmp_path) -> None:
        """Test regex-in-loop with SARIF output."""
        test_file = tmp_path / "regex.py"
        test_file.write_text(PYTHON_REGEX_VIOLATION)

        runner = CliRunner()
        result = runner.invoke(cli, ["regex-in-loop", "--format", "sarif", str(test_file)])

        assert result.exit_code == 1
        data = json.loads(result.output)
        assert data["version"] == "2.1.0"
        assert any("regex-in-loop" in r["ruleId"] for r in data["runs"][0]["results"])


# =============================================================================
# Config File Tests
# =============================================================================


class TestPerfCLIConfig:
    """Test perf command with config file options."""

    def test_with_config_file(self, tmp_path) -> None:
        """Test perf command respects config file."""
        test_file = tmp_path / "concat.py"
        test_file.write_text(PYTHON_STRING_CONCAT_VIOLATION)

        config_file = tmp_path / ".thailint.yaml"
        config_file.write_text("""
performance:
  enabled: true
  string-concat-loop:
    enabled: true
  regex-in-loop:
    enabled: true
""")

        runner = CliRunner()
        result = runner.invoke(cli, ["perf", "--config", str(config_file), str(test_file)])

        assert result.exit_code == 1
        assert "string-concat-loop" in result.output
