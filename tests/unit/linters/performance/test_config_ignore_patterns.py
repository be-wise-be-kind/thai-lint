"""
Purpose: Regression tests for performance linter's config-level ignore patterns

Scope: File-level ignore patterns from .thailint.yaml performance: config

Overview: Guards against performance.ignore being silently swallowed. docs/performance-linter.md
    has long documented a `performance: ignore: [...]` example as working, but PerformanceConfig
    never had an ignore field and StringConcatLoopRule never consulted one, so any such config
    was dead. Verifies a file matching an ignore glob is skipped entirely, while a non-matching
    file with the same violation is still reported.

Dependencies: pytest, pathlib, unittest.mock, src.linters.performance.linter

Exports: TestPerformanceIgnorePatterns

Interfaces: Tests StringConcatLoopRule.check() with ignore patterns in config metadata

Implementation: Mock-based testing with configuration injection containing ignore patterns
"""

from pathlib import Path
from unittest.mock import Mock

from src.linters.performance.linter import StringConcatLoopRule

STRING_CONCAT_CODE = """
def build_message(items):
    result = ""
    for item in items:
        result += str(item)
    return result
"""


class TestPerformanceIgnorePatterns:
    """Test configuration-based ignore patterns for the performance linter."""

    def test_ignores_glob_pattern_from_config(self) -> None:
        """A file matching performance.ignore must report zero violations."""
        rule = StringConcatLoopRule()
        context = Mock()
        context.file_path = Path("legacy/builder.py")
        context.file_content = STRING_CONCAT_CODE
        context.language = "python"
        context.metadata = {"performance": {"ignore": ["legacy/**"]}}

        violations = rule.check(context)

        assert len(violations) == 0, "File under legacy/** should be ignored"

    def test_processes_file_not_in_ignore_list(self) -> None:
        """A file not matching performance.ignore must still be checked."""
        rule = StringConcatLoopRule()
        context = Mock()
        context.file_path = Path("src/builder.py")
        context.file_content = STRING_CONCAT_CODE
        context.language = "python"
        context.metadata = {"performance": {"ignore": ["legacy/**"]}}

        violations = rule.check(context)

        assert len(violations) > 0, "File outside legacy/** should still be flagged"
