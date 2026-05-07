"""
Purpose: Test violation message formatting for Law of Demeter linter

Scope: Violation message content, rule_id format, severity, and suggestion text

Overview: Validates that LoD violations are reported with correct rule_id format,
    meaningful error messages including chain depth and chain representation,
    proper severity (ERROR), file path and line number, and helpful suggestions
    for refactoring.

Dependencies: pytest, src.linters.law_of_demeter.linter, unittest.mock, pathlib

Exports: TestViolationMessages (5 tests)

Interfaces: Tests violation object fields produced by LawOfDemeterRule.check()

Implementation: Creates violations via rule.check() with known code samples,
    inspects Violation dataclass fields
"""

from pathlib import Path
from unittest.mock import Mock

from src.core.types import Severity


def _create_python_context(code: str, filename: str = "app.py") -> Mock:
    """Create mock lint context for Python code."""
    context = Mock()
    context.file_content = code
    context.file_path = Path(filename)
    context.language = "python"
    context.metadata = {}
    return context


class TestViolationMessages:
    """Test violation message content and format."""

    def test_rule_id_format(self) -> None:
        """Should use 'law-of-demeter.chain-depth' rule_id."""
        from src.linters.law_of_demeter.linter import LawOfDemeterRule

        code = """
def f():
    x = a.b.c.d
"""
        rule = LawOfDemeterRule()
        violations = rule.check(_create_python_context(code))
        assert len(violations) >= 1
        assert "law-of-demeter" in violations[0].rule_id

    def test_severity_is_error(self) -> None:
        """Should report ERROR severity."""
        from src.linters.law_of_demeter.linter import LawOfDemeterRule

        code = """
def f():
    x = a.b.c.d
"""
        rule = LawOfDemeterRule()
        violations = rule.check(_create_python_context(code))
        assert len(violations) >= 1
        assert violations[0].severity == Severity.ERROR

    def test_message_includes_chain_depth(self) -> None:
        """Should mention chain depth in the message."""
        from src.linters.law_of_demeter.linter import LawOfDemeterRule

        code = """
def f():
    x = a.b.c.d
"""
        rule = LawOfDemeterRule()
        violations = rule.check(_create_python_context(code))
        assert len(violations) >= 1
        # Message should reference depth or chain
        msg = violations[0].message.lower()
        assert "chain" in msg or "depth" in msg or "demeter" in msg

    def test_file_path_set(self) -> None:
        """Should include file path in violation."""
        from src.linters.law_of_demeter.linter import LawOfDemeterRule

        code = """
def f():
    x = a.b.c.d
"""
        rule = LawOfDemeterRule()
        violations = rule.check(_create_python_context(code, "src/handler.py"))
        assert len(violations) >= 1
        assert "handler.py" in violations[0].file_path

    def test_suggestion_provides_guidance(self) -> None:
        """Should provide actionable refactoring suggestion."""
        from src.linters.law_of_demeter.linter import LawOfDemeterRule

        code = """
def f():
    x = a.b.c.d
"""
        rule = LawOfDemeterRule()
        violations = rule.check(_create_python_context(code))
        assert len(violations) >= 1
        suggestion = violations[0].suggestion
        assert suggestion is not None
        assert len(suggestion) > 10  # Should be meaningful text
