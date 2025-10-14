"""
File: tests/unit/linters/file_header/test_mandatory_fields.py
Purpose: Test suite for mandatory field validation in Python file headers
Exports: TestMandatoryFieldDetection, TestMissingFieldMessages, TestAllFieldsPresent
Depends: pytest, conftest.create_mock_context, src.linters.file_header.linter.FileHeaderRule
Related: test_python_header_validation.py, test_atemporal_language.py

Overview:
    Comprehensive tests for detecting missing or invalid mandatory fields in Python
    file headers. Tests all required fields (Purpose, Scope, Overview, Dependencies,
    Exports, Interfaces, Implementation) and validates error messages and violation
    details. All tests initially fail (TDD RED phase) since FileHeaderRule does not
    exist yet.

Usage:
    pytest tests/unit/linters/file_header/test_mandatory_fields.py -v
"""

from tests.unit.linters.file_header.conftest import create_mock_context


class TestMandatoryFieldDetection:
    """Test detection of missing mandatory fields."""

    def test_detects_missing_purpose_field(self):
        """Should detect when Purpose field is missing."""
        code = '''"""
Scope: Test scope
Overview: Test overview
Dependencies: None
Exports: TestClass
Interfaces: test_method()
Implementation: Test implementation
"""
'''
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(code, "test.py")
        violations = rule.check(context)

        assert len(violations) >= 1
        assert any("Purpose" in v.message for v in violations)
        assert any("missing" in v.message.lower() for v in violations)

    def test_detects_missing_scope_field(self):
        """Should detect when Scope field is missing."""
        code = '''"""
Purpose: Test purpose
Overview: Test overview
Dependencies: None
Exports: TestClass
Interfaces: test_method()
Implementation: Test implementation
"""
'''
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(code, "test.py")
        violations = rule.check(context)

        assert len(violations) >= 1
        assert any("Scope" in v.message for v in violations)

    def test_detects_missing_overview_field(self):
        """Should detect when Overview field is missing."""
        code = '''"""
Purpose: Test purpose
Scope: Test scope
Dependencies: None
Exports: TestClass
Interfaces: test_method()
Implementation: Test implementation
"""
'''
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(code, "test.py")
        violations = rule.check(context)

        assert len(violations) >= 1
        assert any("Overview" in v.message for v in violations)

    def test_detects_missing_dependencies_field(self):
        """Should detect when Dependencies field is missing."""
        code = '''"""
Purpose: Test purpose
Scope: Test scope
Overview: Test overview
Exports: TestClass
Interfaces: test_method()
Implementation: Test implementation
"""
'''
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(code, "test.py")
        violations = rule.check(context)

        assert len(violations) >= 1
        assert any("Dependencies" in v.message for v in violations)

    def test_detects_missing_exports_field(self):
        """Should detect when Exports field is missing."""
        code = '''"""
Purpose: Test purpose
Scope: Test scope
Overview: Test overview
Dependencies: None
Interfaces: test_method()
Implementation: Test implementation
"""
'''
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(code, "test.py")
        violations = rule.check(context)

        assert len(violations) >= 1
        assert any("Exports" in v.message for v in violations)

    def test_detects_missing_interfaces_field(self):
        """Should detect when Interfaces field is missing."""
        code = '''"""
Purpose: Test purpose
Scope: Test scope
Overview: Test overview
Dependencies: None
Exports: TestClass
Implementation: Test implementation
"""
'''
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(code, "test.py")
        violations = rule.check(context)

        assert len(violations) >= 1
        assert any("Interfaces" in v.message for v in violations)

    def test_detects_missing_implementation_field(self):
        """Should detect when Implementation field is missing."""
        code = '''"""
Purpose: Test purpose
Scope: Test scope
Overview: Test overview
Dependencies: None
Exports: TestClass
Interfaces: test_method()
"""
'''
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(code, "test.py")
        violations = rule.check(context)

        assert len(violations) >= 1
        assert any("Implementation" in v.message for v in violations)

    def test_detects_multiple_missing_fields(self):
        """Should detect multiple missing mandatory fields."""
        code = '''"""
Purpose: Test purpose only
"""
'''
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(code, "test.py")
        violations = rule.check(context)

        # Should have violations for: Scope, Overview, Dependencies, Exports,
        # Interfaces, Implementation
        assert len(violations) >= 6
        missing_fields = [v.message for v in violations]
        assert any("Scope" in msg for msg in missing_fields)
        assert any("Overview" in msg for msg in missing_fields)
        assert any("Dependencies" in msg for msg in missing_fields)
        assert any("Exports" in msg for msg in missing_fields)
        assert any("Interfaces" in msg for msg in missing_fields)
        assert any("Implementation" in msg for msg in missing_fields)


class TestMissingFieldMessages:
    """Test violation message quality for missing fields."""

    def test_missing_field_violation_has_field_name(self):
        """Should include field name in violation message."""
        code = '"""Purpose: Test\\n"""'
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(code, "test.py")
        violations = rule.check(context)

        # Pick one violation and check it mentions a field name
        assert len(violations) >= 1
        # Should mention at least one missing field by name
        has_field_name = False
        for violation in violations:
            if any(
                field in violation.message
                for field in [
                    "Scope",
                    "Overview",
                    "Dependencies",
                    "Exports",
                    "Interfaces",
                    "Implementation",
                ]
            ):
                has_field_name = True
                break
        assert has_field_name

    def test_missing_field_violation_suggests_fix(self):
        """Should provide suggestion for fixing missing field."""
        code = '"""Purpose: Test\\n"""'
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(code, "test.py")
        violations = rule.check(context)

        assert len(violations) >= 1
        # Should have suggestion field (may be empty but attribute should exist)
        assert hasattr(violations[0], "suggestion") or "add" in violations[0].message.lower()


class TestAllFieldsPresent:
    """Test that no violations when all mandatory fields present."""

    def test_accepts_all_mandatory_fields_present(self):
        """Should not flag when all mandatory fields present."""
        code = '''"""
Purpose: Complete header with all fields
Scope: Test module scope
Overview: Comprehensive overview explaining module purpose and functionality
Dependencies: pytest, mock
Exports: TestClass, test_function
Interfaces: public_method(), another_method()
Implementation: Uses composition pattern with helper classes
"""
'''
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(code, "test.py")
        violations = rule.check(context)

        # Filter out any non-mandatory-field violations (like atemporal language)
        mandatory_violations = [v for v in violations if "missing" in v.message.lower()]
        assert len(mandatory_violations) == 0

    def test_accepts_empty_field_values_as_present(self):
        """Should accept empty values like 'None' or 'N/A' as present fields."""
        code = '''"""
Purpose: Module with minimal dependencies
Scope: Testing
Overview: Test module with no external dependencies
Dependencies: None
Exports: N/A
Interfaces: None
Implementation: Simple direct implementation
"""
'''
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(code, "test.py")
        violations = rule.check(context)

        # None/N/A should be acceptable as field values
        mandatory_violations = [v for v in violations if "missing" in v.message.lower()]
        assert len(mandatory_violations) == 0
