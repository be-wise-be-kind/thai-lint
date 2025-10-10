"""
Purpose: Tests for DRY linter violation message formatting and content

Scope: Violation message content including locations, counts, suggestions, and formatting

Overview: Comprehensive test suite for violation message quality covering line count inclusion,
    occurrence count reporting, cross-file location references, line number precision,
    refactoring suggestions, message consistency, long path handling, and many-occurrence
    scenarios. Validates helpful and actionable violation messages.

Dependencies: pytest, src.Linter, pathlib, tmp_path fixture

Exports: 8 test functions for violation message scenarios

Interfaces: Uses Linter class and Violation objects

Implementation: TDD approach - tests written before implementation. All tests should
    initially fail with ModuleNotFoundError. Uses tmp_path for isolated file fixtures.
    Tests use cache_enabled: false for isolation, which triggers in-memory fallback mode
    (Decision 6): DRYRule maintains dict[int, list[CodeBlock]] instead of SQLite, providing
    same stateful behavior without persistence between test runs.
"""
