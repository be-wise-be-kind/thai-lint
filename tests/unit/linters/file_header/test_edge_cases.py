"""
File: tests/unit/linters/file_header/test_edge_cases.py

Purpose: Test suite for edge cases in file header validation

Exports: TestEdgeCases test class with ~8 tests

Depends: pytest, unittest.mock, src.linters.file_header.linter.FileHeaderRule

Implements: TDD RED phase tests for edge case handling

Related: conftest.py for edge case fixtures

Overview: Tests edge cases and unusual scenarios including files without docstrings,
    malformed docstrings, very long headers, Unicode handling, multi-line field values,
    empty files, and files with only comments. Ensures robustness of linter
    implementation. TDD RED phase - all tests initially fail.

Usage: Run via pytest: `pytest tests/unit/linters/file_header/test_edge_cases.py`

Notes: All tests FAIL initially until FileHeaderRule edge case handling in PR3
"""

from pathlib import Path
from unittest.mock import Mock


class TestEdgeCases:
    """Tests for edge cases and unusual scenarios."""

    def test_handles_file_without_docstring(self, python_code_without_docstring):
        """Should handle Python file without any docstring."""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = python_code_without_docstring
        context.language = "python"
        context.metadata = {}

        violations = rule.check(context)
        # Should detect missing docstring/header
        assert len(violations) >= 1
        assert any(
            "docstring" in v.message.lower() or "header" in v.message.lower() for v in violations
        )

    def test_handles_empty_file(self, python_code_empty_file):
        """Should handle completely empty file."""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = python_code_empty_file
        context.language = "python"
        context.metadata = {}

        violations = rule.check(context)
        # Should detect missing header
        assert len(violations) >= 1

    def test_handles_malformed_docstring(self):
        """Should handle malformed docstring without field markers."""
        code = '''"""
This is just a plain docstring without any structured fields.
It contains multiple lines but no field markers like Purpose: or Scope:.
Just regular text that happens to be in a docstring.
"""

def func():
    pass
'''
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}

        violations = rule.check(context)
        # Should detect missing mandatory fields
        assert len(violations) >= 7  # All 7 mandatory fields missing

    def test_handles_very_long_header(self):
        """Should handle very long header text."""
        long_overview = "Long overview text. " * 500  # 10,000+ characters
        code = f'''"""
Purpose: Test purpose with very long header
Scope: Test scope
Overview: {long_overview}
Dependencies: None
Exports: TestClass
Interfaces: test_method()
Implementation: Standard implementation
"""

class TestClass:
    pass
'''
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}

        violations = rule.check(context)
        # Should handle long text without crashing
        assert isinstance(violations, list)

    def test_handles_unicode_characters(self):
        """Should handle Unicode characters in header."""
        code = '''"""
Purpose: Authentication with émojis 🔐 and special çharacters

Scope: User authentication módule with Ünîcødê

Overview: Handles authentication with Unicode support including émojis 🚀,
    accented characters (café, naïve, résumé), and various scripts (日本語, العربية)

Dependencies: None

Exports: AuthHandler

Interfaces: authenticate()

Implementation: Standard Unicode handling
"""

def authenticate():
    pass
'''
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}

        violations = rule.check(context)
        # Should handle Unicode without errors
        assert isinstance(violations, list)

    def test_handles_only_comments_no_code(self):
        """Should handle file with only comments, no code."""
        code = '''"""
Purpose: Test module
Scope: Testing
Overview: Test file with header but no code
Dependencies: None
Exports: Nothing
Interfaces: None
Implementation: No implementation
"""

# Just some comments
# No actual Python code
'''
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}

        violations = rule.check(context)
        # Should still validate header even if no code follows
        # Check that it doesn't crash
        assert isinstance(violations, list)

    def test_handles_syntax_error_in_code(self):
        """Should handle Python file with syntax errors in code."""
        code = '''"""
Purpose: Test
Scope: Test
Overview: Test
Dependencies: None
Exports: Test
Interfaces: test()
Implementation: Standard
"""

def func(  # Syntax error - unclosed parenthesis
    pass
'''
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}

        violations = rule.check(context)
        # Should still check header even if code has syntax errors
        # May fail to parse, but should handle gracefully
        assert isinstance(violations, list)

    def test_handles_multiline_field_with_colons(self):
        """Should handle multi-line fields containing colons."""
        code = '''"""
Purpose: Test purpose with colon: like this

Scope: Test scope

Overview: This overview contains colons: for example, ratios like 10:1 or
    time like 12:30, and URLs like http://example.com should not break parsing

Dependencies: pytest: for testing, mock: for mocking

Exports: TestClass

Interfaces: test_method()

Implementation: Standard
"""

class TestClass:
    pass
'''
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}

        violations = rule.check(context)
        # Should handle colons within field values correctly
        # Should not treat colons in values as new field markers
        missing_violations = [v for v in violations if "missing" in v.message.lower()]
        assert len(missing_violations) == 0  # All fields should be detected
