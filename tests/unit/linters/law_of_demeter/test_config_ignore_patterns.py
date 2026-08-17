"""
Purpose: Regression tests for law-of-demeter linter's config-level ignore patterns

Scope: File-level ignore patterns from .thailint.yaml law_of_demeter: config

Overview: Guards against law_of_demeter.ignore being silently swallowed.
    docs/law-of-demeter-linter.md has long documented a "Configuration-Based Ignore"
    section as working, but LawOfDemeterConfig never had an ignore field and
    LawOfDemeterRule never consulted one, so any such config was dead. Verifies a file
    matching an ignore glob is skipped entirely, while a non-matching file with the same
    violation is still reported.

Dependencies: pytest, pathlib, unittest.mock, src.linters.law_of_demeter.linter

Exports: TestLawOfDemeterIgnorePatterns

Interfaces: Tests LawOfDemeterRule.check() with ignore patterns in config metadata

Implementation: Mock-based testing with configuration injection containing ignore patterns
"""

from pathlib import Path
from unittest.mock import Mock

from src.linters.law_of_demeter.linter import LawOfDemeterRule

DEEP_CHAIN_CODE = """
def process_order(order):
    name = order.customer.address.city
"""


class TestLawOfDemeterIgnorePatterns:
    """Test configuration-based ignore patterns for the law-of-demeter linter."""

    def test_ignores_glob_pattern_from_config(self) -> None:
        """A file matching law_of_demeter.ignore must report zero violations."""
        rule = LawOfDemeterRule()
        context = Mock()
        context.file_path = Path("legacy/orders.py")
        context.file_content = DEEP_CHAIN_CODE
        context.language = "python"
        context.metadata = {"law_of_demeter": {"ignore": ["legacy/**"]}}

        violations = rule.check(context)

        assert len(violations) == 0, "File under legacy/** should be ignored"

    def test_processes_file_not_in_ignore_list(self) -> None:
        """A file not matching law_of_demeter.ignore must still be checked."""
        rule = LawOfDemeterRule()
        context = Mock()
        context.file_path = Path("src/orders.py")
        context.file_content = DEEP_CHAIN_CODE
        context.language = "python"
        context.metadata = {"law_of_demeter": {"ignore": ["legacy/**"]}}

        violations = rule.check(context)

        assert len(violations) > 0, "File outside legacy/** should still be flagged"
