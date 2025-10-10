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


class TestViolationMessages:
    """Test helpful violation messages."""
