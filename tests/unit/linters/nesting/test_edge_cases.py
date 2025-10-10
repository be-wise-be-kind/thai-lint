"""
Purpose: Test edge cases for nesting depth linter

Scope: Empty files, files with no functions, malformed code, and extreme nesting

Overview: Validates robust error handling and edge case behavior for the nesting depth linter
    including empty file handling (no violations), files without functions (module-level code),
    syntax error handling (graceful failure without crashes), extremely deep nesting detection
    (10+ levels), empty function bodies (pass statements only), comment-only functions, mixed
    sync and async function handling, and nested function definitions with independent depth
    tracking. Ensures linter handles unusual inputs gracefully, provides helpful error messages
    for malformed code, and correctly analyzes edge cases without false positives or crashes.

Dependencies: pytest for testing framework, src.linters.nesting.linter for NestingDepthRule,
    pathlib for Path handling, unittest.mock for Mock objects

Exports: TestEdgeCases (8 tests) covering empty files, no functions, syntax errors, extreme
    nesting, empty bodies, comments, mixed functions, and nested definitions

Interfaces: Tests NestingDepthRule.check(context) with edge case code samples

Implementation: Uses unusual code patterns as test fixtures, verifies graceful handling and
    correct behavior for each edge case
"""


class TestEdgeCases:
    """Test edge cases and error handling."""
