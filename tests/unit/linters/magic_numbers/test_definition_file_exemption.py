"""
Purpose: Test suite for definition file exemption in magic numbers linter

Scope: Verify that constant definition files are correctly exempted from magic number detection

Overview: Tests the fix for false positives where definition files (like status_codes.py,
    constants.py) containing legitimate constant definitions were flagged. These files
    exist specifically to define named constants. These tests verify:
    1. Files named *_codes.py are exempt
    2. Files named *_constants.py or constants.py are exempt
    3. Files with many UPPERCASE constant assignments are detected and exempt
    4. Files with dict containing many int keys are detected and exempt
    5. The exemption can be configured via exempt_definition_files setting
    6. Regular code files are still checked

Dependencies: pytest, src.linters.magic_numbers.linter.MagicNumberRule

Exports: TestDefinitionFileExemption class with test cases

Interfaces: Tests MagicNumberRule.check(context) -> list[Violation]

Implementation: Uses code samples representing definition file patterns
"""

from pathlib import Path
from unittest.mock import Mock


class TestDefinitionFileByName:
    """Test exemption based on file naming patterns."""

    def test_status_codes_file_is_exempt(self) -> None:
        """Files named *_codes.py should be exempt."""
        code = """
HTTP_OK = 200
HTTP_CREATED = 201
HTTP_ACCEPTED = 202
HTTP_NO_CONTENT = 204
HTTP_BAD_REQUEST = 400
HTTP_UNAUTHORIZED = 401
HTTP_FORBIDDEN = 403
HTTP_NOT_FOUND = 404
HTTP_INTERNAL_ERROR = 500
"""
        from src.linters.magic_numbers.linter import MagicNumberRule

        rule = MagicNumberRule()
        context = Mock()
        context.file_path = Path("src/http_status_codes.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}

        violations = rule.check(context)
        assert len(violations) == 0, "status_codes.py file should be exempt"

    def test_error_codes_file_is_exempt(self) -> None:
        """Files named *_codes.py should be exempt."""
        code = """
ERR_NONE = 0
ERR_INVALID_INPUT = 1001
ERR_NOT_FOUND = 1002
ERR_PERMISSION_DENIED = 1003
ERR_TIMEOUT = 1004
"""
        from src.linters.magic_numbers.linter import MagicNumberRule

        rule = MagicNumberRule()
        context = Mock()
        context.file_path = Path("src/error_codes.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}

        violations = rule.check(context)
        assert len(violations) == 0, "error_codes.py file should be exempt"

    def test_constants_file_is_exempt(self) -> None:
        """Files named constants.py should be exempt."""
        code = """
MAX_CONNECTIONS = 100
DEFAULT_TIMEOUT = 30
BUFFER_SIZE = 4096
MAX_RETRIES = 5
CACHE_TTL = 3600
"""
        from src.linters.magic_numbers.linter import MagicNumberRule

        rule = MagicNumberRule()
        context = Mock()
        context.file_path = Path("src/constants.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}

        violations = rule.check(context)
        assert len(violations) == 0, "constants.py file should be exempt"

    def test_app_constants_file_is_exempt(self) -> None:
        """Files named *_constants.py should be exempt."""
        code = """
APP_VERSION = 123
BUILD_NUMBER = 456
RELEASE_YEAR = 2024
"""
        from src.linters.magic_numbers.linter import MagicNumberRule

        rule = MagicNumberRule()
        context = Mock()
        context.file_path = Path("config/app_constants.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}

        violations = rule.check(context)
        assert len(violations) == 0, "app_constants.py file should be exempt"


class TestDefinitionFileByContent:
    """Test exemption based on file content patterns."""

    def test_file_with_many_uppercase_constants_is_exempt(self) -> None:
        """Files with 10+ UPPERCASE constant assignments should be exempt."""
        code = """
# API Response Codes
SUCCESS = 0
INVALID_REQUEST = 1
UNAUTHORIZED = 2
FORBIDDEN = 3
NOT_FOUND = 4
METHOD_NOT_ALLOWED = 5
CONFLICT = 6
GONE = 7
UNPROCESSABLE = 8
TOO_MANY_REQUESTS = 9
INTERNAL_ERROR = 10
"""
        from src.linters.magic_numbers.linter import MagicNumberRule

        rule = MagicNumberRule()
        context = Mock()
        context.file_path = Path("src/api/responses.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}

        violations = rule.check(context)
        assert len(violations) == 0, "File with many UPPERCASE constants should be exempt"

    def test_dict_with_many_int_keys_is_exempt(self) -> None:
        """Files with dict containing 5+ int keys should be exempt."""
        code = """
STATUS_CODES = {
    200: "OK",
    201: "Created",
    204: "No Content",
    400: "Bad Request",
    401: "Unauthorized",
    403: "Forbidden",
    404: "Not Found",
    500: "Internal Server Error",
}
"""
        from src.linters.magic_numbers.linter import MagicNumberRule

        rule = MagicNumberRule()
        context = Mock()
        context.file_path = Path("src/responses.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}

        violations = rule.check(context)
        assert len(violations) == 0, "File with dict of int keys should be exempt"


class TestNonDefinitionFiles:
    """Test that non-definition files are still checked."""

    def test_regular_code_file_is_checked(self) -> None:
        """Regular code files should still be checked for magic numbers."""
        code = """
def calculate_price(quantity):
    if quantity > 100:
        return quantity * 0.9
    return quantity * 1.0

def get_timeout():
    return 3600  # Should be flagged
"""
        from src.linters.magic_numbers.linter import MagicNumberRule

        rule = MagicNumberRule()
        context = Mock()
        context.file_path = Path("src/pricing.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}

        violations = rule.check(context)
        # 0.9, 1.0 might be allowed, but 3600 should be flagged
        assert any("3600" in v.message for v in violations), (
            "Regular code should be checked for magic numbers"
        )

    def test_file_with_few_constants_is_checked(self) -> None:
        """Files with only a few constants should still be checked."""
        code = """
MAX_ITEMS = 50
TIMEOUT = 3600

def process_items(items):
    if len(items) > 999:  # Magic number
        raise ValueError("Too many items")
"""
        from src.linters.magic_numbers.linter import MagicNumberRule

        rule = MagicNumberRule()
        context = Mock()
        context.file_path = Path("src/processor.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}

        violations = rule.check(context)
        # 999 should be flagged (not a common constant)
        assert any("999" in v.message for v in violations), (
            "Files with few constants should still be checked"
        )


class TestExemptionConfig:
    """Test that exemption can be configured."""

    def test_exemption_can_be_disabled(self) -> None:
        """Definition file exemption can be disabled via config."""
        # Note: We use a dict with int keys (not UPPERCASE constants) because
        # individual UPPERCASE constant definitions are always exempt via context_analyzer.
        # The exempt_definition_files config controls whole-file exemption for definition patterns.
        code = """
status_messages = {
    200: "OK",
    201: "Created",
    404: "Not Found",
    500: "Internal Error",
    502: "Bad Gateway",
}
"""
        from src.linters.magic_numbers.linter import MagicNumberRule

        rule = MagicNumberRule()
        context = Mock()
        context.file_path = Path("src/responses.py")
        context.file_content = code
        context.language = "python"
        context.config = {"exempt_definition_files": False}
        context.metadata = {}

        violations = rule.check(context)
        # When exemption is disabled, dict int keys should be flagged
        assert len(violations) > 0, "Should flag when definition file exemption is disabled"
