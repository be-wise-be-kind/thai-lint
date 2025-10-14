"""
File: tests/unit/linters/file_header/test_edge_cases.py
Purpose: Test suite for edge case handling in file header linter
Exports: TestFilesWithoutDocstrings, TestMalformedHeaders, TestSpecialContent, TestEmptyFiles
Depends: pytest, conftest.create_mock_context, src.linters.file_header.linter.FileHeaderRule
Related: test_python_header_validation.py, test_mandatory_fields.py

Overview:
    Tests for edge cases and unusual file structures including files without docstrings,
    malformed docstrings, very long headers, Unicode in headers, multi-line field values,
    empty files, and files with only comments. Validates robust error handling and
    graceful degradation. All tests initially fail (TDD RED phase) since FileHeaderRule
    does not exist yet.

Usage:
    pytest tests/unit/linters/file_header/test_edge_cases.py -v
"""

from tests.unit.linters.file_header.conftest import create_mock_context


class TestFilesWithoutDocstrings:
    """Test handling of files without docstrings."""

    def test_detects_file_without_docstring(self):
        """Should detect when file has no docstring at all."""
        code = """
import sys
import os

def my_function():
    pass
"""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(code, "test.py")
        violations = rule.check(context)

        # Should detect missing docstring
        assert len(violations) >= 1
        assert any("docstring" in v.message.lower() for v in violations)

    def test_handles_empty_file(self):
        """Should handle completely empty files."""
        code = ""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(code, "test.py")
        violations = rule.check(context)

        # Should detect missing docstring
        assert len(violations) >= 1


class TestMalformedHeaders:
    """Test handling of malformed headers."""

    def test_handles_unclosed_docstring(self):
        """Should handle unclosed docstring gracefully."""
        code = '''"""Purpose: Test module
Scope: Test
'''
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(code, "test.py")
        violations = rule.check(context)

        # Should detect syntax errors or treat as no docstring
        assert len(violations) >= 1

    def test_handles_single_line_docstring_no_fields(self):
        """Should handle single-line docstring without structured fields."""
        code = '''"""Just a brief description"""

import sys
'''
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(code, "test.py")
        violations = rule.check(context)

        # Should detect missing mandatory fields
        assert len(violations) >= 6  # Missing all 7 mandatory fields


class TestSpecialContent:
    """Test handling of special content in headers."""

    def test_handles_unicode_in_header(self):
        """Should handle Unicode characters in header fields."""
        code = '''"""
Purpose: Module with Unicode: 中文, Émojis 🚀
Scope: Testing Unicode support
Overview: Tests handling of non-ASCII characters including Chinese, accents, émojis
Dependencies: None
Exports: UnicodeHandler
Interfaces: process_unicode()
Implementation: UTF-8 encoding
"""
'''
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(code, "test.py")
        violations = rule.check(context)

        # Should parse Unicode without errors
        # May have no violations if all fields present
        assert isinstance(violations, list)

    def test_handles_very_long_header(self):
        """Should handle very long headers efficiently."""
        long_overview = "Very detailed overview. " * 100  # 2400+ characters
        code = f'''"""
Purpose: Module with very long header
Scope: Testing long content
Overview: {long_overview}
Dependencies: None
Exports: LongHandler
Interfaces: process()
Implementation: Standard
"""
'''
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(code, "test.py")
        violations = rule.check(context)

        # Should handle long content without performance issues
        assert isinstance(violations, list)

    def test_handles_multiline_field_values(self):
        """Should correctly parse multi-line field values."""
        code = '''"""
Purpose: Multi-line test module
Scope: Testing multi-line field parsing
Overview: This is a multi-line overview that spans
    several lines with proper indentation. It continues
    here and provides detailed information about the
    module functionality and purpose.
Dependencies: pytest, mock, requests
Exports: TestClass, HelperClass, utility_function
Interfaces: main_method(), helper_method(), process()
Implementation: Uses composition pattern with several
    helper classes for modularity
"""
'''
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(code, "test.py")
        violations = rule.check(context)

        # Should parse multi-line values correctly
        # Should not have violations for missing fields
        missing_violations = [v for v in violations if "missing" in v.message.lower()]
        assert len(missing_violations) == 0


class TestEmptyFiles:
    """Test handling of empty or minimal files."""

    def test_handles_file_with_only_comments(self):
        """Should handle files with only comments (no code)."""
        code = """# This is a comment
# Another comment
# No actual code here
"""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(code, "test.py")
        violations = rule.check(context)

        # Should detect missing docstring
        assert len(violations) >= 1
        assert any("docstring" in v.message.lower() for v in violations)

    def test_handles_file_with_only_shebang(self):
        """Should handle files with only shebang line."""
        code = """#!/usr/bin/env python3
"""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(code, "test.py")
        violations = rule.check(context)

        # Should detect missing docstring
        assert len(violations) >= 1

    def test_handles_whitespace_only_file(self):
        """Should handle files with only whitespace."""
        code = "    \n\n    \n"
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(code, "test.py")
        violations = rule.check(context)

        # Should detect missing docstring
        assert len(violations) >= 1
