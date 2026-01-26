"""
Purpose: Test suite for test class exemption in stateless-class linter

Scope: Verify that test classes are correctly exempted from stateless class detection

Overview: Tests the fix for false positives where test classes (like unittest.TestCase
    subclasses or classes named Test*) were incorrectly flagged as stateless. Test classes
    commonly have multiple methods without instance state because they use setup/teardown
    patterns and assertion methods. These tests verify:
    1. Classes named Test* are exempt
    2. Classes inheriting from unittest.TestCase are exempt
    3. Classes in test files (test_*.py, tests/) are exempt
    4. The exemption can be configured via exempt_test_classes setting
    5. Non-test classes are still detected

Dependencies: pytest, src.linters.stateless_class.linter.StatelessClassRule

Exports: TestTestClassExemption class with test cases for test class detection

Interfaces: Tests StatelessClassRule.check(context) -> list[Violation]

Implementation: Uses code samples with test class patterns, verifies exemption behavior
"""

from pathlib import Path
from unittest.mock import Mock


class TestTestClassExemption:
    """Test that test classes are exempted from stateless class detection."""

    def test_class_named_test_prefix_is_exempt(self) -> None:
        """Classes starting with 'Test' should be exempt."""
        code = """
class TestUserService:
    def test_create_user(self):
        user = create_user("test")
        assert user.name == "test"

    def test_delete_user(self):
        delete_user("test")
        assert get_user("test") is None

    def test_update_user(self):
        update_user("test", name="new")
        assert get_user("test").name == "new"
"""
        from src.linters.stateless_class.linter import StatelessClassRule

        rule = StatelessClassRule()
        context = Mock()
        context.file_path = Path("test_user.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}

        violations = rule.check(context)
        assert len(violations) == 0, "Test class (Test* prefix) should be exempt"

    def test_class_inheriting_unittest_testcase_is_exempt(self) -> None:
        """Classes inheriting from unittest.TestCase should be exempt."""
        code = """
import unittest

class UserServiceTest(unittest.TestCase):
    def test_create_user(self):
        user = create_user("test")
        self.assertEqual(user.name, "test")

    def test_delete_user(self):
        delete_user("test")
        self.assertIsNone(get_user("test"))
"""
        from src.linters.stateless_class.linter import StatelessClassRule

        rule = StatelessClassRule()
        context = Mock()
        context.file_path = Path("test_user.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}

        violations = rule.check(context)
        assert len(violations) == 0, "unittest.TestCase subclass should be exempt"

    def test_class_inheriting_testcase_without_import_is_exempt(self) -> None:
        """Classes inheriting from TestCase (short form) should be exempt."""
        code = """
from unittest import TestCase

class UserServiceTest(TestCase):
    def test_create_user(self):
        user = create_user("test")
        self.assertEqual(user.name, "test")

    def test_delete_user(self):
        delete_user("test")
        self.assertIsNone(get_user("test"))
"""
        from src.linters.stateless_class.linter import StatelessClassRule

        rule = StatelessClassRule()
        context = Mock()
        context.file_path = Path("test_user.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}

        violations = rule.check(context)
        assert len(violations) == 0, "TestCase subclass should be exempt"

    def test_class_in_test_file_is_exempt(self) -> None:
        """Classes in test files (test_*.py) should be exempt."""
        code = """
class UserServiceTests:
    def test_create_user(self):
        user = create_user("test")
        assert user.name == "test"

    def test_delete_user(self):
        delete_user("test")
        assert get_user("test") is None
"""
        from src.linters.stateless_class.linter import StatelessClassRule

        rule = StatelessClassRule()
        context = Mock()
        context.file_path = Path("test_user_service.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}

        violations = rule.check(context)
        assert len(violations) == 0, "Class in test_*.py file should be exempt"

    def test_class_in_tests_directory_is_exempt(self) -> None:
        """Classes in tests/ directory should be exempt."""
        code = """
class UserServiceTests:
    def test_create_user(self):
        user = create_user("test")
        assert user.name == "test"

    def test_delete_user(self):
        delete_user("test")
        assert get_user("test") is None
"""
        from src.linters.stateless_class.linter import StatelessClassRule

        rule = StatelessClassRule()
        context = Mock()
        context.file_path = Path("tests/unit/test_user.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}

        violations = rule.check(context)
        assert len(violations) == 0, "Class in tests/ directory should be exempt"

    def test_non_test_class_is_still_detected(self) -> None:
        """Non-test stateless classes should still be detected."""
        code = """
class UserHelper:
    def format_name(self, name):
        return name.strip().title()

    def validate_email(self, email):
        return "@" in email
"""
        from src.linters.stateless_class.linter import StatelessClassRule

        rule = StatelessClassRule()
        context = Mock()
        context.file_path = Path("src/helpers.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}

        violations = rule.check(context)
        assert len(violations) == 1, "Non-test stateless class should be detected"
        assert "UserHelper" in violations[0].message

    def test_exemption_can_be_disabled(self) -> None:
        """Test class exemption can be disabled via config."""
        code = """
class TestUserService:
    def test_create_user(self):
        user = create_user("test")
        assert user.name == "test"

    def test_delete_user(self):
        delete_user("test")
        assert get_user("test") is None
"""
        from src.linters.stateless_class.linter import StatelessClassRule

        rule = StatelessClassRule()
        context = Mock()
        context.file_path = Path("test_user.py")
        context.file_content = code
        context.language = "python"
        context.config = {"exempt_test_classes": False}
        context.metadata = {}

        violations = rule.check(context)
        # When exemption is disabled, test classes should be flagged
        assert len(violations) == 1, "Test class should be flagged when exemption disabled"


class TestPytestStyleTests:
    """Test exemption for pytest-style test classes."""

    def test_pytest_class_with_test_prefix(self) -> None:
        """Pytest-style test class (no inheritance) should be exempt."""
        code = """
class TestAuthentication:
    def test_login_success(self):
        result = login("user", "pass")
        assert result.success

    def test_login_failure(self):
        result = login("user", "wrong")
        assert not result.success

    def test_logout(self):
        logout("user")
        assert not is_logged_in("user")
"""
        from src.linters.stateless_class.linter import StatelessClassRule

        rule = StatelessClassRule()
        context = Mock()
        context.file_path = Path("test_auth.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}

        violations = rule.check(context)
        assert len(violations) == 0, "Pytest-style test class should be exempt"
