"""
File: tests/unit/linters/file_header/test_atemporal_language.py

Purpose: Test suite for atemporal language detection in file headers

Exports: TestAtemporalLanguageDetection test class with ~12 tests

Depends: pytest, unittest.mock, src.linters.file_header.linter.FileHeaderRule

Implements: TDD RED phase tests for temporal language pattern detection

Related: docs/ai-doc-standard.md for atemporal language requirements

Overview: Comprehensive tests for detecting temporal language patterns that violate
    atemporal documentation requirements. Tests date detection, temporal qualifiers,
    state change language, and future references. Validates that only present-tense,
    factual descriptions are accepted. Critical feature for enforcing documentation
    standards.

Usage: Run via pytest: `pytest tests/unit/linters/file_header/test_atemporal_language.py`

Notes: All tests FAIL initially (TDD RED phase) until implementation in PR3
"""

from pathlib import Path
from unittest.mock import Mock


class TestAtemporalLanguageDetection:
    """Tests for detecting temporal language violations."""

    def test_detects_iso_date_format(self):
        """Should detect ISO date format (YYYY-MM-DD)."""
        code = '''"""
Purpose: Created 2025-01-15 for user authentication
Scope: Authentication module
Overview: Handles user login and session management
Dependencies: oauth2
Exports: AuthHandler
Interfaces: authenticate()
Implementation: Standard
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
            "2025-01-15" in v.message
            or "temporal" in v.message.lower()
            or "date" in v.message.lower()
            for v in violations
        )

    def test_detects_month_year_format(self):
        """Should detect Month YYYY format."""
        code = '''"""
Purpose: Authentication handler
Scope: Updated January 2025 with new features
Overview: Handles user authentication
Dependencies: oauth2
Exports: AuthHandler
Interfaces: authenticate()
Implementation: Standard
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
            "temporal" in v.message.lower() or "January 2025" in v.message for v in violations
        )

    def test_detects_currently_qualifier(self):
        """Should detect 'currently' temporal qualifier."""
        code = '''"""
Purpose: Authentication handler
Scope: Authentication module
Overview: Currently supports OAuth and SAML authentication methods
Dependencies: oauth2
Exports: AuthHandler
Interfaces: authenticate()
Implementation: Standard
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
        assert any("temporal" in v.message.lower() or "currently" in v.message for v in violations)

    def test_detects_now_qualifier(self):
        """Should detect 'now' temporal qualifier."""
        code = '''"""
Purpose: Authentication handler
Scope: Authentication module
Overview: Now includes support for multi-factor authentication
Dependencies: oauth2
Exports: AuthHandler
Interfaces: authenticate()
Implementation: Standard
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
        assert any("temporal" in v.message.lower() or "now" in v.message for v in violations)

    def test_detects_recently_qualifier(self):
        """Should detect 'recently' temporal qualifier."""
        code = '''"""
Purpose: Authentication handler
Scope: Authentication module
Overview: Recently added support for OAuth2
Dependencies: oauth2
Exports: AuthHandler
Interfaces: authenticate()
Implementation: Standard
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
        assert any("temporal" in v.message.lower() or "recently" in v.message for v in violations)

    def test_detects_state_change_replaces(self):
        """Should detect state change language like 'replaces'."""
        code = '''"""
Purpose: Authentication handler
Scope: Authentication module
Overview: This replaces the old authentication system with a new implementation
Dependencies: oauth2
Exports: AuthHandler
Interfaces: authenticate()
Implementation: Standard
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
        assert any("temporal" in v.message.lower() or "replaces" in v.message for v in violations)

    def test_detects_state_change_migrated(self):
        """Should detect 'migrated from' state change language."""
        code = '''"""
Purpose: Authentication handler
Scope: Authentication module
Overview: Migrated from legacy auth system
Dependencies: oauth2
Exports: AuthHandler
Interfaces: authenticate()
Implementation: Standard
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
        assert any("temporal" in v.message.lower() or "migrated" in v.message for v in violations)

    def test_detects_future_reference_will_be(self):
        """Should detect future reference language."""
        code = '''"""
Purpose: Authentication handler
Scope: Authentication module
Overview: Will be extended to support biometric authentication
Dependencies: oauth2
Exports: AuthHandler
Interfaces: authenticate()
Implementation: Standard
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
            "temporal" in v.message.lower() or "future" in v.message.lower() for v in violations
        )

    def test_detects_future_reference_planned(self):
        """Should detect 'planned' future reference."""
        code = '''"""
Purpose: Authentication handler
Scope: Authentication module
Overview: Planned to add OAuth3 support
Dependencies: oauth2
Exports: AuthHandler
Interfaces: authenticate()
Implementation: Standard
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
        assert any("temporal" in v.message.lower() or "planned" in v.message for v in violations)

    def test_accepts_present_tense_factual(self, valid_python_header):
        """Should accept present-tense factual descriptions."""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = valid_python_header
        context.language = "python"
        context.metadata = {}

        violations = rule.check(context)
        # Filter only temporal violations
        temporal_violations = [
            v for v in violations if "temporal" in v.message.lower() or "date" in v.message.lower()
        ]
        assert len(temporal_violations) == 0

    def test_detects_multiple_temporal_violations(self):
        """Should detect multiple temporal violations in same header."""
        code = '''"""
Purpose: Created 2025-01-15 for authentication
Scope: Authentication module
Overview: Currently supports OAuth. Will be extended soon.
Dependencies: oauth2
Exports: AuthHandler
Interfaces: authenticate()
Implementation: Standard
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
        # Should detect at least 3 violations: date, "Currently", "Will be", "soon"
        temporal_violations = [
            v for v in violations if "temporal" in v.message.lower() or "date" in v.message.lower()
        ]
        assert len(temporal_violations) >= 3

    def test_violation_includes_line_number(self):
        """Should include line number in temporal violations."""
        code = '''"""
Purpose: Authentication handler
Scope: Authentication module
Overview: Currently supports OAuth
Dependencies: oauth2
Exports: AuthHandler
Interfaces: authenticate()
Implementation: Standard
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
        temporal_violations = [
            v for v in violations if "temporal" in v.message.lower() or "currently" in v.message
        ]
        if len(temporal_violations) > 0:
            v = temporal_violations[0]
            assert hasattr(v, "line")
            assert v.line > 0  # Line number should be positive
