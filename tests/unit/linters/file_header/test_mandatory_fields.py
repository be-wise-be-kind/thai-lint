"""
File: tests/unit/linters/file_header/test_mandatory_fields.py

Purpose: Test suite for mandatory field validation in Python file headers

Exports: TestMandatoryFieldsDetection test class with ~12 tests

Depends: pytest, unittest.mock, src.linters.file_header.linter.FileHeaderRule

Implements: TDD RED phase tests for required field detection (will initially fail)

Related: conftest.py for fixtures, PR_BREAKDOWN.md for field requirements

Overview: Comprehensive tests for detecting missing or invalid mandatory fields in
    Python file headers. Tests all required fields (Purpose, Scope, Overview, Dependencies,
    Exports, Interfaces, Implementation) and validates error messages and violation details.
    Follows TDD RED phase approach where all tests initially fail before implementation.

Usage: Run via pytest: `pytest tests/unit/linters/file_header/test_mandatory_fields.py`

Notes: All tests FAIL initially until FileHeaderRule implementation in PR3
"""

from pathlib import Path
from unittest.mock import Mock


class TestMandatoryFieldsDetection:
    """Tests for detecting missing mandatory fields."""

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
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}

        violations = rule.check(context)
        assert len(violations) >= 1
        assert any("Purpose" in v.message for v in violations)

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
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}

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
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}

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
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}

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
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}

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
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}

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
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}

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
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}

        violations = rule.check(context)
        # Should have violations for: Scope, Overview, Dependencies, Exports, Interfaces, Implementation
        assert len(violations) >= 6
        missing_fields = [v.message for v in violations]
        assert any("Scope" in msg for msg in missing_fields)
        assert any("Overview" in msg for msg in missing_fields)

    def test_accepts_all_mandatory_fields_present(self, valid_python_header):
        """Should not flag when all mandatory fields present."""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = valid_python_header
        context.language = "python"
        context.metadata = {}

        violations = rule.check(context)
        # Filter out any non-mandatory-field violations
        mandatory_violations = [v for v in violations if "missing" in v.message.lower()]
        assert len(mandatory_violations) == 0

    def test_detects_empty_purpose_field(self):
        """Should detect when Purpose field exists but is empty."""
        code = '''"""
Purpose:
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
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}

        violations = rule.check(context)
        assert len(violations) >= 1
        assert any(
            "Purpose" in v.message
            and ("empty" in v.message.lower() or "missing" in v.message.lower())
            for v in violations
        )

    def test_detects_whitespace_only_field(self):
        """Should detect when field contains only whitespace."""
        code = '''"""
Purpose:
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
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}

        violations = rule.check(context)
        assert len(violations) >= 1
        assert any("Purpose" in v.message for v in violations)

    def test_violation_messages_are_clear(self):
        """Should provide clear, actionable violation messages."""
        code = '''"""
Scope: Test scope
"""
'''
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}

        violations = rule.check(context)
        assert len(violations) >= 1
        # Messages should be clear and mention the field name
        for v in violations:
            assert len(v.message) > 10  # Not just field name
            assert v.message[0].isupper() or v.message.startswith("Missing")  # Proper sentence
