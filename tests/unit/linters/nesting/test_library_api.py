"""
Purpose: Test programmatic library API for nesting linter

Scope: Python API usage via Linter class and direct rule instantiation

Overview: Validates programmatic library API for the nesting depth linter enabling programmatic
    usage from Python code without CLI. Tests verify direct rule instantiation and checking,
    Linter class integration with rule filtering, violation object structure and metadata,
    custom configuration support through config files, and orchestrator integration. Ensures
    library API provides clean, Pythonic interface for embedding nesting depth checks in other
    tools, scripts, or CI/CD pipelines.

Dependencies: pytest for testing framework, src.linters.nesting.linter for NestingDepthRule,
    pathlib for Path handling, unittest.mock for Mock objects

Exports: TestNestingLibraryAPI (4 tests) covering direct usage, rule filtering, violation objects,
    and custom config

Interfaces: Tests NestingDepthRule class and integration with Linter API

Implementation: Creates rule instances directly, builds mock contexts, verifies violation
    detection and metadata structure
"""

from pathlib import Path
from unittest.mock import Mock

import pytest


class TestNestingLibraryAPI:
    """Test programmatic library API."""

    @pytest.mark.skip(reason="100% duplicate")
    def test_direct_rule_usage_detects_violations(self):
        """NestingDepthRule.check() should detect violations when used directly."""
        from src.linters.nesting.linter import NestingDepthRule

        code = """
def nested_func():
    for i in range(5):
        for j in range(5):
            for k in range(5):
                for m in range(5):
                    print(i, j, k, m)
"""
        rule = NestingDepthRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}

        violations = rule.check(context)
        assert len(violations) > 0, "Should detect nesting violations"
        assert all(hasattr(v, "message") for v in violations), "All violations should have message"

    @pytest.mark.skip(reason="100% duplicate")
    def test_rule_filtering_by_id(self):
        """Should be able to filter for nesting rule specifically."""
        from src.linters.nesting.linter import NestingDepthRule

        rule = NestingDepthRule()

        # Verify rule has correct ID
        assert hasattr(rule, "rule_id"), "Rule should have rule_id property"
        rule_id = rule.rule_id
        assert "nesting" in rule_id.lower(), f"Rule ID should contain 'nesting', got: {rule_id}"

    @pytest.mark.skip(reason="100% duplicate")
    def test_violation_objects_have_metadata(self):
        """Violations should have proper metadata structure."""
        from src.linters.nesting.linter import NestingDepthRule

        code = """
def problem_func():
    for i in range(5):
        for j in range(5):
            for k in range(5):
                for m in range(5):
                    print("violation")
"""
        rule = NestingDepthRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}

        violations = rule.check(context)
        assert len(violations) > 0, "Should have violations"

        # Verify violation structure
        violation = violations[0]
        required_attrs = ["rule_id", "message", "file_path", "line"]
        for attr in required_attrs:
            assert hasattr(violation, attr), f"Violation should have {attr} attribute"

        # Verify metadata values
        assert violation.line > 0, "Line number should be positive"
        assert str(violation.file_path) == "test.py", "File path should match"

    @pytest.mark.skip(reason="100% duplicate")
    def test_custom_config_via_context_metadata(self):
        """Should accept custom config via context metadata."""
        from src.linters.nesting.linter import NestingDepthRule

        # Code with depth 3
        code = """
def test_func():
    if True:
        if True:
            print("depth 3")
"""
        rule = NestingDepthRule()

        # Test with limit 4 (should pass)
        context_pass = Mock()
        context_pass.file_path = Path("test.py")
        context_pass.file_content = code
        context_pass.language = "python"
        context_pass.metadata = {"nesting": {"max_nesting_depth": 4}}
        violations_pass = rule.check(context_pass)
        assert len(violations_pass) == 0, "Depth 3 should pass with limit 4"

        # Test with limit 2 (should fail)
        context_fail = Mock()
        context_fail.file_path = Path("test.py")
        context_fail.file_content = code
        context_fail.language = "python"
        context_fail.metadata = {"nesting": {"max_nesting_depth": 2}}
        violations_fail = rule.check(context_fail)
        assert len(violations_fail) > 0, "Depth 3 should fail with limit 2"
