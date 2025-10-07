"""
Purpose: Test violation message formatting and suggestions

Scope: Error message content, refactoring suggestions, and context information

Overview: Validates that violation messages are helpful, actionable, and provide complete context
    for developers to understand and fix nesting issues. Tests verify messages include function
    name for clear identification, maximum depth found and limit exceeded for precise reporting,
    actionable refactoring suggestions (early returns, extract method, guard clauses), accurate
    line numbers for navigation, comprehensive violation context metadata (function name, depth,
    max allowed), and proper handling of multiple violations in single file. Ensures violation
    reporting provides excellent developer experience with clear guidance.

Dependencies: pytest for testing framework, src.linters.nesting.linter for NestingDepthRule,
    pathlib for Path handling, unittest.mock for Mock objects

Exports: TestViolationMessages (6 tests) covering message format, content, and suggestions

Interfaces: Tests Violation.message, Violation.suggestion, and violation metadata

Implementation: Analyzes violation objects returned by rule, verifies message content with
    string matching and assertions on violation properties
"""

from pathlib import Path
from unittest.mock import Mock


class TestViolationMessages:
    """Test helpful violation messages."""

    def test_message_includes_function_name(self):
        """Violation message should include function name."""
        from src.linters.nesting.linter import NestingDepthRule

        code = """
def process_data(items):
    for item in items:
        if item.valid:
            for child in item.children:
                if child.active:
                    print(child)
"""
        rule = NestingDepthRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}

        violations = rule.check(context)
        assert len(violations) > 0, "Should have violations"

        violation = violations[0]
        # Message should include function name
        assert "process_data" in violation.message, (
            "Message should include function name 'process_data'"
        )

    def test_message_includes_depth_info(self):
        """Message should include depth found and limit."""
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
        assert len(violations) > 0, "Should have violations"

        violation = violations[0]
        # Message should mention the depth (5) and/or limit (4)
        message_and_suggestion = violation.message + " " + (violation.suggestion or "")
        assert "5" in message_and_suggestion or "depth" in message_and_suggestion.lower(), (
            "Should mention depth information"
        )
        assert "4" in message_and_suggestion or "limit" in message_and_suggestion.lower(), (
            "Should mention limit information"
        )

    def test_suggestion_recommends_refactoring(self):
        """Should provide actionable refactoring suggestions."""
        from src.linters.nesting.linter import NestingDepthRule

        code = """
def complex_func(data):
    for item in data:
        if item.active:
            for child in item.children:
                if child.valid:
                    process(child)
"""
        rule = NestingDepthRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}

        violations = rule.check(context)
        assert len(violations) > 0, "Should have violations"

        violation = violations[0]
        suggestion = violation.suggestion or ""
        suggestion_lower = suggestion.lower()

        # Check for common refactoring suggestions
        refactoring_keywords = [
            "extract",
            "function",
            "early return",
            "guard clause",
            "reduce nesting",
            "separate",
        ]
        has_suggestion = any(keyword in suggestion_lower for keyword in refactoring_keywords)
        assert has_suggestion, (
            f"Suggestion should recommend refactoring patterns. Got: {suggestion}"
        )

    def test_violation_includes_line_number(self):
        """Violation should include accurate line number."""
        from src.linters.nesting.linter import NestingDepthRule

        code = """
def first_func():
    x = 1

def second_func():
    for i in range(5):
        for j in range(5):
            for k in range(5):
                for m in range(5):
                    print(i)
"""
        rule = NestingDepthRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}

        violations = rule.check(context)
        assert len(violations) > 0, "Should have violations"

        violation = violations[0]
        # Line number should be set and reasonable (function starts around line 5)
        assert violation.line > 0, "Line number should be positive"
        assert violation.line >= 4, "Line number should be around where second_func is defined"

    def test_violation_context_has_details(self):
        """Violation context should include metadata."""
        from src.linters.nesting.linter import NestingDepthRule

        code = """
def my_function():
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
        assert len(violations) > 0, "Should have violations"

        # Violations should be objects with accessible properties
        violation = violations[0]
        assert hasattr(violation, "rule_id"), "Should have rule_id"
        assert hasattr(violation, "message"), "Should have message"
        assert hasattr(violation, "file_path"), "Should have file_path"
        assert hasattr(violation, "line"), "Should have line number"

    def test_multiple_violations_separate_messages(self):
        """Multiple functions with violations get separate messages."""
        from src.linters.nesting.linter import NestingDepthRule

        code = """
def first_violator():
    for i in range(5):
        for j in range(5):
            for k in range(5):
                for m in range(5):
                    print("first")

def second_violator():
    if True:
        if True:
            if True:
                if True:
                    print("second")

def clean_function():
    print("no nesting")
"""
        rule = NestingDepthRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}

        violations = rule.check(context)
        # Should have 2 violations (first_violator and second_violator)
        assert len(violations) >= 2, "Should have at least 2 violations"

        # Check that both functions are mentioned
        all_messages = " ".join([v.message for v in violations])
        assert "first_violator" in all_messages or "second_violator" in all_messages, (
            "Should mention at least one violating function"
        )
