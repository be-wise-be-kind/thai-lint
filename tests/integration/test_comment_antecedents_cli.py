"""
Purpose: Integration tests for comment-antecedents output through the file-header CLI command

Scope: Text, JSON, and SARIF v2.1.0 output and exit codes for the comment-antecedents rule id

Overview: Test suite verifying that the comment-antecedents rule reaches users through the existing
    file-header command rather than a command of its own. The command selects violations by rule-id
    namespace, so a rule registered under the file-header prefix inherits text, json, and SARIF output
    without new CLI wiring. These tests pin that inheritance, confirm the SARIF run declares a descriptor
    for the new rule id so CI tooling can address it separately from header validation, and check exit
    code behaviour for clean and failing runs.

Dependencies: pytest, click.testing.CliRunner, src.cli.main.cli

Exports: TestCommentAntecedentsCliOutput, TestCommentAntecedentsExitCodes

Interfaces: Invokes the file-header CLI command with --format text, json, and sarif

Implementation: CliRunner invocation against files written into tmp_path, with JSON and SARIF responses
    parsed and asserted structurally
"""

import json

import pytest
from click.testing import CliRunner

from src.cli.main import cli

RULE_ID = "file-header.comment-antecedents"

# A complete, valid header. Every mandatory field is present so that header validation itself
# reports nothing and the only violation a fixture can produce is a comment-antecedents one.
PY_HEADER = '''"""
Purpose: Fixture module exercising comment-antecedents output formats
Scope: Integration test fixture
Overview: Provides a syntactically complete file header so that header field validation
    reports nothing, isolating the comment-antecedents rule as the only possible source
    of a violation in these fixtures.
Dependencies: None
Exports: A single module-level assignment
Interfaces: None
Implementation: Module-level assignment beneath a mid-file comment
"""
'''


@pytest.fixture
def offending_file(tmp_path):
    """Write a Python file carrying one comment-antecedents violation."""
    path = tmp_path / "offender.py"
    path.write_text(f"{PY_HEADER}\n\n# the flag used to be a boolean\nx = 1\n")
    return path


@pytest.fixture
def clean_file(tmp_path):
    """Write a Python file with no matching comment."""
    path = tmp_path / "clean.py"
    path.write_text(f"{PY_HEADER}\n\n# the flag is a boolean\nx = 1\n")
    return path


class TestCommentAntecedentsCliOutput:
    """Test the three inherited output formats."""

    def test_json_output_carries_the_new_rule_id(self, offending_file):
        """Should emit the comment-antecedents rule id in JSON output."""
        runner = CliRunner()
        result = runner.invoke(cli, ["file-header", "--format", "json", str(offending_file)])

        payload = json.loads(result.output)
        violations = payload if isinstance(payload, list) else payload.get("violations", [])

        assert any(v["rule_id"] == RULE_ID for v in violations)

    def test_text_output_names_the_rule(self, offending_file):
        """Should name the rule in human-readable output."""
        runner = CliRunner()
        result = runner.invoke(cli, ["file-header", "--format", "text", str(offending_file)])

        assert RULE_ID in result.output

    def test_sarif_output_declares_the_new_rule_descriptor(self, offending_file):
        """Should emit SARIF v2.1.0 declaring a descriptor for the comment-antecedents rule id."""
        runner = CliRunner()
        result = runner.invoke(cli, ["file-header", "--format", "sarif", str(offending_file)])

        sarif = json.loads(result.output)
        descriptors = sarif["runs"][0]["tool"]["driver"]["rules"]

        assert sarif["version"] == "2.1.0"
        assert any(d["id"] == RULE_ID for d in descriptors)


class TestCommentAntecedentsExitCodes:
    """Test process exit codes."""

    def test_a_run_with_violations_exits_non_zero(self, offending_file):
        """Should exit non-zero when a comment-antecedents violation is found."""
        runner = CliRunner()
        result = runner.invoke(cli, ["file-header", str(offending_file)])

        assert result.exit_code != 0

    def test_a_clean_run_exits_zero(self, clean_file):
        """Should exit zero when no violation is found."""
        runner = CliRunner()
        result = runner.invoke(cli, ["file-header", str(clean_file)])

        assert result.exit_code == 0
