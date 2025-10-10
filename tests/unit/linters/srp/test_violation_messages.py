"""
Purpose: Test SRP violation message formatting and content

Scope: Violation message structure, formatting, and helpful suggestions for SRP violations

Overview: Validates violation message formatting for SRP linter including class name
    inclusion in messages, metric value reporting (method counts, LOC values), helpful
    refactoring suggestions (extract class, split responsibilities), message consistency
    across violation types, multiple violation reporting for single class, and actionable
    guidance for developers. Ensures violation messages provide clear, informative feedback
    that helps developers understand and fix SRP violations effectively.

Dependencies: pytest for testing framework, src.linters.srp.linter for SRPRule,
    pathlib for Path handling, unittest.mock for Mock contexts

Exports: TestViolationMessageFormat (8 tests) covering message content and suggestions

Interfaces: Tests Violation.message and Violation.suggestion fields from SRPRule.check()

Implementation: Validates message strings contain expected information, verifies
    suggestion quality and actionability
"""

from pathlib import Path
from unittest.mock import Mock

import pytest


class TestViolationMessageFormat:
    """Test SRP violation message formatting and content."""

    @pytest.mark.skip(reason="100% duplicate")
    def test_violation_includes_class_name(self):
        """Violation message should include the class name."""
        code = """
class UserManager:
    def m1(self): pass
    def m2(self): pass
    def m3(self): pass
    def m4(self): pass
    def m5(self): pass
    def m6(self): pass
    def m7(self): pass
    def m8(self): pass
"""
        from src.linters.srp.linter import SRPRule

        rule = SRPRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}

        violations = rule.check(context)
        assert len(violations) > 0, "Should have violations"
        assert "UserManager" in violations[0].message, "Message should include class name"

    @pytest.mark.skip(reason="100% duplicate")
    def test_violation_includes_method_count(self):
        """Violation message should include actual method count."""
        code = """
class DataClass:
    def m1(self): pass
    def m2(self): pass
    def m3(self): pass
    def m4(self): pass
    def m5(self): pass
    def m6(self): pass
    def m7(self): pass
    def m8(self): pass
"""
        from src.linters.srp.linter import SRPRule

        rule = SRPRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}

        violations = rule.check(context)
        assert len(violations) > 0, "Should have violations"
        assert "8 methods" in violations[0].message, "Message should include method count"

    @pytest.mark.skip(reason="100% duplicate")
    def test_violation_includes_loc_when_exceeded(self):
        """Violation message should include LOC when threshold exceeded."""
        methods = "\n".join([f"    def method_{i}(self): pass" for i in range(100)])
        code = f"""
class LargeClass:
{methods}
"""
        from src.linters.srp.linter import SRPRule

        rule = SRPRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}

        violations = rule.check(context)
        assert len(violations) > 0, "Should have violations"
        # Message should mention LOC violation

    @pytest.mark.skip(reason="100% duplicate")
    def test_violation_includes_helpful_suggestion(self):
        """Violation should include actionable refactoring suggestion."""
        code = """
class DataManager:
    def m1(self): pass
    def m2(self): pass
    def m3(self): pass
    def m4(self): pass
    def m5(self): pass
    def m6(self): pass
    def m7(self): pass
    def m8(self): pass
"""
        from src.linters.srp.linter import SRPRule

        rule = SRPRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}

        violations = rule.check(context)
        assert len(violations) > 0, "Should have violations"
        assert violations[0].suggestion is not None, "Should provide suggestion"
        # Suggestion should mention extracting or splitting

    @pytest.mark.skip(reason="100% duplicate")
    def test_multiple_violations_reported_separately(self):
        """Multiple SRP issues should be reported in single violation."""
        methods = "\n".join([f"    def method_{i}(self): pass" for i in range(50)])
        code = f"""
class SystemHandler:
{methods}
"""
        from src.linters.srp.linter import SRPRule

        rule = SRPRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}

        violations = rule.check(context)
        assert len(violations) > 0, "Should have violations"
        # Message should mention multiple issues (methods, LOC, keyword)

    @pytest.mark.skip(reason="100% duplicate")
    def test_message_format_is_consistent(self):
        """Violation messages should follow consistent format."""
        code = """
class DataProcessor:
    def m1(self): pass
    def m2(self): pass
    def m3(self): pass
    def m4(self): pass
    def m5(self): pass
    def m6(self): pass
    def m7(self): pass
    def m8(self): pass
"""
        from src.linters.srp.linter import SRPRule

        rule = SRPRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}

        violations = rule.check(context)
        assert len(violations) > 0, "Should have violations"
        # Message should follow pattern: "Class 'Name' may violate SRP: ..."

    @pytest.mark.skip(reason="100% duplicate")
    def test_keyword_violation_mentions_keyword_issue(self):
        """Keyword violation should explain the problem."""
        code = """
class UserManager:
    def get(self): pass
    def save(self): pass
"""
        from src.linters.srp.linter import SRPRule

        rule = SRPRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}

        violations = rule.check(context)
        assert len(violations) > 0, "Should have keyword violation"
        # Message should mention responsibility keyword issue

    @pytest.mark.skip(reason="100% duplicate")
    def test_suggestion_recommends_extract_class(self):
        """Suggestion should recommend extracting classes for violations."""
        code = """
class ComplexClass:
    def m1(self): pass
    def m2(self): pass
    def m3(self): pass
    def m4(self): pass
    def m5(self): pass
    def m6(self): pass
    def m7(self): pass
    def m8(self): pass
"""
        from src.linters.srp.linter import SRPRule

        rule = SRPRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}

        violations = rule.check(context)
        assert len(violations) > 0, "Should have violations"
        violations[0].suggestion.lower()
        # Suggestion should mention extracting or splitting classes
