"""
File: tests/unit/linters/file_header/test_python_header_validation.py
Purpose: Test suite for Python file header structure validation
Exports: TestPythonDocstringExtraction, TestHeaderPresenceDetection, TestHeaderStructure
Depends: pytest, conftest.create_mock_context, src.linters.file_header.linter.FileHeaderRule
Related: test_mandatory_fields.py, test_atemporal_language.py

Overview:
    Tests basic header structure validation for Python files including docstring
    extraction, header presence detection, and format validation. Covers Python-specific
    docstring parsing and basic structural requirements before detailed field validation.
    All tests initially fail (TDD RED phase) since FileHeaderRule does not exist yet.

Usage:
    pytest tests/unit/linters/file_header/test_python_header_validation.py -v
"""

from tests.unit.linters.file_header.conftest import create_mock_context


class TestPythonDocstringExtraction:
    """Test extraction of module-level docstrings from Python files."""

    def test_extracts_module_docstring_triple_double_quotes(self):
        """Should extract docstring using triple double quotes."""
        code = '''"""
Purpose: Test module
Scope: Testing
Overview: Module for testing
"""

import sys
'''
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(code, "test.py")
        violations = rule.check(context)

        # Should not have "missing docstring" violation
        missing_docstring_violations = [v for v in violations if "docstring" in v.message.lower()]
        assert len(missing_docstring_violations) == 0

    def test_extracts_module_docstring_triple_single_quotes(self):
        """Should extract docstring using triple single quotes."""
        code = """'''
Purpose: Test module
Scope: Testing
Overview: Module for testing
'''

import sys
"""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(code, "test.py")
        violations = rule.check(context)

        # Should not have "missing docstring" violation
        missing_docstring_violations = [v for v in violations if "docstring" in v.message.lower()]
        assert len(missing_docstring_violations) == 0

    def test_ignores_class_and_function_docstrings(self):
        """Should only extract module-level docstring, not class/function docstrings."""
        code = '''"""
Purpose: Module header
"""

class MyClass:
    """Class docstring that is not the header."""
    pass
'''
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(code, "test.py")
        violations = rule.check(context)

        # Should extract "Purpose: Module header", not class docstring
        missing_docstring_violations = [v for v in violations if "docstring" in v.message.lower()]
        assert len(missing_docstring_violations) == 0


class TestHeaderPresenceDetection:
    """Test detection of missing or present file headers."""

    def test_detects_missing_docstring(self):
        """Should detect when file has no module-level docstring."""
        code = """
import sys

def my_function():
    pass
"""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(code, "test.py")
        violations = rule.check(context)

        # Should have violation for missing docstring
        assert len(violations) >= 1
        assert any("docstring" in v.message.lower() for v in violations)

    def test_detects_file_with_only_comments(self):
        """Should detect missing docstring in file with only comments."""
        code = """# This is just a comment
# Not a docstring

import sys
"""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(code, "test.py")
        violations = rule.check(context)

        # Should have violation for missing docstring
        assert len(violations) >= 1
        assert any("docstring" in v.message.lower() for v in violations)

    def test_accepts_file_with_valid_header(self):
        """Should not flag file with valid header structure."""
        code = '''"""
Purpose: Module with valid header
Scope: Testing module
Overview: Comprehensive test module for validating functionality
Dependencies: pytest
Exports: test_function
Interfaces: test_function()
Implementation: Test implementation pattern
"""

def test_function():
    pass
'''
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(code, "test.py")
        violations = rule.check(context)

        # May have violations for other reasons, but not missing docstring
        missing_docstring_violations = [v for v in violations if "docstring" in v.message.lower()]
        assert len(missing_docstring_violations) == 0


class TestHeaderStructure:
    """Test basic header structure requirements."""

    def test_accepts_multiline_field_values(self):
        """Should accept fields with multi-line values."""
        code = '''"""
Purpose: Multi-line test
Scope: Testing scope
Overview: This is a multi-line overview that spans
    multiple lines with proper indentation and continues
    across several lines to provide detailed information
Dependencies: pytest, mock
Exports: MyClass
Interfaces: my_method()
Implementation: Standard pattern
"""
'''
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(code, "test.py")
        violations = rule.check(context)

        # Should successfully parse multi-line field values
        # No violations expected for structure issues
        structure_violations = [
            v
            for v in violations
            if "structure" in v.message.lower() or "format" in v.message.lower()
        ]
        assert len(structure_violations) == 0

    def test_detects_malformed_docstring(self):
        """Should handle malformed docstrings gracefully."""
        code = '''"""Malformed docstring without proper fields
'''
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(code, "test.py")
        violations = rule.check(context)

        # Should have violations for missing mandatory fields
        assert len(violations) >= 1
