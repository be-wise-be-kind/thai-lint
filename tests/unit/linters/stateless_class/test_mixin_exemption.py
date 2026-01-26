"""
Purpose: Test suite for mixin class exemption in stateless-class linter

Scope: Verify that mixin classes are correctly exempted from stateless class detection

Overview: Tests the fix for false positives where mixin classes (like SessionRedirectMixin)
    were incorrectly flagged as stateless. Mixin classes provide reusable methods intended
    to be combined with other classes via multiple inheritance, so they commonly have
    multiple methods without instance state. These tests verify:
    1. Classes with "Mixin" in their name are exempt
    2. The exemption can be configured via exempt_mixins setting
    3. Non-mixin classes are still detected

Dependencies: pytest, src.linters.stateless_class.linter.StatelessClassRule

Exports: TestMixinExemption class with test cases for mixin detection

Interfaces: Tests StatelessClassRule.check(context) -> list[Violation]

Implementation: Uses code samples with mixin patterns, verifies exemption behavior
"""

from pathlib import Path
from unittest.mock import Mock


class TestMixinExemption:
    """Test that mixin classes are exempted from stateless class detection."""

    def test_class_with_mixin_suffix_is_exempt(self) -> None:
        """Classes ending with 'Mixin' should be exempt."""
        code = """
class SessionRedirectMixin:
    def resolve_redirects(self, response):
        return self._handle_redirect(response)

    def _handle_redirect(self, response):
        return response.headers.get("Location")

    def should_follow_redirect(self, response):
        return response.status_code in (301, 302, 303, 307, 308)
"""
        from src.linters.stateless_class.linter import StatelessClassRule

        rule = StatelessClassRule()
        context = Mock()
        context.file_path = Path("src/mixins.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}

        violations = rule.check(context)
        assert len(violations) == 0, "Mixin class (Mixin suffix) should be exempt"

    def test_class_with_mixin_in_middle_is_exempt(self) -> None:
        """Classes with 'Mixin' in the middle of name should be exempt."""
        code = """
class AuthMixinBase:
    def authenticate(self, request):
        return self._check_credentials(request)

    def _check_credentials(self, request):
        return request.headers.get("Authorization")
"""
        from src.linters.stateless_class.linter import StatelessClassRule

        rule = StatelessClassRule()
        context = Mock()
        context.file_path = Path("src/auth.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}

        violations = rule.check(context)
        assert len(violations) == 0, "Class with Mixin in name should be exempt"

    def test_class_with_mixin_prefix_is_exempt(self) -> None:
        """Classes starting with 'Mixin' should be exempt."""
        code = """
class MixinForLogging:
    def log_request(self, request):
        print(f"Request: {request.method}")

    def log_response(self, response):
        print(f"Response: {response.status_code}")
"""
        from src.linters.stateless_class.linter import StatelessClassRule

        rule = StatelessClassRule()
        context = Mock()
        context.file_path = Path("src/logging.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}

        violations = rule.check(context)
        assert len(violations) == 0, "Class starting with Mixin should be exempt"

    def test_non_mixin_class_is_still_detected(self) -> None:
        """Non-mixin stateless classes should still be detected."""
        code = """
class HttpHelper:
    def get_headers(self, request):
        return request.headers

    def get_body(self, request):
        return request.body
"""
        from src.linters.stateless_class.linter import StatelessClassRule

        rule = StatelessClassRule()
        context = Mock()
        context.file_path = Path("src/helpers.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}

        violations = rule.check(context)
        assert len(violations) == 1, "Non-mixin stateless class should be detected"
        assert "HttpHelper" in violations[0].message

    def test_exemption_can_be_disabled(self) -> None:
        """Mixin exemption can be disabled via config."""
        code = """
class SessionMixin:
    def get_session(self, request):
        return request.session

    def set_session(self, request, data):
        request.session.update(data)
"""
        from src.linters.stateless_class.linter import StatelessClassRule

        rule = StatelessClassRule()
        context = Mock()
        context.file_path = Path("src/mixins.py")
        context.file_content = code
        context.language = "python"
        context.config = {"exempt_mixins": False}
        context.metadata = {}

        violations = rule.check(context)
        # When exemption is disabled, mixin classes should be flagged
        assert len(violations) == 1, "Mixin should be flagged when exemption disabled"


class TestMixinCaseInsensitivity:
    """Test that mixin detection is case-insensitive."""

    def test_lowercase_mixin_is_exempt(self) -> None:
        """Classes with lowercase 'mixin' should be exempt."""
        code = """
class Sessionmixin:
    def get_session(self, request):
        return request.session

    def set_session(self, request, data):
        request.session.update(data)
"""
        from src.linters.stateless_class.linter import StatelessClassRule

        rule = StatelessClassRule()
        context = Mock()
        context.file_path = Path("src/mixins.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}

        violations = rule.check(context)
        assert len(violations) == 0, "Class with lowercase mixin should be exempt"

    def test_mixed_case_mixin_is_exempt(self) -> None:
        """Classes with mixed case 'MiXiN' should be exempt."""
        code = """
class AuthMIXINHandler:
    def authenticate(self, request):
        return self._check_auth(request)

    def _check_auth(self, request):
        return bool(request.user)
"""
        from src.linters.stateless_class.linter import StatelessClassRule

        rule = StatelessClassRule()
        context = Mock()
        context.file_path = Path("src/auth.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}

        violations = rule.check(context)
        assert len(violations) == 0, "Class with mixed case MIXIN should be exempt"
