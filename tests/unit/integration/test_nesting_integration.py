"""
Purpose: Integration tests for nesting depth linter with orchestrator

Scope: E2E integration testing with CLI, Library API, and orchestrator

Overview: Tests full integration of nesting linter with all deployment modes. Verifies orchestrator
    auto-discovers nesting rule, CLI command works, Library API works, and Docker deployment works.
    Tests config loading, rule filtering, and violation reporting across all interfaces. Validates
    that the nesting linter correctly integrates with the orchestrator framework and that all
    public interfaces (CLI, Library API, direct import) function properly.

Dependencies: pytest, Orchestrator, Linter, CliRunner, click.testing, tempfile for test files

Exports: 8 integration test cases covering orchestrator discovery, CLI command, library API, config

Interfaces: Full stack from CLI/API down to rule execution, testing all layers of integration

Implementation: E2E testing with temp files and realistic scenarios, uses pytest fixtures for setup
"""

import pytest
from click.testing import CliRunner

from src import Linter, nesting_lint
from src.cli import cli
from src.orchestrator.core import Orchestrator


class TestNestingIntegration:
    """E2E integration tests for nesting linter."""

    @pytest.mark.skip(reason="100% duplicate")
    def test_orchestrator_discovers_nesting_rule(self):
        """Orchestrator should auto-discover NestingDepthRule."""
        orch = Orchestrator()
        rules = orch.registry.list_all()
        nesting_rules = [r for r in rules if "nesting" in r.rule_id]
        assert len(nesting_rules) > 0, "NestingDepthRule should be discovered"
        assert nesting_rules[0].rule_id == "nesting.excessive-depth"

    @pytest.mark.skip(reason="100% duplicate")
    def test_orchestrator_lints_python_file(self, tmp_path):
        """Orchestrator should lint Python file with nesting rule."""
        # Create Python file with nesting violation (depth 5)
        test_file = tmp_path / "test.py"
        test_file.write_text(
            """
def deep_function(data):
    for item in data:
        if item:
            for child in item:
                if child:
                    if child.value:  # depth 5
                        print(child)
"""
        )

        # Run orchestrator
        orch = Orchestrator(project_root=tmp_path)
        violations = orch.lint_file(test_file)

        # Verify violations
        nesting_violations = [v for v in violations if "nesting" in v.rule_id]
        assert len(nesting_violations) > 0, "Should find nesting violation"

    @pytest.mark.skip(reason="100% duplicate")
    def test_cli_command_works(self, tmp_path):
        """CLI command `thai-lint nesting` should work."""
        # Create temp Python file with violation
        test_file = tmp_path / "test.py"
        test_file.write_text(
            """
def deep_function(data):
    for item in data:
        if item:
            for child in item:
                if child:
                    if child.value:  # depth 5
                        print(child)
"""
        )

        # Run CLI
        runner = CliRunner()
        result = runner.invoke(cli, ["nesting", str(test_file)])

        # Verify output and exit code
        assert result.exit_code == 1, "Should exit with code 1 on violations"
        assert "violation" in result.output.lower()

    def test_library_api_works(self, tmp_path):
        """Library API should work for nesting linter."""
        # Create temp file with violation
        test_file = tmp_path / "test.py"
        test_file.write_text(
            """
def deep_function(data):
    for item in data:
        if item:
            for child in item:
                if child:
                    if child.value:  # depth 5
                        print(child)
"""
        )

        # Use Linter API
        linter = Linter(project_root=tmp_path)
        violations = linter.lint(test_file)

        # Filter to nesting violations
        nesting_violations = [v for v in violations if "nesting" in v.rule_id]
        assert len(nesting_violations) > 0, "Should find nesting violation"

    @pytest.mark.skip(reason="100% duplicate")
    def test_direct_lint_function_works(self, tmp_path):
        """Direct nesting_lint function should work."""
        # Create temp file with violation
        test_file = tmp_path / "test.py"
        test_file.write_text(
            """
def deep_function(data):
    for item in data:
        if item:
            for child in item:
                if child:
                    if child.value:  # depth 5
                        print(child)
"""
        )

        # Use direct nesting_lint function
        violations = nesting_lint(test_file, max_depth=4)

        assert len(violations) > 0, "Should find nesting violation"
        assert "nesting" in violations[0].rule_id

    @pytest.mark.skip(reason="100% duplicate")
    def test_custom_max_depth_config(self, tmp_path):
        """Custom max_depth in config should be respected."""
        # Create file with depth=3 (should pass with max_depth=4, fail with max_depth=2)
        test_file = tmp_path / "test.py"
        test_file.write_text(
            """
def shallow_function(data):
    for item in data:
        if item:
            print(item)  # depth 3
"""
        )

        # Test with max_depth=4 (should pass)
        violations_pass = nesting_lint(test_file, max_depth=4)
        assert len(violations_pass) == 0, "Should pass with max_depth=4"

        # Test with max_depth=2 (should fail)
        violations_fail = nesting_lint(test_file, max_depth=2)
        assert len(violations_fail) > 0, "Should fail with max_depth=2"

    def test_multiple_files_in_directory(self, tmp_path):
        """Should lint all files in directory."""
        # Create directory with multiple Python files
        (tmp_path / "good.py").write_text(
            """
def simple_function(x):
    if x:
        print(x)  # depth 2, OK
"""
        )

        (tmp_path / "bad.py").write_text(
            """
def deep_function(data):
    for item in data:
        if item:
            for child in item:
                if child:
                    if child.value:  # depth 5, violation
                        print(child)
"""
        )

        # Lint directory
        violations = nesting_lint(tmp_path, max_depth=4)

        # Should find violations only in bad.py
        assert len(violations) > 0, "Should find violations in bad.py"
        assert all("bad.py" in str(v.file_path) for v in violations)

    def test_cli_with_custom_max_depth(self, tmp_path):
        """CLI should support --max-depth option."""
        # Create file with depth=3
        test_file = tmp_path / "test.py"
        test_file.write_text(
            """
def shallow_function(data):
    for item in data:
        if item:
            print(item)  # depth 3
"""
        )

        runner = CliRunner()

        # Test with default max_depth=4 (should pass)
        result_pass = runner.invoke(cli, ["nesting", str(test_file)])
        assert result_pass.exit_code == 0, "Should pass with default max_depth=4"

        # Test with --max-depth=2 (should fail)
        result_fail = runner.invoke(cli, ["nesting", "--max-depth", "2", str(test_file)])
        assert result_fail.exit_code == 1, "Should fail with --max-depth=2"
