"""
Purpose: Test inline ignore directives for Law of Demeter violations

Scope: Inline comments to suppress LoD warnings using thailint ignore syntax

Overview: Validates inline ignore directive functionality for suppressing Law of Demeter
    violations through special comments. Tests verify violations can be suppressed with
    rule-specific inline comments (# thailint: ignore law-of-demeter), supports ignore-all
    directive, and respects rule-specific ignores (law-of-demeter vs other rules).

Dependencies: pytest, src.linters.law_of_demeter.linter, pathlib, unittest.mock

Exports: TestIgnoreDirectives (4 tests)

Interfaces: Tests inline comment parsing and violation suppression in
    LawOfDemeterRule.check()

Implementation: Uses code samples with ignore comments, verifies violations are
    suppressed or reported based on ignore directive presence
"""

from pathlib import Path
from unittest.mock import Mock


def _create_python_context(code: str, filename: str = "app.py") -> Mock:
    """Create mock lint context for Python code."""
    context = Mock()
    context.file_content = code
    context.file_path = Path(filename)
    context.language = "python"
    context.metadata = {}
    return context


class TestIgnoreDirectives:
    """Test inline ignore directives for LoD linter."""

    def test_ignore_all_suppresses(self) -> None:
        """# thailint: ignore-all should suppress LoD violations."""
        from src.linters.law_of_demeter.linter import LawOfDemeterRule

        code = """
def f():  # thailint: ignore-all
    x = a.b.c.d
"""
        rule = LawOfDemeterRule()
        violations = rule.check(_create_python_context(code))
        assert len(violations) == 0

    def test_ignore_specific_rule_suppresses(self) -> None:
        """# thailint: ignore law-of-demeter should suppress LoD violations."""
        from src.linters.law_of_demeter.linter import LawOfDemeterRule

        code = """
def f():
    x = a.b.c.d  # thailint: ignore law-of-demeter
"""
        rule = LawOfDemeterRule()
        violations = rule.check(_create_python_context(code))
        assert len(violations) == 0

    def test_ignore_wrong_rule_doesnt_suppress(self) -> None:
        """# thailint: ignore other-rule should NOT suppress LoD violations."""
        from src.linters.law_of_demeter.linter import LawOfDemeterRule

        code = """
def f():
    x = a.b.c.d  # thailint: ignore nesting
"""
        rule = LawOfDemeterRule()
        violations = rule.check(_create_python_context(code))
        assert len(violations) >= 1

    def test_no_ignore_reports_violation(self) -> None:
        """Without ignore directive, violations should be reported."""
        from src.linters.law_of_demeter.linter import LawOfDemeterRule

        code = """
def f():
    x = a.b.c.d
"""
        rule = LawOfDemeterRule()
        violations = rule.check(_create_python_context(code))
        assert len(violations) >= 1
