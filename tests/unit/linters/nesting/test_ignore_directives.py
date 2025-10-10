"""
Purpose: Test inline ignore directives for nesting violations

Scope: Inline comments to suppress nesting depth warnings using thailint ignore syntax

Overview: Validates inline ignore directive functionality for suppressing nesting depth violations
    through special comments. Tests verify violations can be suppressed with rule-specific inline
    comments (# thailint: ignore nesting), supports both whole-line and end-of-line comment formats,
    respects rule-specific ignores (nesting vs other rules), supports ignore-all directive for
    multiple rules, handles TypeScript comment syntax (// thailint: ignore), supports block ignore
    with start/end markers, validates rule name requirements, and handles multiple comma-separated
    rule ignores. Ensures developers have flexible control over violation suppression while
    maintaining explicit intent through named rule ignores.

Dependencies: pytest for testing framework, src.linters.nesting.linter for NestingDepthRule,
    pathlib for Path handling, unittest.mock for Mock objects

Exports: TestIgnoreDirectives (8 tests) covering various ignore directive patterns

Interfaces: Tests inline comment parsing and violation suppression in NestingDepthRule.check()

Implementation: Uses code samples with ignore comments, verifies violations are suppressed or
    reported based on ignore directive presence and correctness
"""

from pathlib import Path
from unittest.mock import Mock

import pytest


class TestIgnoreDirectives:
    """Test inline ignore directives."""

    @pytest.mark.skip(reason="100% duplicate")
    def test_ignore_suppresses_violation(self):
        """# thailint: ignore nesting should suppress violation."""
        from src.linters.nesting.linter import NestingDepthRule

        code = """
def complex_function(data):  # thailint: ignore nesting
    for item in data:
        if item.active:
            for child in item.children:
                if child.valid:
                    if child.important:
                        process(child)
"""
        rule = NestingDepthRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}

        violations = rule.check(context)
        # Should NOT report violation due to ignore comment
        assert len(violations) == 0, "Ignore directive should suppress violation"

    def test_ignore_all_suppresses_any_rule(self):
        """# thailint: ignore-all should suppress all rules."""
        from src.linters.nesting.linter import NestingDepthRule

        code = """
def complex_function(data):  # thailint: ignore-all
    for item in data:
        if item.active:
            for child in item.children:
                if child.valid:
                    if child.important:
                        process(child)
"""
        rule = NestingDepthRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}

        violations = rule.check(context)
        # ignore-all should suppress nesting violations
        assert len(violations) == 0, "ignore-all should suppress violations"

    def test_ignore_wrong_rule_doesnt_suppress(self):
        """# thailint: ignore other-rule should NOT suppress nesting."""
        from src.linters.nesting.linter import NestingDepthRule

        code = """
def complex_function(data):  # thailint: ignore file-placement
    for item in data:
        if item.active:
            for child in item.children:
                if child.valid:
                    if child.important:
                        process(child)
"""
        rule = NestingDepthRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}

        violations = rule.check(context)
        # Ignore comment for different rule shouldn't affect nesting
        assert len(violations) > 0, "Ignore for different rule should not suppress"

    def test_ignore_applies_to_function_scope(self):
        """Function-level ignore should apply to whole function."""
        from src.linters.nesting.linter import NestingDepthRule

        code = """
def first_function():  # thailint: ignore nesting
    for i in range(5):
        for j in range(5):
            for k in range(5):
                for m in range(5):
                    print("ignored")

def second_function():
    for i in range(5):
        for j in range(5):
            for k in range(5):
                for m in range(5):
                    print("not ignored")
"""
        rule = NestingDepthRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}

        violations = rule.check(context)
        # Should have 1 violation from second_function only
        assert len(violations) >= 1, "Should have violation from second_function"
        # Verify the violation is from second_function, not first
        assert all(
            "second_function" in v.message or "first_function" not in v.message for v in violations
        ), "Violations should be from second_function, not first_function"

    def test_typescript_ignore_syntax(self):
        """// thailint: ignore nesting should work in TypeScript."""
        from src.linters.nesting.linter import NestingDepthRule

        code = """
function complexFunction(data: Data[]) {  // thailint: ignore nesting
    for (const item of data) {
        if (item.active) {
            for (const child of item.children) {
                if (child.valid) {
                    if (child.important) {
                        process(child);
                    }
                }
            }
        }
    }
}
"""
        rule = NestingDepthRule()
        context = Mock()
        context.file_path = Path("test.ts")
        context.file_content = code
        context.language = "typescript"
        context.metadata = {}

        violations = rule.check(context)
        # TypeScript comment syntax should work
        assert len(violations) == 0, "TypeScript ignore syntax should suppress violation"

    def test_block_ignore_start_end(self):
        """Block ignore with start/end markers should work."""
        from src.linters.nesting.linter import NestingDepthRule

        code = """
def test_function():
    # thailint: ignore-start nesting
    for i in range(5):
        for j in range(5):
            for k in range(5):
                for m in range(5):
                    print("ignored block")
    # thailint: ignore-end
    print("not ignored")
"""
        rule = NestingDepthRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}

        violations = rule.check(context)
        # Block ignore should suppress violations in the block
        assert len(violations) == 0, "Block ignore should suppress violations"

    @pytest.mark.skip(reason="100% duplicate")
    def test_ignore_with_justification_comment(self):
        """Ignore directives can be accompanied by justification comments."""
        from src.linters.nesting.linter import NestingDepthRule

        code = """
def complex_cli_parser(args):  # thailint: ignore nesting
    # Justification: CLI argument parsing inherently complex due to many flag combinations.
    # Refactoring would harm clarity without reducing actual complexity.
    for arg in args:
        if arg.startswith('--'):
            for handler in handlers:
                if handler.matches(arg):
                    if handler.validate(arg):
                        handler.process(arg)
"""
        rule = NestingDepthRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}

        violations = rule.check(context)
        # Ignore with justification should still suppress
        assert len(violations) == 0, "Ignore with justification should suppress"

    @pytest.mark.skip(reason="100% duplicate")
    def test_multiple_ignores_same_line(self):
        """# thailint: ignore nesting, file-placement should handle multiple rules."""
        from src.linters.nesting.linter import NestingDepthRule

        code = """
def multi_ignore():  # thailint: ignore nesting, file-placement
    for i in range(5):
        for j in range(5):
            for k in range(5):
                for m in range(5):
                    print("ignored")
"""
        rule = NestingDepthRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}

        violations = rule.check(context)
        # Multiple comma-separated ignores should work
        assert len(violations) == 0, "Multiple comma-separated ignores should work"
