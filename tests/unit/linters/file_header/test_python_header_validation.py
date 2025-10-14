"""
File: tests/unit/linters/file_header/test_python_header_validation.py

Purpose: Test suite for basic Python file header structure validation

Exports: TestHeaderExtraction, TestBasicValidation test classes with ~10 tests total

Depends: pytest, unittest.mock, src.linters.file_header.linter.FileHeaderRule

Implements: TDD RED phase tests (will initially fail - no implementation exists)

Related: conftest.py for fixtures, test_mandatory_fields.py for field-specific tests

Overview: Tests basic Python file header validation including docstring extraction,
    header presence detection, and format validation. Covers fundamental header
    structure requirements without delving into specific field validation (covered
    in test_mandatory_fields.py) or atemporal language (test_atemporal_language.py).
    Tests use mock contexts following project patterns.

Usage: Run via pytest: `pytest tests/unit/linters/file_header/test_python_header_validation.py`

Notes: All tests will FAIL initially (TDD RED phase) until FileHeaderRule implementation exists
"""

from pathlib import Path
from unittest.mock import Mock


class TestHeaderExtraction:
    """Tests for extracting headers from Python files."""

    def test_extracts_module_docstring(self, valid_python_header):
        """Should extract module-level docstring from Python file."""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = valid_python_header
        context.language = "python"
        context.metadata = {}

        violations = rule.check(context)
        # Should not have "missing docstring" violation since valid header exists
        assert not any("docstring" in v.message.lower() for v in violations)

    def test_detects_missing_docstring(self, python_code_without_docstring):
        """Should detect when Python file has no docstring."""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = python_code_without_docstring
        context.language = "python"
        context.metadata = {}

        violations = rule.check(context)
        assert len(violations) >= 1
        assert any(
            "docstring" in v.message.lower() or "header" in v.message.lower() for v in violations
        )

    def test_handles_empty_file(self, python_code_empty_file):
        """Should handle empty Python file gracefully."""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = python_code_empty_file
        context.language = "python"
        context.metadata = {}

        violations = rule.check(context)
        assert len(violations) >= 1
        # Should report missing header/docstring


class TestBasicValidation:
    """Tests for basic header structure validation."""

    def test_accepts_valid_complete_header(self, valid_python_header):
        """Should not flag valid header with all required fields."""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = valid_python_header
        context.language = "python"
        context.metadata = {}

        violations = rule.check(context)
        # Should have 0 violations for complete, valid header
        assert len(violations) == 0

    def test_detects_malformed_docstring(self):
        """Should detect malformed docstring structure."""
        code = '''"""
        This is a malformed header without proper field structure
        Just some random text
        No field markers at all
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
        assert len(violations) >= 1

    def test_handles_multiline_field_values(self):
        """Should handle field values spanning multiple lines."""
        code = '''"""
Purpose: Multi-line purpose description
    that spans multiple lines with proper indentation

Scope: Module scope

Overview: This is a comprehensive overview
    that continues on multiple lines
    with proper indentation maintained

Dependencies: pytest, mock

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
        # Should accept multi-line field values
        # Check for absence of "missing" violations for fields that are present
        missing_violations = [v for v in violations if "missing" in v.message.lower()]
        assert len(missing_violations) == 0

    def test_validates_python_files_only(self):
        """Should only validate Python files, skip other languages."""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = Mock()
        context.file_path = Path("test.js")
        context.file_content = "// JavaScript code"
        context.language = "javascript"  # Non-Python
        context.metadata = {}

        violations = rule.check(context)
        # Should skip non-Python files in PR2/PR3 (Python-only implementation)
        assert len(violations) == 0

    def test_returns_violation_objects(self, python_code_without_docstring):
        """Should return proper Violation objects with required attributes."""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = python_code_without_docstring
        context.language = "python"
        context.metadata = {}

        violations = rule.check(context)
        if len(violations) > 0:
            v = violations[0]
            # Violation should have required attributes
            assert hasattr(v, "rule_id")
            assert hasattr(v, "message")
            assert hasattr(v, "file_path")
            assert hasattr(v, "line")
            assert hasattr(v, "severity")

    def test_rule_properties(self):
        """Should have correct rule properties."""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        assert rule.rule_id is not None
        assert isinstance(rule.rule_id, str)
        assert rule.rule_name is not None
        assert isinstance(rule.rule_name, str)
        assert rule.description is not None
        assert isinstance(rule.description, str)

    def test_handles_unicode_in_headers(self):
        """Should handle Unicode characters in header text."""
        code = '''"""
Purpose: Authentication with émojis 🔐 and spëcial çharacters

Scope: User authentication módule

Overview: Handles authentication with Ünicode support

Dependencies: None

Exports: AuthHandler

Interfaces: authenticate()

Implementation: Standard approach
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
        # Check that it doesn't crash and can still detect fields
        assert isinstance(violations, list)
