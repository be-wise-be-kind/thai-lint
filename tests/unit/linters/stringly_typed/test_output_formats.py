"""
Purpose: Tests for stringly-typed linter output formats (text, JSON, SARIF)

Scope: Output format validation for stringly-typed CLI command

Overview: Test suite validating the three output formats supported by stringly-typed
    linter: text (human-readable), JSON (machine-readable), and SARIF (CI/CD integration).
    Tests verify format correctness, structure, rule IDs, and cross-format consistency.

Dependencies: pytest, click.testing.CliRunner, src.cli, json

Exports: Test functions for output format validation

Interfaces: Uses Click CLI framework via CliRunner

Implementation: TDD approach with isolated temp directory fixtures
"""

import json

from click.testing import CliRunner

from src.cli import cli


class TestStringlyTypedTextOutput:
    """Tests for stringly-typed text output format."""

    def test_text_format_is_default(self, tmp_path):
        """Test that text format is used by default."""
        file1 = tmp_path / "file1.py"
        file1.write_text("def foo(): pass")

        runner = CliRunner()
        result = runner.invoke(cli, ["stringly-typed", str(tmp_path)])

        # Should not be JSON (no opening brace)
        assert not result.output.strip().startswith("{")

    def test_text_format_explicit(self, tmp_path):
        """Test explicit --format text option."""
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

        runner = CliRunner()
        result = runner.invoke(cli, ["stringly-typed", str(tmp_path), "--format", "text"])

        assert result.exit_code == 1
        # Text format should contain file path and line info
        assert ":" in result.output or "stringly" in result.output.lower()

    def test_text_format_shows_violation_message(self, tmp_path):
        """Test that text format shows violation message."""
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

        runner = CliRunner()
        result = runner.invoke(cli, ["stringly-typed", str(tmp_path), "--format", "text"])

        assert result.exit_code == 1
        # Should mention the pattern or string values
        assert "active" in result.output or "stringly" in result.output.lower()


class TestStringlyTypedJsonOutput:
    """Tests for stringly-typed JSON output format."""

    def test_json_format_is_valid_json(self, tmp_path):
        """Test that JSON format produces valid JSON."""
        file1 = tmp_path / "file1.py"
        file1.write_text("def foo(): pass")

        runner = CliRunner()
        result = runner.invoke(cli, ["stringly-typed", str(tmp_path), "--format", "json"])

        output = json.loads(result.output)
        assert isinstance(output, dict)

    def test_json_format_has_violations_array(self, tmp_path):
        """Test that JSON format has violations array."""
        file1 = tmp_path / "file1.py"
        file1.write_text("def foo(): pass")

        runner = CliRunner()
        result = runner.invoke(cli, ["stringly-typed", str(tmp_path), "--format", "json"])

        output = json.loads(result.output)
        assert "violations" in output
        assert isinstance(output["violations"], list)

    def test_json_format_with_violations(self, tmp_path):
        """Test JSON format structure when violations are found."""
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

        runner = CliRunner()
        result = runner.invoke(cli, ["stringly-typed", str(tmp_path), "--format", "json"])

        assert result.exit_code == 1
        output = json.loads(result.output)

        assert len(output["violations"]) > 0
        violation = output["violations"][0]
        assert "rule_id" in violation
        assert "file_path" in violation
        assert "line" in violation
        assert "message" in violation

    def test_json_format_rule_id_prefix(self, tmp_path):
        """Test that JSON violations have stringly-typed rule ID prefix."""
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

        runner = CliRunner()
        result = runner.invoke(cli, ["stringly-typed", str(tmp_path), "--format", "json"])

        output = json.loads(result.output)
        for violation in output["violations"]:
            assert violation["rule_id"].startswith("stringly-typed.")


class TestStringlyTypedSarifOutput:
    """Tests for stringly-typed SARIF output format."""

    def test_sarif_format_is_valid_json(self, tmp_path):
        """Test that SARIF format produces valid JSON."""
        file1 = tmp_path / "file1.py"
        file1.write_text("def foo(): pass")

        runner = CliRunner()
        result = runner.invoke(cli, ["stringly-typed", str(tmp_path), "--format", "sarif"])

        output = json.loads(result.output)
        assert isinstance(output, dict)

    def test_sarif_format_has_required_fields(self, tmp_path):
        """Test that SARIF format has required top-level fields."""
        file1 = tmp_path / "file1.py"
        file1.write_text("def foo(): pass")

        runner = CliRunner()
        result = runner.invoke(cli, ["stringly-typed", str(tmp_path), "--format", "sarif"])

        output = json.loads(result.output)
        assert "version" in output
        assert output["version"] == "2.1.0"
        assert "$schema" in output
        assert "runs" in output
        assert isinstance(output["runs"], list)

    def test_sarif_format_has_tool_metadata(self, tmp_path):
        """Test that SARIF format includes tool metadata."""
        file1 = tmp_path / "file1.py"
        file1.write_text("def foo(): pass")

        runner = CliRunner()
        result = runner.invoke(cli, ["stringly-typed", str(tmp_path), "--format", "sarif"])

        output = json.loads(result.output)
        driver = output["runs"][0]["tool"]["driver"]
        assert driver["name"] == "thai-lint"
        assert "version" in driver

    def test_sarif_format_has_results_array(self, tmp_path):
        """Test that SARIF format has results array."""
        file1 = tmp_path / "file1.py"
        file1.write_text("def foo(): pass")

        runner = CliRunner()
        result = runner.invoke(cli, ["stringly-typed", str(tmp_path), "--format", "sarif"])

        output = json.loads(result.output)
        run = output["runs"][0]
        assert "results" in run
        assert isinstance(run["results"], list)

    def test_sarif_format_with_violations(self, tmp_path):
        """Test SARIF format structure when violations are found."""
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

        runner = CliRunner()
        result = runner.invoke(cli, ["stringly-typed", str(tmp_path), "--format", "sarif"])

        assert result.exit_code == 1
        output = json.loads(result.output)

        results = output["runs"][0]["results"]
        assert len(results) > 0

        sarif_result = results[0]
        assert "ruleId" in sarif_result
        assert sarif_result["ruleId"].startswith("stringly-typed.")
        assert "message" in sarif_result
        assert "locations" in sarif_result

    def test_sarif_format_rule_descriptions(self, tmp_path):
        """Test that SARIF rules have proper descriptions."""
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

        runner = CliRunner()
        result = runner.invoke(cli, ["stringly-typed", str(tmp_path), "--format", "sarif"])

        output = json.loads(result.output)
        rules = output["runs"][0]["tool"]["driver"]["rules"]

        assert len(rules) > 0
        for rule in rules:
            assert "id" in rule
            assert "shortDescription" in rule
            assert "text" in rule["shortDescription"]

    def test_sarif_format_location_structure(self, tmp_path):
        """Test that SARIF locations have proper structure."""
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

        runner = CliRunner()
        result = runner.invoke(cli, ["stringly-typed", str(tmp_path), "--format", "sarif"])

        output = json.loads(result.output)
        results = output["runs"][0]["results"]

        for sarif_result in results:
            location = sarif_result["locations"][0]
            physical = location["physicalLocation"]
            assert "artifactLocation" in physical
            assert "uri" in physical["artifactLocation"]
            assert "region" in physical
            assert "startLine" in physical["region"]
            assert "startColumn" in physical["region"]


class TestStringlyTypedOutputConsistency:
    """Tests for consistency across output formats."""

    def test_exit_code_consistent_across_formats(self, tmp_path):
        """Test that exit codes are consistent across formats."""
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

        runner = CliRunner()
        text_result = runner.invoke(cli, ["stringly-typed", str(tmp_path), "--format", "text"])
        json_result = runner.invoke(cli, ["stringly-typed", str(tmp_path), "--format", "json"])
        sarif_result = runner.invoke(cli, ["stringly-typed", str(tmp_path), "--format", "sarif"])

        assert text_result.exit_code == json_result.exit_code == sarif_result.exit_code

    def test_violation_count_consistent_across_formats(self, tmp_path):
        """Test that violation counts are consistent across formats."""
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

        runner = CliRunner()
        json_result = runner.invoke(cli, ["stringly-typed", str(tmp_path), "--format", "json"])
        sarif_result = runner.invoke(cli, ["stringly-typed", str(tmp_path), "--format", "sarif"])

        json_output = json.loads(json_result.output)
        sarif_output = json.loads(sarif_result.output)

        json_count = len(json_output["violations"])
        sarif_count = len(sarif_output["runs"][0]["results"])

        assert json_count == sarif_count

    def test_short_format_option_works(self, tmp_path):
        """Test that -f short option works for all formats."""
        file1 = tmp_path / "file1.py"
        file1.write_text("def foo(): pass")

        runner = CliRunner()

        # Test each format with -f
        text_result = runner.invoke(cli, ["stringly-typed", str(tmp_path), "-f", "text"])
        json_result = runner.invoke(cli, ["stringly-typed", str(tmp_path), "-f", "json"])
        sarif_result = runner.invoke(cli, ["stringly-typed", str(tmp_path), "-f", "sarif"])

        assert text_result.exit_code == 0
        assert json_result.exit_code == 0
        assert sarif_result.exit_code == 0

        # JSON format should be valid
        json.loads(json_result.output)
        json.loads(sarif_result.output)
