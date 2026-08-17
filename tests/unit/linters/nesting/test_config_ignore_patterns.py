"""
Purpose: Regression tests for nesting linter's config-level ignore patterns

Scope: File-level ignore patterns from .thailint.yaml nesting: config

Overview: Guards against nesting.ignore being silently swallowed. docs/configuration.md
    has long documented a `nesting: ignore: [...]` example as working, but NestingConfig
    never had an ignore field and NestingDepthRule never consulted one, so any such config
    was dead. Verifies a file matching an ignore glob is skipped entirely, while a
    non-matching file with the same violation is still reported.

Dependencies: pytest, pathlib, unittest.mock, src.linters.nesting.linter

Exports: TestNestingIgnorePatterns

Interfaces: Tests NestingDepthRule.check() with ignore patterns in config metadata

Implementation: Mock-based testing with configuration injection containing ignore patterns
"""

from pathlib import Path
from unittest.mock import Mock

from src.linters.nesting.linter import NestingDepthRule

DEEPLY_NESTED_CODE = """
def process():
    for i in range(5):
        for j in range(5):
            for k in range(5):
                for m in range(5):
                    print(i, j, k, m)
"""


class TestNestingIgnorePatterns:
    """Test configuration-based ignore patterns for the nesting linter."""

    def test_ignores_glob_pattern_from_config(self) -> None:
        """A file matching nesting.ignore must report zero violations."""
        rule = NestingDepthRule()
        context = Mock()
        context.file_path = Path("legacy/deep.py")
        context.file_content = DEEPLY_NESTED_CODE
        context.language = "python"
        context.metadata = {
            "nesting": {
                "max_nesting_depth": 2,
                "ignore": ["legacy/**"],
            }
        }

        violations = rule.check(context)

        assert len(violations) == 0, "File under legacy/** should be ignored"

    def test_processes_file_not_in_ignore_list(self) -> None:
        """A file not matching nesting.ignore must still be checked."""
        rule = NestingDepthRule()
        context = Mock()
        context.file_path = Path("src/deep.py")
        context.file_content = DEEPLY_NESTED_CODE
        context.language = "python"
        context.metadata = {
            "nesting": {
                "max_nesting_depth": 2,
                "ignore": ["legacy/**"],
            }
        }

        violations = rule.check(context)

        assert len(violations) > 0, "File outside legacy/** should still be flagged"
