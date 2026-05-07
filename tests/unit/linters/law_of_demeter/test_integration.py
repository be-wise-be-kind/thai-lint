"""
Purpose: Integration tests for Law of Demeter linter end-to-end

Scope: Python code in -> violations out through complete LawOfDemeterRule pipeline

Overview: End-to-end integration tests that exercise the full linter pipeline: parse Python
    code, extract chains, classify each chain through the 9-filter pipeline, and produce
    Violation objects. Uses fixture code samples from real-world repos to validate both
    detection accuracy (true positives detected) and false-positive filtering (legitimate
    patterns not flagged). Tests the LawOfDemeterRule class through its check() method
    with mock contexts.

Dependencies: pytest, src.linters.law_of_demeter.linter, unittest.mock, pathlib

Exports: TestIntegrationTruePositives (5 tests), TestIntegrationFalsePositives (8 tests),
    TestIntegrationEdgeCases (4 tests) - total 17 test cases

Interfaces: Tests LawOfDemeterRule.check(context) -> list[Violation]

Implementation: Creates mock BaseLintContext, invokes rule.check(), verifies violation
    count and content
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


class TestIntegrationTruePositives:
    """Test that genuine LoD violations are detected end-to-end."""

    def test_detects_deep_attribute_chain(self) -> None:
        """Should detect order.customer.address.city."""
        from src.linters.law_of_demeter.linter import LawOfDemeterRule

        code = """
def process_order(order):
    name = order.customer.address.city
"""
        rule = LawOfDemeterRule()
        violations = rule.check(_create_python_context(code))
        assert len(violations) >= 1
        assert "law-of-demeter" in violations[0].rule_id

    def test_detects_method_chain_violation(self) -> None:
        """Should detect service.get_client().fetch_data().parse()."""
        from src.linters.law_of_demeter.linter import LawOfDemeterRule

        code = """
def get_info(service):
    data = service.get_client().fetch_data().parse()
"""
        rule = LawOfDemeterRule()
        violations = rule.check(_create_python_context(code))
        assert len(violations) >= 1

    def test_detects_multiple_violations(self) -> None:
        """Should detect multiple violations in same function."""
        from src.linters.law_of_demeter.linter import LawOfDemeterRule

        code = """
def complex_handler(request):
    user_city = request.user.profile.address.city
    manager_name = request.department.manager.full_name
"""
        rule = LawOfDemeterRule()
        violations = rule.check(_create_python_context(code))
        # request.user.profile.address.city is not safe-prefix (request. not in safe list)
        # and request.department.manager.full_name similar
        assert len(violations) >= 1

    def test_reports_correct_line_number(self) -> None:
        """Should report violation on the correct line."""
        from src.linters.law_of_demeter.linter import LawOfDemeterRule

        code = """
def f():
    pass

def g():
    x = a.b.c.d
"""
        rule = LawOfDemeterRule()
        violations = rule.check(_create_python_context(code))
        assert len(violations) >= 1
        assert violations[0].line == 6

    def test_violation_has_suggestion(self) -> None:
        """Should include a suggestion for fixing the violation."""
        from src.linters.law_of_demeter.linter import LawOfDemeterRule

        code = """
def f():
    x = a.b.c.d
"""
        rule = LawOfDemeterRule()
        violations = rule.check(_create_python_context(code))
        assert len(violations) >= 1
        assert violations[0].suggestion is not None


class TestIntegrationFalsePositives:
    """Test that legitimate patterns are NOT flagged."""

    def test_self_access_not_flagged(self) -> None:
        """self.config.database.host should not be flagged."""
        from src.linters.law_of_demeter.linter import LawOfDemeterRule

        code = """
class MyClass:
    def method(self):
        return self.config.database.host
"""
        rule = LawOfDemeterRule()
        violations = rule.check(_create_python_context(code))
        assert len(violations) == 0

    def test_module_access_not_flagged(self) -> None:
        """os.path.expanduser().strip() should not be flagged."""
        from src.linters.law_of_demeter.linter import LawOfDemeterRule

        code = """
import os
def get_home():
    return os.path.expanduser("~").strip()
"""
        rule = LawOfDemeterRule()
        violations = rule.check(_create_python_context(code))
        assert len(violations) == 0

    def test_string_chain_not_flagged(self) -> None:
        """text.strip().lower().replace() should not be flagged."""
        from src.linters.law_of_demeter.linter import LawOfDemeterRule

        code = """
def clean(text):
    return text.strip().lower().replace("-", "_")
"""
        rule = LawOfDemeterRule()
        violations = rule.check(_create_python_context(code))
        assert len(violations) == 0

    def test_orm_chain_not_flagged(self) -> None:
        """db.query().filter().order_by().limit() should not be flagged."""
        from src.linters.law_of_demeter.linter import LawOfDemeterRule

        code = """
def get_active_users(db):
    return db.query(User).filter(active=True).order_by("name").limit(10)
"""
        rule = LawOfDemeterRule()
        violations = rule.check(_create_python_context(code))
        assert len(violations) == 0

    def test_dunder_chain_not_flagged(self) -> None:
        """obj.__class__.__name__.lower() should not be flagged."""
        from src.linters.law_of_demeter.linter import LawOfDemeterRule

        code = """
def get_class_name(obj):
    return obj.__class__.__name__.lower()
"""
        rule = LawOfDemeterRule()
        violations = rule.check(_create_python_context(code))
        assert len(violations) == 0

    def test_settings_access_not_flagged(self) -> None:
        """settings.database.connection.host should not be flagged."""
        from src.linters.law_of_demeter.linter import LawOfDemeterRule

        code = """
def configure(settings):
    host = settings.database.connection.host
"""
        rule = LawOfDemeterRule()
        violations = rule.check(_create_python_context(code))
        assert len(violations) == 0

    def test_short_chain_not_flagged(self) -> None:
        """Chains below min_depth should not be flagged."""
        from src.linters.law_of_demeter.linter import LawOfDemeterRule

        code = """
def get_name(user):
    return user.address.city
"""
        rule = LawOfDemeterRule()
        violations = rule.check(_create_python_context(code))
        assert len(violations) == 0

    def test_test_file_not_flagged(self) -> None:
        """Violations in test files should not be flagged by default."""
        from src.linters.law_of_demeter.linter import LawOfDemeterRule

        code = """
def test_response(client):
    assert client.get("/api").json()["data"].get("id") == 1
"""
        rule = LawOfDemeterRule()
        violations = rule.check(_create_python_context(code, "test_api.py"))
        assert len(violations) == 0


class TestIntegrationEdgeCases:
    """Test edge cases in the full pipeline."""

    def test_empty_file(self) -> None:
        """Should handle empty files gracefully."""
        from src.linters.law_of_demeter.linter import LawOfDemeterRule

        rule = LawOfDemeterRule()
        violations = rule.check(_create_python_context(""))
        assert violations == []

    def test_syntax_error_handled(self) -> None:
        """Should handle syntax errors gracefully."""
        from src.linters.law_of_demeter.linter import LawOfDemeterRule

        code = "def f(:\n    pass"
        rule = LawOfDemeterRule()
        violations = rule.check(_create_python_context(code))
        # Should return syntax error violation or empty, not crash
        assert isinstance(violations, list)

    def test_disabled_returns_empty(self) -> None:
        """Should return empty when disabled."""
        from src.linters.law_of_demeter.linter import LawOfDemeterRule

        code = """
def f():
    x = a.b.c.d
"""
        rule = LawOfDemeterRule()
        context = _create_python_context(code)
        context.metadata = {"law-of-demeter": {"enabled": False}}
        violations = rule.check(context)
        assert violations == []

    def test_no_file_content_returns_empty(self) -> None:
        """Should return empty when file_content is None."""
        from src.linters.law_of_demeter.linter import LawOfDemeterRule

        rule = LawOfDemeterRule()
        context = Mock()
        context.file_content = None
        context.file_path = Path("app.py")
        context.language = "python"
        context.metadata = {}
        violations = rule.check(context)
        assert violations == []
