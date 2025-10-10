"""
Purpose: Test edge cases and special scenarios for SRP linter

Scope: Unusual code patterns, edge cases, error handling for SRP analysis

Overview: Validates SRP linter behavior with edge cases including empty files, files
    with only functions (no classes), files with only imports, syntax error handling,
    abstract base classes, dataclasses with many fields (shouldn't count as methods),
    property decorators (shouldn't count as methods), inherited methods (shouldn't count),
    class methods and static methods, async methods, nested function definitions,
    and various Python/TypeScript language edge cases. Ensures robust handling of
    unusual inputs without false positives or crashes.

Dependencies: pytest for testing framework, src.linters.srp.linter for SRPRule,
    pathlib for Path handling, unittest.mock for Mock contexts

Exports: TestEdgeCases (10 tests) covering unusual code patterns and error handling

Interfaces: Tests SRPRule.check() with edge case code samples

Implementation: Tests boundary conditions, unusual syntax, and graceful error handling
"""


class TestEdgeCases:
    """Test SRP linter edge cases and special scenarios."""

    # Graceful handling expected

    # Dataclass fields should not count as methods

    # Properties should not count as methods

    # DerivedClass only has 2 methods (should pass)
